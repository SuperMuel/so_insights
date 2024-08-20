from typing import Literal
from fastapi import APIRouter
from shared.set_of_unique_articles import SetOfUniqueArticles
from src.dependencies import (
    ExistingCluster,
    ExistingClusteringSession,
    ExistingWorkspace,
)
from beanie.operators import In, Exists, Or
from shared.models import Article, ClusteringSession, Cluster, RelevanceLevel
from src.schemas import ArticlePreview, ClusterWithArticles

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


type RelevancyFilter = Literal[RelevanceLevel, "all", "unknown"]


@router.get(
    "/sessions/{session_id}/clusters-with-articles",
    response_model=list[ClusterWithArticles],
    operation_id="list_clusters_with_articles_for_session",
)
async def list_clusters_with_articles(
    session: ExistingClusteringSession,
    relevancy_filter: RelevancyFilter = "all",
    n_articles: int = 5,
):
    """List all clusters with their top N articles for a specific clustering session"""

    clusters = Cluster.find(
        Cluster.session_id == session.id,
        Cluster.workspace_id == session.workspace_id,
    )

    if relevancy_filter == "all":
        pass
    elif relevancy_filter == "unknown":
        clusters = clusters.find(
            Or(
                Exists(Cluster.evaluation, False),
                Cluster.evaluation == None,  # noqa: E711 # type: ignore
            )
        )
    else:
        clusters = clusters.find(
            Exists(Cluster.evaluation),
            Cluster.evaluation.relevance_level == relevancy_filter,  # type: ignore
        )

    clusters = await clusters.sort(
        -Cluster.articles_count,  # type: ignore
    ).to_list()

    result = []
    for cluster in clusters:
        articles = SetOfUniqueArticles(
            await Article.find(
                In(Article.id, cluster.articles_ids[:n_articles])
            ).to_list()
        )

        article_previews = [
            ArticlePreview(
                id=str(article.id),
                title=article.title,
                url=article.url,
                body=article.body,
                date=article.date,
                source=article.source,
            )
            for article in articles
        ]
        result.append(ClusterWithArticles.from_cluster(cluster, article_previews))

    return result
