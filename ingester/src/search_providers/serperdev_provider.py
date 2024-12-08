from sdk.so_insights_client.models.region import Region
from sdk.so_insights_client.models.time_limit import TimeLimit
from src.search import BaseArticle
from src.search_providers.base import BaseSearchProvider


class SerperdevProvider(BaseSearchProvider):
    def search(
        self,
        query: str,
        *,
        region: Region,
        max_results: int,
        time_limit: TimeLimit,
    ) -> list[BaseArticle]:
        raise NotImplementedError

    def batch_search(
        self,
        queries: list[str],
        *,
        region: Region,
        max_results: int,
        time_limit: TimeLimit,
    ):
        raise NotImplementedError
