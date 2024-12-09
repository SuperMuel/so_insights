import asyncio
import logging
from datetime import datetime

from duckduckgo_search import AsyncDDGS
from tenacity import (
    after_log,
    before_sleep_log,
    retry,
    stop_after_attempt,
    wait_exponential,
)
from tqdm.asyncio import tqdm

from shared.models import Region, TimeLimit
from src.ingester_settings import ingester_settings
from src.search_providers.base import BaseArticle, BaseSearchProvider, SearchException

logger = logging.getLogger(__name__)


@retry(
    reraise=True,
    stop=stop_after_attempt(ingester_settings.MAX_RETRIES_PER_QUERY),
    wait=wait_exponential(
        multiplier=3,
        min=ingester_settings.MIN_RETRY_SLEEP_TIME_S,
        max=ingester_settings.MAX_RETRY_SLEEP_TIME_S,
    ),
    before_sleep=before_sleep_log(logger, logging.INFO),
    after=after_log(logger, logging.INFO),
)
async def _search_with_retry(
    *,
    query: str,
    region: Region,
    max_results: int,
    time_limit: TimeLimit,
    ddgs: AsyncDDGS,
):
    """
    Performs an asynchronous search using DuckDuckGo Search API with retry logic.

    This function is decorated with retry logic to handle potential failures:
    - Maximum retries: Configured in ingester_settings.MAX_RETRIES_PER_QUERY
    - Exponential backoff: Starting at 3s, bounded by MIN/MAX_RETRY_SLEEP_TIME_S
    - Logging: Before sleep and after retry attempts

    Args:
        query (str): The search query string
        region (Region): The region to focus the search on
        max_results (int): The maximum number of results to return
        time_limit (TimeLimit): The time limit for the search
        ddgs (AsyncDDGS): An instance of the AsyncDDGS client

    Returns:
        list[dict[str, str]]: A list of dictionaries containing search results

    Raises:
        SearchException: If the search fails after maximum retries
    """

    try:
        return await ddgs.anews(
            keywords=query,
            region=region.value,
            max_results=max_results,
            timelimit=time_limit,
        )
    except Exception as e:
        logger.error(f"Search '{query}' failed: {e}")
        raise SearchException(f"Search '{query}' failed", e)


def duckduckgo_result_to_base_article(
    result: dict[str, str],
    *,
    found_at: datetime | None = None,
) -> BaseArticle:
    """
    Converts a DuckDuckGo search result to a BaseArticle instance.

    Args:
        result (dict[str, str]): A dictionary containing search result information

    Returns:
        BaseArticle: An instance of BaseArticle
    """

    result["provider"] = "duckduckgo"

    obj = BaseArticle.model_validate(result)

    if found_at is not None:
        obj.found_at = found_at

    return obj


class DuckDuckGoProvider(BaseSearchProvider):
    def __init__(
        self,
        ddgs: AsyncDDGS,
    ):
        self.ddgs = ddgs

    async def search(
        self,
        query: str,
        *,
        region: Region,
        max_results: int,
        time_limit: TimeLimit,
    ) -> list[BaseArticle]:
        result = await _search_with_retry(
            query=query,
            region=region,
            max_results=max_results,
            time_limit=time_limit,
            ddgs=self.ddgs,
        )

        articles = map(duckduckgo_result_to_base_article, result)

        return list(articles)

    async def batch_search(
        self,
        queries: list[str],
        *,
        region: Region,
        max_results: int,
        time_limit: TimeLimit,
    ) -> list[BaseArticle]:
        """
        Performs multiple searches based on a list of queries with progress tracking.
        Includes sleep between queries to avoid overwhelming the API.
        """
        all_articles = []

        for query in (bar := tqdm(queries)):
            bar.set_description(f"Searching for '{query}'")

            results = await self.search(
                query=query,
                region=region,
                max_results=max_results,
                time_limit=time_limit,
            )
            all_articles.extend(results)

            # Sleep between queries to respect rate limits
            if queries.index(query) < len(queries) - 1:  # Don't sleep after last query
                await asyncio.sleep(ingester_settings.SLEEP_BETWEEN_QUERIES_S)

        return all_articles
