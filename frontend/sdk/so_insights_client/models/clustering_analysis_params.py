from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.analysis_type import AnalysisType
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.hdbscan_settings import HdbscanSettings


T = TypeVar("T", bound="ClusteringAnalysisParams")


@_attrs_define
class ClusteringAnalysisParams:
    """Parameters specific to clustering analysis.

    Attributes:
        hdbscan_settings (HdbscanSettings):
        analysis_type (Union[Unset, AnalysisType]):
    """

    hdbscan_settings: "HdbscanSettings"
    analysis_type: Union[Unset, AnalysisType] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        hdbscan_settings = self.hdbscan_settings.to_dict()

        analysis_type: Union[Unset, str] = UNSET
        if not isinstance(self.analysis_type, Unset):
            analysis_type = self.analysis_type.value

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "hdbscan_settings": hdbscan_settings,
            }
        )
        if analysis_type is not UNSET:
            field_dict["analysis_type"] = analysis_type

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        from ..models.hdbscan_settings import HdbscanSettings

        d = src_dict.copy()
        hdbscan_settings = HdbscanSettings.from_dict(d.pop("hdbscan_settings"))

        _analysis_type = d.pop("analysis_type", UNSET)
        analysis_type: Union[Unset, AnalysisType]
        if isinstance(_analysis_type, Unset):
            analysis_type = UNSET
        else:
            analysis_type = AnalysisType(_analysis_type)

        clustering_analysis_params = cls(
            hdbscan_settings=hdbscan_settings,
            analysis_type=analysis_type,
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
