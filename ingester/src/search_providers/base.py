from abc import ABC, abstractmethod
from typing import Literal

from sdk.so_insights_client.models.region import Region
from sdk.so_insights_client.models.time_limit import TimeLimit
from src.search import BaseArticle

type SearchProvider = Literal["duckduckgo", "serperdev"]


class BaseSearchProvider(ABC):
    @abstractmethod
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
        return [
            self.search(
                query,
                region=region,
                max_results=max_results,
                time_limit=time_limit,
            )
            for query in queries
        ]
