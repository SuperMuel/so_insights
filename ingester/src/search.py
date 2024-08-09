import asyncio
from duckduckgo_search import AsyncDDGS

from typing import Annotated

from shared.models import TimeLimit, utc_datetime_factory
from shared.region import Region
from pydantic import (
    BaseModel,
    Field,
    HttpUrl,
    PastDatetime,
    StringConstraints,
    ValidationError,
    field_validator,
)
from tenacity import retry, stop_after_attempt, wait_fixed

from src.ingester_settings import IngesterSettings
from src.util import validate_url

import logging

logger = logging.getLogger(__name__)

settings = IngesterSettings()


class BaseArticle(BaseModel):
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
        if not validate_url(v):
            return None
        return v

    @classmethod
    def try_parse(cls, d: dict):
        """Try to parse a dictionary into an article, returning None if it fails."""
        try:
            return cls(**d)
        except ValidationError:
            logger.warning(f"Failed to parse article: {d}")
        except Exception:
            pass
        return None


@retry(
    reraise=True,
    stop=stop_after_attempt(settings.MAX_RETRIES_PER_QUERY),
    wait=wait_fixed(settings.RETRY_SLEEP_TIME_S),
)
async def search(
    ddgs: AsyncDDGS,
    query,
    region: Region,
    max_results: int,
    time_limit: TimeLimit,
) -> list[dict[str, str]]:
    return await ddgs.anews(
        keywords=query,
        region=region,
        max_results=max_results,
        timelimit=time_limit,
    )


class RunResult:
    def __init__(self, articles: list[BaseArticle], successfull_queries: int):
        self.articles = articles
        self.successfull_queries = successfull_queries


async def perform_search(
    ddgs: AsyncDDGS,
    queries: list[str],
    region: Region,
    max_results: int,
    time_limit: TimeLimit,
    stop_after_consecutive_failures: int = 5,
    verbose: bool = False,
) -> RunResult:
    # TODO : handle KeyboardInterrupt and return partial results
    all_articles = []

    consecutive_failures = 0
    successfull_queries = 0

    for i, query in enumerate(queries):
        if verbose:
            logger.info(f"Searching for query {i + 1}/{len(queries)}: '{query}'")
        if consecutive_failures >= stop_after_consecutive_failures:
            logger.error(
                f"Stopping search after {stop_after_consecutive_failures} consecutive failures"
            )
            break

        try:
            results = await ddgs.anews(
                keywords=query,
                region=region,
                max_results=max_results,
                timelimit=time_limit,
            )
        except Exception:
            consecutive_failures += 1
            continue

        successfull_queries += 1
        consecutive_failures = 0

        articles = map(BaseArticle.try_parse, results)
        all_articles.extend(filter(None, articles))

        await asyncio.sleep(settings.SLEEP_BETWEEN_QUERIES_S)

    return RunResult(all_articles, successfull_queries)
