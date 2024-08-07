from fastapi import APIRouter, status
from src.dependencies import ExistingWorkspace
from shared.shared.models import Workspace, utc_datetime_factory
from src.schemas import WorkspaceUpdate

router = APIRouter(tags=["workspaces"])


@router.post(
    "/",
    response_model=Workspace,
    status_code=status.HTTP_201_CREATED,
    operation_id="create_workspace",
)
async def create_workspace(workspace: Workspace):
    await workspace.insert()
    return workspace


@router.get(
    "/",
    response_model=list[Workspace],
    operation_id="list_workspaces",
)
async def list_workspaces():
    return await Workspace.find_all().to_list()


@router.get(
    "/{workspace_id}",
    response_model=Workspace,
    operation_id="get_workspace",
)
async def get_workspace(workspace: ExistingWorkspace):
    return workspace


@router.put(
    "/{workspace_id}",
    response_model=Workspace,
    operation_id="update_workspace",
)
async def update_workspace(
    workspace_update: WorkspaceUpdate, workspace: ExistingWorkspace
):
    update_data = workspace_update.model_dump(exclude_unset=True)
    update_data["updated_at"] = utc_datetime_factory()
    return await workspace.update({"$set": update_data})
