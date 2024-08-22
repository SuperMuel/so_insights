from typing import Any, Dict, Type, TypeVar, Union

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

    def to_dict(self) -> Dict[str, Any]:
        name = self.name

        language = self.language.value

        description = self.description

        field_dict: Dict[str, Any] = {}
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
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
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
