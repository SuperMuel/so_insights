from typing import Annotated

from beanie import PydanticObjectId
from fastapi import Depends, HTTPException

from shared.models import (
    Cluster,
    ClusteringSession,
    IngestionConfig,
    IngestionRun,
    RssIngestionConfig,
    SearchIngestionConfig,
    Workspace,
)


async def get_workspace(workspace_id: str | PydanticObjectId) -> Workspace:
    workspace = await Workspace.get(workspace_id)
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")
    assert workspace.id
    return workspace


ExistingWorkspace = Annotated[Workspace, Depends(get_workspace)]


async def get_ingestion_config(
    ingestion_config_id: str | PydanticObjectId, workspace: ExistingWorkspace
) -> IngestionConfig:
    ingestion_config = await IngestionConfig.get(
        ingestion_config_id, with_children=True
    )
    if not ingestion_config or ingestion_config.workspace_id != workspace.id:
        raise HTTPException(status_code=404, detail="Ingestion config not found")
    return ingestion_config


ExistingIngestionConfig = Annotated[IngestionConfig, Depends(get_ingestion_config)]


async def get_search_ingestion_config(
    search_ingestion_config_id: str | PydanticObjectId, workspace: ExistingWorkspace
) -> SearchIngestionConfig:
    ingestion_config = await SearchIngestionConfig.get(search_ingestion_config_id)
    if not ingestion_config or ingestion_config.workspace_id != workspace.id:
        raise HTTPException(status_code=404, detail="Search ingestion config not found")
    return ingestion_config


async def get_rss_ingestion_config(
    rss_ingestion_config_id: str | PydanticObjectId, workspace: ExistingWorkspace
) -> RssIngestionConfig:
    ingestion_config = await RssIngestionConfig.get(rss_ingestion_config_id)
    if not ingestion_config or ingestion_config.workspace_id != workspace.id:
        raise HTTPException(status_code=404, detail="RSS ingestion config not found")
    return ingestion_config


ExistingRssIngestionConfig = Annotated[
    RssIngestionConfig, Depends(get_rss_ingestion_config)
]


ExistingSearchIngestionConfig = Annotated[
    SearchIngestionConfig, Depends(get_search_ingestion_config)
]


async def get_ingestion_run(
    ingestion_run_id: str | PydanticObjectId, workspace: ExistingWorkspace
) -> IngestionRun:
    ingestion_run = await IngestionRun.get(ingestion_run_id)
    if not ingestion_run or ingestion_run.workspace_id != workspace.id:
        raise HTTPException(status_code=404, detail="Ingestion run not found")
    return ingestion_run


ExistingIngestionRun = Annotated[IngestionRun, Depends(get_ingestion_run)]


async def get_clustering_session(
    session_id: str | PydanticObjectId, workspace: ExistingWorkspace
) -> ClusteringSession:
    session = await ClusteringSession.get(session_id)
    if not session or session.workspace_id != workspace.id:
        raise HTTPException(status_code=404, detail="Clustering session not found")
    return session


ExistingClusteringSession = Annotated[
    ClusteringSession, Depends(get_clustering_session)
]


async def get_cluster(
    cluster_id: str | PydanticObjectId, workspace: ExistingWorkspace
) -> Cluster:
    cluster = await Cluster.get(cluster_id)
    if not cluster or cluster.workspace_id != workspace.id:
        raise HTTPException(status_code=404, detail="Cluster not found")
    return cluster


ExistingCluster = Annotated[Cluster, Depends(get_cluster)]
