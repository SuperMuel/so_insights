from datetime import datetime
from enum import Enum
from typing import Annotated, Any, Dict, Literal, Self

from beanie import Document, Indexed, PydanticObjectId
from beanie.odm.queries.find import FindMany
from beanie.operators import Exists
from pydantic import (
    BaseModel,
    Field,
    HttpUrl,
    PastDatetime,
    SecretStr,
    StringConstraints,
    field_validator,
)
from pymongo import IndexModel

from shared.content_fetching_models import ContentFetchingResult
from shared.db_settings import db_settings
from shared.language import Language
from shared.region import Region
from shared.util import utc_datetime_factory


type SearchProvider = Literal["duckduckgo", "serperdev", "rss"]

ModelTitle = Annotated[
    str, StringConstraints(min_length=3, max_length=30, strip_whitespace=True)
]

ModelDescription = Annotated[
    str, StringConstraints(max_length=10000, strip_whitespace=True)
]

type TimeLimit = Literal["d", "w", "m", "y"]


class Status(str, Enum):
    pending = "pending"
    running = "running"
    completed = "completed"
    failed = "failed"


class HdbscanSettings(BaseModel):
    min_cluster_size: int = Field(
        default=3, description="Minimum number of points required to form a cluster"
    )
    min_samples: int = Field(
        default=1,
        description="Number of samples in a neighborhood for a point to be considered as a core point",
    )
    cluster_selection_epsilon: float = Field(
        default=0.0,
        description="A distance threshold. Clusters below this value will be merged.",
    )


class Organization(Document):
    """
    Represents an organization within the SO Insights system.

    Organizations group related workspaces and restrict access to them using a shared
    secret code. Users must provide the correct secret code to access the workspaces
    associated with an organization.

    They are created by admins.

    Warning:
    This authentication mechanism is not designed for secure environments.
    The secret code approach provides minimal security and should not be
    relied upon for sensitive or confidential data. Consider using
    more robust authentication methods for enhanced security.
    """

    name: ModelTitle = Field(..., description="Unique name of the organization")

    secret_code: SecretStr = Field(
        ...,
        description="Shared secret passphrase for access. Could be easy to guess, not secure.",
        min_length=8,
        max_length=64,
    )
    created_at: datetime = Field(default_factory=utc_datetime_factory)
    updated_at: datetime = Field(default_factory=utc_datetime_factory)

    content_analysis_enabled: bool = Field(
        default=False,
        description="When enabled, the system will collect and analyze the articles contents, not just title and metadata",
    )

    class Settings:
        name = db_settings.mongodb_organizations_collection
        indexes = [
            IndexModel("name", unique=True),
            IndexModel("secret_code", unique=True),
        ]


class Workspace(Document):
    """
    Represents a project workspace for organizing and managing content.

    A Workspace is like a container for a specific research topic or project. It holds
    settings and metadata that apply to all the content within it.

    Each workspace belongs to an organization.
    """

    organization_id: PydanticObjectId = Field(
        ..., description="Reference to the organization that owns this workspace"
    )

    name: ModelTitle = Field(..., description="The name of the workspace")
    description: ModelDescription = Field(
        default="", description="A detailed description of the workspace's purpose"
    )
    created_at: PastDatetime = Field(
        default_factory=utc_datetime_factory,
        description="Timestamp when the workspace was created",
    )
    updated_at: PastDatetime = Field(
        default_factory=utc_datetime_factory,
        description="Timestamp of the last update to the workspace",
    )
    language: Language = Field(
        default=Language.fr, description="The primary language of the workspace content"
    )
    hdbscan_settings: HdbscanSettings = Field(
        default_factory=HdbscanSettings,
        description="HDBSCAN algorithm settings for clustering",
    )
    enabled: bool = Field(
        default=True,
        description="When disabled, nor the ingester nor the analyzer will run for this workspace",
    )

    class Settings:
        name: str = db_settings.mongodb_workspaces_collection

    def get_sorted_sessions(self) -> FindMany["ClusteringSession"]:
        return ClusteringSession.find(
            ClusteringSession.workspace_id == self.id,
        ).sort(
            -ClusteringSession.data_end  # type:ignore
        )

    async def get_starters(self) -> list["Starters"]:
        return await Starters.find(
            Starters.workspace_id == self.id,
        ).to_list()

    async def get_last_starters(self) -> "Starters | None":
        return (
            await Starters.find(
                Starters.workspace_id == self.id,
            )
            .sort(
                -Starters.created_at  # type:ignore
            )
            .first_or_none()
        )

    @classmethod
    def get_active_workspaces(cls) -> FindMany["Workspace"]:
        return Workspace.find(Workspace.enabled == True)  # noqa: E712


