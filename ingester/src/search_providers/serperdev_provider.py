import logging
from datetime import datetime

import dateparser
import requests
from pydantic import SecretStr
from pydantic_core import Url

from shared.models import TimeLimit
from shared.region import Region
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
        datetime: The parsed datetime object

    Raises:
        ValueError: If the date string cannot be parsed

    Example:
        >>> serper_date_to_datetime("2 days ago")
        datetime(2024, 3, 20, 14, 30, 0)  # if today is March 22
    """
    dt = dateparser.parse(date)
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
        url=Url(article["link"]),
        image=Url(article["imageUrl"]) if "imageUrl" in article else None,
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

    country, laguage = region.value.split("-")
    return {"gl": country, "hl": laguage}


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

        response = requests.get(self.url, headers=headers, params=params)

        response.raise_for_status()

        data = response.json()

        credits = data["credits"]
        search_parameters = data["searchParameters"]

        logger.info(f"{credits=}")
        logger.info(f"{search_parameters=}")

        articles = data["news"]

        return [serper_result_to_base_article(article) for article in articles]

    # async def batch_search(
    #     self,
    #     queries: list[str],
    #     *,
    #     region: Region,
    #     max_results: int,
    #     time_limit: TimeLimit,
    # ) -> list[BaseArticle]:
    #     raise NotImplementedError
