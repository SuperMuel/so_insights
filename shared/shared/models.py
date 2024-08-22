from datetime import UTC, datetime
from typing import Annotated, Any, Dict, Literal

from beanie import Document, Indexed, PydanticObjectId
from beanie.operators import Exists
from pydantic import BaseModel, Field, HttpUrl, PastDatetime, field_validator
from pymongo import IndexModel

from shared.language import Language
from shared.region import Region
from shared.db_settings import DBSettings

from pydantic import StringConstraints


def utc_datetime_factory():
    return datetime.now(UTC)


ModelTitle = Annotated[
    str, StringConstraints(min_length=3, max_length=30, strip_whitespace=True)
]

ModelDescription = Annotated[
    str, StringConstraints(max_length=500, strip_whitespace=True)
]

type TimeLimit = Literal["d", "w", "m", "y"]


class Workspace(Document):
    name: ModelTitle
    description: ModelDescription = Field(default="")
    created_at: PastDatetime = Field(default_factory=utc_datetime_factory)
    updated_at: PastDatetime = Field(default_factory=utc_datetime_factory)
    language: Language = Language.fr

    class Settings:
        name: str = DBSettings().mongodb_workspaces_collection


class SearchQuerySet(Document):
    workspace_id: Annotated[PydanticObjectId, Indexed()]
    queries: list[str]
    title: ModelTitle
    region: Region
    created_at: PastDatetime = Field(default_factory=utc_datetime_factory)
    updated_at: PastDatetime = Field(default_factory=utc_datetime_factory)
    deleted: bool = False
    deleted_at: PastDatetime | None = None

    class Settings:
        name: str = DBSettings().mongodb_search_query_sets_collection

    async def find_last_finished_run(self) -> "IngestionRun | None":
        return (
            await IngestionRun.find(
                IngestionRun.workspace_id == self.workspace_id,
                IngestionRun.queries_set_id == self.id,
            )
            .sort(-IngestionRun.end_at)  # type: ignore
            .first_or_none()
        )


class IngestionRun(Document):
    workspace_id: Annotated[PydanticObjectId, Indexed()]
    queries_set_id: Annotated[PydanticObjectId, Indexed()]
    time_limit: TimeLimit
    max_results: int = Field(..., ge=1, le=100)
    created_at: PastDatetime = Field(default_factory=utc_datetime_factory)
    end_at: PastDatetime | None = None
    status: Literal["running", "completed", "failed"]
    successfull_queries: int | None = None
    error: str | None = (
        None  # can be timeout (we should check for long duration ingestion and mark it as failed)
    )

    # Number of new articles found, that didn't exist in the database before
    n_inserted: int | None = None

    class Settings:
        name = DBSettings().mongodb_ingestion_runs_collection

    def is_finished(self) -> bool:
        return self.status in ("completed", "failed")

    def is_running(self) -> bool:
        return not self.is_finished()


class Article(Document):
    workspace_id: PydanticObjectId
    title: Annotated[
        str, StringConstraints(min_length=1, max_length=200, strip_whitespace=True)
    ]
    url: HttpUrl
    body: Annotated[str, StringConstraints(max_length=1000, strip_whitespace=True)] = ""
    found_at: PastDatetime = Field(default_factory=utc_datetime_factory)
    date: PastDatetime
    region: Region | None = None
    image: HttpUrl | None = None
    source: Annotated[str, StringConstraints(max_length=100, strip_whitespace=True)] = (
        ""
    )

    vector_indexed: bool = False

    @field_validator("title", mode="before")
    @classmethod
    def truncate_title(cls, v: str) -> str:
        return v[:200] if len(v) > 200 else v

    @field_validator("body", mode="before")
    @classmethod
    def truncate_body(cls, v: str) -> str:
        if not v:
            return ""
        return v[:1000] if len(v) > 1000 else v

    @field_validator("source", mode="before")
    @classmethod
    def truncate_source(cls, v: str) -> str:
        if not v:
            return ""
        v = str(v)
        return v[:100] if len(v) > 100 else v

    class Settings:
        name = DBSettings().mongodb_articles_collection
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


RelevanceLevel = Literal["highly_relevant", "somewhat_relevant", "not_relevant"]


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
        name = DBSettings().mongodb_clustering_sessions_collection

    async def get_sorted_clusters(
        self, relevance_level: RelevanceLevel | None = None
    ) -> list["Cluster"]:
        clusters = Cluster.find_many(Cluster.session_id == self.id)

        if relevance_level:
            clusters = clusters.find(
                Exists(Cluster.evaluation),
                Cluster.evaluation != None,  # noqa: E711
                Cluster.evaluation.relevance_level == relevance_level,  # type: ignore "relevance_level" is not a known attribute of "None"
            )

        clusters = clusters.sort(-Cluster.articles_count)  # type: ignore

        return await clusters.to_list()


class ClusterEvaluation(BaseModel):
    justification: str = Field(
        ..., description="Your explanation for the relevance level."
    )
    relevance_level: RelevanceLevel
    confidence_score: float = Field(..., ge=0.0, le=1.0)


class ClusterOverview(BaseModel):
    title: Annotated[
        str,
        StringConstraints(
            min_length=5, max_length=200, strip_whitespace=True
        ),  # TODO : force model to output smaller titles and update this value
    ]
    summary: Annotated[
        str, StringConstraints(min_length=5, max_length=1000, strip_whitespace=True)
    ]
    language: Language


class ClusterFeedback(BaseModel):
    relevant: bool


class Cluster(Document):
    workspace_id: Annotated[PydanticObjectId, Indexed()]
    session_id: Annotated[PydanticObjectId, Indexed()]
    articles_count: int = Field(
        ...,
        description="Number of articles in the cluster.",
    )
    articles_ids: list[PydanticObjectId] = Field(
        ...,
        description="IDs of articles in the cluster, sorted by their distance to the cluster center",
    )

    overview: ClusterOverview | None = None
    overview_generation_error: str | None = None

    evaluation: ClusterEvaluation | None = None

    feedback: ClusterFeedback | None = None

    first_image: HttpUrl | None = None

    class Settings:
        name = DBSettings().mongodb_clusters_collection

    async def get_articles(self) -> list[Article]:
        return await Article.find_many({"_id": {"$in": self.articles_ids}}).to_list()
