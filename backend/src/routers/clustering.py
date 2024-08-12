from fastapi import APIRouter
from src.dependencies import (
    ExistingCluster,
    ExistingClusteringSession,
    ExistingWorkspace,
)
from shared.models import ClusteringSession, Cluster

router = APIRouter(tags=["clustering"])


@router.get(
    "/sessions",
    response_model=list[ClusteringSession],
    operation_id="list_clustering_sessions",
)
async def list_clustering_sessions(workspace: ExistingWorkspace):
    """List all clustering sessions for a workspace"""
    sessions = (
        await ClusteringSession.find(ClusteringSession.workspace_id == workspace.id)
        .sort(-ClusteringSession.session_start)  # type: ignore
        .to_list()
    )
    return sessions


@router.get(
    "/sessions/{session_id}",
    response_model=ClusteringSession,
    operation_id="get_clustering_session",
)
async def get_clustering_session(session: ExistingClusteringSession):
    """Get a specific clustering session"""
    return session


@router.get(
    "/sessions/{session_id}/clusters",
    response_model=list[Cluster],
    operation_id="list_clusters_for_session",
)
async def list_clusters(session: ExistingClusteringSession):
    """List all clusters for a specific clustering session"""
    clusters = (
        await Cluster.find(
            Cluster.session_id == session.id,
            Cluster.workspace_id == session.workspace_id,
        )
        .sort(-Cluster.articles_count)  # type: ignore
        .to_list()
    )
    return clusters


@router.get(
    "/clusters/{cluster_id}", response_model=Cluster, operation_id="get_cluster"
)
async def get_cluster(cluster: ExistingCluster):
    """Get a specific cluster"""
    return cluster
