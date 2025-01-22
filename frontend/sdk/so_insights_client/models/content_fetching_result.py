from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.article_content_cleaner_output import ArticleContentCleanerOutput
    from ..models.url_to_markdown_conversion import UrlToMarkdownConversion


T = TypeVar("T", bound="ContentFetchingResult")


@_attrs_define
class ContentFetchingResult:
    """Represents the result of fetching and cleaning content from a URL.

    Attributes:
        url (str): The URL of the content
        url_to_markdown_conversion (UrlToMarkdownConversion): Represents the result of converting a URL to Markdown.
        content_cleaner_output (ArticleContentCleanerOutput): Output for the article content cleaner.
    """

    url: str
    url_to_markdown_conversion: "UrlToMarkdownConversion"
    content_cleaner_output: "ArticleContentCleanerOutput"
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        url = self.url

        url_to_markdown_conversion = self.url_to_markdown_conversion.to_dict()

        content_cleaner_output = self.content_cleaner_output.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "url": url,
                "url_to_markdown_conversion": url_to_markdown_conversion,
                "content_cleaner_output": content_cleaner_output,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        from ..models.article_content_cleaner_output import ArticleContentCleanerOutput
        from ..models.url_to_markdown_conversion import UrlToMarkdownConversion

        d = src_dict.copy()
        url = d.pop("url")

        url_to_markdown_conversion = UrlToMarkdownConversion.from_dict(d.pop("url_to_markdown_conversion"))

        content_cleaner_output = ArticleContentCleanerOutput.from_dict(d.pop("content_cleaner_output"))

        content_fetching_result = cls(
            url=url,
            url_to_markdown_conversion=url_to_markdown_conversion,
            content_cleaner_output=content_cleaner_output,
        )

        content_fetching_result.additional_properties = d
        return content_fetching_result

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
