import logging

from shared.models import TimeLimit
from shared.region import Region
from src.search_providers.base import BaseArticle, BaseSearchProvider

logger = logging.getLogger(__name__)


class SerperdevProvider(BaseSearchProvider):
    async def search(
        self,
        query: str,
        *,
        region: Region,
        max_results: int,
        time_limit: TimeLimit,
    ) -> list[BaseArticle]:
        raise NotImplementedError

    async def batch_search(
        self,
        queries: list[str],
        *,
        region: Region,
        max_results: int,
        time_limit: TimeLimit,
    ) -> list[BaseArticle]:
        raise NotImplementedError
