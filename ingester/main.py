import asyncio
import logging
from datetime import datetime, timedelta
from itertools import batched
from typing import Callable, Optional

from fastapi import FastAPI
from shared.region import Region
from src.rss import ingest_rss_feed
import typer
from beanie import BulkWriter, PydanticObjectId, UpdateResponse
from beanie.odm.operators.update.general import Set
from dotenv import load_dotenv
from duckduckgo_search import AsyncDDGS
from langchain_core.documents import Document
from langchain_pinecone import PineconeVectorStore
from langchain_voyageai import VoyageAIEmbeddings
from pymongo.errors import BulkWriteError
from src.ingester_settings import IngesterSettings
from src.search import BaseArticle, perform_search

from shared.db import get_client, my_init_beanie
from shared.models import (
    Article,
    IngestionConfig,
    IngestionConfigType,
    IngestionRun,
    RssIngestionConfig,
    SearchIngestionConfig,
    Status,
    TimeLimit,
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


PineconeIndexGetter = Callable[[str | PydanticObjectId], PineconeVectorStore]


def get_pinecone_index(namespace: str | PydanticObjectId) -> PineconeVectorStore:
    return PineconeVectorStore(
        pinecone_api_key=settings.PINECONE_API_KEY,
        index_name=settings.PINECONE_INDEX,
        embedding=embeddings,
        namespace=str(namespace),
    )


def has_recent_run(last_run: IngestionRun, t: timedelta) -> bool:
    assert t.total_seconds() > 0, "t must be greater than 0 seconds"

    end_at = last_run.end_at

    assert (
        end_at is not None
    ), "You should first verify that the last run has finished, and thus has an end_at date"

    return end_at > datetime.now() - t


def deduplicate_articles(articles: list[BaseArticle]) -> list[BaseArticle]:
    return list({article.url: article for article in articles}.values())


def article_to_document(article: Article) -> Document:
    return Document(
        page_content=f"{article.title}\n{article.body}",
        id=str(article.id),
        metadata={
            "title": article.title,
            "url": str(article.url),
            "body": article.body,
            "found_at": article.found_at.timestamp(),
            "date": article.date.timestamp(),
        },
    )


async def index_not_indexed_articles(
    pinecone_index: PineconeVectorStore,
) -> list[Article]:
    assert pinecone_index._namespace
    not_indexed = await Article.find(
        Article.workspace_id == PydanticObjectId(pinecone_index._namespace),
        Article.vector_indexed == False,  # noqa: E712
    ).to_list()

    if not not_indexed:
        logger.info("No articles to index")
        return []

    logger.info(f"Indexing {len(not_indexed)} articles")

    documents = list(map(article_to_document, not_indexed))

    await pinecone_index.aadd_documents(
        documents, ids=[str(article.id) for article in not_indexed]
    )

    return not_indexed


async def mark_articles_as_vector_indexed(articles: list[Article]):
    logger.info(f"Marking {len(articles)} articles as vector indexed")
    async with BulkWriter() as bulk_writer:
        for article in articles:
            await article.update(
                Set({Article.vector_indexed: True}),
                bulk_writer=bulk_writer,
            )
    logger.info("Marked as vector indexed.")


async def perform_search_and_deduplicate_results(
    ddgs: AsyncDDGS,
    queries: list[str],
    region: Region,
    max_results: int,
    time_limit: TimeLimit,
) -> list[BaseArticle]:
    """Performs the search for all queries of the SearchConfig, deduplicates the results and returns the number of successful queries and the deduplicated articles"""

    result = await perform_search(
        ddgs,
        queries=queries,
        region=region,
        max_results=max_results,
        time_limit=time_limit,
        verbose=settings.VERBOSE_SEARCH,
    )
    logger.info(
        f"{result.successfull_queries}/{len(queries)} queries were successful. "
        f"Found {len(result.articles)} (undeduplicated) articles"
    )
    articles = deduplicate_articles(result.articles)
    logger.info(f"Deduplicated to {len(articles)} articles")
    return articles


async def insert_articles_in_mongodb(
    articles: list[Article],
) -> int:
    assert all([article.ingestion_run_id for article in articles])

    if not articles:
        logger.info("No articles to upsert")
        return 0

    logger.info("Upserting articles to mongodb")
    try:
        inserted = await Article.insert_many(
            articles,
            ordered=False,
        )
        n_inserted = len(inserted.inserted_ids)
        logger.info(f"Inserted {n_inserted} articles to mongodb")
        return n_inserted
    except BulkWriteError as e:
        n_inserted = e.details["nInserted"]
        logger.info(f"Inserted {n_inserted} new documents into MongoDB.")
        logger.info(f"Encountered {len(e.details['writeErrors'])} duplicates.")

        return n_inserted


async def index_articles_in_vector_db(workspace_id: str):
    try:
        pinecone_index = get_pinecone_index(workspace_id)
        indexed = await index_not_indexed_articles(pinecone_index)
        await mark_articles_as_vector_indexed(indexed)
    except Exception as e:
        logger.error(
            f"Error while indexing articles: {e}. In mongoDB, we won't mark them as indexed. "
            f"You'll have to manually check the synchronization between the vector store and mongodb."
        )


async def handle_search_ingestion_config(
    ddgs: AsyncDDGS,
    run: IngestionRun,
    config: SearchIngestionConfig,
) -> list[Article]:
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
    assert run.status == Status.running and run.start_at

    logger.info(
        f"Processing RssIngestionConfig {config.id} for workspace {run.workspace_id}"
        f"({config.title}, {config.rss_feed_url=})"
    )

    assert run.id
    return await ingest_rss_feed(config, ingestion_run_id=run.id)


async def handle_ingestion_run(run: IngestionRun, ddgs: AsyncDDGS):
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
                articles = await handle_search_ingestion_config(
                    ddgs=ddgs, run=run, config=config
                )
            case IngestionConfigType.rss:
                assert isinstance(config, RssIngestionConfig)
                articles = await handle_rss_ingestion_config(config, run)

    except Exception as e:
        logger.info(f"Error while processing ingestion run: {e}")
        return await run.mark_as_finished(Status.failed, error=str(e))

    run.n_inserted = await insert_articles_in_mongodb(articles)

    await index_articles_in_vector_db(workspace_id=str(run.workspace_id))
    await run.mark_as_finished(Status.completed)

    assert run.end_at and run.status in [Status.completed, Status.failed]
    logger.info(
        "Finished processing ingestion run. Found {run.n_inserted} new articles."
    )


async def upsert_articles_of_workspace(
    workspace: Workspace,
    index: PineconeVectorStore,
    batch_size: int = 1000,
    force: bool = False,
):
    assert workspace.id
    logger.info(f"Fetching articles for workspace {workspace.id}")

    if force:
        articles = await Article.find(Article.workspace_id == workspace.id).to_list()
    else:
        articles = await Article.find(
            Article.workspace_id == workspace.id,
            Article.vector_indexed == False,  # noqa: E712
        ).to_list()

    logger.info(
        f"Found {len(articles)} not indexed articles for workspace {workspace.id}"
    )

    nb_batches = len(articles) // batch_size + 1

    for i, batch in enumerate(batched(articles, batch_size)):
        logger.info(
            f"Upserting articles for workspace {workspace.id} ({i + 1}/{nb_batches})"
        )
        documents = [article_to_document(article) for article in batch]
        await index.aadd_documents(
            documents, ids=[str(article.id) for article in batch]
        )
        await mark_articles_as_vector_indexed(list(batch))

    logger.info(f"Finished upserting articles for workspace {workspace.id}")


async def setup():
    mongo_client = get_client(settings.MONGODB_URI)
    await my_init_beanie(mongo_client)

    ddgs = AsyncDDGS(timeout=settings.QUERY_TIMEOUT)

    return mongo_client, ddgs


@app.command()
def create_ingestion_task(
    config_id: str,
):
    """Create ingestion tasks for a single IngestionConfig"""

    async def single_run():
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

    asyncio.run(single_run())


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

    async def create_runs():
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

    asyncio.run(create_runs())


@app.command()
def upsert(
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
    """Upsert articles for a single workspace of all workspaces"""

    async def upsert_articles():
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
            index = get_pinecone_index(workspace.id)
            await upsert_articles_of_workspace(workspace, index, force=force)

        mongo_client.close()

    asyncio.run(upsert_articles())


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
