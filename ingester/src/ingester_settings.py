from typing import Literal
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class IngesterSettings(BaseSettings):
    model_config = SettingsConfigDict(
        case_sensitive=False,
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )
    MAX_RETRIES_PER_QUERY: int = 2
    RETRY_SLEEP_TIME_S: int = 5
    SLEEP_BETWEEN_QUERIES_S: int = 5
    QUERY_TIMEOUT: int = 30

    # Whether to log each search query during the search
    VERBOSE_SEARCH: bool = True

    VOYAGEAI_API_KEY: str = Field(default=...)
    EMBEDDING_MODEL: str = "voyage-large-2-instruct"
    EMBEDDING_BATCH_SIZE: int = 128

    PINECONE_API_KEY: str = Field(default=...)
    PINECONE_INDEX: str = Field(default=...)

    MONGODB_URI: str = Field(default=...)

    # TEMPORARY: these parameters will be in the IngestionSchedule model
    MAX_RESULTS: int = 30
    DEFAULT_TIME_LIMIT: Literal["d", "w", "m", "y"] = "d"
