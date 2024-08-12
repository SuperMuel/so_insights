from fastapi import APIRouter
from src.dependencies import (
    ExistingIngestionRun,
    ExistingSearchQuerySet,
    ExistingWorkspace,
)
from shared.models import IngestionRun
from typing import List

router = APIRouter(tags=["ingestion-runs"])


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
    "/search-query-set/{search_query_set_id}",
    response_model=List[IngestionRun],
    operation_id="list_ingestion_runs_for_search_query_set",
)
async def list_ingestion_runs_for_search_query_set(
    workspace: ExistingWorkspace,
    search_query_set: ExistingSearchQuerySet,
):
    return (
        await IngestionRun.find(
            IngestionRun.workspace_id == workspace.id,
            IngestionRun.queries_set_id == search_query_set.id,
        )
        .sort(-IngestionRun.created_at)  # type: ignore
        .to_list()
    )
