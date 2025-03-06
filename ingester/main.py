import asyncio
import logging
from datetime import datetime, timezone, timedelta
from typing import Optional

import typer
import uvicorn
from beanie import UpdateResponse, PydanticObjectId
from beanie.odm.operators.update.general import Set
from dotenv import load_dotenv
from fastapi import FastAPI
from langchain_voyageai import VoyageAIEmbeddings
from pydantic import SecretStr
from src.content_cleaner import ArticleContentCleaner
from src.content_fetcher import ContentFetcher
from src.ingester_settings import ingester_settings
from src.mongo_db_operations import insert_articles_in_mongodb
from src.rss import ingest_rss_feed
from src.search_providers.base import BaseSearchProvider, deduplicate_articles_by_url
from src.url_to_markdown_converters import FirecrawlUrlToMarkdown
from src.vector_indexing import (
    get_pinecone_index,
    sync_workspace_with_vector_db,
)

from shared.db import get_client, my_init_beanie
from shared.models import (
    Article,
    IngestionConfig,
    IngestionConfigType,
    IngestionRun,
    Organization,
    RssIngestionConfig,
    SearchIngestionConfig,
    Status,
    Workspace,
    utc_datetime_factory,
)

load_dotenv()


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)

logger = logging.getLogger(__name__)

api = FastAPI()


@api.get("/")
async def root():
    return {
        "message": "Welcome to so-insights-ingester",
        "ingester_settings": ingester_settings.model_dump(),
    }


@api.get("/healthz")
async def healthz():
    return {"status": "ok"}


async def run_server():
    config = uvicorn.Config(
        app=api, host="0.0.0.0", port=ingester_settings.PORT, log_level="info"
    )
    server = uvicorn.Server(config)
    await server.serve()


app = typer.Typer(no_args_is_help=True)

logger.info(
    f"Setting up VoyageAI embeddings with model '{ingester_settings.EMBEDDING_MODEL}' and batch size {ingester_settings.EMBEDDING_BATCH_SIZE}"
)
embeddings = VoyageAIEmbeddings(  # type:ignore # Arguments missing for parameters "_client", "_aclient"
    voyage_api_key=ingester_settings.VOYAGEAI_API_KEY.get_secret_value(),  # type: ignore
    model=ingester_settings.EMBEDDING_MODEL,
    batch_size=ingester_settings.EMBEDDING_BATCH_SIZE,
)


async def handle_search_ingestion_run(
    run: IngestionRun,
    *,
    search_provider: BaseSearchProvider,
    config: SearchIngestionConfig,
) -> list[Article]:
    """
    Handles the ingestion process for a search-based ingestion configuration.

    This function performs searches based on the provided configuration, processes the results,
    and converts them into Article objects.

    Args:
        run (IngestionRun): The current ingestion run object.
        search_provider (BaseSearchProvider): The search provider to be used for search-based ingestion.
        config (SearchIngestionConfig): The search ingestion configuration.

    Returns:
        list[Article]: A list of Article objects created from the search results.

    Raises:
        ValueError: If no queries are provided in the configuration.
    """
    assert isinstance(config, SearchIngestionConfig)
    assert run.status == Status.running and run.start_at

    if not config.queries:
        raise ValueError("No queries to process")

    logger.info(
        f"Processing SearchIngestionConfig {config.id} for workspace {run.workspace_id}"
        f"({config.title}, {len(config.queries)} queries, {config.time_limit=}, {config.max_results=})"
    )

    max_results, time_limit = await config.get_max_results_and_time_limit()

    articles = await search_provider.batch_search(
        queries=config.queries,
        region=config.region,
        max_results=max_results,
        time_limit=time_limit,
    )

    logger.info(f"Found {len(articles)} (undeduplicated) articles")
    articles = deduplicate_articles_by_url(articles)
    logger.info(f"Deduplicated to {len(articles)} articles")

    return [
        Article(
            workspace_id=run.workspace_id,
            region=config.region,
            ingestion_run_id=run.id,
            **article.model_dump(),
        )
        for article in articles
    ]


