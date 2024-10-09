from fastapi import APIRouter, status
from src.dependencies import ExistingWorkspace
from shared.models import Workspace, utc_datetime_factory
from src.schemas import WorkspaceUpdate, WorkspaceCreate
from logging import getLogger

logger = getLogger(__name__)

router = APIRouter(tags=["workspaces"])


@router.post(
    "/",
    response_model=Workspace,
    status_code=status.HTTP_201_CREATED,
    operation_id="create_workspace",
)
async def create_workspace(workspace: WorkspaceCreate):
    return await Workspace(**workspace.model_dump()).insert()


@router.get(
    "/",
    response_model=list[Workspace],
    operation_id="list_workspaces",
)
async def list_workspaces():
    return (
        await Workspace.find_all()
        .sort(
            Workspace.created_at,  # type: ignore
        )
        .to_list()
    )


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
    # TODO : this code does not inherit from the Workspace validations
    update_data = workspace_update.model_dump(exclude_unset=True)
    update_data["updated_at"] = utc_datetime_factory()
    return await workspace.update({"$set": update_data})
