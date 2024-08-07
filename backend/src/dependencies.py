from typing import Annotated

from beanie import PydanticObjectId
from fastapi import Depends, HTTPException

from shared.models import SearchQuerySet, Workspace


async def get_workspace(workspace_id: str | PydanticObjectId) -> Workspace:
    workspace = await Workspace.get(workspace_id)
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")
    assert workspace.id
    return workspace


ExistingWorkspace = Annotated[Workspace, Depends(get_workspace)]


async def get_search_query_set(
    search_query_set_id: str | PydanticObjectId, workspace: ExistingWorkspace
) -> SearchQuerySet:
    search_query_set = await SearchQuerySet.get(search_query_set_id)

    if (
        not search_query_set
        or search_query_set.workspace_id != workspace.id
        or search_query_set.deleted
    ):
        raise HTTPException(status_code=404, detail="Search query set not found")

    return search_query_set


ExistingSearchQuerySet = Annotated[SearchQuerySet, Depends(get_search_query_set)]
