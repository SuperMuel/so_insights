from typing import Any, Dict, List, Type, TypeVar, Union, cast

from attrs import define as _attrs_define

from ..models.region import Region
from ..models.time_limit import TimeLimit
from ..types import UNSET, Unset

T = TypeVar("T", bound="SearchIngestionConfigUpdate")


@_attrs_define
class SearchIngestionConfigUpdate:
    """
    Attributes:
        title (Union[None, str]):
        region (Union[None, Region]):
        queries (Union[List[str], None]):
        time_limit (Union[None, TimeLimit]):
        max_results (Union[None, Unset, int]):
    """

    title: Union[None, str]
    region: Union[None, Region]
    queries: Union[List[str], None]
    time_limit: Union[None, TimeLimit]
    max_results: Union[None, Unset, int] = UNSET

    def to_dict(self) -> Dict[str, Any]:
        title: Union[None, str]
        title = self.title

        region: Union[None, str]
        if isinstance(self.region, Region):
            region = self.region.value
        else:
            region = self.region

        queries: Union[List[str], None]
        if isinstance(self.queries, list):
            queries = self.queries

        else:
            queries = self.queries

        time_limit: Union[None, str]
        if isinstance(self.time_limit, TimeLimit):
            time_limit = self.time_limit.value
        else:
            time_limit = self.time_limit

        max_results: Union[None, Unset, int]
        if isinstance(self.max_results, Unset):
            max_results = UNSET
        else:
            max_results = self.max_results

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "title": title,
                "region": region,
                "queries": queries,
                "time_limit": time_limit,
            }
        )
        if max_results is not UNSET:
            field_dict["max_results"] = max_results

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def _parse_title(data: object) -> Union[None, str]:
            if data is None:
                return data
            return cast(Union[None, str], data)

        title = _parse_title(d.pop("title"))

        def _parse_region(data: object) -> Union[None, Region]:
            if data is None:
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                region_type_0 = Region(data)

                return region_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Region], data)

        region = _parse_region(d.pop("region"))

        def _parse_queries(data: object) -> Union[List[str], None]:
            if data is None:
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                queries_type_0 = cast(List[str], data)

                return queries_type_0
            except:  # noqa: E722
                pass
            return cast(Union[List[str], None], data)

        queries = _parse_queries(d.pop("queries"))

        def _parse_time_limit(data: object) -> Union[None, TimeLimit]:
            if data is None:
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                time_limit_type_0 = TimeLimit(data)

                return time_limit_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, TimeLimit], data)

        time_limit = _parse_time_limit(d.pop("time_limit"))

        def _parse_max_results(data: object) -> Union[None, Unset, int]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, int], data)

        max_results = _parse_max_results(d.pop("max_results", UNSET))

        search_ingestion_config_update = cls(
            title=title,
            region=region,
            queries=queries,
            time_limit=time_limit,
            max_results=max_results,
        )

        return search_ingestion_config_update
