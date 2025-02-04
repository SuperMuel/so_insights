from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="ClusteringRunEvaluationResult")


@_attrs_define
class ClusteringRunEvaluationResult:
    """
    Attributes:
        relevant_clusters_count (int): Number of clusters deemed highly relevant
        somewhat_relevant_clusters_count (int): Number of clusters deemed somewhat relevant
        irrelevant_clusters_count (int): Number of clusters deemed not relevant
    """

    relevant_clusters_count: int
    somewhat_relevant_clusters_count: int
    irrelevant_clusters_count: int
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        relevant_clusters_count = self.relevant_clusters_count

        somewhat_relevant_clusters_count = self.somewhat_relevant_clusters_count

        irrelevant_clusters_count = self.irrelevant_clusters_count

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "relevant_clusters_count": relevant_clusters_count,
                "somewhat_relevant_clusters_count": somewhat_relevant_clusters_count,
                "irrelevant_clusters_count": irrelevant_clusters_count,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        d = src_dict.copy()
        relevant_clusters_count = d.pop("relevant_clusters_count")

        somewhat_relevant_clusters_count = d.pop("somewhat_relevant_clusters_count")

        irrelevant_clusters_count = d.pop("irrelevant_clusters_count")

        clustering_run_evaluation_result = cls(
            relevant_clusters_count=relevant_clusters_count,
            somewhat_relevant_clusters_count=somewhat_relevant_clusters_count,
            irrelevant_clusters_count=irrelevant_clusters_count,
        )

        clustering_run_evaluation_result.additional_properties = d
        return clustering_run_evaluation_result

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