class IngestionConfigType(str, Enum):
    search = "search"
    rss = "rss"


class IngestionConfig(Document):
    """
    Base configuration for data ingestion processes.

    An IngestionConfig defines how the system should collect information for a workspace.
    """

    workspace_id: Annotated[PydanticObjectId, Indexed()]
    title: ModelTitle
    created_at: PastDatetime = Field(default_factory=utc_datetime_factory)
    updated_at: PastDatetime = Field(default_factory=utc_datetime_factory)
    type: IngestionConfigType

    last_run_at: PastDatetime | None = None

    class Settings:
        is_root = True
        name = db_settings.mongodb_ingestion_configs_collection

    async def get_last_run(self) -> Self | None:
        return await (
            IngestionRun.find(
                IngestionRun.workspace_id == self.workspace_id,
                IngestionRun.config_id == self.id,
                with_children=True,
            )
            .sort(
                -IngestionRun.created_at  # type:ignore
            )
            .first_or_none()
        )


class SearchIngestionConfig(IngestionConfig):
    """
    Configuration for ingesting data from web searches.

    This config tells the system how to perform web searches to gather content.
    """

    type: IngestionConfigType = IngestionConfigType.search

    queries: list[str] = Field(
        ..., description="List of search queries to use for ingestion"
    )  # TODO : min and max length
    region: Region = Field(..., description="Geographic region to focus the search on")
    max_results: int = Field(
        ..., ge=1, le=100, description="Maximum number of results to fetch per query"
    )
    time_limit: TimeLimit = Field(
        ...,
        description="Time limit for search results (d: day, w: week, m: month, y: year)",
    )
    first_run_max_results: int = Field(
        ...,
        ge=1,
        le=100,
        description="Maximum number of results to fetch per query on the first run",
    )
    first_run_time_limit: TimeLimit = Field(
        ..., description="Time limit for search results on the first run"
    )

    async def get_max_results_and_time_limit(self) -> tuple[int, TimeLimit]:
        """If the config has already run, return the default max_results and time_limit.
        If it's the first run, return the first_run_max_results and first_run_time_limit.
        """
        has_run = await self.get_last_run()

        max_results, time_limit = (
            (self.max_results, self.time_limit)
            if has_run
            else (self.first_run_max_results, self.first_run_time_limit)
        )
        return max_results, time_limit


class RssIngestionConfig(IngestionConfig):
    """
    Configuration for ingesting data from RSS feeds.

    This config specifies an RSS feed to collect content from.
    """

    type: IngestionConfigType = IngestionConfigType.rss

    rss_feed_url: HttpUrl  # TODO : add unique constraint on rss_feed_url


class SearchIngestionRunResult(BaseModel):
    type: IngestionConfigType = IngestionConfigType.search


class RssIngestionRunResult(BaseModel):
    type: IngestionConfigType = IngestionConfigType.rss


