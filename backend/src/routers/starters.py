from fastapi import APIRouter
from shared.models import Starters
from src.dependencies import ExistingWorkspace

router = APIRouter(tags=["starters"])


@router.get(
    "/",
    response_model=list[str],
    operation_id="get_latest_starters",
)
async def get_latest_starters(workspace: ExistingWorkspace):
    latest_starters = (
        await Starters.find(
            Starters.workspace_id == workspace.id,
        )
        .sort(-Starters.created_at)  # type: ignore
        .first_or_none()
    )

    if not latest_starters:
        return []

    return latest_starters.starters
