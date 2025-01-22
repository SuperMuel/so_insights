import datetime
from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.language import Language
from ..types import UNSET, Unset

T = TypeVar("T", bound="ClusterOverview")


@_attrs_define
class ClusterOverview:
    """Provides a summary of what a cluster of articles is about.

    When you have a group of related articles, it's useful to have a quick
    summary of what connects them. The ClusterOverview is the result of an LLM
    generating a title and a brief summary that captures the main theme or topic
    of the majority of articles in a cluster.

        Attributes:
            title (str):
            summary (str):
            language (Language):
            created_at (Union[None, Unset, datetime.datetime]):
    """

    title: str
    summary: str
    language: Language
    created_at: Union[None, Unset, datetime.datetime] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        title = self.title

        summary = self.summary

        language = self.language.value

        created_at: Union[None, Unset, str]
        if isinstance(self.created_at, Unset):
            created_at = UNSET
        elif isinstance(self.created_at, datetime.datetime):
            created_at = self.created_at.isoformat()
        else:
            created_at = self.created_at

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "title": title,
                "summary": summary,
                "language": language,
            }
        )
        if created_at is not UNSET:
            field_dict["created_at"] = created_at

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        d = src_dict.copy()
        title = d.pop("title")

        summary = d.pop("summary")

        language = Language(d.pop("language"))

        def _parse_created_at(data: object) -> Union[None, Unset, datetime.datetime]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                created_at_type_0 = isoparse(data)

                return created_at_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, datetime.datetime], data)

        created_at = _parse_created_at(d.pop("created_at", UNSET))

        cluster_overview = cls(
            title=title,
            summary=summary,
            language=language,
            created_at=created_at,
        )

        cluster_overview.additional_properties = d
        return cluster_overview

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
