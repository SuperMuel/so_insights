from fastapi import APIRouter
from shared.models import Starters
from src.dependencies import ExistingWorkspace

router = APIRouter(tags=["starters"])


@router.get(
    "/",
    response_model=list[str],
    operation_id="get_latest_starters",
)
async def get_latest_starters(workspace: ExistingWorkspace) -> list[str]:
    # Get the most recent starters document
    latest_starters = (
        await Starters.find(
            Starters.workspace_id == workspace.id,
        )
        .sort(-Starters.created_at)  # type: ignore
        .limit(4)
    )

    output: list[str] = []

    while len(output) < 4 and latest_starters:
        output.extend(latest_starters.pop(0).starters)

    return output[:4]
