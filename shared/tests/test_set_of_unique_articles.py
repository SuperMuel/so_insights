from datetime import datetime, timedelta, timezone
from pydantic import HttpUrl
from pydantic_core import Url
import pytest
from beanie import PydanticObjectId, init_beanie
from mongomock_motor import AsyncMongoMockClient
from make_it_sync import make_sync
from shared.models import Article
from shared.set_of_unique_articles import SetOfUniqueArticles


@pytest.fixture(autouse=True)
def my_fixture():
    client = AsyncMongoMockClient()

    make_sync(init_beanie)(
        document_models=[Article],
        database=client.get_database(name="db"),  # type:ignore
    )
    yield


def date(year: int, month: int, day: int) -> datetime:
    return datetime(year, month, day)


def create_article(
    title: str,
    body: str,
    date: datetime = date(2022, 5, 15),
    id: str | PydanticObjectId | None = None,
    url: str = "https://example.com",
) -> Article:
    if id and isinstance(id, str):
        id = PydanticObjectId(id)

    return Article(
        workspace_id=PydanticObjectId("60f1d1b3d4f3b3b3b3b3b3b3"),
        ingestion_run_id=PydanticObjectId("60f1d1b3d4f3b3b3b3b3b3b3"),
        id=id if id else None,
        title=title,
        body=body,
        date=date,
        url=HttpUrl(url),
        found_at=datetime.now(tz=timezone.utc),
        provider="duckduckgo",
    )


def test_longer_body_replaces_shorter():
    articles_set = SetOfUniqueArticles()

    article1 = create_article(
        title="Title",
        body="Short body",
        date=date(2023, 1, 1),
        url="https://example.com",
    )
    article2 = create_article(
        title="Title",
        body="Short body extended with more text",
        date=date(2023, 1, 1),
        url="https://example2.com",
    )

    articles_set.add_article(article1)
    articles_set.add_article(article2)

    articles = articles_set.get_articles()

    assert len(articles) == 1
    assert articles[0].body == "Short body extended with more text"


def test_ignore_case_and_whitespace():
    articles_set = SetOfUniqueArticles()

    article1 = create_article(title="  Title  ", body=" Body ", date=date(2023, 1, 1))
    article2 = create_article(title="title", body="body", date=date(2023, 1, 1))

    articles_set.add_article(article1)
    articles_set.add_article(article2)

    articles = articles_set.get_articles()

    assert len(articles) == 1


def test_iteration_over_articles():
    articles_set = SetOfUniqueArticles()

    article1: Article = create_article(
        title="Title1",
        body="Body1",
        date=date(2023, 1, 1),
        url="https://example.com",
    )
    article2 = create_article(
        title="Title2",
        body="Body2",
        date=date(2023, 1, 2),
        url="https://example2.com",
    )

    articles_set.add_article(article1)
    articles_set.add_article(article2)

    articles = list(articles_set)

    assert len(articles) == 2
    assert articles[0].title == "Title1"
    assert articles[1].title == "Title2"


def test_slicing():
    articles_set = SetOfUniqueArticles()

    article1: Article = create_article(
        title="Title1",
        body="Body1",
        date=date(2023, 1, 1),
        url="https://example.com",
    )
    article2 = create_article(
        title="Title2",
        body="Body2",
        date=date(2023, 1, 2),
        url="https://example2.com",
    )
    article3 = create_article(
        title="Title3",
        body="Body3",
        date=date(2023, 1, 3),
        url="https://example3.com",
    )
    article4 = create_article(
        title="Title4",
        body="Body4",
        date=date(2023, 1, 4),
        url="https://example4.com",
    )

    articles_set.add_article(article1)
    articles_set.add_article(article2)
    articles_set.add_article(article3)
    articles_set.add_article(article4)

    assert articles_set[0].title == "Title1"
    assert articles_set[1].title == "Title2"
    assert articles_set[2].title == "Title3"
    assert articles_set[3].title == "Title4"

    slice = articles_set[1:3]
    assert len(slice) == 2
    assert slice[0].title == "Title2"
    assert slice[1].title == "Title3"


def test_unique_id():
    articles_set = SetOfUniqueArticles()

    unique_id = "60f1d1b3d4f3b3b3b3b3b3b3"

    article1 = create_article(
        title="Title1",
        body="Body1",
        id=unique_id,
        url="https://example.com",
    )
    article2 = create_article(
        title="Title2",
        body="Body2",
        id=unique_id,
        url="https://example2.com",
    )

    articles_set.add_article(article1)
    articles_set.add_article(article2)

    articles = articles_set.get_articles()
    assert len(articles) == 1
    assert articles[0].id == PydanticObjectId(unique_id)
    assert articles[0].title == "Title1"


def test_unique_url():
    articles_set = SetOfUniqueArticles()

    article1 = create_article(title="Title1", body="Body1", url="https://example.com")
    article2 = create_article(title="Title2", body="Body2", url="https://example.com")

    articles_set.add_article(article1)
    articles_set.add_article(article2)

    articles = articles_set.get_articles()
    assert len(articles) == 1
    assert articles[0].url == Url("https://example.com")
    assert articles[0].title == "Title1"


def test_limit():
    articles_set = SetOfUniqueArticles()

    for i in range(9):
        articles_set.add_article(
            create_article(
                title=f"Title{i}",
                body=f"Body{i}",
                date=date(2023, 1, 1) + timedelta(days=i),
                url=f"https://example{i}.com",
                id=PydanticObjectId(f"60f1d1b3d4f3b3b3b3b3b3b{i}"),
            )
        )

    limited_set = articles_set.limit(3)
    articles = limited_set.get_articles()
    assert len(articles) == 3


def test_limit_none():
    articles_set = SetOfUniqueArticles()

    for i in range(9):
        articles_set.add_article(
            create_article(
                title=f"Title{i}",
                body=f"Body{i}",
                date=date(2023, 1, 1) + timedelta(days=i),
                url=f"https://example{i}.com",
                id=PydanticObjectId(f"60f1d1b3d4f3b3b3b3b3b3b{i}"),
            )
        )

    limited_set = articles_set.limit(None)
    articles = limited_set.get_articles()
    assert len(articles) == 9
