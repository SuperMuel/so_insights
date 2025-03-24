import asyncio
import logging

from pydantic import HttpUrl

from shared.content_fetching_models import ContentFetchingResult
from src.content_cleaner import ArticleContentCleaner
from src.url_to_markdown_converters.base import (
    UrlToMarkdownConverter,
    UrlToMarkdownConversionError,
)

logger = logging.getLogger(__name__)


class ContentFetcher:
    def __init__(
        self,
        url_to_markdown_converter: UrlToMarkdownConverter,
        cleaner: ArticleContentCleaner,
    ):
        self.url_to_markdown_converter = url_to_markdown_converter
        self.cleaner = cleaner

    async def convert_and_clean(self, url: HttpUrl) -> ContentFetchingResult:
        logger.info(f"Converting and cleaning content from URL: {url}")

        url_to_markdown = await self.url_to_markdown_converter.convert_url(url)

        cleaned_markdown = await self.cleaner.clean_article_content(
            url_to_markdown.markdown,
            metadata={
                "url": str(url),
                "extraction_method": url_to_markdown.extraction_method,
            },
        )

        return ContentFetchingResult(
            url=url,
            url_to_markdown_conversion=url_to_markdown,
            content_cleaner_output=cleaned_markdown,
        )

    async def abatch_convert_and_clean(
        self, urls: list[HttpUrl]
    ) -> list[ContentFetchingResult | Exception]:
        logger.info(f"Converting and cleaning {len(urls)} URLs")

        # First batch convert all URLs
        url_to_markdown_results = await self.url_to_markdown_converter.convert_urls(
            urls
        )
        assert len(url_to_markdown_results) == len(urls)

        # Prepare a results list preserving input order and cleaning tasks for successful conversions
        results: list[ContentFetchingResult | Exception | None] = [None] * len(urls)
        cleaning_tasks = []

        for idx, (url, conv_result) in enumerate(zip(urls, url_to_markdown_results)):
            if isinstance(conv_result, UrlToMarkdownConversionError):
                logger.error(f"Failed to convert URL {url}: {conv_result}")
                results[idx] = conv_result
            else:
                cleaning_tasks.append(
                    asyncio.create_task(self._clean_task(url, conv_result, idx))
                )

        if cleaning_tasks:
            # Execute cleaning tasks concurrently
            tasks_output = await asyncio.gather(*cleaning_tasks)
            for index, task_result in tasks_output:
                results[index] = task_result

        assert all(result is not None for result in results)

        return [
            result
            for result in results
            if result is not None  # To satisfy type checker
        ]

    async def _clean_task(
        self, url: HttpUrl, conv_result, index: int
    ) -> tuple[int, ContentFetchingResult | Exception]:
        """Helper method to clean markdown content for a single URL."""
        try:
            cleaned_markdown = await self.cleaner.clean_article_content(
                conv_result.markdown,
                metadata={
                    "url": str(url),
                    "extraction_method": conv_result.extraction_method,
                },
            )
            result = ContentFetchingResult(
                url=url,
                url_to_markdown_conversion=conv_result,
                content_cleaner_output=cleaned_markdown,
            )
        except Exception as e:
            # Return the exception instead of raising it
            result = e
        return index, result
