from datetime import date, datetime
from beanie.operators import In
from logging import getLogger
from typing import Literal

from beanie import PydanticObjectId, SortDirection
from fastapi import APIRouter, Query, status

from shared.models import Article, Workspace, utc_datetime_factory
from src.dependencies import ExistingOrganization, ExistingWorkspace
from src.schemas import PaginatedResponse, WorkspaceCreate, WorkspaceUpdate

logger = getLogger(__name__)

router = APIRouter(tags=["workspaces"])


@router.post(
    "/",
    response_model=Workspace,
    status_code=status.HTTP_201_CREATED,
    operation_id="create_workspace",
)
async def create_workspace(
    organization: ExistingOrganization, workspace: WorkspaceCreate
):
    assert organization.id

    return await Workspace(
        organization_id=organization.id,
        **workspace.model_dump(),
    ).insert()


@router.get(
    "/",
    response_model=list[Workspace],
    operation_id="list_workspaces",
)
async def list_workspaces(
    organization: ExistingOrganization,
    enabled: bool | None = None,
):
    workspaces = Workspace.find(
        Workspace.organization_id == organization.id,
        *[Workspace.enabled == enabled] if enabled is not None else [],
    )

    return await workspaces.sort(
        -Workspace.created_at,  # type: ignore
    ).to_list()


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


@router.get(
    "/{workspace_id}/articles/by-ids",
    response_model=list[Article],
    status_code=status.HTTP_200_OK,
    operation_id="get_articles_by_ids",
)
async def get_articles_by_ids(
    workspace: ExistingWorkspace,
    article_ids: list[str] = Query(..., description="List of article IDs to fetch"),
) -> list[Article]:
    """
    Get multiple articles by their IDs for a given workspace.

    Only returns articles that belong to the specified workspace.
    """
    articles = await Article.find(
        Article.workspace_id == workspace.id,
        In(Article.id, [PydanticObjectId(id) for id in article_ids]),
    ).to_list()

    return articles


@router.get(
    "/{workspace_id}/articles",
    response_model=PaginatedResponse[Article],
    status_code=status.HTTP_200_OK,
    operation_id="list_articles",
)
async def list_articles(
    workspace: ExistingWorkspace,
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=20, ge=1, le=100),
    sort_by: Literal["date", "found_at"] = Query(default="date"),
    sort_order: Literal["asc", "desc"] = Query(default="desc"),
    start_date: date | datetime | None = Query(default=None),  # ISO format date string
    end_date: date | datetime | None = Query(default=None),
    content_fetched: bool | None = Query(default=None),
    # ingestion_run_id: str | None = Query(default=None),
):
    """
    List articles for a given workspace.

    Supports filtering, sorting, and pagination.
    """
    query = [Article.workspace_id == workspace.id]

    if start_date:
        query.append(Article.date >= start_date)
    if end_date:
        query.append(Article.date <= end_date)
    if content_fetched is not None:
        query.append(
            Article.content != None if content_fetched else Article.content == None  # noqa: E711
        )

    skip = (page - 1) * per_page

    articles_query = (
        Article.find(*query)
        .sort(
            (
                sort_by,
                SortDirection.DESCENDING
                if sort_order == "desc"
                else SortDirection.ASCENDING,
            )
        )
        .skip(skip)
        .limit(per_page)
    )

    total_count = await Article.find(*query).count()

    return PaginatedResponse(
        total=total_count,
        page=page,
        per_page=per_page,
        items=await articles_query.to_list(),
    )
