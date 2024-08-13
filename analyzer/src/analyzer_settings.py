from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class AnalyzerSettings(BaseSettings):
    model_config = SettingsConfigDict(
        case_sensitive=False,
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    MONGODB_URI: str = Field(default=...)

    PINECONE_API_KEY: str = Field(default=...)
    PINECONE_INDEX: str = Field(default=...)

    DEFAULT_MIN_CLUSTER_SIZE: int = 6
    DEFAULT_MIN_SAMPLES: int = 3
