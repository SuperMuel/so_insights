from typing import Annotated, List, Literal
from fastapi import APIRouter, HTTPException, Query
from shared.set_of_unique_articles import SetOfUniqueArticles
from src.dependencies import (
    ExistingCluster,
    ExistingClusteringSession,
    ExistingWorkspace,
)
from beanie.operators import In, Exists, Or
from beanie.odm.queries.find import FindMany
from shared.models import (
    Article,
    ClusterFeedback,
    ClusteringSession,
    Cluster,
    RelevanceLevel,
    Status,
)
from src.schemas import ArticlePreview, ClusterWithArticles, ClusteringSessionCreate

router = APIRouter(tags=["clustering"])

type RelevancyFilter = Literal[RelevanceLevel, "all", "unknown"]


def filter_clusters_with_relevancy(
    clusters: FindMany[Cluster], relevancy_filter: RelevancyFilter
) -> FindMany[Cluster]:
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
    return clusters


@router.get(
    "/sessions",
    response_model=list[ClusteringSession],
    operation_id="list_clustering_sessions",
)
async def list_clustering_sessions(
    workspace: ExistingWorkspace,
    statuses: Annotated[list[Status] | None, Query()] = None,
    # async def read_items(q: Annotated[list[str] | None, Query()] = None):
):
    """List all clustering sessions for a workspace"""
    sessions = ClusteringSession.find(ClusteringSession.workspace_id == workspace.id)

    if statuses is not None:
        sessions = sessions.find(In(ClusteringSession.status, statuses))

    sessions = sessions.sort(
        -ClusteringSession.created_at,  # type: ignore
    )

    return await sessions.to_list()


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
async def list_clusters(
    session: ExistingClusteringSession,
    relevance_levels: Annotated[List[RelevanceLevel] | None, Query()] = None,
):
    """List all clusters for a specific clustering session"""
    clusters = Cluster.find(
        Cluster.session_id == session.id,
        Cluster.workspace_id == session.workspace_id,
    )

    if relevance_levels is not None:
        clusters = clusters.find(
            Exists(Cluster.evaluation),
            In(Cluster.evaluation.relevance_level, relevance_levels),  # type: ignore
        )

    clusters = await clusters.sort(
        -Cluster.articles_count,  # type: ignore
    ).to_list()

    return clusters


@router.get(
    "/clusters/{cluster_id}", response_model=Cluster, operation_id="get_cluster"
)
async def get_cluster(cluster: ExistingCluster):
    """Get a specific cluster"""
    return cluster


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

    clusters = filter_clusters_with_relevancy(clusters, relevancy_filter)

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


@router.put(
    "/clusters/{cluster_id}/feedback",
    response_model=Cluster,
    operation_id="set_cluster_feedback",
)
async def set_cluster_feedback(
    cluster: ExistingCluster,
    feedback: ClusterFeedback,
):
    """Set or update feedback for a specific cluster"""
    cluster.feedback = feedback
    return await cluster.save()


@router.delete(
    "/clusters/{cluster_id}/feedback",
    response_model=Cluster,
    operation_id="delete_cluster_feedback",
)
async def delete_cluster_feedback(
    cluster: ExistingCluster,
):
    """Delete feedback for a specific cluster"""
    if cluster.feedback is None:
        raise HTTPException(
            status_code=404, detail="No feedback exists for this cluster"
        )

    cluster.feedback = None
    return await cluster.save()


@router.post(
    "/sessions",
    response_model=ClusteringSession,
    operation_id="create_clustering_session",
)
async def create_clustering_session(
    workspace: ExistingWorkspace, session_create: ClusteringSessionCreate
):
    """Create a new pending clustering session"""
    assert workspace.id

    session = ClusteringSession(
        workspace_id=workspace.id,
        data_start=session_create.data_start,
        data_end=session_create.data_end,
        nb_days=(session_create.data_end - session_create.data_start).days,
    )

    return await session.insert()
