from pydantic import BaseModel


class WorkspaceUpdate(BaseModel):
    name: str | None = None
    description: str | None = None

    class Config:
        extra = "forbid"
