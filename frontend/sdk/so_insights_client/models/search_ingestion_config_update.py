from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define

from ..models.region import Region
from ..models.time_limit import TimeLimit
from ..types import UNSET, Unset

T = TypeVar("T", bound="SearchIngestionConfigUpdate")


@_attrs_define
class SearchIngestionConfigUpdate:
    """
    Attributes:
        title (Union[None, Unset, str]):
        region (Union[None, Region, Unset]):
        queries (Union[None, Unset, list[str]]):
        max_results (Union[None, Unset, int]):
        time_limit (Union[None, TimeLimit, Unset]):
    """

    title: Union[None, Unset, str] = UNSET
    region: Union[None, Region, Unset] = UNSET
    queries: Union[None, Unset, list[str]] = UNSET
    max_results: Union[None, Unset, int] = UNSET
    time_limit: Union[None, TimeLimit, Unset] = UNSET

    def to_dict(self) -> dict[str, Any]:
        title: Union[None, Unset, str]
        if isinstance(self.title, Unset):
            title = UNSET
        else:
            title = self.title

        region: Union[None, Unset, str]
        if isinstance(self.region, Unset):
            region = UNSET
        elif isinstance(self.region, Region):
            region = self.region.value
        else:
            region = self.region

        queries: Union[None, Unset, list[str]]
        if isinstance(self.queries, Unset):
            queries = UNSET
        elif isinstance(self.queries, list):
            queries = self.queries

        else:
            queries = self.queries

        max_results: Union[None, Unset, int]
        if isinstance(self.max_results, Unset):
            max_results = UNSET
        else:
            max_results = self.max_results

        time_limit: Union[None, Unset, str]
        if isinstance(self.time_limit, Unset):
            time_limit = UNSET
        elif isinstance(self.time_limit, TimeLimit):
            time_limit = self.time_limit.value
        else:
            time_limit = self.time_limit

        field_dict: dict[str, Any] = {}
        field_dict.update({})
        if title is not UNSET:
            field_dict["title"] = title
        if region is not UNSET:
            field_dict["region"] = region
        if queries is not UNSET:
            field_dict["queries"] = queries
        if max_results is not UNSET:
            field_dict["max_results"] = max_results
        if time_limit is not UNSET:
            field_dict["time_limit"] = time_limit

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        d = src_dict.copy()

        def _parse_title(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        title = _parse_title(d.pop("title", UNSET))

        def _parse_region(data: object) -> Union[None, Region, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                region_type_0 = Region(data)

                return region_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Region, Unset], data)

        region = _parse_region(d.pop("region", UNSET))

        def _parse_queries(data: object) -> Union[None, Unset, list[str]]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                queries_type_0 = cast(list[str], data)

                return queries_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, list[str]], data)

        queries = _parse_queries(d.pop("queries", UNSET))

        def _parse_max_results(data: object) -> Union[None, Unset, int]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, int], data)

        max_results = _parse_max_results(d.pop("max_results", UNSET))

        def _parse_time_limit(data: object) -> Union[None, TimeLimit, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                time_limit_type_0 = TimeLimit(data)

                return time_limit_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, TimeLimit, Unset], data)

        time_limit = _parse_time_limit(d.pop("time_limit", UNSET))

        search_ingestion_config_update = cls(
            title=title,
            region=region,
            queries=queries,
            max_results=max_results,
            time_limit=time_limit,
        )

        return search_ingestion_config_update
