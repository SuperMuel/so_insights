import datetime
from typing import Any, Dict, List, Type, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.ingestion_run_status import IngestionRunStatus
from ..models.time_limit import TimeLimit
from ..types import UNSET, Unset

T = TypeVar("T", bound="IngestionRun")


@_attrs_define
class IngestionRun:
    """
    Attributes:
        workspace_id (str):  Example: 5eb7cf5a86d9755df3a6c593.
        queries_set_id (str):  Example: 5eb7cf5a86d9755df3a6c593.
        time_limit (TimeLimit):
        max_results (int):
        status (IngestionRunStatus):
        field_id (Union[None, Unset, str]): MongoDB document ObjectID
        created_at (Union[Unset, datetime.datetime]):
        end_at (Union[None, Unset, datetime.datetime]):
        successfull_queries (Union[None, Unset, int]):
        error (Union[None, Unset, str]):
        n_inserted (Union[None, Unset, int]):
    """

    workspace_id: str
    queries_set_id: str
    time_limit: TimeLimit
    max_results: int
    status: IngestionRunStatus
    field_id: Union[None, Unset, str] = UNSET
    created_at: Union[Unset, datetime.datetime] = UNSET
    end_at: Union[None, Unset, datetime.datetime] = UNSET
    successfull_queries: Union[None, Unset, int] = UNSET
    error: Union[None, Unset, str] = UNSET
    n_inserted: Union[None, Unset, int] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        workspace_id = self.workspace_id

        queries_set_id = self.queries_set_id

        time_limit = self.time_limit.value

        max_results = self.max_results

        status = self.status.value

        field_id: Union[None, Unset, str]
        if isinstance(self.field_id, Unset):
            field_id = UNSET
        else:
            field_id = self.field_id

        created_at: Union[Unset, str] = UNSET
        if not isinstance(self.created_at, Unset):
            created_at = self.created_at.isoformat()

        end_at: Union[None, Unset, str]
        if isinstance(self.end_at, Unset):
            end_at = UNSET
        elif isinstance(self.end_at, datetime.datetime):
            end_at = self.end_at.isoformat()
        else:
            end_at = self.end_at

        successfull_queries: Union[None, Unset, int]
        if isinstance(self.successfull_queries, Unset):
            successfull_queries = UNSET
        else:
            successfull_queries = self.successfull_queries

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

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "workspace_id": workspace_id,
                "queries_set_id": queries_set_id,
                "time_limit": time_limit,
                "max_results": max_results,
                "status": status,
            }
        )
        if field_id is not UNSET:
            field_dict["_id"] = field_id
        if created_at is not UNSET:
            field_dict["created_at"] = created_at
        if end_at is not UNSET:
            field_dict["end_at"] = end_at
        if successfull_queries is not UNSET:
            field_dict["successfull_queries"] = successfull_queries
        if error is not UNSET:
            field_dict["error"] = error
        if n_inserted is not UNSET:
            field_dict["n_inserted"] = n_inserted

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        workspace_id = d.pop("workspace_id")

        queries_set_id = d.pop("queries_set_id")

        time_limit = TimeLimit(d.pop("time_limit"))

        max_results = d.pop("max_results")

        status = IngestionRunStatus(d.pop("status"))

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

        def _parse_successfull_queries(data: object) -> Union[None, Unset, int]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, int], data)

        successfull_queries = _parse_successfull_queries(d.pop("successfull_queries", UNSET))

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
            queries_set_id=queries_set_id,
            time_limit=time_limit,
            max_results=max_results,
            status=status,
            field_id=field_id,
            created_at=created_at,
            end_at=end_at,
            successfull_queries=successfull_queries,
            error=error,
            n_inserted=n_inserted,
        )

        ingestion_run.additional_properties = d
        return ingestion_run

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
