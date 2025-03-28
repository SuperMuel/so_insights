import datetime
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.hdbscan_settings import HdbscanSettings


T = TypeVar("T", bound="Workspace")


@_attrs_define
class Workspace:
    """Represents a project workspace for organizing and managing content.

    A Workspace is like a container for a specific research topic or project. It holds
    settings and metadata that apply to all the content within it.

    Each workspace belongs to an organization.

        Attributes:
            organization_id (str): Reference to the organization that owns this workspace Example: 5eb7cf5a86d9755df3a6c593.
            name (str): The name of the workspace
            field_id (Union[None, Unset, str]): MongoDB document ObjectID
            description (Union[Unset, str]): A detailed description of the workspace's purpose Default: ''.
            created_at (Union[Unset, datetime.datetime]): Timestamp when the workspace was created
            updated_at (Union[Unset, datetime.datetime]): Timestamp of the last update to the workspace
            language (Union[Unset, Any]): The primary language of the workspace content Default: 'fr'.
            hdbscan_settings (Union[Unset, HdbscanSettings]):
            enabled (Union[Unset, bool]): When disabled, nor the ingester nor the analyzer will run for this workspace
                Default: True.
    """

    organization_id: str
    name: str
    field_id: Union[None, Unset, str] = UNSET
    description: Union[Unset, str] = ""
    created_at: Union[Unset, datetime.datetime] = UNSET
    updated_at: Union[Unset, datetime.datetime] = UNSET
    language: Union[Unset, Any] = "fr"
    hdbscan_settings: Union[Unset, "HdbscanSettings"] = UNSET
    enabled: Union[Unset, bool] = True
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        organization_id = self.organization_id

        name = self.name

        field_id: Union[None, Unset, str]
        if isinstance(self.field_id, Unset):
            field_id = UNSET
        else:
            field_id = self.field_id

        description = self.description

        created_at: Union[Unset, str] = UNSET
        if not isinstance(self.created_at, Unset):
            created_at = self.created_at.isoformat()

        updated_at: Union[Unset, str] = UNSET
        if not isinstance(self.updated_at, Unset):
            updated_at = self.updated_at.isoformat()

        language = self.language

        hdbscan_settings: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.hdbscan_settings, Unset):
            hdbscan_settings = self.hdbscan_settings.to_dict()

        enabled = self.enabled

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "organization_id": organization_id,
                "name": name,
            }
        )
        if field_id is not UNSET:
            field_dict["_id"] = field_id
        if description is not UNSET:
            field_dict["description"] = description
        if created_at is not UNSET:
            field_dict["created_at"] = created_at
        if updated_at is not UNSET:
            field_dict["updated_at"] = updated_at
        if language is not UNSET:
            field_dict["language"] = language
        if hdbscan_settings is not UNSET:
            field_dict["hdbscan_settings"] = hdbscan_settings
        if enabled is not UNSET:
            field_dict["enabled"] = enabled

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        from ..models.hdbscan_settings import HdbscanSettings

        d = src_dict.copy()
        organization_id = d.pop("organization_id")

        name = d.pop("name")

        def _parse_field_id(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        field_id = _parse_field_id(d.pop("_id", UNSET))

        description = d.pop("description", UNSET)

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

        language = d.pop("language", UNSET)

        _hdbscan_settings = d.pop("hdbscan_settings", UNSET)
        hdbscan_settings: Union[Unset, HdbscanSettings]
        if isinstance(_hdbscan_settings, Unset):
            hdbscan_settings = UNSET
        else:
            hdbscan_settings = HdbscanSettings.from_dict(_hdbscan_settings)

        enabled = d.pop("enabled", UNSET)

        workspace = cls(
            organization_id=organization_id,
            name=name,
            field_id=field_id,
            description=description,
            created_at=created_at,
            updated_at=updated_at,
            language=language,
            hdbscan_settings=hdbscan_settings,
            enabled=enabled,
        )

        workspace.additional_properties = d
        return workspace

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
