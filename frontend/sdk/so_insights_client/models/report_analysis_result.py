from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.analysis_type import AnalysisType
from ..types import UNSET, Unset

T = TypeVar("T", bound="ReportAnalysisResult")


@_attrs_define
class ReportAnalysisResult:
    """Results specific to report-style analysis.

    Attributes:
        report_content (str): Markdown content of the generated report
        analysis_type (Union[Unset, AnalysisType]):
        articles_count (Union[None, Unset, int]): Number of articles processed in this session
        relevant_articles_ids (Union[None, Unset, list[str]]): IDs of articles deemed relevant and used in the report
    """

    report_content: str
    analysis_type: Union[Unset, AnalysisType] = UNSET
    articles_count: Union[None, Unset, int] = UNSET
    relevant_articles_ids: Union[None, Unset, list[str]] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        report_content = self.report_content

        analysis_type: Union[Unset, str] = UNSET
        if not isinstance(self.analysis_type, Unset):
            analysis_type = self.analysis_type.value

        articles_count: Union[None, Unset, int]
        if isinstance(self.articles_count, Unset):
            articles_count = UNSET
        else:
            articles_count = self.articles_count

        relevant_articles_ids: Union[None, Unset, list[str]]
        if isinstance(self.relevant_articles_ids, Unset):
            relevant_articles_ids = UNSET
        elif isinstance(self.relevant_articles_ids, list):
            relevant_articles_ids = self.relevant_articles_ids

        else:
            relevant_articles_ids = self.relevant_articles_ids

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "report_content": report_content,
            }
        )
        if analysis_type is not UNSET:
            field_dict["analysis_type"] = analysis_type
        if articles_count is not UNSET:
            field_dict["articles_count"] = articles_count
        if relevant_articles_ids is not UNSET:
            field_dict["relevant_articles_ids"] = relevant_articles_ids

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        d = src_dict.copy()
        report_content = d.pop("report_content")

        _analysis_type = d.pop("analysis_type", UNSET)
        analysis_type: Union[Unset, AnalysisType]
        if isinstance(_analysis_type, Unset):
            analysis_type = UNSET
        else:
            analysis_type = AnalysisType(_analysis_type)

        def _parse_articles_count(data: object) -> Union[None, Unset, int]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, int], data)

        articles_count = _parse_articles_count(d.pop("articles_count", UNSET))

        def _parse_relevant_articles_ids(data: object) -> Union[None, Unset, list[str]]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                relevant_articles_ids_type_0 = cast(list[str], data)

                return relevant_articles_ids_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, list[str]], data)

        relevant_articles_ids = _parse_relevant_articles_ids(d.pop("relevant_articles_ids", UNSET))

        report_analysis_result = cls(
            report_content=report_content,
            analysis_type=analysis_type,
            articles_count=articles_count,
            relevant_articles_ids=relevant_articles_ids,
        )

        report_analysis_result.additional_properties = d
        return report_analysis_result

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
