from datetime import UTC, datetime
from enum import Enum
from beanie.odm.queries.find import FindMany
from typing import Annotated, Any, Dict, Literal, Self

from beanie import Document, Indexed, PydanticObjectId
from beanie.operators import Exists
from pydantic import BaseModel, Field, HttpUrl, PastDatetime, field_validator
from pymongo import IndexModel

from shared.language import Language
from shared.region import Region
from shared.db_settings import DBSettings

from pydantic import StringConstraints


# TODO auto change update_at like in https://github.com/naoTimesdev/showtimes/blob/79ed15aa647c6fb8ee9a1f694b54d90a5ed7dda0/showtimes/models/database.py#L24
def utc_datetime_factory():
    return datetime.now(UTC)


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
    min_cluster_size: int = 3
    min_samples: int = 1


class Workspace(Document):
    """
    Represents a project workspace for organizing and managing content.

    A Workspace is like a container for a specific research topic or project. It holds
    settings and metadata that apply to all the content within it.
    """

    name: ModelTitle
    description: ModelDescription = Field(default="")
    created_at: PastDatetime = Field(default_factory=utc_datetime_factory)
    updated_at: PastDatetime = Field(default_factory=utc_datetime_factory)
    language: Language = Language.fr
    hdbscan_settings: HdbscanSettings = Field(default_factory=HdbscanSettings)

    class Settings:
        name: str = DBSettings().mongodb_workspaces_collection

    def get_sorted_sessions(self) -> FindMany["ClusteringSession"]:
        return ClusteringSession.find(
            ClusteringSession.workspace_id == self.id,
        ).sort(
            -ClusteringSession.data_end  # type:ignore
        )


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
        name = DBSettings().mongodb_ingestion_configs_collection

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

    queries: list[str]  # TODO : min and max length
    region: Region
    max_results: int = Field(..., ge=1, le=100)
    time_limit: TimeLimit

    first_run_max_results: int = Field(..., ge=1, le=100)
    first_run_time_limit: TimeLimit

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
    config_id: PydanticObjectId

    created_at: PastDatetime = Field(default_factory=utc_datetime_factory)
    start_at: PastDatetime | None = None
    end_at: PastDatetime | None = None

    status: Status = Status.pending
    error: str | None = (
        None  # can be timeout (we should check for long duration ingestion and mark it as failed)
    )

    n_inserted: int | None = None

    class Settings:
        name = DBSettings().mongodb_ingestion_runs_collection

    def is_finished(self) -> bool:
        return self.status in [Status.completed, Status.failed]

    def is_running(self) -> bool:
        return self.status == Status.running

    def is_pending(self) -> bool:
        return self.status == Status.pending

    async def mark_as_finished(self, status: Status, error: str | None = None):
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


class Article(Document):
    """
    Represents a single piece of content collected during ingestion.

    An Article could be a news article, blog post, or any other text-based content
    retrieved from the web
    """

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

    content: str | None = None

    ingestion_run_id: PydanticObjectId | None = None

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
    created_at: PastDatetime = Field(default_factory=utc_datetime_factory)
    session_start: PastDatetime | None = None
    session_end: PastDatetime | None = None

    status: Status = Status.pending
    error: str | None = None

    data_start: PastDatetime
    data_end: datetime
    nb_days: int

    metadata: Dict[str, Any] = Field(default_factory=dict)

    articles_count: int | None = Field(
        default=None,
        description="Number of articles on which the clustering was performed, including noise.",
    )
    clusters_count: int | None = None
    relevant_clusters_count: int | None = None
    somewhat_relevant_clusters_count: int | None = None
    irrelevant_clusters_count: int | None = None

    noise_articles_ids: list[PydanticObjectId] | None = None
    noise_articles_count: int | None = None
    clustered_articles_count: int | None = Field(
        default=None,
        description="Number of articles in clusters, excluding noise.",
    )

    summary: str | None = None

    def pretty_print(self) -> str:
        return f"{self.data_start.strftime('%d %B %Y')} → {self.data_end.strftime('%d %B %Y')}"

    class Settings:
        name = DBSettings().mongodb_clustering_sessions_collection

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


class ClusterFeedback(BaseModel):
    """
    Captures user feedback on the relevance or usefulness of a cluster.

    This simple model allows users to indicate whether they find a particular
    cluster of articles relevant or not. It's a way to incorporate human judgment
    into the system's organization of content, which can help improve the
    cluster evaluation process over time.
    """

    relevant: bool


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
        name: str = DBSettings().mongodb_starters_collection
