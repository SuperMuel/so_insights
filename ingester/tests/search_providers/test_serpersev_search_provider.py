from datetime import datetime

from pydantic_core import Url
import pytest
from dateutil.relativedelta import relativedelta
from shared.region import Region
from src.search_providers.base import BaseArticle
from src.search_providers.serperdev_provider import (
    region_to_gl_hl,
    serper_date_to_datetime,
    serper_result_to_base_article,
    time_limit_to_serper,
)

from shared.models import TimeLimit


@pytest.mark.parametrize(
    "input_date, expected_diff",
    [
        ("1 week ago", {"weeks": 1}),
        ("2 days ago", {"days": 2}),
        ("11 months ago", {"months": 11}),
        ("1 year ago", {"years": 1}),
        ("2 hours ago", {"hours": 2}),
        ("3 minutes ago", {"minutes": 3}),
        ("4 seconds ago", {"seconds": 4}),
        ("just now", {}),
    ],
)
def test_serper_date_to_datetime_relative(input_date, expected_diff):
    now = datetime.now()
    result = serper_date_to_datetime(input_date)

    # Apply the expected difference to the current time
    expected_time = now - relativedelta(**expected_diff)

    # Assert that the result is close to the expected time
    assert (
        abs((result - expected_time).total_seconds()) < 5
    ), f"Failed for input: {input_date}"


@pytest.mark.parametrize(
    "input_date",
    [
        "invalid date",
        "sometime in the future",
    ],
)
def test_serper_date_to_datetime_invalid(input_date):
    with pytest.raises(ValueError):
        serper_date_to_datetime(input_date)


@pytest.mark.parametrize(
    "time_limit,expected",
    [
        ("d", {"tbs": "qdr:d"}),
        ("w", {"tbs": "qdr:w"}),
        ("m", {"tbs": "qdr:m"}),
        ("y", {"tbs": "qdr:y"}),
    ],
)
def test_time_limit_to_serper(time_limit: TimeLimit, expected: dict):
    result = time_limit_to_serper(time_limit)
    assert result == expected


def test_time_limit_to_serper_none():
    result = time_limit_to_serper(None)
    assert result == {}


@pytest.mark.parametrize(
    "article_dict,expected",
    [
        (
            {
                "title": "Elon Musk's more than $50 billion pay deal at Tesla was rejected again. Here is why",
                "link": "https://www.npr.org/2024/12/03/nx-s1-5214484/elon-musk-tesla-compensation",
                "snippet": "A judge in Delaware has for the second time struck down a compensation package for Elon Musk after a Tesla shareholder filed suit.",
                "date": "5 days ago",
                "source": "NPR",
                "imageUrl": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQf84qexVuKvXDn8R2_LIkKrvUv-UFIMOHMjXzIPAjqMUTmnIyaWvFoEnd8og&s",
                "position": 1,
            },
            BaseArticle(
                title="Elon Musk's more than $50 billion pay deal at Tesla was rejected again. Here is why",
                body="A judge in Delaware has for the second time struck down a compensation package for Elon Musk after a Tesla shareholder filed suit.",
                date=serper_date_to_datetime("5 days ago"),
                source="NPR",
                url=Url(
                    "https://www.npr.org/2024/12/03/nx-s1-5214484/elon-musk-tesla-compensation"
                ),
                image=Url(
                    "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQf84qexVuKvXDn8R2_LIkKrvUv-UFIMOHMjXzIPAjqMUTmnIyaWvFoEnd8og&s"
                ),
                provider="serperdev",
            ),
        )
    ],
)
def test_serper_result_to_base_article(article_dict: dict, expected: BaseArticle):
    result = serper_result_to_base_article(article_dict)

    assert result.title == expected.title
    assert result.body == expected.body
    assert result.source == expected.source
    assert result.url == expected.url
    assert result.image == expected.image
    assert result.provider == expected.provider

    assert abs((result.date - expected.date).total_seconds()) < 5


def test_image_url_optional():
    article_dict = {
        "title": "Elon Musk's more than $50 billion pay deal at Tesla was rejected again. Here is why",
        "link": "https://www.npr.org/2024/12/03/nx-s1-5214484/elon-musk-tesla-compensation",
        "snippet": "A judge in Delaware has for the second time struck down a compensation package for Elon Musk after a Tesla shareholder filed suit.",
        "date": "5 days ago",
        "source": "NPR",
        "position": 1,
    }

    result = serper_result_to_base_article(article_dict)

    assert result.image is None


def test_snippet_optional():
    article_dict = {
        "title": "Elon Musk's more than $50 billion pay deal at Tesla was rejected again. Here is why",
        "link": "https://www.npr.org/2024/12/03/nx-s1-5214484/elon-musk-tesla-compensation",
        "date": "5 days ago",
        "source": "NPR",
        "position": 1,
    }

    result = serper_result_to_base_article(article_dict)

    assert result.body == ""


def test_source_optional():
    article_dict = {
        "title": "Elon Musk's more than $50 billion pay deal at Tesla was rejected again. Here is why",
        "link": "https://www.npr.org/2024/12/03/nx-s1-5214484/elon-musk-tesla-compensation",
        "snippet": "A judge in Delaware has for the second time struck down a compensation package for Elon Musk after a Tesla shareholder filed suit.",
        "date": "5 days ago",
        "position": 1,
    }

    result = serper_result_to_base_article(article_dict)

    assert result.source is None


@pytest.mark.parametrize(
    "region,expected_gl_hl",
    [
        (Region.FRANCE, {"gl": "fr", "hl": "fr"}),
        (Region.UNITED_STATES, {"gl": "us", "hl": "en"}),
        (Region.GERMANY, {"gl": "de", "hl": "de"}),
        (Region.UNITED_KINGDOM, {"gl": "uk", "hl": "en"}),
        (Region.SWITZERLAND_IT, {"gl": "ch", "hl": "it"}),
        (Region.NO_REGION, {}),
    ],
)
def test_region_to_gl_hl(region, expected_gl_hl):
    hl_gl = region_to_gl_hl(region)
    assert hl_gl == expected_gl_hl