async def handle_rss_ingestion_run(
    run: IngestionRun,
    *,
    config: RssIngestionConfig,
) -> list[Article]:
    """
    Handles the ingestion process for an RSS-based ingestion configuration.

    This function fetches and processes articles from the specified RSS feed.

    Args:
        run (IngestionRun): The current ingestion run object.
        config (RssIngestionConfig): The RSS ingestion configuration.

    Returns:
        list[Article]: A list of Article objects created from the RSS feed entries.
    """

    assert run.status == Status.running and run.start_at

    logger.info(
        f"Processing RssIngestionConfig {config.id} for workspace {run.workspace_id}"
        f"({config.title}, {config.rss_feed_url=})"
    )

    assert run.id
    return await ingest_rss_feed(config, ingestion_run_id=run.id)


async def handle_ingestion_run(
    run: IngestionRun,
    *,
    search_provider: BaseSearchProvider,
    content_fetcher: ContentFetcher,
):
    """
    Manages the entire process of an ingestion run.

    This function coordinates the ingestion process, handling both search and RSS configurations.
    It updates the run status, processes articles, and syncs them with the vector database.

    Args:
        run (IngestionRun): The ingestion run to be processed.
        search_provider (BaseSearchProvider): The search provider to be used for search-based ingestion.
    """
    assert run.status in [Status.pending, Status.running]

    await run.mark_as_started()

    config: IngestionConfig | None = await IngestionConfig.get(
        run.config_id, with_children=True
    )

    if not config:
        msg = f"Config with id {run.config_id} not found."
        return await run.mark_as_finished(Status.failed, error=msg)

    config.last_run_at = utc_datetime_factory()
    await config.replace()

    logger.info(f"Handling {config.type.upper()} ingestion config '{config.title}'")

    try:
        match config.type:
            case IngestionConfigType.search:
                assert isinstance(config, SearchIngestionConfig)
                articles = await handle_search_ingestion_run(
                    run, search_provider=search_provider, config=config
                )
            case IngestionConfigType.rss:
                assert isinstance(config, RssIngestionConfig)
                articles = await handle_rss_ingestion_run(run, config=config)

    except Exception as e:
        logger.error(f"Error while processing ingestion run: {e}")
        return await run.mark_as_finished(Status.failed, error=str(e))

    assert all(
        [article.ingestion_run_id for article in articles]
    ), "Some articles have no ingestion run id"
    assert all(
        [article.provider for article in articles]
    ), "Some articles have no provider"

    ### Fetching article contents, if enabled
    workspace = await Workspace.get(run.workspace_id)
    assert workspace and workspace.id

    organization = await Organization.get(workspace.organization_id)
    assert organization and organization.id

    if organization.content_analysis_enabled:
        try:
            # First check which articles are new by trying to find existing ones with same workspace_id and url
            existing_articles = await Article.find(
                {
                    "workspace_id": workspace.id,
                    "url": {"$in": [article.url for article in articles]},
                }
            ).to_list()

            logger.info(f"Found {len(existing_articles)} existing articles")

            existing_urls = {article.url for article in existing_articles}
            new_articles = [
                article for article in articles if article.url not in existing_urls
            ]

            if new_articles:
                logger.info(f"Fetching content for {len(new_articles)} new articles...")
                results = await content_fetcher.abatch_convert_and_clean(
                    urls=[article.url for article in new_articles]
                )
                assert len(new_articles) == len(results)
                for article, result in zip(new_articles, results):
                    if isinstance(result, Exception):
                        article.content_cleaning_error = str(result)
                    else:
                        article.content = (
                            result.content_cleaner_output.cleaned_article_content
                        )
                        article.content_cleaning_error = (
                            result.content_cleaner_output.error
                        )
                        article.content_fetching_result = result

                logger.info("Content fetching complete.")
            else:
                logger.info("No new articles to fetch content for.")
        except Exception as e:
            logger.error(
                f"Error while fetching article content: ({e.__class__.__name__}): {str(e)}"
            )
            return await run.mark_as_finished(Status.failed, error=str(e))

    run.n_inserted = await insert_articles_in_mongodb(articles)

    await run.mark_as_finished(Status.completed)

    assert run.end_at and run.status in [Status.completed, Status.failed]
    logger.info(
        f"Finished processing ingestion run. Found {run.n_inserted} new articles."
    )

    try:
        await sync_workspace_with_vector_db(
            workspace=workspace,
            index=get_pinecone_index(workspace.id, embeddings),
            force=False,
        )

    except Exception as e:
        logger.error(
            f"Error while syncing articles with vector db. Ingestion Run is stil marked as succesfull. Error :  {e.__class__.__name__}: {str(e)}"
        )
        # Don't mark the ingestion run as failed. A vector indexing error is not tied to the ingestion run itself.
        raise e


