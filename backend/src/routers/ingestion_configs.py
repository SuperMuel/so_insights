from fastapi import APIRouter, status

from shared.models import (
    IngestionConfig,
    RssIngestionConfig,
    SearchIngestionConfig,
    utc_datetime_factory,
)
from src.dependencies import (
    ExistingRssIngestionConfig,
    ExistingSearchIngestionConfig,
    ExistingWorkspace,
)
from src.schemas import (
    RssIngestionConfigCreate,
    RssIngestionConfigUpdate,
    SearchIngestionConfigCreate,
    SearchIngestionConfigUpdate,
)

router = APIRouter(tags=["ingestion-configs"])


@router.get(
    "/",
    response_model=list[SearchIngestionConfig | RssIngestionConfig],
    operation_id="list_ingestion_configs",
)
async def list_ingestion_configs(workspace: ExistingWorkspace):
    assert workspace.id

    return (
        await IngestionConfig.find(
            IngestionConfig.workspace_id == workspace.id,
            with_children=True,
        )
        .sort(-IngestionConfig.created_at)  # type:ignore
        .to_list()
    )


@router.get(
    "/search/{search_ingestion_config_id}",
    response_model=SearchIngestionConfig,
    operation_id="get_search_ingestion_config",
)
async def get_search_ingestion_config(ingestion_config: ExistingSearchIngestionConfig):
    return ingestion_config


@router.post(
    "/search",
    response_model=SearchIngestionConfig,
    status_code=status.HTTP_201_CREATED,
    operation_id="create_search_ingestion_config",
)
async def create_search_ingestion_config(
    config: SearchIngestionConfigCreate, workspace: ExistingWorkspace
):
    assert workspace.id

    # TODO : prevent creation of config with same title case and whitespace insensitive

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

    return (
        await SearchIngestionConfig.find(
            SearchIngestionConfig.workspace_id == workspace.id
        )
        .sort(
            -SearchIngestionConfig.created_at  # type:ignore
        )
        .to_list()
    )


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


@router.post(
    "/rss",
    response_model=RssIngestionConfig,
    status_code=status.HTTP_201_CREATED,
    operation_id="create_rss_ingestion_config",
)
async def create_rss_ingestion_config(
    config: RssIngestionConfigCreate, workspace: ExistingWorkspace
):
    assert workspace.id

    new_config = RssIngestionConfig(
        **config.model_dump(),
        workspace_id=workspace.id,
    )

    return await new_config.insert()


@router.get(
    "/rss",
    response_model=list[RssIngestionConfig],
    operation_id="list_rss_ingestion_configs",
)
async def list_rss_ingestion_configs(workspace: ExistingWorkspace):
    assert workspace.id

    return (
        await RssIngestionConfig.find(RssIngestionConfig.workspace_id == workspace.id)
        .sort(
            -RssIngestionConfig.created_at  # type:ignore
        )
        .to_list()
    )


@router.get(
    "/rss/{rss_ingestion_config_id}",
    response_model=RssIngestionConfig,
    operation_id="get_rss_ingestion_config",
)
async def get_rss_ingestion_config(ingestion_config: ExistingRssIngestionConfig):
    return ingestion_config


@router.put(
    "/rss/{rss_ingestion_config_id}",
    response_model=RssIngestionConfig,
    operation_id="update_rss_ingestion_config",
)
async def update_rss_ingestion_config(
    config_update: RssIngestionConfigUpdate,
    ingestion_config: ExistingRssIngestionConfig,
):
    update_data = config_update.model_dump(exclude_unset=True)
    update_data["updated_at"] = utc_datetime_factory()
    await ingestion_config.update({"$set": update_data})
    return ingestion_config
