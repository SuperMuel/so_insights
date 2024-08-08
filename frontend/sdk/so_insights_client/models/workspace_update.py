from typing import Any, Dict, Type, TypeVar, Union, cast

from attrs import define as _attrs_define

T = TypeVar("T", bound="WorkspaceUpdate")


@_attrs_define
class WorkspaceUpdate:
    """
    Attributes:
        name (Union[None, str]):
        description (Union[None, str]):
    """

    name: Union[None, str]
    description: Union[None, str]

    def to_dict(self) -> Dict[str, Any]:
        name: Union[None, str]
        name = self.name

        description: Union[None, str]
        description = self.description

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "name": name,
                "description": description,
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

        workspace_update = cls(
            name=name,
            description=description,
        )

        return workspace_update
