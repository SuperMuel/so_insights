from datetime import datetime, timezone
from pydantic_core import Url
import pytest
from unittest.mock import AsyncMock
from shared.region import Region
from shared.models import TimeLimit
from src.search_providers.base import BaseArticle, BaseSearchProvider


class MockSearchProvider(BaseSearchProvider):
    async def search(
        self,
        query: str,
        *,
        region: Region,
        max_results: int,
        time_limit: TimeLimit,
    ) -> list[BaseArticle]:
        return await self._mock_search(query, region, max_results, time_limit)

    _mock_search = AsyncMock()


@pytest.fixture
def search_provider():
    provider = MockSearchProvider()
    provider._mock_search.reset_mock()
    return provider


@pytest.fixture
def sample_article():
    return BaseArticle(
        title="Test Article",
        url=Url("https://example.com/article"),
        date=datetime.now(timezone.utc),
        provider="duckduckgo",
        source="Example",
    )


@pytest.mark.asyncio
async def test_batch_search_single_query(search_provider, sample_article):
    search_provider._mock_search.return_value = [sample_article]

    result = await search_provider.batch_search(
        ["test query"],
        region=Region.FRANCE,
        max_results=10,
        time_limit="w",
    )

    assert len(result) == 1
    assert result[0] == sample_article
    search_provider._mock_search.assert_called_once_with(
        "test query", Region.FRANCE, 10, "w"
    )


@pytest.mark.asyncio
async def test_batch_search_multiple_queries(search_provider, sample_article):
    article1 = sample_article
    article2 = BaseArticle(
        title="Test Article 2",
        url=Url("https://example.com/article2"),
        date=datetime.now(timezone.utc),
        provider="duckduckgo",
    )

    search_provider._mock_search.side_effect = [[article1], [article2]]

    result = await search_provider.batch_search(
        ["query1", "query2"],
        region=Region.FRANCE,
        max_results=10,
        time_limit="w",
    )

    assert len(result) == 2
    assert result[0] == article1
    assert result[1] == article2
    assert search_provider._mock_search.call_count == 2


@pytest.mark.asyncio
async def test_batch_search_empty_queries(search_provider):
    result = await search_provider.batch_search(
        [],
        region=Region.FRANCE,
        max_results=10,
        time_limit="w",
    )

    assert len(result) == 0
    search_provider._mock_search.assert_not_called()
