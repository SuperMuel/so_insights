# src/routers/analysis_tasks.py
from fastapi import APIRouter, HTTPException, status
from beanie import PydanticObjectId
from shared.models import AnalysisTask, Status
from src.dependencies import ExistingWorkspace

from src.schemas import AnalysisTaskCreate

router = APIRouter(tags=["analysis-tasks"])


@router.post(
    "/",
    response_model=AnalysisTask,
    status_code=status.HTTP_201_CREATED,
    operation_id="create_analysis_task",
)
async def create_analysis_task(task: AnalysisTaskCreate, workspace: ExistingWorkspace):
    assert workspace.id
    new_task = AnalysisTask(
        workspace_id=workspace.id,
        status=Status.pending,
        data_start=task.data_start,
        data_end=task.data_end,
    )
    await new_task.insert()
    return new_task


@router.get("/", response_model=list[AnalysisTask], operation_id="list_analysis_tasks")
async def list_analysis_tasks(
    workspace: ExistingWorkspace,
    status: Status | None = None,
):
    tasks = AnalysisTask.find(AnalysisTask.workspace_id == workspace.id)
    if status:
        tasks = tasks.find(AnalysisTask.status == status)

    tasks = await tasks.sort(
        -AnalysisTask.created_at  # type:ignore
    ).to_list()

    return tasks


@router.get("/{task_id}", response_model=AnalysisTask, operation_id="get_analysis_task")
async def get_analysis_task(task_id: PydanticObjectId, workspace: ExistingWorkspace):
    task = await AnalysisTask.get(task_id)
    if not task or task.workspace_id != workspace.id:
        raise HTTPException(status_code=404, detail="Analysis task not found")
    return task
