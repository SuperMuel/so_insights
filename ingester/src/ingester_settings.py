from pydantic import AnyUrl, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class IngesterSettings(BaseSettings):
    model_config = SettingsConfigDict(
        case_sensitive=False,
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Search settings
    MAX_RETRIES_PER_QUERY: int = 2
    MIN_RETRY_SLEEP_TIME_S: int = 3
    MAX_RETRY_SLEEP_TIME_S: int = 10
    SLEEP_BETWEEN_QUERIES_S: int = 4
    QUERY_TIMEOUT: int = 30
    VERBOSE_SEARCH: bool = Field(
        default=True, description="Whether to log each search query during the search"
    )
    PROXY: AnyUrl | None = None

    # Embeddings settings
    VOYAGEAI_API_KEY: str = Field(default=...)
    EMBEDDING_MODEL: str = "voyage-large-2-instruct"
    EMBEDDING_BATCH_SIZE: int = 128

    # Vector database settings
    PINECONE_API_KEY: str = Field(default=...)
    PINECONE_INDEX: str = Field(default=...)

    MONGODB_URI: str = Field(default=...)

    # Watcher settings
    POLLING_INTERVAL_S: int = 10
    MAX_RUNTIME_S: int = 30 * 60  # 30 minutes
    PORT: int = 8081


settings = IngesterSettings()

__all__ = ["settings"]
