from typing import Any, Dict, List, Type, TypeVar, Union, cast

from attrs import define as _attrs_define

from ..models.region import Region
from ..types import UNSET, Unset

T = TypeVar("T", bound="SearchQuerySetUpdate")


@_attrs_define
class SearchQuerySetUpdate:
    """
    Attributes:
        queries (Union[List[str], None, Unset]):
        title (Union[None, Unset, str]):
        region (Union[None, Region, Unset]):
    """

    queries: Union[List[str], None, Unset] = UNSET
    title: Union[None, Unset, str] = UNSET
    region: Union[None, Region, Unset] = UNSET

    def to_dict(self) -> Dict[str, Any]:
        queries: Union[List[str], None, Unset]
        if isinstance(self.queries, Unset):
            queries = UNSET
        elif isinstance(self.queries, list):
            queries = self.queries

        else:
            queries = self.queries

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

        field_dict: Dict[str, Any] = {}
        field_dict.update({})
        if queries is not UNSET:
            field_dict["queries"] = queries
        if title is not UNSET:
            field_dict["title"] = title
        if region is not UNSET:
            field_dict["region"] = region

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def _parse_queries(data: object) -> Union[List[str], None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                queries_type_0 = cast(List[str], data)

                return queries_type_0
            except:  # noqa: E722
                pass
            return cast(Union[List[str], None, Unset], data)

        queries = _parse_queries(d.pop("queries", UNSET))

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

        search_query_set_update = cls(
            queries=queries,
            title=title,
            region=region,
        )

        return search_query_set_update
