import datetime
from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.ingestion_config_type import IngestionConfigType
from ..models.region import Region
from ..models.time_limit import TimeLimit
from ..types import UNSET, Unset

T = TypeVar("T", bound="SearchIngestionConfig")


@_attrs_define
class SearchIngestionConfig:
    """Configuration for ingesting data from web searches.

    This config tells the system how to perform web searches to gather content.

        Attributes:
            workspace_id (str):  Example: 5eb7cf5a86d9755df3a6c593.
            title (str):
            queries (list[str]): List of search queries to use for ingestion
            region (Region):
            max_results (int): Maximum number of results to fetch per query
            time_limit (TimeLimit):
            first_run_max_results (int): Maximum number of results to fetch per query on the first run
            first_run_time_limit (TimeLimit):
            field_id (Union[None, Unset, str]): MongoDB document ObjectID
            created_at (Union[Unset, datetime.datetime]):
            updated_at (Union[Unset, datetime.datetime]):
            type_ (Union[Unset, IngestionConfigType]):
            last_run_at (Union[None, Unset, datetime.datetime]):
    """

    workspace_id: str
    title: str
    queries: list[str]
    region: Region
    max_results: int
    time_limit: TimeLimit
    first_run_max_results: int
    first_run_time_limit: TimeLimit
    field_id: Union[None, Unset, str] = UNSET
    created_at: Union[Unset, datetime.datetime] = UNSET
    updated_at: Union[Unset, datetime.datetime] = UNSET
    type_: Union[Unset, IngestionConfigType] = UNSET
    last_run_at: Union[None, Unset, datetime.datetime] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        workspace_id = self.workspace_id

        title = self.title

        queries = self.queries

        region = self.region.value

        max_results = self.max_results

        time_limit = self.time_limit.value

        first_run_max_results = self.first_run_max_results

        first_run_time_limit = self.first_run_time_limit.value

        field_id: Union[None, Unset, str]
        if isinstance(self.field_id, Unset):
            field_id = UNSET
        else:
            field_id = self.field_id

        created_at: Union[Unset, str] = UNSET
        if not isinstance(self.created_at, Unset):
            created_at = self.created_at.isoformat()

        updated_at: Union[Unset, str] = UNSET
        if not isinstance(self.updated_at, Unset):
            updated_at = self.updated_at.isoformat()

        type_: Union[Unset, str] = UNSET
        if not isinstance(self.type_, Unset):
            type_ = self.type_.value

        last_run_at: Union[None, Unset, str]
        if isinstance(self.last_run_at, Unset):
            last_run_at = UNSET
        elif isinstance(self.last_run_at, datetime.datetime):
            last_run_at = self.last_run_at.isoformat()
        else:
            last_run_at = self.last_run_at

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "workspace_id": workspace_id,
                "title": title,
                "queries": queries,
                "region": region,
                "max_results": max_results,
                "time_limit": time_limit,
                "first_run_max_results": first_run_max_results,
                "first_run_time_limit": first_run_time_limit,
            }
        )
        if field_id is not UNSET:
            field_dict["_id"] = field_id
        if created_at is not UNSET:
            field_dict["created_at"] = created_at
        if updated_at is not UNSET:
            field_dict["updated_at"] = updated_at
        if type_ is not UNSET:
            field_dict["type"] = type_
        if last_run_at is not UNSET:
            field_dict["last_run_at"] = last_run_at

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        d = src_dict.copy()
        workspace_id = d.pop("workspace_id")

        title = d.pop("title")

        queries = cast(list[str], d.pop("queries"))

        region = Region(d.pop("region"))

        max_results = d.pop("max_results")

        time_limit = TimeLimit(d.pop("time_limit"))

        first_run_max_results = d.pop("first_run_max_results")

        first_run_time_limit = TimeLimit(d.pop("first_run_time_limit"))

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

        _updated_at = d.pop("updated_at", UNSET)
        updated_at: Union[Unset, datetime.datetime]
        if isinstance(_updated_at, Unset):
            updated_at = UNSET
        else:
            updated_at = isoparse(_updated_at)

        _type_ = d.pop("type", UNSET)
        type_: Union[Unset, IngestionConfigType]
        if isinstance(_type_, Unset):
            type_ = UNSET
        else:
            type_ = IngestionConfigType(_type_)

        def _parse_last_run_at(data: object) -> Union[None, Unset, datetime.datetime]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                last_run_at_type_0 = isoparse(data)

                return last_run_at_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, datetime.datetime], data)

        last_run_at = _parse_last_run_at(d.pop("last_run_at", UNSET))

        search_ingestion_config = cls(
            workspace_id=workspace_id,
            title=title,
            queries=queries,
            region=region,
            max_results=max_results,
            time_limit=time_limit,
            first_run_max_results=first_run_max_results,
            first_run_time_limit=first_run_time_limit,
            field_id=field_id,
            created_at=created_at,
            updated_at=updated_at,
            type_=type_,
            last_run_at=last_run_at,
        )

        search_ingestion_config.additional_properties = d
        return search_ingestion_config

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
