import datetime
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.url_to_markdown_conversion_metadata import UrlToMarkdownConversionMetadata


T = TypeVar("T", bound="UrlToMarkdownConversion")


@_attrs_define
class UrlToMarkdownConversion:
    """Represents the result of converting a URL to Markdown.

    Attributes:
        url (str):
        markdown (str):
        extraction_method (str): e.g Firecrawl, Jina...
        extracted_at (Union[Unset, datetime.datetime]):
        metadata (Union[Unset, UrlToMarkdownConversionMetadata]): Metadata returned by the extraction method
    """

    url: str
    markdown: str
    extraction_method: str
    extracted_at: Union[Unset, datetime.datetime] = UNSET
    metadata: Union[Unset, "UrlToMarkdownConversionMetadata"] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        url = self.url

        markdown = self.markdown

        extraction_method = self.extraction_method

        extracted_at: Union[Unset, str] = UNSET
        if not isinstance(self.extracted_at, Unset):
            extracted_at = self.extracted_at.isoformat()

        metadata: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.metadata, Unset):
            metadata = self.metadata.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "url": url,
                "markdown": markdown,
                "extraction_method": extraction_method,
            }
        )
        if extracted_at is not UNSET:
            field_dict["extracted_at"] = extracted_at
        if metadata is not UNSET:
            field_dict["metadata"] = metadata

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        from ..models.url_to_markdown_conversion_metadata import UrlToMarkdownConversionMetadata

        d = src_dict.copy()
        url = d.pop("url")

        markdown = d.pop("markdown")

        extraction_method = d.pop("extraction_method")

        _extracted_at = d.pop("extracted_at", UNSET)
        extracted_at: Union[Unset, datetime.datetime]
        if isinstance(_extracted_at, Unset):
            extracted_at = UNSET
        else:
            extracted_at = isoparse(_extracted_at)

        _metadata = d.pop("metadata", UNSET)
        metadata: Union[Unset, UrlToMarkdownConversionMetadata]
        if isinstance(_metadata, Unset):
            metadata = UNSET
        else:
            metadata = UrlToMarkdownConversionMetadata.from_dict(_metadata)

        url_to_markdown_conversion = cls(
            url=url,
            markdown=markdown,
            extraction_method=extraction_method,
            extracted_at=extracted_at,
            metadata=metadata,
        )

        url_to_markdown_conversion.additional_properties = d
        return url_to_markdown_conversion

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
