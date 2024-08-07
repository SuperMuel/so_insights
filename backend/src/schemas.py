from pydantic import BaseModel

from shared.region import Region


class WorkspaceUpdate(BaseModel):
    name: str | None = None
    description: str | None = None

    class Config:
        extra = "forbid"


class SearchQuerySetCreate(BaseModel):
    queries: list[str]
    title: str
    region: Region


class SearchQuerySetUpdate(BaseModel):
    queries: list[str] | None = None
    title: str | None = None
    region: Region | None = None

    class Config:
        extra = "forbid"
