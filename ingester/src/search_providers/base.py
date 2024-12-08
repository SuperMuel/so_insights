import asyncio
import logging
from abc import ABC, abstractmethod
from itertools import chain
from typing import Annotated

from pydantic import (
    BaseModel,
    Field,
    HttpUrl,
    PastDatetime,
    StringConstraints,
    field_validator,
)

from shared.models import SearchProvider, TimeLimit, utc_datetime_factory
from shared.region import Region
from shared.util import validate_url

logger = logging.getLogger(__name__)


class BaseArticle(BaseModel):
    """
    Represents the basic structure of an article retrieved from a search.
    """

    title: Annotated[
        str, StringConstraints(min_length=1, max_length=200, strip_whitespace=True)
    ]
    url: HttpUrl
    body: Annotated[str, StringConstraints(max_length=1000, strip_whitespace=True)] = ""
    date: PastDatetime
    found_at: PastDatetime = Field(default_factory=utc_datetime_factory)
    image: HttpUrl | None = None
    source: (
        Annotated[str, StringConstraints(max_length=100, strip_whitespace=True)] | None
    ) = None

    provider: SearchProvider

    @field_validator("title", mode="before")
    @classmethod
    def truncate_title(cls, v: str) -> str:
        return v[:200] if len(v) > 200 else v

    @field_validator("body", mode="before")
    @classmethod
    def truncate_body(cls, v: str) -> str:
        return v[:1000] if len(v) > 1000 else v

    @field_validator("source", mode="before")
    @classmethod
    def truncate_source(cls, v: str) -> str:
        return v[:100] if len(v) > 100 else v

    @field_validator("image", mode="before")
    @classmethod
    def validate_image_url(cls, v: str) -> str | None:
        return validate_url(v)


class SearchException(Exception):
    """Custom exception for search-related errors."""

    def __init__(self, message: str, original_exception: Exception):
        super().__init__(f"{message}: {original_exception}")
        self.original_exception = original_exception


class BaseSearchProvider(ABC):
    @abstractmethod
    async def search(
        self,
        query: str,
        *,
        region: Region,
        max_results: int,
        time_limit: TimeLimit,
    ) -> list[BaseArticle]:
        raise NotImplementedError

    async def batch_search(
        self,
        queries: list[str],
        *,
        region: Region,
        max_results: int,
        time_limit: TimeLimit,
    ) -> list[BaseArticle]:
        tasks = [
            self.search(
                query,
                region=region,
                max_results=max_results,
                time_limit=time_limit,
            )
            for query in queries
        ]

        return list(chain.from_iterable(await asyncio.gather(*tasks)))
