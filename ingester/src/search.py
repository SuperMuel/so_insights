import asyncio
from duckduckgo_search import AsyncDDGS

from typing import Annotated, Self

from shared.models import TimeLimit, utc_datetime_factory
from shared.region import Region
from pydantic import (
    BaseModel,
    Field,
    HttpUrl,
    PastDatetime,
    StringConstraints,
    ValidationError,
    field_validator,
)
from shared.util import validate_url
from tenacity import retry, stop_after_attempt, wait_fixed

from src.ingester_settings import IngesterSettings

import logging

logger = logging.getLogger(__name__)

settings = IngesterSettings()


class BaseArticle(BaseModel):
    """
    Represents the basic structure of an article retrieved from a search.
    """

    title: Annotated[
        str, StringConstraints(min_length=1, max_length=200, strip_whitespace=True)
    ]
    url: HttpUrl
    body: Annotated[str, StringConstraints(max_length=1000, strip_whitespace=True)] = ""
    date: PastDatetime
    found_at: PastDatetime = Field(default_factory=utc_datetime_factory)
    image: HttpUrl | None = None
    source: (
        Annotated[str, StringConstraints(max_length=100, strip_whitespace=True)] | None
    ) = None

    @field_validator("title", mode="before")
    @classmethod
    def truncate_title(cls, v: str) -> str:
        return v[:200] if len(v) > 200 else v

    @field_validator("body", mode="before")
    @classmethod
    def truncate_body(cls, v: str) -> str:
        return v[:1000] if len(v) > 1000 else v

    @field_validator("source", mode="before")
    @classmethod
    def truncate_source(cls, v: str) -> str:
        return v[:100] if len(v) > 100 else v

    @field_validator("image", mode="before")
    @classmethod
    def validate_image_url(cls, v: str) -> str | None:
        return validate_url(v)

    @classmethod
    def try_parse(cls, d: dict) -> Self | None:
        """Try to parse a dictionary into an article, returning None if it fails."""
        try:
            return cls(**d)
        except ValidationError:
            logger.warning(f"Failed to parse article: {d}")
        except Exception:
            pass
        return None


@retry(
    reraise=True,
    stop=stop_after_attempt(settings.MAX_RETRIES_PER_QUERY),
    wait=wait_fixed(settings.RETRY_SLEEP_TIME_S),
)
async def search(
    ddgs: AsyncDDGS,
    query,
    region: Region,
    max_results: int,
    time_limit: TimeLimit,
) -> list[dict[str, str]]:
    """
    Performs an asynchronous search using DuckDuckGo Search API.

    This function is decorated with retry logic to handle potential failures.

    Args:
        ddgs (AsyncDDGS): An instance of the AsyncDDGS client.
        query: The search query string.
        region (Region): The region to focus the search on.
        max_results (int): The maximum number of results to return.
        time_limit (TimeLimit): The time limit for the search.

    Returns:
        list[dict[str, str]]: A list of dictionaries containing search results.

    Raises:
        Exception: If the search fails after maximum retries.
    """
    return await ddgs.anews(
        keywords=query,
        region=region,
        max_results=max_results,
        timelimit=time_limit,
    )


class _SearchResult:
    """
    Hold the results of a search operation.

    Attributes:
        articles (list[BaseArticle]): A list of parsed BaseArticle instances.
        successfull_queries (int): The number of successful queries performed.
    """

    def __init__(self, articles: list[BaseArticle], successfull_queries: int):
        self.articles = articles
        self.successfull_queries = successfull_queries


async def perform_search(
    ddgs: AsyncDDGS,
    queries: list[str],
    region: Region,
    max_results: int,
    time_limit: TimeLimit,
    stop_after_consecutive_failures: int = 5,
    verbose: bool = False,
) -> _SearchResult:
    """
    Performs multiple searches based on a list of queries.

    Args:
        ddgs (AsyncDDGS): An instance of the AsyncDDGS client.
        queries (list[str]): A list of search queries to perform.
        region (Region): The region to focus the searches on.
        max_results (int): The maximum number of results to return per query.
        time_limit (TimeLimit): The time limit for each search.
        stop_after_consecutive_failures (int, optional): Number of consecutive failures before stopping. Defaults to 5.
        verbose (bool, optional): If True, logs detailed information about each query. Defaults to False.

    Returns:
        _SearchResult: An instance containing the list of articles and the number of successful queries.

    Note:
        This function implements error handling and will stop after a specified number of consecutive failures.
        It also includes a sleep time between queries to avoid overwhelming the search API.
    """
    all_articles = []

    successfull_queries = 0

    for i, query in enumerate(queries):
        if verbose:
            logger.info(f"Searching for query {i + 1}/{len(queries)}: '{query}'")

        results = await search(
            ddgs=ddgs,
            query=query,
            region=region,
            max_results=max_results,
            time_limit=time_limit,
        )

        articles = map(BaseArticle.try_parse, results)
        all_articles.extend(filter(None, articles))

        await asyncio.sleep(settings.SLEEP_BETWEEN_QUERIES_S)

    return _SearchResult(all_articles, successfull_queries)


def deduplicate_articles(articles: list[BaseArticle]) -> list[BaseArticle]:
    return list({article.url: article for article in articles}.values())


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
