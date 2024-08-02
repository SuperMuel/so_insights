from datetime import datetime, UTC
from typing import Any, Dict, Literal

from pymongo import IndexModel
from enum import Enum
from pydantic import HttpUrl
from pydantic import BaseModel, Field, PastDatetime, field_validator
from beanie import Document, Link, PydanticObjectId
import pymongo
from so_insights.settings import AppSettings


def utc_datetime_factory():
    return datetime.now(UTC)


class Region(str, Enum):
    ARABIA = "xa-ar"
    ARABIA_EN = "xa-en"
    ARGENTINA = "ar-es"
    AUSTRALIA = "au-en"
    AUSTRIA = "at-de"
    BELGIUM_FR = "be-fr"
    BELGIUM_NL = "be-nl"
    BRAZIL = "br-pt"
    BULGARIA = "bg-bg"
    CANADA = "ca-en"
    CANADA_FR = "ca-fr"
    CATALAN = "ct-ca"
    CHILE = "cl-es"
    CHINA = "cn-zh"
    COLOMBIA = "co-es"
    CROATIA = "hr-hr"
    CZECH_REPUBLIC = "cz-cs"
    DENMARK = "dk-da"
    ESTONIA = "ee-et"
    FINLAND = "fi-fi"
    FRANCE = "fr-fr"
    GERMANY = "de-de"
    GREECE = "gr-el"
    HONG_KONG = "hk-tzh"
    HUNGARY = "hu-hu"
    INDIA = "in-en"
    INDONESIA = "id-id"
    INDONESIA_EN = "id-en"
    IRELAND = "ie-en"
    ISRAEL = "il-he"
    ITALY = "it-it"
    JAPAN = "jp-jp"
    KOREA = "kr-kr"
    LATVIA = "lv-lv"
    LITHUANIA = "lt-lt"
    LATIN_AMERICA = "xl-es"
    MALAYSIA = "my-ms"
    MALAYSIA_EN = "my-en"
    MEXICO = "mx-es"
    NETHERLANDS = "nl-nl"
    NEW_ZEALAND = "nz-en"
    NORWAY = "no-no"
    PERU = "pe-es"
    PHILIPPINES = "ph-en"
    PHILIPPINES_TL = "ph-tl"
    POLAND = "pl-pl"
    PORTUGAL = "pt-pt"
    ROMANIA = "ro-ro"
    RUSSIA = "ru-ru"
    SINGAPORE = "sg-en"
    SLOVAK_REPUBLIC = "sk-sk"
    SLOVENIA = "sl-sl"
    SOUTH_AFRICA = "za-en"
    SPAIN = "es-es"
    SWEDEN = "se-sv"
    SWITZERLAND_DE = "ch-de"
    SWITZERLAND_FR = "ch-fr"
    SWITZERLAND_IT = "ch-it"
    TAIWAN = "tw-tzh"
    THAILAND = "th-th"
    TURKEY = "tr-tr"
    UKRAINE = "ua-uk"
    UNITED_KINGDOM = "uk-en"
    UNITED_STATES = "us-en"
    UNITED_STATES_ES = "ue-es"
    VENEZUELA = "ve-es"
    VIETNAM = "vn-vi"
    NO_REGION = "wt-wt"


class Article(Document):
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
        name = AppSettings().mongodb_articles_collection
        indexes = [
            IndexModel("url", unique=True),
            IndexModel("vector_indexed"),
            IndexModel("date"),
        ]


class ClusteringSession(Document):
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
        name = AppSettings().mongodb_clustering_sessions_collection

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
    session: Link[ClusteringSession]
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
        name = AppSettings().mongodb_clusters_collection

    async def get_articles(self) -> list[Article]:
        return await Article.find_many({"_id": {"$in": self.articles_ids}}).to_list()
