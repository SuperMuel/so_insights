import asyncio
import logging

from aiolimiter import AsyncLimiter
from firecrawl import FirecrawlApp  # Assuming this is the correct import from the SDK
from pydantic import HttpUrl, SecretStr
from requests import HTTPError
from tenacity import (
    before_sleep_log,
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from . import (
    UrlToMarkdownConversion,
    UrlToMarkdownConversionError,
    UrlToMarkdownConverter,
)

logger = logging.getLogger(__name__)


class FirecrawlUrlToMarkdown(UrlToMarkdownConverter):
    """
    Converts the content of a given URL to Markdown using the Firecrawl API.
    """

    def __init__(self, api_key: SecretStr | str | None = None):
        if api_key is None:
            self.app = FirecrawlApp()
        else:
            api_key = (
                api_key.get_secret_value()
                if isinstance(api_key, SecretStr)
                else api_key
            )
            self.app = FirecrawlApp(api_key=api_key)

        # allow for 10 concurrent entries within a 60 second window
        self._rate_limiter = AsyncLimiter(max_rate=8, time_period=60)

    @property
    def extraction_method(self) -> str:
        return "firecrawl"

    async def convert_url(self, url: HttpUrl) -> UrlToMarkdownConversion:
        """
        Converts the content of the given URL to Markdown using the Firecrawl API.
        Rate limited to avoid overwhelming the API.

        Args:
            url: The URL of the web page to convert.

        Returns: UrlToMarkdownConversion

        """

        async with self._rate_limiter:
            return await self._convert_url(url)

    @retry(
        stop=stop_after_attempt(10),
        wait=wait_exponential(multiplier=3, min=4, max=60),
        retry=retry_if_exception_type((HTTPError)),
        before_sleep=before_sleep_log(logger, logging.WARNING),
        # If all retries fail get the original error (HTTPError)
        retry_error_callback=lambda retry_state: retry_state.outcome.result(),  # type: ignore
    )
    async def _convert_url(self, url: HttpUrl) -> UrlToMarkdownConversion:
        logger.info(f"Converting URL to Markdown using Firecrawl API: {url}")
        try:
            scrape_result = self.app.scrape_url(
                str(url), params={"formats": ["markdown"]}
            )

            if not scrape_result or not isinstance(scrape_result, dict):
                raise UrlToMarkdownConversionError(
                    f"Unexpected response type from Firecrawl API: {type(scrape_result)}"
                )

            markdown_content = scrape_result.get("markdown")

            if not markdown_content:
                raise UrlToMarkdownConversionError(
                    f"Markdown content not found in Firecrawl API response for URL: {url}"
                )

            if metadata := scrape_result.get("metadata", {}):
                if not isinstance(metadata, dict):
                    raise UrlToMarkdownConversionError(
                        f"Metadata must be a dictionary, got {type(metadata)}"
                    )

            return UrlToMarkdownConversion(
                url=url,
                markdown=markdown_content,
                metadata=metadata,
                extraction_method=self.extraction_method,
            )
        except HTTPError as e:
            # Retry on:
            # - 429: Rate limit exceeded, need to wait before retrying
            # - 408: Request timeout, temporary network/server issue
            if e.response.status_code in (429, 408):
                raise  # Will trigger retry
            raise UrlToMarkdownConversionError(
                f"Error converting URL to Markdown using Firecrawl API: {e}"
            ) from e

        except Exception as e:
            raise UrlToMarkdownConversionError(
                f"Error converting URL to Markdown using Firecrawl API: {e}"
            ) from e

    async def convert_urls(self, urls: list[HttpUrl]) -> list[UrlToMarkdownConversion]:
        """
        Converts the content of the given URLs to Markdown using the Firecrawl API.
        Rate limited to avoid overwhelming the API.

        Args:
            urls: The URLs of the web pages to convert.

        Returns: list[UrlToMarkdownConversion]
        """
        return await asyncio.gather(*[self.convert_url(url) for url in urls])
