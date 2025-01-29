from typing import Literal

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

from shared.models import SearchProvider


class IngesterSettings(BaseSettings):
    model_config = SettingsConfigDict(
        case_sensitive=False,
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    SERPERDEV_API_KEY: SecretStr | None = Field(
        default=None,
        description="API key for SerperDev search provider. Can be None if using Duckduckgo.",
    )

    # Search settings
    SEARCH_PROVIDER: SearchProvider = "serperdev"
    MAX_RETRIES_PER_QUERY: int = 2
    MIN_RETRY_SLEEP_TIME_S: int = 3
    MAX_RETRY_SLEEP_TIME_S: int = 10
    SLEEP_BETWEEN_QUERIES_S: float = 4
    QUERY_TIMEOUT: int = 30
    PROXY: SecretStr | Literal["tb"] | None = None

    # Embeddings settings
    VOYAGEAI_API_KEY: SecretStr = Field(default=...)
    EMBEDDING_MODEL: str = "voyage-3"
    EMBEDDING_BATCH_SIZE: int = 128

    # Vector database settings
    PINECONE_API_KEY: SecretStr = Field(default=...)
    PINECONE_INDEX: str = Field(default="so-insights")

    MONGODB_URI: SecretStr = Field(default=...)

    # Watcher settings
    POLLING_INTERVAL_S: int = 10
    MAX_RUNTIME_S: int = 30 * 60  # 30 minutes
    PORT: int = 8081

    # Content Cleaner settings
    CONTENT_CLEANER_MODEL: str = "gpt-4o-mini"
    ARTICLE_CONTENT_CLEANER_PROMPT_REF: str = (
        "clean-article-content-no-structured-output"  # Reference to Langsmith Hub
    )
    FIRECRAWL_API_KEY: SecretStr = Field(default=...)


ingester_settings = IngesterSettings()

__all__ = ["ingester_settings"]
