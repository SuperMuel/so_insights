from typing import Any, Dict, Type, TypeVar, Union, cast

from attrs import define as _attrs_define

from ..models.language import Language

T = TypeVar("T", bound="WorkspaceUpdate")


@_attrs_define
class WorkspaceUpdate:
    """
    Attributes:
        name (Union[None, str]):
        description (Union[None, str]):
        language (Union[Language, None]):
    """

    name: Union[None, str]
    description: Union[None, str]
    language: Union[Language, None]

    def to_dict(self) -> Dict[str, Any]:
        name: Union[None, str]
        name = self.name

        description: Union[None, str]
        description = self.description

        language: Union[None, str]
        if isinstance(self.language, Language):
            language = self.language.value
        else:
            language = self.language

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "name": name,
                "description": description,
                "language": language,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def _parse_name(data: object) -> Union[None, str]:
            if data is None:
                return data
            return cast(Union[None, str], data)

        name = _parse_name(d.pop("name"))

        def _parse_description(data: object) -> Union[None, str]:
            if data is None:
                return data
            return cast(Union[None, str], data)

        description = _parse_description(d.pop("description"))

        def _parse_language(data: object) -> Union[Language, None]:
            if data is None:
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                language_type_0 = Language(data)

                return language_type_0
            except:  # noqa: E722
                pass
            return cast(Union[Language, None], data)

        language = _parse_language(d.pop("language"))

        workspace_update = cls(
            name=name,
            description=description,
            language=language,
        )

        return workspace_update
