import datetime
from typing import Any, Dict, List, Type, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.status import Status
from ..types import UNSET, Unset

T = TypeVar("T", bound="AnalysisTask")


@_attrs_define
class AnalysisTask:
    """
    Attributes:
        workspace_id (str):  Example: 5eb7cf5a86d9755df3a6c593.
        data_start (datetime.datetime):
        data_end (datetime.datetime):
        field_id (Union[None, Unset, str]): MongoDB document ObjectID
        created_at (Union[Unset, datetime.datetime]):
        status (Union[Unset, Status]):  Default: Status.PENDING.
        error (Union[None, Unset, str]):
        session_id (Union[None, Unset, str]):
    """

    workspace_id: str
    data_start: datetime.datetime
    data_end: datetime.datetime
    field_id: Union[None, Unset, str] = UNSET
    created_at: Union[Unset, datetime.datetime] = UNSET
    status: Union[Unset, Status] = Status.PENDING
    error: Union[None, Unset, str] = UNSET
    session_id: Union[None, Unset, str] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        workspace_id = self.workspace_id

        data_start = self.data_start.isoformat()

        data_end = self.data_end.isoformat()

        field_id: Union[None, Unset, str]
        if isinstance(self.field_id, Unset):
            field_id = UNSET
        else:
            field_id = self.field_id

        created_at: Union[Unset, str] = UNSET
        if not isinstance(self.created_at, Unset):
            created_at = self.created_at.isoformat()

        status: Union[Unset, str] = UNSET
        if not isinstance(self.status, Unset):
            status = self.status.value

        error: Union[None, Unset, str]
        if isinstance(self.error, Unset):
            error = UNSET
        else:
            error = self.error

        session_id: Union[None, Unset, str]
        if isinstance(self.session_id, Unset):
            session_id = UNSET
        else:
            session_id = self.session_id

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "workspace_id": workspace_id,
                "data_start": data_start,
                "data_end": data_end,
            }
        )
        if field_id is not UNSET:
            field_dict["_id"] = field_id
        if created_at is not UNSET:
            field_dict["created_at"] = created_at
        if status is not UNSET:
            field_dict["status"] = status
        if error is not UNSET:
            field_dict["error"] = error
        if session_id is not UNSET:
            field_dict["session_id"] = session_id

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        workspace_id = d.pop("workspace_id")

        data_start = isoparse(d.pop("data_start"))

        data_end = isoparse(d.pop("data_end"))

        def _parse_field_id(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        field_id = _parse_field_id(d.pop("_id", UNSET))

        _created_at = d.pop("created_at", UNSET)
        created_at: Union[Unset, datetime.datetime]
        if isinstance(_created_at, Unset):
            created_at = UNSET
        else:
            created_at = isoparse(_created_at)

        _status = d.pop("status", UNSET)
        status: Union[Unset, Status]
        if isinstance(_status, Unset):
            status = UNSET
        else:
            status = Status(_status)

        def _parse_error(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        error = _parse_error(d.pop("error", UNSET))

        def _parse_session_id(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        session_id = _parse_session_id(d.pop("session_id", UNSET))

        analysis_task = cls(
            workspace_id=workspace_id,
            data_start=data_start,
            data_end=data_end,
            field_id=field_id,
            created_at=created_at,
            status=status,
            error=error,
            session_id=session_id,
        )

        analysis_task.additional_properties = d
        return analysis_task

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
