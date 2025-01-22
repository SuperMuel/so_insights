from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="ArticleContentCleanerOutput")


@_attrs_define
class ArticleContentCleanerOutput:
    """Output for the article content cleaner.

    Attributes:
        error (Union[None, Unset, str]): Error message if the content could not be cleaned.
        title (Union[None, Unset, str]): Title of the article
        cleaned_article_content (Union[None, Unset, str]): Cleaned article content in markdown format
    """

    error: Union[None, Unset, str] = UNSET
    title: Union[None, Unset, str] = UNSET
    cleaned_article_content: Union[None, Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        error: Union[None, Unset, str]
        if isinstance(self.error, Unset):
            error = UNSET
        else:
            error = self.error

        title: Union[None, Unset, str]
        if isinstance(self.title, Unset):
            title = UNSET
        else:
            title = self.title

        cleaned_article_content: Union[None, Unset, str]
        if isinstance(self.cleaned_article_content, Unset):
            cleaned_article_content = UNSET
        else:
            cleaned_article_content = self.cleaned_article_content

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if error is not UNSET:
            field_dict["error"] = error
        if title is not UNSET:
            field_dict["title"] = title
        if cleaned_article_content is not UNSET:
            field_dict["cleaned_article_content"] = cleaned_article_content

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        d = src_dict.copy()

        def _parse_error(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        error = _parse_error(d.pop("error", UNSET))

        def _parse_title(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        title = _parse_title(d.pop("title", UNSET))

        def _parse_cleaned_article_content(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        cleaned_article_content = _parse_cleaned_article_content(d.pop("cleaned_article_content", UNSET))

        article_content_cleaner_output = cls(
            error=error,
            title=title,
            cleaned_article_content=cleaned_article_content,
        )

        article_content_cleaner_output.additional_properties = d
        return article_content_cleaner_output

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
