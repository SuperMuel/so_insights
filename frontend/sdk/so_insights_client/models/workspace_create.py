from typing import Any, Dict, Type, TypeVar, Union

from attrs import define as _attrs_define

from ..types import UNSET, Unset

T = TypeVar("T", bound="WorkspaceCreate")


@_attrs_define
class WorkspaceCreate:
    """
    Attributes:
        name (str):
        description (Union[Unset, str]):  Default: ''.
    """

    name: str
    description: Union[Unset, str] = ""

    def to_dict(self) -> Dict[str, Any]:
        name = self.name

        description = self.description

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "name": name,
            }
        )
        if description is not UNSET:
            field_dict["description"] = description

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        name = d.pop("name")

        description = d.pop("description", UNSET)

        workspace_create = cls(
            name=name,
            description=description,
        )

        return workspace_create
