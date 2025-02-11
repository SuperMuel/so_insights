from datetime import datetime
from typing import Annotated, Generic, TypeVar

from beanie import PydanticObjectId
from pydantic import (
    BaseModel,
    Field,
    HttpUrl,
    PastDatetime,
    StringConstraints,
)

from shared.models import (
    AnalysisParams,
    AnalysisType,
    Cluster,
    ClusterEvaluation,
    HdbscanSettings,
    Language,
    ModelDescription,
    ModelTitle,
    TimeLimit,
    Topic,
)
from shared.region import Region


class OrganizationCreate(BaseModel):
    name: ModelTitle = Field(..., description="Unique name of the organization")

    secret_code: Annotated[
        str,
        StringConstraints(
            min_length=8,
            max_length=64,
            strip_whitespace=True,
        ),
    ] = Field(
        ...,
        description="Secret code for organization access. Will be stored in plain text.",
    )

    class Config:
        extra = "forbid"


class WorkspaceCreate(BaseModel):
    name: ModelTitle
    description: ModelDescription = ""
    language: Language

    class Config:
        extra = "forbid"


class WorkspaceUpdate(BaseModel):
    name: ModelTitle | None = None
    description: ModelDescription | None = None
    language: Language | None = None
    hdbscan_settings: HdbscanSettings | None = None
    enabled: bool | None = None

    class Config:
        extra = "forbid"


class SearchIngestionConfigCreate(BaseModel):
    title: ModelTitle
    region: Region
    queries: list[str]

    max_results: int = Field(..., ge=1, le=100)
    time_limit: TimeLimit

    first_run_max_results: int = Field(..., ge=1, le=100)
    first_run_time_limit: TimeLimit

    class Config:
        extra = "forbid"


class SearchIngestionConfigUpdate(BaseModel):
    title: ModelTitle | None = None
    region: Region | None = None
    queries: list[str] | None = None

    max_results: int | None = Field(None, ge=1, le=100)
    time_limit: TimeLimit | None = None

    class Config:
        extra = "forbid"


class RssIngestionConfigCreate(BaseModel):
    title: ModelTitle
    rss_feed_url: HttpUrl

    class Config:
        extra = "forbid"


class RssIngestionConfigUpdate(BaseModel):
    title: ModelTitle | None = None
    rss_feed_url: HttpUrl | None = None

    class Config:
        extra = "forbid"


class ArticlePreview(BaseModel):
    id: str
    title: str
    url: HttpUrl
    body: str
    date: datetime
    source: str | None = None


class TopicWithArticles(BaseModel):
    articles_count: int
    title: str
    summary: str
    summary_with_links: str | None = None
    first_image: HttpUrl | None = None
    articles: list[ArticlePreview]

    @classmethod
    def from_topic(cls, topic: Topic, previews: list[ArticlePreview]):
        return cls(
            title=topic.title,
            summary=topic.body,
            summary_with_links=topic.body_with_links,
            first_image=topic.first_image,
            articles_count=len(topic.articles_ids),
            articles=previews,
        )


class ClusterWithArticles(BaseModel):
    id: str
    workspace_id: str
    run_id: str
    articles_count: int
    title: str | None = None
    summary: str | None = None
    overview_generation_error: str | None = None
    evaluation: ClusterEvaluation | None = None
    first_image: HttpUrl | None = None
    articles: list[ArticlePreview]

    @classmethod
    def from_cluster(cls, cluster: Cluster, previews: list[ArticlePreview]):
        return cls(
            id=str(cluster.id),
            workspace_id=str(cluster.workspace_id),
            run_id=str(cluster.session_id),
            articles_count=cluster.articles_count,
            title=cluster.overview.title if cluster.overview else None,
            summary=cluster.overview.summary if cluster.overview else None,
            overview_generation_error=cluster.overview_generation_error,
            evaluation=cluster.evaluation,
            first_image=cluster.first_image,
            articles=previews,
        )


class IngestionRunCreate(BaseModel):
    ingestion_config_id: PydanticObjectId


class AnalysisRunCreate(BaseModel):
    data_start: PastDatetime
    data_end: datetime
    analysis_type: AnalysisType

    params: AnalysisParams | None = Field(
        default=None,
        description="Parameters for the analysis. If None, default parameters for the workspace will be used.",
    )

    class Config:
        extra = "forbid"


T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    total: int
    page: int
    per_page: int
    items: list[T]
