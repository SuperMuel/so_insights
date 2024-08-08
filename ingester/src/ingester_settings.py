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
    INITIAL_SLEEP_TIME: int = 5
    MAX_SLEEP_TIME: int = 60
    MAX_RETRIES: int = 3
    TIMEOUT: int = 30

    VOYAGE_API_KEY: str = Field(default=...)
    EMBEDDING_MODEL: str = "voyage-large-2-instruct"
    EMBEDDING_BATCH_SIZE = 128

    PINECONE_API_KEY: str = Field(default=...)
    PINECONE_INDEX: str = Field(default=...)

    MONGODB_URI: str = Field(default=...)

    # TEMPORARY: these parameters will be in the IngestionSchedule model
    MAX_RESULTS: int = 30
    TIME_LIMIT: Literal["d", "w", "m", "y"] = "d"
