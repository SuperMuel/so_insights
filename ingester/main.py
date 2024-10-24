import asyncio
import logging
from datetime import datetime
from typing import Optional

from fastapi import FastAPI
from src.mongo_db_operations import insert_articles_in_mongodb
from src.rss import ingest_rss_feed
from src.vector_indexing import (
    get_pinecone_index,
    sync_workspace_with_vector_db,
)
import typer
from beanie import UpdateResponse
from beanie.odm.operators.update.general import Set
from dotenv import load_dotenv
from duckduckgo_search import AsyncDDGS
from langchain_voyageai import VoyageAIEmbeddings
from src.ingester_settings import IngesterSettings
from src.search import (
    perform_search_and_deduplicate_results,
)

from shared.db import get_client, my_init_beanie
from shared.models import (
    Article,
    IngestionConfig,
    IngestionConfigType,
    IngestionRun,
    RssIngestionConfig,
    SearchIngestionConfig,
    Status,
    Workspace,
    utc_datetime_factory,
)
import uvicorn

load_dotenv()

settings = IngesterSettings()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)

logger = logging.getLogger(__name__)

api = FastAPI()


@api.get("/healthz")
async def healthz():
    return {"status": "ok"}


async def run_server():
    config = uvicorn.Config(
        app=api, host="0.0.0.0", port=settings.PORT, log_level="info"
    )
    server = uvicorn.Server(config)
    await server.serve()


app = typer.Typer()

embeddings = VoyageAIEmbeddings(  # type:ignore # Arguments missing for parameters "_client", "_aclient"
    voyage_api_key=settings.VOYAGEAI_API_KEY,
    model=settings.EMBEDDING_MODEL,
    batch_size=settings.EMBEDDING_BATCH_SIZE,
)


async def handle_search_ingestion_config(
    ddgs: AsyncDDGS,
    run: IngestionRun,
    config: SearchIngestionConfig,
) -> list[Article]:
    """
    Handles the ingestion process for a search-based ingestion configuration.

    This function performs searches based on the provided configuration, processes the results,
    and converts them into Article objects.

    Args:
        ddgs (AsyncDDGS): An instance of the AsyncDDGS client for performing searches.
        run (IngestionRun): The current ingestion run object.
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

    articles = await perform_search_and_deduplicate_results(
        ddgs=ddgs,
        queries=config.queries,
        region=config.region,
        max_results=max_results,
        time_limit=time_limit,
    )

    return [
        Article(
            workspace_id=run.workspace_id,
            region=config.region,
            ingestion_run_id=run.id,
            **article.model_dump(),
        )
        for article in articles
    ]


async def handle_rss_ingestion_config(
    config: RssIngestionConfig,
    run: IngestionRun,
) -> list[Article]:
    """
    Handles the ingestion process for an RSS-based ingestion configuration.

    This function fetches and processes articles from the specified RSS feed.

    Args:
        config (RssIngestionConfig): The RSS ingestion configuration.
        run (IngestionRun): The current ingestion run object.

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


async def handle_ingestion_run(run: IngestionRun, ddgs: AsyncDDGS):
    """
    Manages the entire process of an ingestion run.

    This function coordinates the ingestion process, handling both search and RSS configurations.
    It updates the run status, processes articles, and syncs them with the vector database.

    Args:
        run (IngestionRun): The ingestion run to be processed.
        ddgs (AsyncDDGS): An instance of the AsyncDDGS client for performing searches.
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
                articles: list[Article] = await handle_search_ingestion_config(
                    ddgs=ddgs, run=run, config=config
                )
            case IngestionConfigType.rss:
                assert isinstance(config, RssIngestionConfig)
                articles = await handle_rss_ingestion_config(config, run)

    except Exception as e:
        logger.error(f"Error while processing ingestion run: {e}")
        return await run.mark_as_finished(Status.failed, error=str(e))

    assert all([article.ingestion_run_id for article in articles])
    run.n_inserted = await insert_articles_in_mongodb(articles)

    workspace = await Workspace.get(run.workspace_id)
    assert workspace and workspace.id

    await sync_workspace_with_vector_db(
        workspace=workspace,
        index=get_pinecone_index(workspace.id, embeddings),
        force=False,
    )

    await run.mark_as_finished(Status.completed)

    assert run.end_at and run.status in [Status.completed, Status.failed]
    logger.info(
        f"Finished processing ingestion run. Found {run.n_inserted} new articles."
    )


async def setup():
    mongo_client = get_client(settings.MONGODB_URI)
    await my_init_beanie(mongo_client)

    logger.info("Setting up DDGS client...")
    proxy = str(settings.PROXY) if settings.PROXY else None

    if proxy:
        logger.info(f"Using proxy: {proxy}")

    ddgs = AsyncDDGS(
        timeout=settings.QUERY_TIMEOUT,
        proxy=proxy,
    )

    return mongo_client, ddgs


@app.command()
def create_ingestion_task(
    config_id: str,
):
    """
    Creates an ingestion task for a single IngestionConfig.
    """

    async def _create_ingestion_task():
        mongo_client, _ = await setup()

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
        mongo_client, _ = await setup()

        if workspace_id:
            workspace = await Workspace.get(workspace_id)
            if not workspace:
                typer.echo(f"Workspace with id {workspace_id} not found.")
                return
            workspaces = [workspace]
        else:
            workspaces = await Workspace.find_all().to_list()

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
    force: bool = typer.Option(
        False, "--force", help="Force upsert even if the articles are already indexed"
    ),
):
    """Sync articles from MongoDB to the vector database for a single workspace or all workspaces"""

    async def _sync_vector_db():
        mongo_client, _ = await setup()

        if workspace_id:
            workspace = await Workspace.get(workspace_id)
            if not workspace:
                typer.echo(f"Workspace with id {workspace_id} not found.")
                return
            workspaces = [workspace]
        else:
            workspaces = await Workspace.find_all().to_list()

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
        settings.POLLING_INTERVAL_S,
        "--interval",
        "-i",
        help="Check interval in seconds",
    ),
    max_runtime: int = typer.Option(
        settings.MAX_RUNTIME_S,
        "--max-runtime",
        "-r",
        help="Maximum runtime in seconds before exiting",
    ),
):
    """Watch for pending ingestion runs and execute them."""

    async def _watch():
        mongo_client, ddgs = await setup()

        server_task = asyncio.create_task(run_server())

        logger.info(f"Starting watch loop. Will run for up to {max_runtime} seconds.")
        start_time = datetime.now()

        try:
            while (datetime.now() - start_time).total_seconds() < max_runtime:
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

                await handle_ingestion_run(pending_run, ddgs)

                if (datetime.now() - start_time).total_seconds() >= max_runtime:
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


if __name__ == "__main__":
    app()
