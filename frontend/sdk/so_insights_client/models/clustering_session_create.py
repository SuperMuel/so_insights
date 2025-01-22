import datetime
from typing import Any, TypeVar

from attrs import define as _attrs_define
from dateutil.parser import isoparse

T = TypeVar("T", bound="ClusteringSessionCreate")


@_attrs_define
class ClusteringSessionCreate:
    """
    Attributes:
        data_start (datetime.datetime):
        data_end (datetime.datetime):
    """

    data_start: datetime.datetime
    data_end: datetime.datetime

    def to_dict(self) -> dict[str, Any]:
        data_start = self.data_start.isoformat()

        data_end = self.data_end.isoformat()

        field_dict: dict[str, Any] = {}
        field_dict.update(
            {
                "data_start": data_start,
                "data_end": data_end,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        d = src_dict.copy()
        data_start = isoparse(d.pop("data_start"))

        data_end = isoparse(d.pop("data_end"))

        clustering_session_create = cls(
            data_start=data_start,
            data_end=data_end,
        )

        return clustering_session_create
