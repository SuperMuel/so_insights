import datetime
from typing import Any, Dict, List, Type, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

T = TypeVar("T", bound="AnalysisTaskCreate")


@_attrs_define
class AnalysisTaskCreate:
    """
    Attributes:
        data_start (datetime.datetime):
        data_end (datetime.datetime):
    """

    data_start: datetime.datetime
    data_end: datetime.datetime
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        data_start = self.data_start.isoformat()

        data_end = self.data_end.isoformat()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "data_start": data_start,
                "data_end": data_end,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        data_start = isoparse(d.pop("data_start"))

        data_end = isoparse(d.pop("data_end"))

        analysis_task_create = cls(
            data_start=data_start,
            data_end=data_end,
        )

        analysis_task_create.additional_properties = d
        return analysis_task_create

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