class IngestionRun(Document):
    """
    Represents a single execution of an ingestion process.

    An IngestionRun tracks the details of one attempt to collect data using an IngestionConfig.
    """

    workspace_id: Annotated[PydanticObjectId, Indexed()]
    config_id: PydanticObjectId = Field(
        ..., description="ID of the ingestion config used for this run"
    )

    created_at: PastDatetime = Field(default_factory=utc_datetime_factory)

    start_at: PastDatetime | None = Field(
        default=None, description="Timestamp when the run started"
    )
    end_at: PastDatetime | None = Field(
        default=None, description="Timestamp when the run ended"
    )

    status: Status = Field(
        default=Status.pending, description="Current status of the ingestion run"
    )
    error: str | None = Field(
        default=None, description="Error message if the run failed"
    )
    n_inserted: int | None = Field(
        default=None,
        description="Number of new articles inserted in the DB during this run",
    )

    class Settings:
        name = db_settings.mongodb_ingestion_runs_collection

    def is_finished(self) -> bool:
        return self.status in [Status.completed, Status.failed]

    def is_running(self) -> bool:
        return self.status == Status.running

    def is_pending(self) -> bool:
        return self.status == Status.pending

    async def mark_as_finished(self, status: Status, *, error: str | None = None):
        """
        Finish the process and update the status, end time, and error (if any).
        Parameters:
        - status (Status): The status to set for the process.
        - error (str | None): The error message, if any.
        Returns:
        - None
        """
        self.status = status
        self.end_at = utc_datetime_factory()
        self.error = error

        await self.save()

    async def mark_as_started(self):
        """
        Start the process and update the status and start time.
        Returns:
        - None
        """
        if self.status not in [Status.pending, Status.running]:
            raise ValueError("Cannot start a completed process.")

        self.start_at = utc_datetime_factory()

        if self.status == Status.pending:
            self.status = Status.running

        await self.replace()


class ArticleEvaluation(BaseModel):
    """
    Represents an assessment of an article's quality and relevance to the research interest.
    """

    justification: str = Field(
        ...,
        description=(
            "A brief justification (one to two sentences) explaining why the article was classified with the chosen verdict."
        ),
    )
    relevance_level: Literal["relevant", "somewhat_relevant", "not_relevant"] = Field(
        ...,
        description=(
            "The relevance classification of the article with respect to the research interest. "
            "Use 'relevant' if the article strongly addresses the research interest, "
            "'somewhat_relevant' if it partially relates, and 'not_relevant' if it does not relate."
        ),
    )


class Article(Document):
    """
    Represents a single piece of content collected during ingestion.

    An Article could be a news article, blog post, or any other text-based content
    retrieved from the web
    """

    workspace_id: PydanticObjectId
    title: Annotated[
        str, StringConstraints(min_length=1, max_length=200, strip_whitespace=True)
    ] = Field(..., description="Title of the article")
    url: HttpUrl = Field(..., description="URL where the article was found")
    body: Annotated[str, StringConstraints(max_length=1000, strip_whitespace=True)] = (
        Field(
            default="", description="Short excerpt or meta_description of the article"
        )
    )
    found_at: PastDatetime = Field(
        default_factory=utc_datetime_factory,
        description="Timestamp when the article was found",
    )
    date: PastDatetime = Field(..., description="Publication date of the article")
    region: Region | None = Field(
        default=None, description="Geographic region associated with the article"
    )
    image: HttpUrl | None = Field(
        default=None, description="URL of the main image in the article"
    )
    source: Annotated[str, StringConstraints(max_length=100, strip_whitespace=True)] = (
        Field(default="", description="Source of the article")
    )
    content: str | None = Field(default=None, description="Full content of the article")
    content_cleaning_error: str | None = Field(
        default=None, description="Error message if the content could not be cleaned"
    )

    ingestion_run_id: PydanticObjectId | None = Field(
        None, description="ID of the ingestion run that found this article"
    )
    vector_indexed: bool = Field(
        default=False,
        description="Whether this article has been indexed in the vector database",
    )

    provider: SearchProvider = Field(
        ..., description="The provider that found the article"
    )

    content_fetching_result: ContentFetchingResult | None = Field(
        default=None,
        description="The result of fetching and cleaning the article content",
    )

    evaluation: ArticleEvaluation | None = Field(
        default=None,
    )

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
        name = db_settings.mongodb_articles_collection
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


