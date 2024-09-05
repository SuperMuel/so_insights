from fastapi import APIRouter, HTTPException
from src.dependencies import (
    ExistingIngestionRun,
    ExistingSearchQuerySet,
    ExistingWorkspace,
)
from shared.models import IngestionRun, SearchQuerySet
from typing import List

from src.schemas import IngestionRunCreate

router = APIRouter(tags=["ingestion-runs"])


@router.post(
    "/",
    response_model=IngestionRun,
    operation_id="create_ingestion_run",
)
async def create_ingestion_run(
    workspace: ExistingWorkspace,
    run: IngestionRunCreate,
):
    assert workspace.id

    query_set = await SearchQuerySet.get(run.search_query_set_id)
    if not query_set:
        raise HTTPException(status_code=404, detail="Search query set not found")

    if await IngestionRun.find(
        IngestionRun.workspace_id == workspace.id,
        IngestionRun.queries_set_id == query_set.id,
        IngestionRun.status == "running",
    ).count():
        raise HTTPException(
            status_code=400,
            detail="Search query set is already being ingested",
        )

    new_ingestion_run = IngestionRun(
        workspace_id=workspace.id,
        queries_set_id=run.search_query_set_id,
        time_limit=run.time_limit,
        max_results=run.max_results,
        status="pending",
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
