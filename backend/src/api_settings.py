# base settings using pydantic-settings to define the MONGODB_URI and PORT variables from env

import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class APISettings(BaseSettings):
    model_config = SettingsConfigDict(
        case_sensitive=False,
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )
    MONGODB_URI: str = (
        Field(  # If generating client sdk on github_action, ignore the uri
            default="mongodb://localhost:27017" if os.getenv("GITHUB_ACTIONS") else ...
        )
    )
    PORT: int = Field(default=8000)


api_settings = APISettings()

__all__ = ["api_settings"]