class ClusteringAnalysisParams(BaseModel):
    """Parameters specific to clustering analysis."""

    hdbscan_settings: HdbscanSettings = Field(
        default_factory=HdbscanSettings,
        description="HDBSCAN algorithm settings for clustering",
    )


class ReportAnalysisParams(BaseModel):
    """Parameters specific to report-style analysis."""

    # Just an example for now
    # report_template: str | None = Field(
    #     None, description="template to use"
    # )


class AnalysisType(str, Enum):
    CLUSTERING = "clustering"
    REPORT = "report"

    def __str__(self) -> str:
        return str(self.value)


AnalysisParams = ClusteringAnalysisParams | ReportAnalysisParams


class ClusteringRunEvaluationResult(BaseModel):
    relevant_clusters_count: int = Field(
        ..., description="Number of clusters deemed highly relevant"
    )
    somewhat_relevant_clusters_count: int = Field(
        ..., description="Number of clusters deemed somewhat relevant"
    )
    irrelevant_clusters_count: int = Field(
        ..., description="Number of clusters deemed not relevant"
    )


class ClusteringAnalysisResult(BaseModel):
    """Results specific to clustering analysis."""

    analysis_type: AnalysisType = AnalysisType.CLUSTERING

    articles_count: int | None = Field(
        default=None, description="Number of articles processed in this session"
    )

    clusters_count: int = Field(..., description="Total number of clusters formed")
    noise_articles_ids: list[PydanticObjectId] = Field(
        ..., description="IDs of articles classified as noise"
    )
    noise_articles_count: int = Field(
        ..., description="Number of articles classified as noise"
    )
    clustered_articles_count: int = Field(
        ..., description="Number of articles successfully clustered"
    )
    evaluation: ClusteringRunEvaluationResult | None = Field(
        default=None, description="Evaluation of the clustering run"
    )
    summary: str | None = Field(
        default=None, description="Overall summary of the clusters deemed relevant"
    )
    data_loading_time_s: float | None = Field(
        default=None, description="Time taken to load the data, in seconds"
    )
    clustering_time_s: float | None = Field(
        default=None, description="Time taken to cluster the data, in seconds"
    )


class ReportAnalysisResult(BaseModel):
    """Results specific to report-style analysis."""

    analysis_type: AnalysisType = AnalysisType.REPORT

    articles_count: int | None = Field(
        default=None, description="Number of articles processed in this session"
    )

    report_content: str = Field(
        ..., description="Markdown content of the generated report"
    )


AnalysisResult = ClusteringAnalysisResult | ReportAnalysisResult


class AnalysisRun(Document):
    workspace_id: Annotated[PydanticObjectId, Indexed()]

    created_at: PastDatetime = Field(
        default_factory=utc_datetime_factory,
        description="Timestamp when the run was created",
    )

    analysis_type: AnalysisType = Field(
        ...,
        description="Type of analysis performed in this run (e.g., 'clustering', 'report')",
    )

    status: Status = Field(
        default=Status.pending, description="Current status of the analysis run"
    )

    error: str | None = Field(
        default=None, description="Error message if the run failed"
    )

    session_start: PastDatetime | None = Field(
        default=None, description="Timestamp when the session started"
    )
    session_end: PastDatetime | None = Field(
        default=None, description="Timestamp when the session ended"
    )

    data_start: PastDatetime = Field(
        default=..., description="Start date of the data range used for analysis"
    )
    data_end: datetime = Field(
        default=..., description="End date of the data range used for analysis"
    )

    params: AnalysisParams
    result: AnalysisResult | None = Field(
        default=None, description="Result of the analysis"
    )

    def pretty_print(self) -> str:
        return f"{self.analysis_type} analysis: {self.data_start.strftime('%d %B %Y')} → {self.data_end.strftime('%d %B %Y')}"

    class Settings:
        name = db_settings.mongodb_analysis_runs_collection

    async def get_sorted_clusters(
        self,
        relevance_level: RelevanceLevel | None = None,
        limit: int | None = None,
    ) -> list["Cluster"]:
        """
        Get a list of clusters from the Clustering run.

        Args:
            relevance_level: The relevance level to filter the clusters by.
            limit: The maximum number of clusters to return.

        Returns:
            A list of clusters sorted by the number of articles in each cluster.

        Raises:
            ValueError: If the run is not a clustering run.
        """
        if self.analysis_type != AnalysisType.CLUSTERING:
            raise ValueError(f"Run {self.id} is not a clustering run")

        clusters = Cluster.find_many(Cluster.session_id == self.id)

        if relevance_level:
            clusters = clusters.find(
                Exists(Cluster.evaluation),
                Cluster.evaluation != None,  # noqa: E711
                Cluster.evaluation.relevance_level == relevance_level,  # type: ignore "relevance_level" is not a known attribute of "None"
            )

        clusters = clusters.sort(-Cluster.articles_count)  # type: ignore

        if limit:
            clusters = clusters.limit(limit)

        return await clusters.to_list()


