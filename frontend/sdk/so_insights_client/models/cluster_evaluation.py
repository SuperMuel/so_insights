from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.cluster_evaluation_relevance_level import ClusterEvaluationRelevanceLevel

T = TypeVar("T", bound="ClusterEvaluation")


@_attrs_define
class ClusterEvaluation:
    """Represents an assessment of a cluster's quality and relevance to the workspace.

    After articles are grouped into clusters, it's important to understand how
    good these groupings are for the workspace owner. The ClusterEvaluation provides
    a way to score and explain the relevance of a cluster.

    It includes a justification for the evaluation, a relevance level
    (like "highly relevant", "somewhat relevant", or "not relevant"), and a
    confidence score for this evaluation.

    Done automatically by LLM after clustering and overview generation.

        Attributes:
            justification (str): Your explanation for the relevance level.
            relevance_level (ClusterEvaluationRelevanceLevel):
            confidence_score (float): A score between 0 and 1 indicating how confident we are in the relevance level of this
                cluster
    """

    justification: str
    relevance_level: ClusterEvaluationRelevanceLevel
    confidence_score: float
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        justification = self.justification

        relevance_level = self.relevance_level.value

        confidence_score = self.confidence_score

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "justification": justification,
                "relevance_level": relevance_level,
                "confidence_score": confidence_score,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        d = src_dict.copy()
        justification = d.pop("justification")

        relevance_level = ClusterEvaluationRelevanceLevel(d.pop("relevance_level"))

        confidence_score = d.pop("confidence_score")

        cluster_evaluation = cls(
            justification=justification,
            relevance_level=relevance_level,
            confidence_score=confidence_score,
        )

        cluster_evaluation.additional_properties = d
        return cluster_evaluation

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
