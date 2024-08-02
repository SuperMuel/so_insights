from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(
        case_sensitive=False,
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    mongodb_uri: str = Field(default=...)
    mongodb_database: str = "so_insights"
    mongodb_articles_collection: str = "articles"
    mongodb_clusters_collection: str = "clusters"
    mongodb_clustering_sessions_collection: str = "clustering_sessions"
