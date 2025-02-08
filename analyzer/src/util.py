import asyncio

from datetime import datetime, timezone
import logging
import aiohttp
from beanie import PydanticObjectId
from pydantic import HttpUrl, ValidationError
from shared.content_fetching_models import (
    ArticleContentCleanerOutput,
    ContentFetchingResult,
    UrlToMarkdownConversion,
)
from shared.models import Article, SearchProvider
from shared.region import Region


logger = logging.getLogger(__name__)


def create_test_article(
    workspace_id: PydanticObjectId = PydanticObjectId("507f1f77bcf86cd799439011"),
    title: str = "Test Article Title",
    url: HttpUrl = HttpUrl("https://example.com/test-article"),
    body: str = "This is a test article body with some content for testing purposes.",
    found_at: datetime = datetime(2024, 1, 1, tzinfo=timezone.utc),
    date: datetime = datetime(2024, 1, 1, tzinfo=timezone.utc),
    region: Region = Region.FRANCE,
    image: HttpUrl | None = HttpUrl("https://example.com/test-image.jpg"),
    source: str = "Test Source",
    content: str = "Full content of the test article goes here.",
    ingestion_run_id: PydanticObjectId = PydanticObjectId("507f1f77bcf86cd799439012"),
    vector_indexed: bool = False,
    provider: SearchProvider = "serperdev",
    content_fetching_result: ContentFetchingResult | None = ContentFetchingResult(
        url=HttpUrl("https://example.com/test-article"),
        content_cleaner_output=ArticleContentCleanerOutput(
            title="Test Article Title",
            cleaned_article_content="Full content of the test article goes here.",
        ),
        url_to_markdown_conversion=UrlToMarkdownConversion(
            url=HttpUrl("https://example.com/test-article"),
            markdown="# Test Article\n\nTest content",
            extraction_method="firecrawl",
            metadata={
                "og:image": "https://example.com/og-image.jpg",
                "og:title": "Test Article Title",
            },
        ),
    ),
    content_cleaning_error: str | None = None,
) -> Article:
    return Article(
        workspace_id=workspace_id,
        title=title,
        url=url,
        body=body,
        found_at=found_at,
        date=date,
        region=region,
        image=image,
        source=source,
        content=content,
        ingestion_run_id=ingestion_run_id,
        vector_indexed=vector_indexed,
        provider=provider,
        content_fetching_result=content_fetching_result,
        content_cleaning_error=content_cleaning_error,
    )


def try_get_firecrawl_image(article: Article) -> HttpUrl | None:
    if not article.content_fetching_result:
        return None

    fetch_result = article.content_fetching_result.url_to_markdown_conversion
    if not fetch_result.metadata:
        return None

    image_url = fetch_result.metadata.get("og:image")
    if not image_url:
        return None

    try:
        parsed_url = HttpUrl(image_url)
    except ValidationError:
        logger.error(f"Error while parsing image URL: {image_url}")
        return None

    return parsed_url


async def get_first_valid_image(articles: list[Article]) -> HttpUrl | None:
    """
    Asynchronously retrieves the first valid image URL from a list of articles.

    This function iterates through the provided articles and checks each article's
    image URL for validity. It returns the first URL that successfully responds
    with an image content type.

    Args:
        articles (list[Article]): A list of Article objects to check for valid image URLs.

    Returns:
        HttpUrl | None: The first valid image URL found, or None if no valid image URL is found.
    """
    timeout = aiohttp.ClientTimeout(total=5)  # 5 seconds timeout for the entire request

    async with aiohttp.ClientSession(timeout=timeout) as session:
        for article in articles:
            # first try to get the image we got from Firecrawl since it's often better quality.
            image_url = try_get_firecrawl_image(article) or article.image

            if not image_url:
                continue

            try:
                async with session.head(str(image_url)) as response:
                    if response.status == 200:
                        content_type = response.headers.get("Content-Type", "")
                        if content_type.startswith("image/"):
                            return image_url

            except aiohttp.ClientError:
                continue
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                logger.error(f"Error while fetching image: {e}")
                continue
    return None
