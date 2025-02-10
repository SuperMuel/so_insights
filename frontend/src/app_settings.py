from pydantic import Field, SecretStr
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
    )  # type: ignore

    VOYAGEAI_API_KEY: SecretStr = Field(default=...)
    EMBEDDING_MODEL: str = "voyage-3"
    EMBEDDING_BATCH_SIZE: int = 128

    PINECONE_API_KEY: SecretStr = Field(default=...)
    PINECONE_INDEX: str = Field(default="so-insights")

    RETRIEVER_K: int = 30

    OPENAI_API_KEY: SecretStr = Field(default=...)
    ANTHROPIC_API_KEY: SecretStr = Field(default=...)

    GETIMG_API_KEY: SecretStr = Field(default=...)

    LOGO_LIGHT_URL: str | None = None
    LOGO_DARK_URL: str | None = None

    IMAGE_PROMPT_LLM: str = "gpt-4o-mini"

    CLUSTERS_PER_PAGE: int = 30

    # Temporary limit the number of ingestion_runs to display in the workspaces page to improve performance.
    # In the future, implement pagination instead of just trimming the list.
    MAX_RUNS_TO_DISPLAY: int = 30

    INGESTION_HISTORY_AUTO_REFRESH_INTERVAL_S: int = 15

    # Prompts references to Langsmith Hub
    SIMPLE_CONTENT_GEN_PROMPT_REF: str = "simple-content-gen"
    IMAGE_GEN_PROMPT_REF: str = "img-gen"
    CONTEXTUALIZE_PROMPT_REF: str = "contextualize"
    QA_RAG_PROMPT_REF: str = "qa-rag"

    # Pages
    CONTENT_STUDIO_PAGE_ENABLED: bool = False


app_settings = AppSettings()

__all__ = ["app_settings"]
