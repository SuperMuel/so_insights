from typing import Any, Dict, List, Type, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.region import Region

T = TypeVar("T", bound="SearchQuerySetCreate")


@_attrs_define
class SearchQuerySetCreate:
    """
    Attributes:
        queries (List[str]):
        title (str):
        region (Region):
    """

    queries: List[str]
    title: str
    region: Region
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        queries = self.queries

        title = self.title

        region = self.region.value

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "queries": queries,
                "title": title,
                "region": region,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        queries = cast(List[str], d.pop("queries"))

        title = d.pop("title")

        region = Region(d.pop("region"))

        search_query_set_create = cls(
            queries=queries,
            title=title,
            region=region,
        )

        search_query_set_create.additional_properties = d
        return search_query_set_create

    @property
    def additional_keys(self) -> List[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
