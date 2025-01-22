from typing import Any, TypeVar, cast

from attrs import define as _attrs_define

from ..models.region import Region
from ..models.time_limit import TimeLimit

T = TypeVar("T", bound="SearchIngestionConfigCreate")


@_attrs_define
class SearchIngestionConfigCreate:
    """
    Attributes:
        title (str):
        region (Region):
        queries (list[str]):
        max_results (int):
        time_limit (TimeLimit):
        first_run_max_results (int):
        first_run_time_limit (TimeLimit):
    """

    title: str
    region: Region
    queries: list[str]
    max_results: int
    time_limit: TimeLimit
    first_run_max_results: int
    first_run_time_limit: TimeLimit

    def to_dict(self) -> dict[str, Any]:
        title = self.title

        region = self.region.value

        queries = self.queries

        max_results = self.max_results

        time_limit = self.time_limit.value

        first_run_max_results = self.first_run_max_results

        first_run_time_limit = self.first_run_time_limit.value

        field_dict: dict[str, Any] = {}
        field_dict.update(
            {
                "title": title,
                "region": region,
                "queries": queries,
                "max_results": max_results,
                "time_limit": time_limit,
                "first_run_max_results": first_run_max_results,
                "first_run_time_limit": first_run_time_limit,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        d = src_dict.copy()
        title = d.pop("title")

        region = Region(d.pop("region"))

        queries = cast(list[str], d.pop("queries"))

        max_results = d.pop("max_results")

        time_limit = TimeLimit(d.pop("time_limit"))

        first_run_max_results = d.pop("first_run_max_results")

        first_run_time_limit = TimeLimit(d.pop("first_run_time_limit"))

        search_ingestion_config_create = cls(
            title=title,
            region=region,
            queries=queries,
            max_results=max_results,
            time_limit=time_limit,
            first_run_max_results=first_run_max_results,
            first_run_time_limit=first_run_time_limit,
        )

        return search_ingestion_config_create
