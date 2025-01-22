from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define

from ..models.language import Language
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.hdbscan_settings import HdbscanSettings


T = TypeVar("T", bound="WorkspaceUpdate")


@_attrs_define
class WorkspaceUpdate:
    """
    Attributes:
        name (Union[None, Unset, str]):
        description (Union[None, Unset, str]):
        language (Union[Language, None, Unset]):
        hdbscan_settings (Union['HdbscanSettings', None, Unset]):
        enabled (Union[None, Unset, bool]):
    """

    name: Union[None, Unset, str] = UNSET
    description: Union[None, Unset, str] = UNSET
    language: Union[Language, None, Unset] = UNSET
    hdbscan_settings: Union["HdbscanSettings", None, Unset] = UNSET
    enabled: Union[None, Unset, bool] = UNSET

    def to_dict(self) -> dict[str, Any]:
        from ..models.hdbscan_settings import HdbscanSettings

        name: Union[None, Unset, str]
        if isinstance(self.name, Unset):
            name = UNSET
        else:
            name = self.name

        description: Union[None, Unset, str]
        if isinstance(self.description, Unset):
            description = UNSET
        else:
            description = self.description

        language: Union[None, Unset, str]
        if isinstance(self.language, Unset):
            language = UNSET
        elif isinstance(self.language, Language):
            language = self.language.value
        else:
            language = self.language

        hdbscan_settings: Union[None, Unset, dict[str, Any]]
        if isinstance(self.hdbscan_settings, Unset):
            hdbscan_settings = UNSET
        elif isinstance(self.hdbscan_settings, HdbscanSettings):
            hdbscan_settings = self.hdbscan_settings.to_dict()
        else:
            hdbscan_settings = self.hdbscan_settings

        enabled: Union[None, Unset, bool]
        if isinstance(self.enabled, Unset):
            enabled = UNSET
        else:
            enabled = self.enabled

        field_dict: dict[str, Any] = {}
        field_dict.update({})
        if name is not UNSET:
            field_dict["name"] = name
        if description is not UNSET:
            field_dict["description"] = description
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

        def _parse_name(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        name = _parse_name(d.pop("name", UNSET))

        def _parse_description(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        description = _parse_description(d.pop("description", UNSET))

        def _parse_language(data: object) -> Union[Language, None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                language_type_0 = Language(data)

                return language_type_0
            except:  # noqa: E722
                pass
            return cast(Union[Language, None, Unset], data)

        language = _parse_language(d.pop("language", UNSET))

        def _parse_hdbscan_settings(data: object) -> Union["HdbscanSettings", None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                hdbscan_settings_type_0 = HdbscanSettings.from_dict(data)

                return hdbscan_settings_type_0
            except:  # noqa: E722
                pass
            return cast(Union["HdbscanSettings", None, Unset], data)

        hdbscan_settings = _parse_hdbscan_settings(d.pop("hdbscan_settings", UNSET))

        def _parse_enabled(data: object) -> Union[None, Unset, bool]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, bool], data)

        enabled = _parse_enabled(d.pop("enabled", UNSET))

        workspace_update = cls(
            name=name,
            description=description,
            language=language,
            hdbscan_settings=hdbscan_settings,
            enabled=enabled,
        )

        return workspace_update
