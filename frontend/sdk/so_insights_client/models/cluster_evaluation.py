from typing import Any, Dict, List, Type, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="ClusterEvaluation")


@_attrs_define
class ClusterEvaluation:
    """
    Attributes:
        justification (str):
        relevant (bool):
        irrelevancy_reason (Union[None, Unset, str]):
    """

    justification: str
    relevant: bool
    irrelevancy_reason: Union[None, Unset, str] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        justification = self.justification

        relevant = self.relevant

        irrelevancy_reason: Union[None, Unset, str]
        if isinstance(self.irrelevancy_reason, Unset):
            irrelevancy_reason = UNSET
        else:
            irrelevancy_reason = self.irrelevancy_reason

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "justification": justification,
                "relevant": relevant,
            }
        )
        if irrelevancy_reason is not UNSET:
            field_dict["irrelevancy_reason"] = irrelevancy_reason

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        justification = d.pop("justification")

        relevant = d.pop("relevant")

        def _parse_irrelevancy_reason(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        irrelevancy_reason = _parse_irrelevancy_reason(d.pop("irrelevancy_reason", UNSET))

        cluster_evaluation = cls(
            justification=justification,
            relevant=relevant,
            irrelevancy_reason=irrelevancy_reason,
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
