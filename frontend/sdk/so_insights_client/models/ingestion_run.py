import datetime
from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.status import Status
from ..types import UNSET, Unset

T = TypeVar("T", bound="IngestionRun")


@_attrs_define
class IngestionRun:
    """Represents a single execution of an ingestion process.

    An IngestionRun tracks the details of one attempt to collect data using an IngestionConfig.

        Attributes:
            workspace_id (str):  Example: 5eb7cf5a86d9755df3a6c593.
            config_id (str): ID of the ingestion config used for this run Example: 5eb7cf5a86d9755df3a6c593.
            field_id (Union[None, Unset, str]): MongoDB document ObjectID
            created_at (Union[Unset, datetime.datetime]):
            start_at (Union[None, Unset, datetime.datetime]): Timestamp when the run started
            end_at (Union[None, Unset, datetime.datetime]): Timestamp when the run ended
            status (Union[Unset, Status]):  Default: Status.PENDING.
            error (Union[None, Unset, str]): Error message if the run failed
            n_inserted (Union[None, Unset, int]): Number of new articles inserted in the DB during this run
    """

    workspace_id: str
    config_id: str
    field_id: Union[None, Unset, str] = UNSET
    created_at: Union[Unset, datetime.datetime] = UNSET
    start_at: Union[None, Unset, datetime.datetime] = UNSET
    end_at: Union[None, Unset, datetime.datetime] = UNSET
    status: Union[Unset, Status] = Status.PENDING
    error: Union[None, Unset, str] = UNSET
    n_inserted: Union[None, Unset, int] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        workspace_id = self.workspace_id

        config_id = self.config_id

        field_id: Union[None, Unset, str]
        if isinstance(self.field_id, Unset):
            field_id = UNSET
        else:
            field_id = self.field_id

        created_at: Union[Unset, str] = UNSET
        if not isinstance(self.created_at, Unset):
            created_at = self.created_at.isoformat()

        start_at: Union[None, Unset, str]
        if isinstance(self.start_at, Unset):
            start_at = UNSET
        elif isinstance(self.start_at, datetime.datetime):
            start_at = self.start_at.isoformat()
        else:
            start_at = self.start_at

        end_at: Union[None, Unset, str]
        if isinstance(self.end_at, Unset):
            end_at = UNSET
        elif isinstance(self.end_at, datetime.datetime):
            end_at = self.end_at.isoformat()
        else:
            end_at = self.end_at

        status: Union[Unset, str] = UNSET
        if not isinstance(self.status, Unset):
            status = self.status.value

        error: Union[None, Unset, str]
        if isinstance(self.error, Unset):
            error = UNSET
        else:
            error = self.error

        n_inserted: Union[None, Unset, int]
        if isinstance(self.n_inserted, Unset):
            n_inserted = UNSET
        else:
            n_inserted = self.n_inserted

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "workspace_id": workspace_id,
                "config_id": config_id,
            }
        )
        if field_id is not UNSET:
            field_dict["_id"] = field_id
        if created_at is not UNSET:
            field_dict["created_at"] = created_at
        if start_at is not UNSET:
            field_dict["start_at"] = start_at
        if end_at is not UNSET:
            field_dict["end_at"] = end_at
        if status is not UNSET:
            field_dict["status"] = status
        if error is not UNSET:
            field_dict["error"] = error
        if n_inserted is not UNSET:
            field_dict["n_inserted"] = n_inserted

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        d = src_dict.copy()
        workspace_id = d.pop("workspace_id")

        config_id = d.pop("config_id")

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

        def _parse_start_at(data: object) -> Union[None, Unset, datetime.datetime]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                start_at_type_0 = isoparse(data)

                return start_at_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, datetime.datetime], data)

        start_at = _parse_start_at(d.pop("start_at", UNSET))

        def _parse_end_at(data: object) -> Union[None, Unset, datetime.datetime]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                end_at_type_0 = isoparse(data)

                return end_at_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, datetime.datetime], data)

        end_at = _parse_end_at(d.pop("end_at", UNSET))

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

        def _parse_n_inserted(data: object) -> Union[None, Unset, int]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, int], data)

        n_inserted = _parse_n_inserted(d.pop("n_inserted", UNSET))

        ingestion_run = cls(
            workspace_id=workspace_id,
            config_id=config_id,
            field_id=field_id,
            created_at=created_at,
            start_at=start_at,
            end_at=end_at,
            status=status,
            error=error,
            n_inserted=n_inserted,
        )

        ingestion_run.additional_properties = d
        return ingestion_run

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
