from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.hdbscan_settings import HdbscanSettings


T = TypeVar("T", bound="ClusteringAnalysisParams")


@_attrs_define
class ClusteringAnalysisParams:
    """Parameters specific to clustering analysis.

    Attributes:
        hdbscan_settings (Union[Unset, HdbscanSettings]):
    """

    hdbscan_settings: Union[Unset, "HdbscanSettings"] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        hdbscan_settings: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.hdbscan_settings, Unset):
            hdbscan_settings = self.hdbscan_settings.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if hdbscan_settings is not UNSET:
            field_dict["hdbscan_settings"] = hdbscan_settings

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        from ..models.hdbscan_settings import HdbscanSettings

        d = src_dict.copy()
        _hdbscan_settings = d.pop("hdbscan_settings", UNSET)
        hdbscan_settings: Union[Unset, HdbscanSettings]
        if isinstance(_hdbscan_settings, Unset):
            hdbscan_settings = UNSET
        else:
            hdbscan_settings = HdbscanSettings.from_dict(_hdbscan_settings)

        clustering_analysis_params = cls(
            hdbscan_settings=hdbscan_settings,
        )

        clustering_analysis_params.additional_properties = d
        return clustering_analysis_params

    @property
    def additional_keys(self) -> list[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