class ClusteringSession(Document):
    """
    Represents a session of grouping similar articles together.

    A ClusteringSession is like a large-scale organization effort. It takes all the
    articles collected within a certain time frame and groups them based on their
    similarities. This helps in identifying trends, recurring themes, or related
    pieces of information across many articles.

    The session keeps track of various statistics about the clustering process,
    such as how many groups were formed, how many articles were processed, and
    how relevant or useful these groups are estimated to be.
    """

    workspace_id: Annotated[PydanticObjectId, Indexed()]
    created_at: PastDatetime = Field(
        default_factory=utc_datetime_factory,
        description="Timestamp when the session was created",
    )
    session_start: PastDatetime | None = Field(
        default=None, description="Timestamp when the clustering session started"
    )
    session_end: PastDatetime | None = Field(
        default=None, description="Timestamp when the clustering session ended"
    )
    status: Status = Field(
        default=Status.pending, description="Current status of the clustering session"
    )
    error: str | None = Field(
        default=None, description="Error message if the session failed"
    )
    data_start: PastDatetime = Field(
        default=..., description="Start date of the data range used for clustering"
    )
    data_end: datetime = Field(
        default=..., description="End date of the data range used for clustering"
    )
    nb_days: int = Field(..., description="Number of days in the data range")
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata about the clustering session",
    )
    articles_count: int | None = Field(
        default=None, description="Number of articles processed in this session"
    )
    clusters_count: int | None = Field(
        default=None, description="Total number of clusters formed"
    )
    relevant_clusters_count: int | None = Field(
        default=None, description="Number of clusters deemed highly relevant"
    )
    somewhat_relevant_clusters_count: int | None = Field(
        default=None, description="Number of clusters deemed somewhat relevant"
    )
    irrelevant_clusters_count: int | None = Field(
        default=None, description="Number of clusters deemed not relevant"
    )
    noise_articles_ids: list[PydanticObjectId] | None = Field(
        default=None, description="IDs of articles classified as noise"
    )
    noise_articles_count: int | None = Field(
        default=None, description="Number of articles classified as noise"
    )
    clustered_articles_count: int | None = Field(
        default=None, description="Number of articles successfully clustered"
    )
    summary: str | None = Field(
        default=None, description="Overall summary of the clusteres deemed relevant"
    )

    def pretty_print(self) -> str:
        return f"{self.data_start.strftime('%d %B %Y')} → {self.data_end.strftime('%d %B %Y')}"

    class Settings:
        name = db_settings.mongodb_clustering_sessions_collection

    async def get_sorted_clusters(
        self,
        relevance_level: RelevanceLevel | None = None,
        limit: int | None = None,
    ) -> list["Cluster"]:
        clusters = Cluster.find_many(Cluster.session_id == self.id)

        if relevance_level:
            clusters = clusters.find(
                Exists(Cluster.evaluation),
                Cluster.evaluation != None,  # noqa: E711
                Cluster.evaluation.relevance_level == relevance_level,  # type: ignore "relevance_level" is not a known attribute of "None"
            )

        clusters = clusters.sort(-Cluster.articles_count)  # type: ignore

        if limit:
            clusters = clusters.limit(limit)

        return await clusters.to_list()


