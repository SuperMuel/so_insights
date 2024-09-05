from datetime import datetime
from beanie import PydanticObjectId
from pydantic import BaseModel, HttpUrl

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


class SearchQuerySetCreate(BaseModel):
    queries: list[str]
    title: ModelTitle
    region: Region


class SearchQuerySetUpdate(BaseModel):
    queries: list[str] | None = None
    title: ModelTitle | None = None
    region: Region | None = None

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


class AnalysisTaskCreate(BaseModel):
    data_start: datetime
    data_end: datetime


class IngestionRunCreate(BaseModel):
    time_limit: TimeLimit
    max_results: int
    search_query_set_id: PydanticObjectId
