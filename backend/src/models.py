from datetime import UTC, datetime
from typing import Annotated, Any, Dict, Literal

from beanie import Document, Indexed, Link, PydanticObjectId
from pydantic import BaseModel, Field, HttpUrl, PastDatetime, field_validator
from pymongo import IndexModel

from src.region import Region
from backend.src.api_settings import ApiSettings


def utc_datetime_factory():
    return datetime.now(UTC)


class Workspace(Document):
    name: str
    description: str = ""
    created_at: PastDatetime = Field(default_factory=utc_datetime_factory)
    updated_at: PastDatetime = Field(default_factory=utc_datetime_factory)

    class Settings:
        name: str = ApiSettings().mongodb_workspaces_collection


class SearchQueries(Document):
    workspace_id: Annotated[PydanticObjectId, Indexed()]
    queries: list[str]
    title: str
    region: Region
    created_at: PastDatetime = Field(default_factory=utc_datetime_factory)
    updated_at: PastDatetime = Field(default_factory=utc_datetime_factory)

    class Settings:
        name: str = ApiSettings().mongodb_search_queries_collection


class IngestionRun(Document):
    workspace_id: Annotated[PydanticObjectId, Indexed()]
    time_limit: Literal["d", "w", "m", "y"]
    max_results: int = Field(..., ge=1, le=100)
    created_at: PastDatetime = Field(default_factory=utc_datetime_factory)
    trigger: str = "manual"
    status: Literal["running", "completed", "failed"]
    error: str | None = None
    # TODO : search result

    class Settings:
        name = ApiSettings().mongodb_ingestion_runs_collection


# TODO class ScheduledIngestion(Document):
#     workspace_id: Annotated[PydanticObjectId, Indexed()]
#     cron_expression: str
#     timezone: str
#     next_run_time: PastDatetime
#     last_run_time: PastDatetime | None = None
#     enabled: bool = True

#     class Settings:
#         name = AppSettings().mongodb_scheduled_ingestion_collection


class Article(Document):
    workspace_id: PydanticObjectId
    title: str = Field(..., min_length=1, max_length=200)
    url: HttpUrl
    body: str = Field(default="", max_length=1000)
    found_at: PastDatetime = Field(default_factory=utc_datetime_factory)
    date: PastDatetime
    region: Region | None = None
    image: HttpUrl | None = None
    source: str | None = Field(default=None, max_length=100)
    vector_indexed: bool = False

    @field_validator("title", mode="before")
    @classmethod
    def truncate_title(cls, v: str) -> str:
        return v[:200] if len(v) > 200 else v

    @field_validator("body", mode="before")
    @classmethod
    def truncate_body(cls, v: str) -> str:
        return v[:1000] if len(v) > 1000 else v

    class Settings:
        name = ApiSettings().mongodb_articles_collection
        indexes = [
            IndexModel(
                [
                    ("workspace_id", 1),
                    ("url", 1),
                ],
                unique=True,
            ),
            IndexModel("vector_indexed"),
            IndexModel("date"),
        ]


class ClusteringSession(Document):
    workspace_id: Annotated[PydanticObjectId, Indexed()]
    session_start: datetime = Field(default_factory=lambda: datetime.now(UTC))
    session_end: datetime | None = None

    data_start: datetime
    data_end: datetime

    metadata: Dict[str, Any]

    articles_count: int = Field(
        ...,
        description="Number of articles on which the clustering was performed, including noise.",
    )
    clusters_count: int

    noise_articles_ids: list[PydanticObjectId]
    noise_articles_count: int
    clustered_articles_count: int = Field(
        ...,
        description="Number of articles in clusters, excluding noise.",
    )

    class Settings:
        name = ApiSettings().mongodb_clustering_sessions_collection

    async def get_included_sorted_clusters(self) -> list["Cluster"]:
        return await (
            Cluster.find_many(
                Cluster.session.ref.id == self.id,
                ClusterEvaluation.decision == "include",
            )
            .sort(-Cluster.articles_count)  # type: ignore
            .to_list()
        )  # TODO test this


class ClusterEvaluation(BaseModel):
    justification: str
    decision: Literal["include", "exclude"]
    exclusion_reason: str | None = None


class Cluster(Document):
    workspace_id: Annotated[PydanticObjectId, Indexed()]
    session: Link[
        ClusteringSession
    ]  # TODO : change to simple session_id for consistency
    articles_count: int = Field(
        ...,
        description="Number of articles in the cluster.",
    )
    articles_ids: list[PydanticObjectId] = Field(
        ...,
        description="IDs of articles in the cluster, sorted by their distance to the cluster center",
    )

    title: str | None = Field(
        default=None, description="AI generated title of the cluster"
    )
    summary: str | None = Field(
        default=None, description="AI generated summary of the cluster"
    )

    overview_generation_error: str | None = Field(
        default=None, description="Error message if the overview generation failed"
    )

    evaluation: ClusterEvaluation | None = None

    class Settings:
        name = ApiSettings().mongodb_clusters_collection

    async def get_articles(self) -> list[Article]:
        return await Article.find_many({"_id": {"$in": self.articles_ids}}).to_list()
