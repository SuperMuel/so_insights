from typing import Any, Dict, List, Type, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.time_limit import TimeLimit

T = TypeVar("T", bound="IngestionRunCreate")


@_attrs_define
class IngestionRunCreate:
    """
    Attributes:
        time_limit (TimeLimit):
        max_results (int):
        search_query_set_id (str):  Example: 5eb7cf5a86d9755df3a6c593.
    """

    time_limit: TimeLimit
    max_results: int
    search_query_set_id: str
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        time_limit = self.time_limit.value

        max_results = self.max_results

        search_query_set_id = self.search_query_set_id

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "time_limit": time_limit,
                "max_results": max_results,
                "search_query_set_id": search_query_set_id,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        time_limit = TimeLimit(d.pop("time_limit"))

        max_results = d.pop("max_results")

        search_query_set_id = d.pop("search_query_set_id")

        ingestion_run_create = cls(
            time_limit=time_limit,
            max_results=max_results,
            search_query_set_id=search_query_set_id,
        )

        ingestion_run_create.additional_properties = d
        return ingestion_run_create

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