async def setup():
    mongo_client = get_client(ingester_settings.MONGODB_URI)
    await my_init_beanie(mongo_client)

    match ingester_settings.SEARCH_PROVIDER:
        case "duckduckgo":
            from duckduckgo_search import AsyncDDGS
            from src.search_providers.duckduckgo_provider import DuckDuckGoProvider

            logger.info("Setting up DDGS client...")
            if proxy := (
                ingester_settings.PROXY.get_secret_value()
                if isinstance(ingester_settings.PROXY, SecretStr)
                else str(ingester_settings.PROXY)
                if ingester_settings.PROXY
                else None
            ):
                logger.info(f"Using proxy: {proxy}")

            search_provider = DuckDuckGoProvider(
                AsyncDDGS(
                    timeout=ingester_settings.QUERY_TIMEOUT,
                    proxy=proxy,
                )
            )
        case "serperdev":
            from src.search_providers.serperdev_provider import SerperdevProvider

            api_key = ingester_settings.SERPERDEV_API_KEY

            assert (
                api_key is not None and len(api_key.get_secret_value()) > 0
            ), "SerperDev API key is required"

            search_provider = SerperdevProvider(api_key=api_key)
        case _:
            raise ValueError(
                f"Unknown search provider: {ingester_settings.SEARCH_PROVIDER}"
            )

    content_fetcher = ContentFetcher(
        url_to_markdown_converter=FirecrawlUrlToMarkdown(),
        cleaner=ArticleContentCleaner(),
    )

    return mongo_client, search_provider, content_fetcher


@app.command()
def create_ingestion_task(
    config_id: str,
):
    """
    Creates an ingestion task for a single IngestionConfig.
    """

    async def _create_ingestion_task():
        mongo_client, _, __ = await setup()

        config = await IngestionConfig.get(config_id, with_children=True)
        if not config:
            typer.echo(f"Config with id {config_id} not found.")
            return
        assert config.id

        run = await IngestionRun(
            workspace_id=config.workspace_id,
            config_id=config.id,
            status=Status.pending,
        ).create()

        logger.info(
            f"Created ingestion run {run.id} for config {config.id} ({config.title})"
        )

        mongo_client.close()

    asyncio.run(_create_ingestion_task())


@app.command()
def create_ingestion_tasks(
    workspace_id: Optional[str] = typer.Option(
        None,
        "-w",
        "--workspace-id",
        help="To create ingestion tasks for a specific workspace. If not provided, tasks will be created for all workspaces.",
    ),
    type: Optional[IngestionConfigType] = typer.Option(
        None,
        "-t",
        "--type",
        help="To create ingestion tasks for a specific type of ingestion config. If not provided, tasks will be created for all types.",
    ),
):
    """Create ingestion tasks for all IngestionConfigs of a workspace or all workspaces"""

    async def _create_ingestion_tasks():
        mongo_client, _, __ = await setup()

        if workspace_id:
            workspace = await Workspace.get(workspace_id)
            if not workspace:
                typer.echo(f"Workspace with id {workspace_id} not found.")
                return
            workspaces = [workspace]
        else:
            workspaces = await Workspace.get_active_workspaces().to_list()

        for workspace in workspaces:
            assert workspace.id
            logger.info(
                f"Creating ingestion tasks for workspace {workspace.id} ({workspace.name})"
            )

            configs = await IngestionConfig.find(
                IngestionConfig.workspace_id == workspace.id,
                *([IngestionConfig.type == type] if type else []),
                with_children=True,
            ).to_list()

            for config in configs:
                assert config.id

                run = await IngestionRun(
                    workspace_id=workspace.id,
                    config_id=config.id,
                    status=Status.pending,
                ).create()

                logger.info(f"\tCreated ingestion run {run.id} for config {config.id}")

        mongo_client.close()

    asyncio.run(_create_ingestion_tasks())


