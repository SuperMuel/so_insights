from datetime import datetime
from beanie import PydanticObjectId
from pydantic import BaseModel, Field, HttpUrl, PastDatetime

from shared.models import (
    Cluster,
    ClusterEvaluation,
    HdbscanSettings,
    Language,
    ModelDescription,
    ModelTitle,
    TimeLimit,
)
from shared.region import Region


class WorkspaceCreate(BaseModel):
    name: ModelTitle
    description: ModelDescription = ""
    language: Language

    class Config:
        extra = "forbid"


class WorkspaceUpdate(BaseModel):
    name: ModelTitle | None
    description: ModelDescription | None
    language: Language | None
    hdbscan_settings: HdbscanSettings | None

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
    title: ModelTitle | None
    region: Region | None
    queries: list[str] | None

    max_results: int | None = Field(None, ge=1, le=100)
    time_limit: TimeLimit | None

    class Config:
        extra = "forbid"


class RssIngestionConfigCreate(BaseModel):
    title: ModelTitle
    rss_feed_url: HttpUrl

    class Config:
        extra = "forbid"


class RssIngestionConfigUpdate(BaseModel):
    title: ModelTitle | None
    rss_feed_url: HttpUrl | None

    class Config:
        extra = "forbid"


class ArticlePreview(BaseModel):
    id: str
    title: str
    url: HttpUrl
    body: str
    date: datetime
    source: str | None = None


class ClusterWithArticles(BaseModel):
    id: str
    workspace_id: str
    session_id: str
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
            session_id=str(cluster.session_id),
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


class ClusteringSessionCreate(BaseModel):
    data_start: PastDatetime
    data_end: datetime

    class Config:
        extra = "forbid"
