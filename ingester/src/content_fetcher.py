import asyncio
import logging

from pydantic import HttpUrl

from shared.content_fetching_models import ContentFetchingResult
from src.content_cleaner import ArticleContentCleaner
from src.url_to_markdown_converters.base import (
    UrlToMarkdownConverter,
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
    ) -> list[ContentFetchingResult]:
        logger.info(f"Converting and cleaning {len(urls)} URLs")

        return await asyncio.gather(*[self.convert_and_clean(url) for url in urls])
