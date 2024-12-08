from datetime import datetime
from duckduckgo_search import AsyncDDGS
from shared.models import Region, TimeLimit
from src.ingester_settings import ingester_settings
from src.search_providers.base import BaseArticle, BaseSearchProvider, SearchException

import logging

from tenacity import (
    after_log,
    before_sleep_log,
    retry,
    stop_after_attempt,
    wait_exponential,
)

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
        raise NotImplementedError()


# async def perform_search(
#     *,
#     search_provider: BaseSearchProvider,
#     queries: list[str],
#     region: Region,
#     max_results: int,
#     time_limit: TimeLimit,
# ) -> _SearchResult:
#     """
#     Performs multiple searches based on a list of queries.

#     Args:
#         search_provider (BaseSearchProvider): The search provider to use.
#         queries (list[str]): A list of search queries to perform.
#         region (Region): The region to focus the searches on.
#         max_results (int): The maximum number of results to return per query.
#         time_limit (TimeLimit): The time limit for each search.
#         stop_after_consecutive_failures (int, optional): Number of consecutive failures before stopping. Defaults to 5.
#         verbose (bool, optional): If True, logs detailed information about each query. Defaults to False.

#     Returns:
#         _SearchResult: An instance containing the list of articles and the number of successful queries.

#     Note:
#         This function implements error handling and will stop after a specified number of consecutive failures.
#         It also includes a sleep time between queries to avoid overwhelming the search API.
#     """
#     all_articles = []

#     for query in (bar := tqdm(queries)):
#         bar.set_description(f"Searching for '{query}'")
#         results = search_provider.search(
#             query=query,
#             region=region,
#             max_results=max_results,
#             time_limit=time_limit,
#         )

#         articles = map(BaseArticle.try_parse, results)
#         all_articles.extend(filter(None, articles))

#         await asyncio.sleep(ingester_settings.SLEEP_BETWEEN_QUERIES_S)

#     return all_articles
