from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.analysis_type import AnalysisType
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.clustering_run_evaluation_result import ClusteringRunEvaluationResult


T = TypeVar("T", bound="ClusteringAnalysisResult")


@_attrs_define
class ClusteringAnalysisResult:
    """Results specific to clustering analysis.

    Attributes:
        clusters_count (int): Total number of clusters formed
        noise_articles_ids (list[str]): IDs of articles classified as noise
        noise_articles_count (int): Number of articles classified as noise
        clustered_articles_count (int): Number of articles successfully clustered
        analysis_type (Union[Unset, AnalysisType]):
        articles_count (Union[None, Unset, int]): Number of articles processed in this session
        evaluation (Union['ClusteringRunEvaluationResult', None, Unset]): Evaluation of the clustering run
        summary (Union[None, Unset, str]): Overall summary of the clusters deemed relevant
        data_loading_time_s (Union[None, Unset, float]): Time taken to load the data, in seconds
        clustering_time_s (Union[None, Unset, float]): Time taken to cluster the data, in seconds
    """

    clusters_count: int
    noise_articles_ids: list[str]
    noise_articles_count: int
    clustered_articles_count: int
    analysis_type: Union[Unset, AnalysisType] = UNSET
    articles_count: Union[None, Unset, int] = UNSET
    evaluation: Union["ClusteringRunEvaluationResult", None, Unset] = UNSET
    summary: Union[None, Unset, str] = UNSET
    data_loading_time_s: Union[None, Unset, float] = UNSET
    clustering_time_s: Union[None, Unset, float] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.clustering_run_evaluation_result import ClusteringRunEvaluationResult

        clusters_count = self.clusters_count

        noise_articles_ids = self.noise_articles_ids

        noise_articles_count = self.noise_articles_count

        clustered_articles_count = self.clustered_articles_count

        analysis_type: Union[Unset, str] = UNSET
        if not isinstance(self.analysis_type, Unset):
            analysis_type = self.analysis_type.value

        articles_count: Union[None, Unset, int]
        if isinstance(self.articles_count, Unset):
            articles_count = UNSET
        else:
            articles_count = self.articles_count

        evaluation: Union[None, Unset, dict[str, Any]]
        if isinstance(self.evaluation, Unset):
            evaluation = UNSET
        elif isinstance(self.evaluation, ClusteringRunEvaluationResult):
            evaluation = self.evaluation.to_dict()
        else:
            evaluation = self.evaluation

        summary: Union[None, Unset, str]
        if isinstance(self.summary, Unset):
            summary = UNSET
        else:
            summary = self.summary

        data_loading_time_s: Union[None, Unset, float]
        if isinstance(self.data_loading_time_s, Unset):
            data_loading_time_s = UNSET
        else:
            data_loading_time_s = self.data_loading_time_s

        clustering_time_s: Union[None, Unset, float]
        if isinstance(self.clustering_time_s, Unset):
            clustering_time_s = UNSET
        else:
            clustering_time_s = self.clustering_time_s

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "clusters_count": clusters_count,
                "noise_articles_ids": noise_articles_ids,
                "noise_articles_count": noise_articles_count,
                "clustered_articles_count": clustered_articles_count,
            }
        )
        if analysis_type is not UNSET:
            field_dict["analysis_type"] = analysis_type
        if articles_count is not UNSET:
            field_dict["articles_count"] = articles_count
        if evaluation is not UNSET:
            field_dict["evaluation"] = evaluation
        if summary is not UNSET:
            field_dict["summary"] = summary
        if data_loading_time_s is not UNSET:
            field_dict["data_loading_time_s"] = data_loading_time_s
        if clustering_time_s is not UNSET:
            field_dict["clustering_time_s"] = clustering_time_s

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        from ..models.clustering_run_evaluation_result import ClusteringRunEvaluationResult

        d = src_dict.copy()
        clusters_count = d.pop("clusters_count")

        noise_articles_ids = cast(list[str], d.pop("noise_articles_ids"))

        noise_articles_count = d.pop("noise_articles_count")

        clustered_articles_count = d.pop("clustered_articles_count")

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

        def _parse_evaluation(data: object) -> Union["ClusteringRunEvaluationResult", None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                evaluation_type_0 = ClusteringRunEvaluationResult.from_dict(data)

                return evaluation_type_0
            except:  # noqa: E722
                pass
            return cast(Union["ClusteringRunEvaluationResult", None, Unset], data)

        evaluation = _parse_evaluation(d.pop("evaluation", UNSET))

        def _parse_summary(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        summary = _parse_summary(d.pop("summary", UNSET))

        def _parse_data_loading_time_s(data: object) -> Union[None, Unset, float]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, float], data)

        data_loading_time_s = _parse_data_loading_time_s(d.pop("data_loading_time_s", UNSET))

        def _parse_clustering_time_s(data: object) -> Union[None, Unset, float]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, float], data)

        clustering_time_s = _parse_clustering_time_s(d.pop("clustering_time_s", UNSET))

        clustering_analysis_result = cls(
            clusters_count=clusters_count,
            noise_articles_ids=noise_articles_ids,
            noise_articles_count=noise_articles_count,
            clustered_articles_count=clustered_articles_count,
            analysis_type=analysis_type,
            articles_count=articles_count,
            evaluation=evaluation,
            summary=summary,
            data_loading_time_s=data_loading_time_s,
            clustering_time_s=clustering_time_s,
        )

        clustering_analysis_result.additional_properties = d
        return clustering_analysis_result

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
