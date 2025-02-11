from pydantic_settings import BaseSettings, SettingsConfigDict


class DBSettings(BaseSettings):
    model_config = SettingsConfigDict(
        case_sensitive=False,
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    mongodb_database: str = "so_insights"
    mongodb_workspaces_collection: str = "workspaces"
    mongodb_ingestion_runs_collection: str = "ingestion_runs"
    mongodb_articles_collection: str = "articles"
    mongodb_clusters_collection: str = "clusters"
    mongodb_clustering_sessions_collection: str = "clustering_sessions"
    mongodb_analysis_runs_collection: str = "analysis_runs"
    mongodb_starters_collection: str = "starters"
    mongodb_ingestion_configs_collection: str = "ingestion_configs"
    mongodb_organizations_collection: str = "organizations"
    mongodb_topics_collection: str = "topics"


db_settings = DBSettings()

__all__ = ["db_settings"]