@app.command()
def sync_vector_db(
    workspace_id: Optional[str] = typer.Option(
        None,
        "-w",
        "--workspace-id",
        help="To upsert articles for a specific workspace. If not provided, articles will be upserted for all workspaces.",
    ),
    exclude_workspace_ids: Optional[list[str]] = typer.Option(
        None,
        "-e",
        "--exclude-workspace-ids",
        help="To exclude specific workspaces from the upsert. Provide a comma-separated list of workspace ids.",
    ),
    force: bool = typer.Option(
        False, "--force", help="Force upsert even if the articles are already indexed"
    ),
):
    """Sync articles from MongoDB to the vector database for a single workspace or all workspaces"""

    async def _sync_vector_db():
        mongo_client, _, __ = await setup()

        if workspace_id:
            workspace = await Workspace.get(workspace_id)
            if not workspace:
                typer.echo(f"Workspace with id {workspace_id} not found.")
                return
            workspaces = [workspace]
        else:
            workspaces = await Workspace.get_active_workspaces().to_list()

        if exclude_workspace_ids:
            assert all(
                "," not in id for id in exclude_workspace_ids
            ), "Don't use comas to separate workspace ids. Use multiple `-e` instead"
            logger.info(f"Excluding {exclude_workspace_ids}")
            workspaces = [
                workspace
                for workspace in workspaces
                if str(workspace.id) not in exclude_workspace_ids
            ]

        logger.info(f"Syncing {len(workspaces)} workspaces with vector db.")

        for i, workspace in enumerate(workspaces):
            logger.info(
                f"Upserting articles for workspace {workspace.id} ({workspace.name}) ({i + 1}/{len(workspaces)})"
            )
            assert workspace.id
            index = get_pinecone_index(workspace.id, embeddings)
            await sync_workspace_with_vector_db(workspace, index, force=force)

        mongo_client.close()

    asyncio.run(_sync_vector_db())


@app.command()
def watch(
    interval: int = typer.Option(
        ingester_settings.POLLING_INTERVAL_S,
        "--interval",
        "-i",
        help="Check interval in seconds",
    ),
    max_runtime: int = typer.Option(
        ingester_settings.MAX_RUNTIME_S,
        "--max-runtime",
        "-r",
        help="Maximum runtime in seconds before exiting",
    ),
):
    """Watch for pending ingestion runs and execute them."""

    async def _watch():
        mongo_client, search_provider, content_fetcher = await setup()

        server_task = asyncio.create_task(run_server())

        logger.info(f"Starting watch loop. Will run for up to {max_runtime} seconds.")
        logger.info(ingester_settings.model_dump())
        start_time = datetime.now(tz=timezone.utc)

        try:
            while (
                datetime.now(tz=timezone.utc) - start_time
            ).total_seconds() < max_runtime:
                logger.info("Checking for pending ingestion runs")
                pending_run = await IngestionRun.find_one(
                    IngestionRun.status == Status.pending
                ).update_one(
                    Set({IngestionRun.status: Status.running}),
                    response_type=UpdateResponse.NEW_DOCUMENT,
                )

                assert isinstance(pending_run, IngestionRun) or pending_run is None

                if not pending_run:
                    await asyncio.sleep(interval)
                    continue

                logger.info(
                    f"Processing ingestion run {pending_run.id} for workspace {pending_run.workspace_id}"
                )

                await handle_ingestion_run(
                    pending_run,
                    search_provider=search_provider,
                    content_fetcher=content_fetcher,
                )

                if (
                    datetime.now(tz=timezone.utc) - start_time
                ).total_seconds() >= max_runtime:
                    logger.info("Reached maximum runtime. Exiting.")
                    break
        finally:
            logger.info("Watch function completed. Shutting down server.")
            server_task.cancel()
            try:
                await server_task
            except asyncio.CancelledError:
                pass
            mongo_client.close()

    asyncio.run(_watch())


