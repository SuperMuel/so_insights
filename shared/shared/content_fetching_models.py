from typing import Any
from pydantic import BaseModel, Field, HttpUrl, PastDatetime
from shared.util import utc_datetime_factory


class UrlToMarkdownConversion(BaseModel):
    """
    Represents the result of converting a URL to Markdown.
    """

    url: HttpUrl
    markdown: str
    extracted_at: PastDatetime = Field(default_factory=utc_datetime_factory)
    extraction_method: str = Field(..., description="e.g Firecrawl, Jina...")
    metadata: dict[str, Any] = Field(
        default_factory=dict, description="Metadata returned by the extraction method"
    )


class ArticleContentCleanerOutput(BaseModel):
    """Output for the article content cleaner."""

    error: str | None = Field(
        None, description="Error message if the content could not be cleaned."
    )
    title: str | None = Field(..., description="Title of the article")
    cleaned_markdown: str | None = Field(..., description="Cleaned markdown content")


class ContentFetchingResult(BaseModel):
    """
    Represents the result of fetching and cleaning content from a URL.
    """

    url: HttpUrl = Field(..., description="The URL of the content")
    cleaned_markdown: str = Field(..., description="The cleaned markdown content")
    url_to_markdown_conversion: UrlToMarkdownConversion
    content_cleaner_output: ArticleContentCleanerOutput
