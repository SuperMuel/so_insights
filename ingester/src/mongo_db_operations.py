import logging
from beanie import BulkWriter
from beanie.operators import Set

from pymongo.errors import BulkWriteError

from shared.models import Article

logger = logging.getLogger(__name__)


async def insert_articles_in_mongodb(
    articles: list[Article],
) -> int:
    """
    Inserts a list of articles into MongoDB, handling potential duplicates.

    This function attempts to insert multiple articles into the MongoDB database
    in a single operation. It uses unordered insertion to continue inserting
    even if some documents cause errors (e.g., duplicates).

    Args:
        articles (list[Article]): A list of Article objects to be inserted.

    Returns:
        int: The number of articles successfully inserted.
    """

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


async def mark_articles_as_vector_indexed(articles: list[Article]):
    """
    Marks a list of articles as indexed in the vector database.

    This function updates the 'vector_indexed' field of each provided article
    to True in the MongoDB database.

    Args:
        articles (list[Article]): A list of Article objects to be marked as indexed.

    This function should be called after successfully indexing articles
    in the vector database to keep the MongoDB records in sync.
    """
    logger.info(f"Marking {len(articles)} articles as vector indexed")
    async with BulkWriter() as bulk_writer:
        for article in articles:
            await article.update(
                Set({Article.vector_indexed: True}),
                bulk_writer=bulk_writer,
            )
    logger.info("Marked as vector indexed.")
