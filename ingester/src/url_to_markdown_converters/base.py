from abc import ABC, abstractmethod

from pydantic import HttpUrl
from shared.content_fetching_models import UrlToMarkdownConversion


class UrlToMarkdownConversionError(Exception):
    """Custom exception raised for errors during URL to Markdown conversion."""

    pass


class UrlToMarkdownConverter(ABC):
    """
    Abstract base class for converting the content of a URL to Markdown.

    This interface defines the contract for any class that provides
    functionality to fetch and convert web page content into Markdown format.
    """

    @property
    @abstractmethod
    def extraction_method(self) -> str:
        """The name of the extraction method used by this converter"""
        pass

    @abstractmethod
    async def convert_url(self, url: HttpUrl) -> UrlToMarkdownConversion:
        """
        Converts the content of the given URL to Markdown.

        Args:
            url: The URL of the web page to convert.

        Returns:
            A `UrlToMarkdownConversion` object containing the URL, the converted
            Markdown content, and the timestamp when the content was extracted.
        """
        pass

    @abstractmethod
    async def convert_urls(self, urls: list[HttpUrl]) -> list[UrlToMarkdownConversion]:
        """
        Converts the content of the given URLs to Markdown.

        Args:
            urls: A list of URLs to convert.

        Returns:
            A list of `UrlToMarkdownConversion` objects containing the URLs, the converted
            Markdown content, and the timestamp when the content was extracted.
        """
        pass
