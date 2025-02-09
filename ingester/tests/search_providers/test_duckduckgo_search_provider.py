from datetime import datetime, timezone

import pytest
from pydantic import ValidationError
from shared.models import utc_datetime_factory
from src.search_providers.duckduckgo_provider import duckduckgo_result_to_base_article
from src.search_providers.base import BaseArticle


def get_result():
    return {
        "date": "2024-12-06T11:00:00+00:00",
        "title": "The Top Three Misconceptions About Facial Recognition Technology",
        "body": "Facial recognition technology is a powerful tool that significantly improves security in stores and other public spaces.",
        "url": "https://www.forbes.com/councils/forbestechcouncil/2024/12/06/the-top-three-misconceptions-about-facial-recognition-technology/",
        "image": "https://imageio.forbes.com/specials-images/imageserve/63975d9bf6b7e6166e620ec1/0x0.jpg?format=jpg&height=900&width=1600&fit=bounds",
        "source": "Forbes",
    }


def test_duckduckgo_result_to_base_article_minimum_fields():
    result = get_result()

    # Arrange
    result.pop("body")
    result.pop("image")
    result.pop("source")

    found_at = datetime.now(tz=timezone.utc)

    # Act
    article = duckduckgo_result_to_base_article(result, found_at=found_at)

    # Assert
    assert isinstance(article, BaseArticle)
    assert article.title == result["title"]
    assert str(article.url) == result["url"]
    assert article.body == ""
    assert article.date == datetime.fromisoformat(result["date"])
    assert article.provider == "duckduckgo"
    assert article.found_at == found_at


def test_duckduckgo_result_to_base_article_all_fields():
    # Arrange
    result = get_result()
    found_at = datetime.now(tz=timezone.utc)

    # Act
    article = duckduckgo_result_to_base_article(result, found_at=found_at)

    # Assert
    assert isinstance(article, BaseArticle)
    assert article.title == result["title"]
    assert str(article.url) == result["url"]
    assert article.body == result["body"]
    assert article.date == datetime.fromisoformat(result["date"])
    assert str(article.image) == result["image"]
    assert article.provider == "duckduckgo"
    assert article.found_at == found_at


def test_duckduckgo_result_to_base_article_default_found_at():
    # Arrange
    result = get_result()
    now = utc_datetime_factory()

    # Act
    article = duckduckgo_result_to_base_article(result)

    # Assert
    assert isinstance(article, BaseArticle)

    assert abs((article.found_at - now).total_seconds()) < 1


def test_duckduckgo_result_to_base_article_missing_fields():
    missing_fields = [
        "date",
        "title",
        "url",
    ]

    for field in missing_fields:
        # Arrange
        result = get_result()
        result.pop(field)

        # Act / Assert
        with pytest.raises(ValidationError):
            duckduckgo_result_to_base_article(result)
