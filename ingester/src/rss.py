from datetime import datetime, timezone
import logging
from typing import Any

import aiohttp
import feedparser
from beanie import PydanticObjectId

from shared.models import Article, RssIngestionConfig


logger = logging.getLogger(__name__)


async def _fetch_rss_feed(session: aiohttp.ClientSession, url: str) -> str:
    """
    Asynchronously fetches the content of an RSS feed.

    Args:
        session (aiohttp.ClientSession): An aiohttp client session for making the request.
        url (str): The URL of the RSS feed to fetch.

    Returns:
        str: The raw content of the RSS feed as a string.
    """
    async with session.get(url) as response:
        return await response.text()


async def _parse_rss_feed(feed_content: str) -> list[dict[str, Any]]:
    """
    Parses the content of an RSS feed.

    Args:
        feed_content (str): The raw content of the RSS feed.

    Returns:
        List[Dict[str, Any]]: A list of dictionaries, each representing an entry in the RSS feed.
    """
    feed = feedparser.parse(feed_content)
    return feed.entries


def _entry_to_published_date(published_parsed) -> datetime | None:
    """
    Converts the published date from an RSS entry to a datetime object.

    Args:
        published_parsed: The parsed published date from the RSS entry.

    Returns:
        datetime | None: A datetime object representing the published date, or None if conversion fails.

    Note:
        This function attempts to create a UTC datetime object from the first 6 elements
        of the published_parsed tuple. If it fails, it logs a warning and returns None.
    """
    try:
        return datetime(*published_parsed[:6], tzinfo=timezone.utc)
    except Exception:
        logger.warning(f"Failed to extract published date from {published_parsed=}")


def _convert_to_article(
    entry: dict[str, Any],
    workspace_id: PydanticObjectId,
    ingestion_run_id: PydanticObjectId,
) -> Article:
    """
    Converts an RSS feed entry to an Article object.

    Args:
        entry (Dict[str, Any]): A dictionary representing an RSS feed entry.
        workspace_id (PydanticObjectId): The ID of the workspace this article belongs to.
        ingestion_run_id (PydanticObjectId): The ID of the ingestion run that created this article.

    Returns:
        Article: An Article object populated with data from the RSS feed entry.

    Note:
        This function extracts relevant information from the RSS entry and creates
        an Article object. If the published date is not available, it uses the current time.
    """

    published_date = _entry_to_published_date(
        entry.get("published_parsed")
    ) or datetime.now(timezone.utc)

    return Article(
        workspace_id=workspace_id,
        ingestion_run_id=ingestion_run_id,
        title=entry.get("title", ""),
        url=entry.get("link", ""),
        body=entry.get("summary", ""),
        date=published_date,
        source=entry.get("author", "") or entry.get("source", {}).get("title", ""),
        content=str(entry["content"]) if "content" in entry else None,
        provider="rss",
    )


async def ingest_rss_feed(
    config: RssIngestionConfig, ingestion_run_id: PydanticObjectId
) -> list[Article]:
    """
    Ingests articles from an RSS feed based on the provided configuration.

    Args:
        config (RssIngestionConfig): The configuration for the RSS feed ingestion.
        ingestion_run_id (PydanticObjectId): The ID of the current ingestion run.

    Returns:
        list[Article]: A list of Article objects created from the RSS feed entries. Entries that
        fail to convert to an Article object are logged with an exception and not included in the list.
    """
    async with aiohttp.ClientSession() as session:
        feed_content = await _fetch_rss_feed(session, str(config.rss_feed_url))

    entries = await _parse_rss_feed(feed_content)

    articles = []

    for entry in entries:
        try:
            article = _convert_to_article(
                entry, config.workspace_id, ingestion_run_id=ingestion_run_id
            )
            articles.append(article)
        except Exception as e:
            logger.exception("Failed to convert RSS entry to Article", exc_info=e)

    return articles
