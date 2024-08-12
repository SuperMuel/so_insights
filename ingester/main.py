import asyncio
from typing import Literal
from beanie import BulkWriter
from beanie.odm.operators.update.general import Set
from pymongo.errors import BulkWriteError
from duckduckgo_search import AsyncDDGS
from langchain_pinecone import PineconeVectorStore
from langchain_voyageai import VoyageAIEmbeddings
from shared.models import Article, IngestionRun, SearchQuerySet
from langchain_core.documents import Document

from src.ingester_settings import IngesterSettings
from shared.db import my_init_beanie, get_client
from datetime import datetime, timedelta, timezone
import logging

from src.search import BaseArticle, perform_search
from dotenv import load_dotenv

load_dotenv()

settings = IngesterSettings()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)

logger = logging.getLogger(__name__)


def has_run_less_than_24h_ago(last_run: IngestionRun) -> bool:
    end_at = last_run.end_at

    assert (
        end_at is not None
    ), "You should first verify that the last run has finished, and thus has an end_at date"

    return end_at > datetime.now() - timedelta(days=1)


def deduplicate_articles(articles: list[BaseArticle]) -> list[BaseArticle]:
    return list({article.url: article for article in articles}.values())


def article_to_document(article: Article) -> Document:
    return Document(
        page_content=f"{article.title}\n{article.body}",
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
        Article.workspace_id == pinecone_index._namespace,
        Article.vector_indexed == False,  # noqa: E712
    ).to_list()

    logger.info(f"Indexing {len(not_indexed)} articles")

    documents = list(map(article_to_document, not_indexed))

    await pinecone_index.aadd_documents(documents)

    print("Indexed.")
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


async def check_search_query_set_eligibility(search_query_set: SearchQuerySet) -> bool:
    if not search_query_set.queries:
        logger.info(
            f"Skipping search query set {search_query_set.id} because it has no queries"
        )
        return False

    last_run = await search_query_set.find_last_finished_run()

    if last_run is not None:
        if last_run.is_running():
            logger.warning(
                f"Skipping search query set {search_query_set.id} because the last run is not finished"
            )
            return False
        if has_run_less_than_24h_ago(last_run):
            logger.info(
                f"Skipping search query set {search_query_set.id} because the last run was less than 24h ago"
            )
            return False

    return True


async def create_ingestion_run(
    search_query_set: SearchQuerySet,
    status: Literal["running", "completed", "failed"] = "running",
) -> IngestionRun:
    """Creates and insert an IngestionRun for this SearchQuerySet"""
    assert search_query_set.id
    return await IngestionRun(
        workspace_id=search_query_set.workspace_id,
        queries_set_id=search_query_set.id,
        status=status,
        time_limit=settings.TIME_LIMIT,
        max_results=settings.MAX_RESULTS,
    ).insert()


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


async def handle_search_query_set(
    search_query_set: SearchQuerySet,
    ddgs: AsyncDDGS,
    get_pinecone_index,
):
    assert search_query_set.id

    logger.info(
        f"Processing search query set {search_query_set.id} "
        f"({search_query_set.title}, {len(search_query_set.queries)} queries, timelimit='{settings.TIME_LIMIT}')"
    )

    run = await create_ingestion_run(search_query_set)

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


async def handle_all_search_query_sets(ddgs: AsyncDDGS, get_pinecone_index):
    search_query_sets = await SearchQuerySet.find_all().to_list()

    logger.info(f"Processing {len(search_query_sets)} search query sets")

    for i, search_query_set in enumerate(search_query_sets):
        if not await check_search_query_set_eligibility(search_query_set):
            continue

        logger.info(
            f"Processing search query set {search_query_set.title} ({search_query_set.id}) ({i + 1}/{len(search_query_sets)})"
        )
        await handle_search_query_set(
            search_query_set=search_query_set,
            ddgs=ddgs,
            get_pinecone_index=get_pinecone_index,
        )

        logger.info(f"Finished processing search query set {search_query_set.id}")

    logger.info("Finished processing all search query sets")


async def main():
    mongo_client = get_client(settings.MONGODB_URI)
    await my_init_beanie(mongo_client)

    embeddings = VoyageAIEmbeddings(  # type:ignore # Arguments missing for parameters "_client", "_aclient"PylancereportCallIssue
        voyage_api_key=settings.VOYAGEAI_API_KEY,
        model=settings.EMBEDDING_MODEL,
        batch_size=settings.EMBEDDING_BATCH_SIZE,
    )

    def get_pinecone_index(namespace: str):
        return PineconeVectorStore(
            pinecone_api_key=settings.PINECONE_API_KEY,
            index_name=settings.PINECONE_INDEX,
            embedding=embeddings,
            namespace=namespace,
        )

    ddgs = AsyncDDGS(timeout=settings.QUERY_TIMEOUT)

    await handle_all_search_query_sets(ddgs, get_pinecone_index)

    mongo_client.close()


if __name__ == "__main__":
    asyncio.run(main())
