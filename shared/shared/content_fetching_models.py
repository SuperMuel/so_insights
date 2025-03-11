from typing import Any, Literal
from pydantic import BaseModel, Field, HttpUrl, PastDatetime, field_validator
from shared.util import utc_datetime_factory


class UrlToMarkdownConversion(BaseModel):
    """
    Represents the result of converting a URL to Markdown.
    """

    url: HttpUrl
    markdown: str
    extracted_at: PastDatetime = Field(default_factory=utc_datetime_factory)
    extraction_method: Literal["firecrawl", "jina"] = Field(
        ..., description="e.g Firecrawl, Jina..."
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict, description="Metadata returned by the extraction method"
    )


class ArticleContentCleanerOutput(BaseModel):
    """Output for the article content cleaner."""

    error: str | None = Field(
        default=None, description="Error message if the content could not be cleaned."
    )
    title: str | None = Field(default=None, description="Title of the article")
    cleaned_article_content: str | None = Field(
        default=None, description="Cleaned article content in markdown format"
    )

    @field_validator("error")
    def empty_string_to_none(cls, v: str | None) -> str | None:
        if isinstance(v, str) and not v.strip():
            return None
        return v


class ContentFetchingResult(BaseModel):
    """
    Represents the result of fetching and cleaning content from a URL.
    """

    url: HttpUrl = Field(..., description="The URL of the content")
    url_to_markdown_conversion: UrlToMarkdownConversion
    content_cleaner_output: ArticleContentCleanerOutput
