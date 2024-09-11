from datetime import datetime, timezone
import logging
from typing import List, Dict, Any

import aiohttp
import feedparser
from beanie import PydanticObjectId

from shared.models import Article, RssIngestionConfig


logger = logging.getLogger(__name__)


async def fetch_rss_feed(session: aiohttp.ClientSession, url: str) -> str:
    async with session.get(url) as response:
        return await response.text()


async def parse_rss_feed(feed_content: str) -> List[Dict[str, Any]]:
    feed = feedparser.parse(feed_content)
    return feed.entries


def entry_to_published_date(published_parsed) -> datetime | None:
    try:
        return datetime(*published_parsed[:6], tzinfo=timezone.utc)
    except Exception:
        logger.warning(f"Failed to extract published date from {published_parsed=}")


def convert_to_article(
    entry: Dict[str, Any],
    workspace_id: PydanticObjectId,
    ingestion_run_id: PydanticObjectId,
) -> Article:
    # Convert the published date to a datetime object
    published = entry.get("published_parsed")
    if published:
        published_date = datetime(*published[:6], tzinfo=timezone.utc)
    else:
        published_date = datetime.now(timezone.utc)

    return Article(
        workspace_id=workspace_id,
        ingestion_run_id=ingestion_run_id,
        title=entry.get("title", ""),
        url=entry.get("link", ""),
        body=entry.get("summary", ""),
        date=published_date,
        source=entry.get("author", "") or entry.get("source", {}).get("title", ""),
        content=str(entry["content"]) if "content" in entry else None,
    )


async def ingest_rss_feed(
    config: RssIngestionConfig, ingestion_run_id: PydanticObjectId
) -> list[Article]:
    async with aiohttp.ClientSession() as session:
        feed_content = await fetch_rss_feed(session, str(config.rss_feed_url))

    entries = await parse_rss_feed(feed_content)

    articles = [
        convert_to_article(
            entry,
            config.workspace_id,
            ingestion_run_id=ingestion_run_id,
        )
        for entry in entries
    ]

    return articles
