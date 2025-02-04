from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.analysis_result_analysis_type import AnalysisResultAnalysisType
from ..types import UNSET, Unset

T = TypeVar("T", bound="AnalysisResult")


@_attrs_define
class AnalysisResult:
    """Base class for analysis results.

    Attributes:
        analysis_type (AnalysisResultAnalysisType):
        articles_count (Union[None, Unset, int]): Number of articles processed in this session
    """

    analysis_type: AnalysisResultAnalysisType
    articles_count: Union[None, Unset, int] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        analysis_type = self.analysis_type.value

        articles_count: Union[None, Unset, int]
        if isinstance(self.articles_count, Unset):
            articles_count = UNSET
        else:
            articles_count = self.articles_count

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "analysis_type": analysis_type,
            }
        )
        if articles_count is not UNSET:
            field_dict["articles_count"] = articles_count

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        d = src_dict.copy()
        analysis_type = AnalysisResultAnalysisType(d.pop("analysis_type"))

        def _parse_articles_count(data: object) -> Union[None, Unset, int]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, int], data)

        articles_count = _parse_articles_count(d.pop("articles_count", UNSET))

        analysis_result = cls(
            analysis_type=analysis_type,
            articles_count=articles_count,
        )

        analysis_result.additional_properties = d
        return analysis_result

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
