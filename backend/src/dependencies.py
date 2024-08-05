from typing import Annotated

from beanie import PydanticObjectId
from fastapi import Depends, HTTPException

from src.models import Workspace


async def get_workspace(workspace_id: str | PydanticObjectId) -> Workspace:
    workspace = await Workspace.get(workspace_id)
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")
    return workspace


ExistingWorkspace = Annotated[Workspace, Depends(get_workspace)]
