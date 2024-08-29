from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
import os


class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(
        case_sensitive=False,
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    SO_INSIGHTS_API_URL: str = Field(
        default=... if os.getenv("DYNO") else "http://localhost:8000"
    )

    VOYAGEAI_API_KEY: str = Field(default=...)
    EMBEDDING_MODEL: str = "voyage-large-2-instruct"
    EMBEDDING_BATCH_SIZE: int = 128

    PINECONE_API_KEY: str = Field(default=...)
    PINECONE_INDEX: str = Field(default=...)

    RETRIEVER_K: int = 30

    OPENAI_API_KEY: str = Field(default=...)
    ANTHROPIC_API_KEY: str = Field(default=...)

    GETIMG_API_KEY: str = Field(default=...)

    LOGO_URL: str | None = None