class ClusterEvaluation(BaseModel):
    """
    Represents an assessment of a cluster's quality and relevance to the workspace.

    After articles are grouped into clusters, it's important to understand how
    good these groupings are for the workspace owner. The ClusterEvaluation provides
    a way to score and explain the relevance of a cluster.

    It includes a justification for the evaluation, a relevance level
    (like "highly relevant", "somewhat relevant", or "not relevant"), and a
    confidence score for this evaluation.

    Done automatically by LLM after clustering and overview generation.
    """

    justification: str = Field(
        ..., description="Your explanation for the relevance level."
    )
    relevance_level: RelevanceLevel
    confidence_score: float = Field(..., ge=0.0, le=1.0)


class ClusterOverview(BaseModel):
    """
    Provides a summary of what a cluster of articles is about.

    When you have a group of related articles, it's useful to have a quick
    summary of what connects them. The ClusterOverview is the result of an LLM
    generating a title and a brief summary that captures the main theme or topic
    of the majority of articles in a cluster.
    """

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

    created_at: PastDatetime | None = Field(default_factory=utc_datetime_factory)


class ClusterFeedback(BaseModel):
    """
    Captures user feedback on the relevance or usefulness of a cluster.

    This simple model allows users to indicate whether they find a particular
    cluster of articles relevant or not. It's a way to incorporate human judgment
    into the system's organization of content, which can help improve the
    cluster evaluation process over time.
    """

    relevant: bool = Field(
        ..., description="User feedback on whether the cluster is relevant"
    )
    created_at: PastDatetime | None = Field(default_factory=utc_datetime_factory)


class Cluster(Document):
    """
    Represents a group of related articles identified during clustering.

    A Cluster is the result of the grouping process. It contains multiple articles
    that the system has determined are related in some way. Each cluster includes
    references to its articles, an overview summarizing the cluster's theme,
    an evaluation of its quality, and any user feedback received.

    Clusters are the key output of the analysis process, providing a structured way
    to understand and navigate large amounts of collected content.
    """

    workspace_id: Annotated[PydanticObjectId, Indexed()] = Field(
        ..., description="ID of the workspace this cluster belongs to"
    )
    session_id: Annotated[PydanticObjectId, Indexed()] = Field(
        ..., description="ID of the clustering session that created this cluster"
    )
    articles_count: int = Field(..., description="Number of articles in the cluster")
    articles_ids: list[PydanticObjectId] = Field(
        ...,
        description="IDs of articles in the cluster, sorted by their distance to the cluster center",
    )
    overview: ClusterOverview | None = Field(
        default=None, description="Generated overview of the cluster's content"
    )
    overview_generation_error: str | None = Field(
        default=None, description="Error message if overview generation failed"
    )
    evaluation: ClusterEvaluation | None = Field(
        default=None, description="Evaluation of the cluster's relevance and quality"
    )
    feedback: ClusterFeedback | None = Field(
        default=None, description="User feedback on the cluster"
    )
    first_image: HttpUrl | None = Field(
        default=None,
        description="URL of the first image found in the cluster's articles",
    )

    class Settings:
        name = db_settings.mongodb_clusters_collection


class Starters(Document):
    """
    Stores predefined conversation starters or prompts to use in the workspace's chatbot.

    Starters are like icebreakers or guiding questions. They can be used to help
    users begin interacting with the collected and organized information in a
    workspace.
    """

    workspace_id: Annotated[PydanticObjectId, Indexed()]
    starters: list[str]
    created_at: PastDatetime = Field(default_factory=utc_datetime_factory)

    class Settings:
        name: str = db_settings.mongodb_starters_collection
