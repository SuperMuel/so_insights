from pydantic import BaseModel

from shared.models import ModelDescription, ModelTitle
from shared.region import Region


class WorkspaceCreate(BaseModel):
    name: ModelTitle
    description: ModelDescription = ""

    class Config:
        extra = "forbid"


class WorkspaceUpdate(BaseModel):
    name: ModelTitle | None
    description: ModelDescription | None

    class Config:
        extra = "forbid"


class SearchQuerySetCreate(BaseModel):
    queries: list[str]
    title: ModelTitle
    region: Region


class SearchQuerySetUpdate(BaseModel):
    queries: list[str] | None = None
    title: ModelTitle | None = None
    region: Region | None = None

    class Config:
        extra = "forbid"
