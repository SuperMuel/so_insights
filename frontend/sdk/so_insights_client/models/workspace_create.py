from typing import Any, TypeVar, Union

from attrs import define as _attrs_define

from ..models.language import Language
from ..types import UNSET, Unset

T = TypeVar("T", bound="WorkspaceCreate")


@_attrs_define
class WorkspaceCreate:
    """
    Attributes:
        name (str):
        language (Language):
        description (Union[Unset, str]):  Default: ''.
    """

    name: str
    language: Language
    description: Union[Unset, str] = ""

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        language = self.language.value

        description = self.description

        field_dict: dict[str, Any] = {}
        field_dict.update(
            {
                "name": name,
                "language": language,
            }
        )
        if description is not UNSET:
            field_dict["description"] = description

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        d = src_dict.copy()
        name = d.pop("name")

        language = Language(d.pop("language"))

        description = d.pop("description", UNSET)

        workspace_create = cls(
            name=name,
            language=language,
            description=description,
        )

        return workspace_create
