from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.ingestion_config_type import IngestionConfigType
from ..types import UNSET, Unset

T = TypeVar("T", bound="SearchIngestionRunResult")


@_attrs_define
class SearchIngestionRunResult:
    """
    Attributes:
        successfull_queries (int):
        n_inserted (int):
        type (Union[Unset, IngestionConfigType]):  Default: IngestionConfigType.SEARCH.
    """

    successfull_queries: int
    n_inserted: int
    type: Union[Unset, IngestionConfigType] = IngestionConfigType.SEARCH
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        successfull_queries = self.successfull_queries

        n_inserted = self.n_inserted

        type: Union[Unset, str] = UNSET
        if not isinstance(self.type, Unset):
            type = self.type.value

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "successfull_queries": successfull_queries,
                "n_inserted": n_inserted,
            }
        )
        if type is not UNSET:
            field_dict["type"] = type

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        successfull_queries = d.pop("successfull_queries")

        n_inserted = d.pop("n_inserted")

        _type = d.pop("type", UNSET)
        type: Union[Unset, IngestionConfigType]
        if isinstance(_type, Unset):
            type = UNSET
        else:
            type = IngestionConfigType(_type)

        search_ingestion_run_result = cls(
            successfull_queries=successfull_queries,
            n_inserted=n_inserted,
            type=type,
        )

        search_ingestion_run_result.additional_properties = d
        return search_ingestion_run_result

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
