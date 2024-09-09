from fastapi import APIRouter, status
from src.dependencies import ExistingWorkspace, ExistingSearchIngestionConfig
from shared.models import utc_datetime_factory, SearchIngestionConfig
from src.schemas import SearchIngestionConfigCreate, SearchIngestionConfigUpdate

router = APIRouter(tags=["ingestion-configs"])


@router.get(
    "/search/{search_ingestion_config_id}",
    response_model=SearchIngestionConfig,
    operation_id="get_search_ingestion_config",
)
async def get_search_ingestion_config(ingestion_config: ExistingSearchIngestionConfig):
    return ingestion_config


@router.post(
    "/search",
    response_model=SearchIngestionConfigCreate,
    status_code=status.HTTP_201_CREATED,
    operation_id="create_search_ingestion_config",
)
async def create_search_ingestion_config(
    config: SearchIngestionConfigCreate, workspace: ExistingWorkspace
):
    assert workspace.id

    new_config = SearchIngestionConfig(
        **config.model_dump(),
        workspace_id=workspace.id,
    )

    return await new_config.insert()


@router.get(
    "/search",
    response_model=list[SearchIngestionConfig],
    operation_id="list_search_ingestion_configs",
)
async def list_search_ingestion_configs(workspace: ExistingWorkspace):
    assert workspace.id

    return await SearchIngestionConfig.find(
        SearchIngestionConfig.workspace_id == workspace.id
    ).to_list()


@router.put(
    "/search/{search_ingestion_config_id}",
    response_model=SearchIngestionConfig,
    operation_id="update_search_ingestion_config",
)
async def update_search_ingestion_config(
    config_update: SearchIngestionConfigUpdate,
    ingestion_config: ExistingSearchIngestionConfig,
):
    update_data = config_update.model_dump(exclude_unset=True)
    update_data["updated_at"] = utc_datetime_factory()
    await ingestion_config.update({"$set": update_data})
    return ingestion_config
