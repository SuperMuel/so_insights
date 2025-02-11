from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="Topic")


@_attrs_define
class Topic:
    """
    Attributes:
        articles_ids (list[str]): IDs of articles associated with the topic
        title (str): Concise title summarizing the topic
        body (str): Detailed body describing the topic, generated by AI
        body_with_links (Union[None, Unset, str]): Body with links to the articles, formatted in the style
            [[number]](url)]
        first_image (Union[None, Unset, str]): URL of a representative image for the topic, if available
    """

    articles_ids: list[str]
    title: str
    body: str
    body_with_links: Union[None, Unset, str] = UNSET
    first_image: Union[None, Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        articles_ids = self.articles_ids

        title = self.title

        body = self.body

        body_with_links: Union[None, Unset, str]
        if isinstance(self.body_with_links, Unset):
            body_with_links = UNSET
        else:
            body_with_links = self.body_with_links

        first_image: Union[None, Unset, str]
        if isinstance(self.first_image, Unset):
            first_image = UNSET
        else:
            first_image = self.first_image

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "articles_ids": articles_ids,
                "title": title,
                "body": body,
            }
        )
        if body_with_links is not UNSET:
            field_dict["body_with_links"] = body_with_links
        if first_image is not UNSET:
            field_dict["first_image"] = first_image

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        d = src_dict.copy()
        articles_ids = cast(list[str], d.pop("articles_ids"))

        title = d.pop("title")

        body = d.pop("body")

        def _parse_body_with_links(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        body_with_links = _parse_body_with_links(d.pop("body_with_links", UNSET))

        def _parse_first_image(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        first_image = _parse_first_image(d.pop("first_image", UNSET))

        topic = cls(
            articles_ids=articles_ids,
            title=title,
            body=body,
            body_with_links=body_with_links,
            first_image=first_image,
        )

        topic.additional_properties = d
        return topic

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
