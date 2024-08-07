from fastapi import APIRouter, status
from src.dependencies import ExistingWorkspace, ExistingSearchQuerySet
from src.models import SearchQuerySet, utc_datetime_factory
from src.schemas import SearchQuerySetCreate, SearchQuerySetUpdate

router = APIRouter(tags=["search-query-sets"])


@router.post(
    "/",
    response_model=SearchQuerySet,
    status_code=status.HTTP_201_CREATED,
    operation_id="create_search_query_set",
)
async def create_search_query_set(
    search_query_set: SearchQuerySetCreate, workspace: ExistingWorkspace
):
    assert workspace.id  # To remove the warning below. TODO : find another way
    new_search_query_set = SearchQuerySet(
        **search_query_set.model_dump(), workspace_id=workspace.id
    )
    return await new_search_query_set.insert()


@router.get(
    "/",
    response_model=list[SearchQuerySet],
    operation_id="list_search_query_sets",
)
async def list_search_query_sets(workspace: ExistingWorkspace):
    return await SearchQuerySet.find(
        SearchQuerySet.workspace_id == workspace.id,
        SearchQuerySet.deleted == False,  # noqa
    ).to_list()


@router.get(
    "/{search_query_set_id}",
    response_model=SearchQuerySet,
    operation_id="get_search_query_set",
)
async def get_search_query_set(search_query_set: ExistingSearchQuerySet):
    return search_query_set


@router.put(
    "/{search_query_set_id}",
    response_model=SearchQuerySet,
    operation_id="update_search_query_set",
)
async def update_search_query_set(
    search_query_set_update: SearchQuerySetUpdate,
    search_query_set: ExistingSearchQuerySet,
):
    update_data = search_query_set_update.model_dump(exclude_unset=True)
    update_data["updated_at"] = utc_datetime_factory()
    await search_query_set.update({"$set": update_data})
    return search_query_set


@router.delete(
    "/{search_query_set_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    operation_id="delete_search_query_set",
)
async def delete_search_query_set(search_query_set: ExistingSearchQuerySet):
    search_query_set.deleted = True
    search_query_set.deleted_at = utc_datetime_factory()
    await search_query_set.replace()
    return None
