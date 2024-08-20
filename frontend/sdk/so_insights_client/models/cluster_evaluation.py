from typing import Any, Dict, List, Type, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.cluster_evaluation_relevance_level import ClusterEvaluationRelevanceLevel

T = TypeVar("T", bound="ClusterEvaluation")


@_attrs_define
class ClusterEvaluation:
    """
    Attributes:
        justification (str): Your explanation for the relevance level.
        relevance_level (ClusterEvaluationRelevanceLevel):
        confidence_score (float):
    """

    justification: str
    relevance_level: ClusterEvaluationRelevanceLevel
    confidence_score: float
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        justification = self.justification

        relevance_level = self.relevance_level.value

        confidence_score = self.confidence_score

        field_dict: Dict[str, Any] = {}
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
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
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