@app.command()
def timeout_stalled_runs(
    timeout_hours: float = typer.Option(
        2.0,
        "--timeout-hours",
        "-t",
        help="Number of hours after which an in-progress run should be marked as failed (default: 2.0)",
    ),
    workspace_id: Optional[str] = typer.Option(
        None,
        "-w",
        "--workspace-id",
        help="To timeout runs for a specific workspace. If not provided, runs from all workspaces will be checked.",
    ),
    dry_run: bool = typer.Option(
        False,
        "--dry-run",
        "-d",
        help="Show which runs would be marked as failed without actually updating them.",
    ),
):
    """
    Checks for ingestion runs that have been in progress for too long and marks them as failed.

    This is useful for handling runs that might have crashed or stalled without properly updating their status.
    The default timeout is 2 hours, but can be customized.

    Use --dry-run to preview which runs would be affected without making any changes.
    """

    async def _timeout_stalled_runs():
        mongo_client, _, _ = await setup()

        timeout_datetime = datetime.now(tz=timezone.utc) - timedelta(
            hours=timeout_hours
        )

        # Find all runs that are still in progress and started before the timeout threshold
        # First find runs with status "running" and make sure start_at exists
        find_query = IngestionRun.find(
            IngestionRun.status == Status.running,
            IngestionRun.start_at != None,
            IngestionRun.start_at < timeout_datetime,  # type: ignore
        )

        if workspace_id:
            # Filter by workspace_id if provided
            find_query = find_query.find(
                IngestionRun.workspace_id == PydanticObjectId(workspace_id)
            )

        stalled_runs = await find_query.to_list()

        if dry_run:
            typer.echo("DRY RUN MODE: No runs will actually be updated")

        if not stalled_runs:
            typer.echo(
                f"No stalled ingestion runs found (timeout: {timeout_hours} hours)"
            )
            return

        typer.echo(
            f"Found {len(stalled_runs)} stalled ingestion runs (timeout: {timeout_hours} hours)"
        )

        # Fetch workspaces for all runs for display purposes
        workspace_ids = {run.workspace_id for run in stalled_runs if run.workspace_id}
        workspaces = {
            workspace.id: workspace
            for workspace in await Workspace.find(
                {"_id": {"$in": list(workspace_ids)}}
            ).to_list()
        }

        for run in stalled_runs:
            assert run.start_at is not None  # We've already filtered these out

            # Get workspace name for better logging
            workspace_name = "Unknown"
            if run.workspace_id and run.workspace_id in workspaces:
                workspace_name = workspaces[run.workspace_id].name

            # Handle timezone conversion properly
            if run.start_at.tzinfo is None:
                # If naive datetime, assume it's in UTC
                start_at_with_tz = run.start_at.replace(tzinfo=timezone.utc)
            else:
                # If datetime already has timezone, ensure it's in UTC
                start_at_with_tz = run.start_at.astimezone(timezone.utc)

            duration = datetime.now(tz=timezone.utc) - start_at_with_tz
            duration_hours = duration.total_seconds() / 3600

            if dry_run:
                typer.echo(
                    f"Would mark run {run.id} ({workspace_name}) as failed (in progress for {duration_hours:.2f} hours)"
                )
            else:
                typer.echo(
                    f"Marking run {run.id} ({workspace_name}) as failed (in progress for {duration_hours:.2f} hours)"
                )

                # Mark the run as failed
                await run.mark_as_finished(
                    Status.failed,
                    error=f"Timeout. Automatically marked as failed after being in progress for {duration_hours:.2f} hours",
                )

        mongo_client.close()

    asyncio.run(_timeout_stalled_runs())


if __name__ == "__main__":
    app()
