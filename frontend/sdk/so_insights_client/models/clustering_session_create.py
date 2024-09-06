import datetime
from typing import Any, Dict, Type, TypeVar

from attrs import define as _attrs_define
from dateutil.parser import isoparse

T = TypeVar("T", bound="ClusteringSessionCreate")


@_attrs_define
class ClusteringSessionCreate:
    """
    Attributes:
        workspace_id (str):  Example: 5eb7cf5a86d9755df3a6c593.
        data_start (datetime.datetime):
        data_end (datetime.datetime):
    """

    workspace_id: str
    data_start: datetime.datetime
    data_end: datetime.datetime

    def to_dict(self) -> Dict[str, Any]:
        workspace_id = self.workspace_id

        data_start = self.data_start.isoformat()

        data_end = self.data_end.isoformat()

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "workspace_id": workspace_id,
                "data_start": data_start,
                "data_end": data_end,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        workspace_id = d.pop("workspace_id")

        data_start = isoparse(d.pop("data_start"))

        data_end = isoparse(d.pop("data_end"))

        clustering_session_create = cls(
            workspace_id=workspace_id,
            data_start=data_start,
            data_end=data_end,
        )

        return clustering_session_create
