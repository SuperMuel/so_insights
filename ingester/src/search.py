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
from tenacity import (
    after_log,
    before_sleep_log,
    retry,
    stop_after_attempt,
    wait_exponential,
)

from src.ingester_settings import ingester_settings

import logging

logger = logging.getLogger(__name__)


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


class SearchException(Exception):
    """Custom exception for search-related errors."""

    def __init__(self, message: str, original_exception: Exception):
        super().__init__(f"{message}: {original_exception}")
        self.original_exception = original_exception


@retry(
    reraise=True,
    stop=stop_after_attempt(ingester_settings.MAX_RETRIES_PER_QUERY),
    wait=wait_exponential(
        multiplier=1,
        min=ingester_settings.MIN_RETRY_SLEEP_TIME_S,
        max=ingester_settings.MAX_RETRY_SLEEP_TIME_S,
    ),
    before_sleep=before_sleep_log(logger, logging.INFO),
    after=after_log(logger, logging.INFO),
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
        SearchException: If the search fails after maximum retries.
    """

    try:
        return await ddgs.anews(
            keywords=query,
            region=region,
            max_results=max_results,
            timelimit=time_limit,
        )
    except Exception as e:
        logger.error(f"Search '{query}' failed: {e}")
        raise SearchException(f"Search '{query}' failed", e)


class _SearchResult:
    """
    Hold the results of a search operation.

    Attributes:
        articles (list[BaseArticle]): A list of parsed BaseArticle instances.
    """

    def __init__(self, articles: list[BaseArticle]):
        self.articles = articles


async def perform_search(
    ddgs: AsyncDDGS,
    queries: list[str],
    region: Region,
    max_results: int,
    time_limit: TimeLimit,
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

        await asyncio.sleep(ingester_settings.SLEEP_BETWEEN_QUERIES_S)

    return _SearchResult(all_articles)


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
        verbose=ingester_settings.VERBOSE_SEARCH,
    )
    logger.info(f"Found {len(result.articles)} (undeduplicated) articles")
    articles = deduplicate_articles(result.articles)
    logger.info(f"Deduplicated to {len(articles)} articles")
    return articles
