import asyncio
import logging
from datetime import datetime, timedelta, timezone
from enum import Enum
from itertools import batched
from typing import Optional

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
from shared.models import Article, IngestionRun, SearchQuerySet, TimeLimit, Workspace

load_dotenv()

settings = IngesterSettings()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)

logger = logging.getLogger(__name__)


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
    ddgs: AsyncDDGS, search_query_set: SearchQuerySet, run: IngestionRun
) -> tuple[int, list[BaseArticle]]:
    """Performs the search for all queries of the query set, deduplicates the results and returns the number of successful queries and the deduplicated articles"""

    result = await perform_search(
        ddgs,
        queries=search_query_set.queries,
        region=search_query_set.region,
        max_results=run.max_results,
        time_limit=run.time_limit,
        verbose=settings.VERBOSE_SEARCH,
    )
    logger.info(
        f"{result.successfull_queries}/{len(search_query_set.queries)} queries were successful. "
        f"Found {len(result.articles)} (undeduplicated) articles"
    )
    articles = deduplicate_articles(result.articles)
    logger.info(f"Deduplicated to {len(articles)} articles")
    return result.successfull_queries, articles


async def insert_articles_in_mongodb(
    search_query_set: SearchQuerySet, articles: list[BaseArticle]
) -> int:
    if not articles:
        logger.info("No articles to upsert")
        return 0

    logger.info("Upserting articles to mongodb")
    try:
        inserted = await Article.insert_many(
            [
                Article(
                    workspace_id=search_query_set.workspace_id,
                    region=search_query_set.region,
                    **article.model_dump(),
                )
                for article in articles
            ],
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


async def index_articles_in_vector_db(
    search_query_set: SearchQuerySet, get_pinecone_index
):
    try:
        pinecone_index = get_pinecone_index(str(search_query_set.workspace_id))
        indexed = await index_not_indexed_articles(pinecone_index)
        await mark_articles_as_vector_indexed(indexed)
    except Exception as e:
        logger.error(
            f"Error while indexing articles: {e}. In mongoDB, we won't mark them as indexed. "
            f"You'll have to manually check the synchronization between the vector store and mongodb."
        )


async def handle_ingestion_run(
    ddgs: AsyncDDGS,
    get_pinecone_index,
    run: IngestionRun,
):
    search_query_set = await SearchQuerySet.get(run.queries_set_id)
    assert search_query_set

    assert run.status in ["pending", "running"]

    if run.status == "pending":
        run.status = "running"
        await run.replace()

    logger.info(
        f"Processing search query set {search_query_set.id} "
        f"({search_query_set.title}, {len(search_query_set.queries)} queries, {run.time_limit=})"
    )

    try:
        successful_queries, articles = await perform_search_and_deduplicate_results(
            ddgs, search_query_set, run
        )
        n_inserted = await insert_articles_in_mongodb(search_query_set, articles)
        await index_articles_in_vector_db(search_query_set, get_pinecone_index)

        run.successfull_queries = successful_queries
        run.n_inserted = n_inserted
        run.status = "completed"
    except Exception as e:
        logger.error(
            f"Error while processing search query set {search_query_set.id}: {e}"
        )
        run.status = "failed"
        run.error = str(e)
    finally:
        run.end_at = datetime.now(timezone.utc)
        await run.replace()

    logger.info(f"Finished processing search query set {search_query_set.id}")


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


async def upsert_articles_all_workspaces(get_pinecone_index):
    workspaces = await Workspace.find_all().to_list()

    logger.info(f"Upserting articles for {len(workspaces)} workspaces")

    for i, workspace in enumerate(workspaces):
        logger.info(
            f"Upserting articles for workspace {workspace.id} ({i + 1}/{len(workspaces)})"
        )
        index = get_pinecone_index(workspace.id)
        await upsert_articles_of_workspace(workspace, index)

    logger.info("Finished upserting articles for all workspaces")


app = typer.Typer()


async def setup():
    mongo_client = get_client(settings.MONGODB_URI)
    await my_init_beanie(mongo_client)

    embeddings = VoyageAIEmbeddings(  # type:ignore # Arguments missing for parameters "_client", "_aclient"
        voyage_api_key=settings.VOYAGEAI_API_KEY,
        model=settings.EMBEDDING_MODEL,
        batch_size=settings.EMBEDDING_BATCH_SIZE,
    )

    def get_pinecone_index(namespace: str | PydanticObjectId):
        return PineconeVectorStore(
            pinecone_api_key=settings.PINECONE_API_KEY,
            index_name=settings.PINECONE_INDEX,
            embedding=embeddings,
            namespace=str(namespace),
        )

    ddgs = AsyncDDGS(timeout=settings.QUERY_TIMEOUT)

    return mongo_client, ddgs, get_pinecone_index


class TimeLimitEnum(str, Enum):
    # Because Typer do not support Literal for enums
    d = "d"
    w = "w"
    m = "m"
    y = "y"

    def to_literal(self) -> TimeLimit:
        return self.value

    @classmethod
    def from_literal(cls, value: TimeLimit) -> "TimeLimitEnum":
        return TimeLimitEnum(value)


@app.command()
def create_ingestion_task(
    search_query_set_id: str,
    time_limit: TimeLimitEnum = typer.Option(
        TimeLimitEnum.from_literal(settings.DEFAULT_TIME_LIMIT), "-t", "--time-limit"
    ),
    max_results: int = typer.Option(
        settings.MAX_RESULTS, "-m", "--max-results", help="Maximum number of results"
    ),
):
    """Create ingestion tasks for a single SearchQuerySet"""

    async def single_run():
        mongo_client, ddgs, get_pinecone_index = await setup()

        search_query_set = await SearchQuerySet.get(search_query_set_id)
        if not search_query_set:
            typer.echo(f"SearchQuerySet with id {search_query_set_id} not found.")
            return
        assert search_query_set.id

        run = await IngestionRun(
            workspace_id=search_query_set.workspace_id,
            queries_set_id=search_query_set.id,
            time_limit=time_limit.to_literal(),
            status="pending",
            max_results=max_results,
        ).create()

        logger.info(
            f"Created ingestion run {run.id} for search query set {search_query_set.id}"
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
    time_limit: TimeLimitEnum = typer.Option(
        TimeLimitEnum.from_literal(settings.DEFAULT_TIME_LIMIT), "-t", "--time-limit"
    ),
    max_results: int = typer.Option(
        settings.MAX_RESULTS, "-m", "--max-results", help="Maximum number of results"
    ),
):
    """Create ingestion tasks for all SearchQuerySets of a workspace or all workspaces"""

    async def create_runs():
        mongo_client, ddgs, get_pinecone_index = await setup()

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
            query_sets = await SearchQuerySet.find(
                SearchQuerySet.workspace_id == workspace.id
            ).to_list()

            for query_set in query_sets:
                assert query_set.id

                run = await IngestionRun(
                    workspace_id=workspace.id,
                    queries_set_id=query_set.id,
                    time_limit=time_limit.to_literal(),
                    status="pending",
                    max_results=max_results,
                ).create()

                logger.info(
                    f"Created ingestion run {run.id} for search query set {query_set.id}"
                )

        mongo_client.close()

    asyncio.run(create_runs())


@app.command()
def upsert(
    workspace_id: str,
    force: bool = typer.Option(
        False, "--force", help="Force upsert even if the articles are already indexed"
    ),
):
    """Upsert articles for a single workspace"""

    async def upsert_articles():
        mongo_client, ddgs, get_pinecone_index = await setup()

        workspace = await Workspace.get(workspace_id)
        if not workspace:
            typer.echo(f"Workspace with id {workspace_id} not found.")
            return

        index = get_pinecone_index(workspace_id)
        await upsert_articles_of_workspace(workspace, index, force=force)

        mongo_client.close()

    asyncio.run(upsert_articles())


@app.command()
def upsert_all():
    """Upsert articles for all workspaces"""

    async def upsert_all_articles():
        mongo_client, ddgs, get_pinecone_index = await setup()

        await upsert_articles_all_workspaces(get_pinecone_index)

        mongo_client.close()

    asyncio.run(upsert_all_articles())


@app.command()
def watch(
    interval: int = typer.Option(
        10, "--interval", "-i", help="Check interval in seconds"
    ),
):
    """Watch for pending ingestion runs and execute them."""

    async def _watch():
        mongo_client, ddgs, get_pinecone_index = await setup()

        logger.info(f"Starting watch loop. Checking every {interval} seconds.")

        while True:
            pending_run = await IngestionRun.find_one(
                IngestionRun.status == "pending"
            ).update_one(
                Set({IngestionRun.status: "running"}),
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
                ddgs=ddgs,
                get_pinecone_index=get_pinecone_index,
                run=pending_run,
            )

    asyncio.run(_watch())


if __name__ == "__main__":
    app()
