# base settings using pydantic-settings to define the MONGODB_URI and PORT variables from env

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class APISettings(BaseSettings):
    model_config = SettingsConfigDict(
        case_sensitive=False,
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )
    MONGODB_URI: str = Field(default=...)
    PORT: int = Field(default=8000)
