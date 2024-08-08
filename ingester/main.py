import asyncio
from langchain_pinecone import PineconeVectorStore
from langchain_voyageai import VoyageAIEmbeddings
from shared.models import IngestionRun, SearchQuerySet

from ingester.src.ingester_settings import IngesterSettings
from shared.db import my_init_beanie, get_client
from datetime import datetime, timedelta, timezone
import logging

logger = logging.getLogger(__name__)


def has_run_less_than_24h_ago(last_run: IngestionRun) -> bool:
    end_at = last_run.end_at

    assert (
        end_at is not None
    ), "You should first verify that the last run has finished, and thus has an end_at date"

    return end_at > datetime.now(timezone.utc) - timedelta(days=1)


async def main():
    settings = IngesterSettings()

    mongo_client = get_client(settings.MONGODB_URI)
    await my_init_beanie(mongo_client)

    embeddings = VoyageAIEmbeddings(  # type:ignore # Arguments missing for parameters "_client", "_aclient"PylancereportCallIssue
        voyage_api_key=settings.VOYAGE_API_KEY,
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

    # TODO : do not get all SearchQuerySets, but implement a ScheduledSearch class that will be responsible for scheduling the search queries, and can be disabled at any time
    search_query_sets = await SearchQuerySet.find_all().to_list()

    for i, search_query_set in enumerate(search_query_sets):
        assert search_query_set.id

        logger.info(
            f"Processing search query set {search_query_set.id} ({i + 1}/{len(search_query_sets)})"
        )

        if not search_query_set.queries:
            logger.info(
                f"Skipping search query set {search_query_set.id} because it has no queries"
            )
            continue

        last_run = await search_query_set.find_last_run()

        if last_run is not None:
            if last_run.is_not_finished():
                logger.warning(
                    f"Skipping search query set {search_query_set.id} because the last run is not finished"
                )
                continue
            if has_run_less_than_24h_ago(last_run):
                logger.info(
                    f"Skipping search query set {search_query_set.id} because the last run was less than 24h ago"
                )
                continue

        # Search can begin
        run = await IngestionRun(
            workspace_id=search_query_set.workspace_id,
            queries_set_id=search_query_set.id,
            status="running",
            time_limit=settings.TIME_LIMIT,
            max_results=settings.MAX_RESULTS,
        ).insert()

        pinecone_index = get_pinecone_index(
            namespace=str(search_query_set.workspace_id)
        )

        try:
            pass
            # execute the search
            # get the search results
            # TODO : we can start upserting the results before the search finishes
            # await for article in execute_search(search_query_set):
            #     # upsert article to pinecone
            # upsert to mongodb with
        except Exception as e:
            logger.error(
                f"Error while processing search query set {search_query_set.id}: {e}"
            )
            run.status = "failed"
            run.error = str(e)
            await run.replace()
            continue

        logger.info(
            f"Upsert vectors to pinecone with namespace {search_query_set.workspace_id}"
        )
        # TODO : upsert vectors

        logger.info("Finished upserting vectors to pinecone")
        logger.info("Upserting articles to mongodb")

        # TODO : UPSERT MONGODB

        run.status = "completed"
        await run.replace()

        logger.info(f"Finished processing search query set {search_query_set.id}")

    logger.info("Finished processing all search query sets")
    mongo_client.close()


if __name__ == "__main__":
    asyncio.run(main())
