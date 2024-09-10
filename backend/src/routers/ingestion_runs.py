from fastapi import APIRouter
from src.dependencies import (
    ExistingIngestionConfig,
    ExistingIngestionRun,
    ExistingWorkspace,
)
from shared.models import IngestionRun, Status
from typing import List


router = APIRouter(tags=["ingestion-runs"])


@router.post(
    "/",
    response_model=IngestionRun,
    operation_id="create_ingestion_run",
)
async def create_ingestion_run(
    workspace: ExistingWorkspace,
    config: ExistingIngestionConfig,
):
    assert workspace.id and config.id

    new_ingestion_run = IngestionRun(
        workspace_id=workspace.id,
        config_id=config.id,
        status=Status.pending,
    )
    return await new_ingestion_run.insert()


@router.get("/", response_model=List[IngestionRun], operation_id="list_ingestion_runs")
async def list_ingestion_runs(workspace: ExistingWorkspace):
    return (
        await IngestionRun.find(IngestionRun.workspace_id == workspace.id)
        .sort(-IngestionRun.created_at)  # type: ignore
        .to_list()
    )


@router.get(
    "/{ingestion_run_id}", response_model=IngestionRun, operation_id="get_ingestion_run"
)
async def get_ingestion_run(ingestion_run: ExistingIngestionRun):
    return ingestion_run


@router.get(
    "/ingestion_config/{ingestion_config_id}",
    response_model=List[IngestionRun],
    operation_id="list_ingestion_runs_for_ingestion_config",
)
async def list_ingestion_runs_for_ingestion_config(
    workspace: ExistingWorkspace,
    config: ExistingIngestionConfig,
):
    return (
        await IngestionRun.find(
            IngestionRun.workspace_id == workspace.id,
            IngestionRun.config_id == config.id,
        )
        .sort(-IngestionRun.created_at)  # type: ignore
        .to_list()
    )
