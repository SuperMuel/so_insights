import pytest
from make_it_sync import make_sync
from mongomock_motor import AsyncMongoMockClient
from pydantic_core import Url
from src.util import create_test_article, try_get_firecrawl_image

from shared.content_fetching_models import (
    ArticleContentCleanerOutput,
    ContentFetchingResult,
    UrlToMarkdownConversion,
)
from shared.db import my_init_beanie


@pytest.fixture(autouse=True)
def my_fixture():
    client = AsyncMongoMockClient()
    make_sync(my_init_beanie)(client)
    yield


def test_try_get_firecrawl_image():
    # Test case 1: Article with valid og:image
    article1 = create_test_article()
    result1 = try_get_firecrawl_image(article1)
    assert isinstance(result1, Url)
    assert str(result1) == "https://example.com/og-image.jpg"

    # Test case 2: Article without content_fetching_result
    article2 = create_test_article(content_fetching_result=None)
    result2 = try_get_firecrawl_image(article2)
    assert result2 is None

    # Test case 3: Article with empty metadata
    article3 = create_test_article(
        content_fetching_result=ContentFetchingResult(
            url=Url("https://example.com/test-article"),
            content_cleaner_output=ArticleContentCleanerOutput(
                title="Test Article Title",
                cleaned_article_content="Test content",
            ),
            url_to_markdown_conversion=UrlToMarkdownConversion(
                url=Url("https://example.com/test-article"),
                markdown="# Test Article\n\nTest content",
                extraction_method="firecrawl",
                metadata={},
            ),
        ),
    )
    result3 = try_get_firecrawl_image(article3)
    assert result3 is None

    # Test case 4: Article with invalid URL
    article4 = create_test_article(
        content_fetching_result=ContentFetchingResult(
            url=Url("https://example.com/test-article"),
            content_cleaner_output=ArticleContentCleanerOutput(
                title="Test Article Title",
                cleaned_article_content="Test content",
            ),
            url_to_markdown_conversion=UrlToMarkdownConversion(
                url=Url("https://example.com/test-article"),
                markdown="# Test Article\n\nTest content",
                extraction_method="firecrawl",
                metadata={"og:image": "not_a_valid_url"},
            ),
        ),
    )
    result4 = try_get_firecrawl_image(article4)
    assert result4 is None
