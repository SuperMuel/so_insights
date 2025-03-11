import logging
from datetime import datetime, timezone

import dateparser
from dateparser.conf import Settings
import httpx
from pydantic import HttpUrl, SecretStr

from shared.models import TimeLimit
from shared.region import Region
from shared.util import validate_url
from src.search_providers.base import BaseArticle, BaseSearchProvider

logger = logging.getLogger(__name__)


def time_limit_to_serper(time_limit: TimeLimit | None) -> dict:
    return {"tbs": "qdr:" + time_limit} if time_limit is not None else {}


def serper_date_to_datetime(date: str) -> datetime:
    """
    Convert a Serper.dev date string to a datetime object.

    Handles relative date strings like:
    - "X weeks/days/months/years ago"
    - "X hours/minutes/seconds ago"
    - "just now"

    Args:
        date (str): A date string in Serper.dev format (e.g. "2 days ago")

    Returns:
        datetime: The parsed datetime object in UTC timezone

    Raises:
        ValueError: If the date string cannot be parsed

    Example:
        >>> serper_date_to_datetime("2 days ago")
        datetime(2024, 3, 20, 14, 30, 0, tzinfo=timezone.utc)  # if today is March 22
    """
    dt = dateparser.parse(
        date,
        settings={
            "TIMEZONE": "UTC",
            "RETURN_AS_TIMEZONE_AWARE": True,
            "TO_TIMEZONE": "UTC",
            "RELATIVE_BASE": datetime.now(timezone.utc),
        },
    )
    if dt is None:
        raise ValueError(f"Could not parse date: {date}")

    return dt


def serper_result_to_base_article(article: dict[str, str]) -> BaseArticle:
    """Convert a SerperDev search result to a BaseArticle.
    {
        'title': 'What do we know about the economics of AI?',
        'link': 'https://news.mit.edu/2024/what-do-we-know-about-economics-ai-1206',
        'snippet': 'For all the talk about artificial intelligence upending the world, its economic effects remain uncertain. There is massive investment in AI...',
        'date': '2 days ago',
        'source': 'MIT News',
        'imageUrl': 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcROytnLg6DlN9HEix0aUQZcLylGEXrjpxrjAtgAbbeD9lbX3XE_uLCQZc0XxQ&s',
        'position': 10
    }
    """

    return BaseArticle(
        title=article["title"],
        body=article["snippet"] if "snippet" in article else "",
        date=serper_date_to_datetime(article["date"]),
        source=article["source"] if "source" in article else None,
        url=HttpUrl(article["link"]),
        image=validate_url(article["imageUrl"]) if "imageUrl" in article else None,
        provider="serperdev",
    )


def region_to_gl_hl(region: Region) -> dict[str, str]:
    """
    Map Region to Serper's `gl` (country) and `hl` (language) parameters.

    Args:
        region (Region): The region enum value.

    Returns:
        dict[str, str]: A tuple containing the country (gl) and language (hl) parameters.
        Empty dict if the region is NO_REGION.
    """
    if region == Region.NO_REGION:
        return {}
    country, language = region.value.split("-")
    return {"gl": country, "hl": language}


class SerperdevProvider(BaseSearchProvider):
    def __init__(self, api_key: SecretStr):
        self.url = "https://google.serper.dev/news"
        self.api_key = api_key

        assert self.api_key.get_secret_value(), "Empty API key for SerperDev"

    async def search(
        self,
        query: str,
        *,
        region: Region,
        max_results: int,
        time_limit: TimeLimit,
    ) -> list[BaseArticle]:
        logger.info(f"Searching for '{query}' in {region} with {max_results} results")

        headers = {
            "X-API-KEY": self.api_key.get_secret_value(),
            "Content-Type": "application/json",
        }

        params = {
            "q": query,
            "num": max_results,
            "autocorrect": False,
            **time_limit_to_serper(time_limit),
            **region_to_gl_hl(region),
        }

        async with httpx.AsyncClient() as client:
            response = await client.get(self.url, headers=headers, params=params)

        response.raise_for_status()

        data = response.json()

        credits = data["credits"]
        search_parameters = data["searchParameters"]

        logger.info(f"{credits=}")
        logger.info(f"{search_parameters=}")

        articles = data["news"]

        return [serper_result_to_base_article(article) for article in articles]

    async def batch_search(
        self,
        queries: list[str],
        *,
        region: Region,
        max_results: int,
        time_limit: TimeLimit,
    ) -> list[BaseArticle]:
        assert queries

        headers = {
            "X-API-KEY": self.api_key.get_secret_value(),
            "Content-Type": "application/json",
        }

        max_batch_size = 100  # Serper.dev maximum batch size
        total_articles = []

        async with httpx.AsyncClient() as client:
            for i in range(0, len(queries), max_batch_size):
                batch_queries = queries[i : i + max_batch_size]
                logger.info(f"Performing batch search for {len(batch_queries)} queries")

                payload = [
                    {
                        "q": query,
                        "num": max_results,
                        "autocorrect": False,
                        **time_limit_to_serper(time_limit),
                        **region_to_gl_hl(region),
                    }
                    for query in batch_queries
                ]

                response = await client.post(self.url, headers=headers, json=payload)
                response.raise_for_status()

                batch_results = response.json()
                batch_articles = []

                for result in batch_results:
                    logger.info(result.get("searchParameters"))
                    batch_articles.extend(
                        serper_result_to_base_article(article)
                        for article in result["news"]
                    )

                logger.info(
                    f"Batch search completed with {len(batch_articles)} articles"
                )
                total_articles.extend(batch_articles)

        logger.info(f"Total articles fetched: {len(total_articles)}")
        return total_articles
