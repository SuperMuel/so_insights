from pydantic_core import Url
import pytest
from shared.db import my_init_beanie
from src.rss import entry_to_published_date, convert_to_article
from datetime import datetime, timezone
from shared.models import Article

from beanie import PydanticObjectId

from mongomock_motor import AsyncMongoMockClient
from make_it_sync import make_sync


@pytest.fixture(autouse=True)
def my_fixture():
    client = AsyncMongoMockClient()
    make_sync(my_init_beanie)(client)
    yield


@pytest.mark.parametrize(
    "published_parsed, expected_date",
    [
        (
            (2023, 10, 1, 12, 0, 0, 0, 0, 0),
            datetime(2023, 10, 1, 12, 0, 0, tzinfo=timezone.utc),
        ),
        (
            (2023, 10, 1, 12, 0),
            datetime(2023, 10, 1, 12, 0, tzinfo=timezone.utc),
        ),
        (
            (2023, 10, 1, 12),
            datetime(2023, 10, 1, 12, tzinfo=timezone.utc),
        ),
        (
            (2023, 10, 1),
            datetime(2023, 10, 1, tzinfo=timezone.utc),
        ),
        ((), None),  # Empty date tuple
        (None, None),  # None as input
    ],
)
def test_entry_to_published_date(published_parsed, expected_date):
    result: datetime | None = entry_to_published_date(published_parsed)
    assert result == expected_date


WORKSPACE_ID = PydanticObjectId()


def test_convert_to_article():
    entry = {
        "title": "Test Article",
        "link": "http://example.com/test-article",
        "summary": "This is a test article.",
        "published_parsed": (2023, 10, 1, 12, 0, 0, 0, 0, 0),
        "author": "Test Author",
        "content": "content",
    }
    expected_article = Article(
        title="Test Article",
        url=Url("http://example.com/test-article"),
        body="This is a test article.",
        date=datetime(2023, 10, 1, 12, 0, 0, tzinfo=timezone.utc),
        source="Test Author",
        workspace_id=WORKSPACE_ID,
        content="content",
    )

    workspace_id = PydanticObjectId()
    expected_article.workspace_id = workspace_id

    article = convert_to_article(entry, workspace_id)

    assert article.workspace_id == expected_article.workspace_id
    assert article.title == expected_article.title
    assert article.url == expected_article.url
    assert article.body == expected_article.body
    assert article.date == expected_article.date
    assert article.source == expected_article.source
    assert article.content == expected_article.content
