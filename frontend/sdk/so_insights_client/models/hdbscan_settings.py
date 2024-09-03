from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="HdbscanSettings")


@_attrs_define
class HdbscanSettings:
    """
    Attributes:
        min_cluster_size (Union[Unset, int]):  Default: 3.
        min_samples (Union[Unset, int]):  Default: 1.
    """

    min_cluster_size: Union[Unset, int] = 3
    min_samples: Union[Unset, int] = 1
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        min_cluster_size = self.min_cluster_size

        min_samples = self.min_samples

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if min_cluster_size is not UNSET:
            field_dict["min_cluster_size"] = min_cluster_size
        if min_samples is not UNSET:
            field_dict["min_samples"] = min_samples

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        min_cluster_size = d.pop("min_cluster_size", UNSET)

        min_samples = d.pop("min_samples", UNSET)

        hdbscan_settings = cls(
            min_cluster_size=min_cluster_size,
            min_samples=min_samples,
        )

        hdbscan_settings.additional_properties = d
        return hdbscan_settings

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
