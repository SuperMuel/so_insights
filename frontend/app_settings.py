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

    so_insights_api_url: str = Field(
        default=... if os.getenv("DYNO") else "http://localhost:8000"
    )
