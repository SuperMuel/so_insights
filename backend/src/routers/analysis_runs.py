from typing import Annotated, List, Literal

from beanie.odm.queries.find import FindMany
from beanie.operators import Exists, In, Or
from fastapi import APIRouter, HTTPException, Query

from shared.models import (
    AnalysisParams,
    AnalysisRun,
    AnalysisType,
    Article,
    Cluster,
    ClusterFeedback,
    ClusteringAnalysisParams,
    RelevanceLevel,
    ReportAnalysisParams,
    Status,
    Workspace,
)
from shared.set_of_unique_articles import SetOfUniqueArticles
from src.dependencies import (
    ExistingAnalysisRun,
    ExistingCluster,
    ExistingClusteringRun,
    ExistingReportRun,
    ExistingWorkspace,
)
from src.schemas import (
    AnalysisRunCreate,
    ArticlePreview,
    ClusterWithArticles,
)

router = APIRouter(tags=["analysis_runs"])

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
    "/",
    response_model=List[AnalysisRun],
    operation_id="list_analysis_runs",
)
async def list_analysis_runs(
    workspace: ExistingWorkspace,
    statuses: Annotated[list[Status] | None, Query()] = None,
):
    """List all analysis runs for a workspace"""
    runs = AnalysisRun.find(AnalysisRun.workspace_id == workspace.id)

    if statuses is not None:
        runs = runs.find(In(AnalysisRun.status, statuses))

    runs = runs.sort(
        -AnalysisRun.created_at,  # type: ignore
    )

    return await runs.to_list()


@router.get(
    "/{analysis_run_id}",
    response_model=AnalysisRun,
    operation_id="get_analysis_run",
)
async def get_analysis_run(
    analysis_run: ExistingAnalysisRun,
):
    """Get a specific analysis run"""
    return analysis_run


@router.get(
    "/{analysis_run_id}/clusters",
    response_model=list[Cluster],
    operation_id="list_clusters_for_clustering_run",
)
async def list_clusters(
    analysis_run: ExistingClusteringRun,
    relevance_levels: Annotated[List[RelevanceLevel] | None, Query()] = None,
):
    """List all clusters for a specific analysis run"""
    clusters = Cluster.find(
        Cluster.session_id == analysis_run.id,
        Cluster.workspace_id == analysis_run.workspace_id,
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
    "/{analysis_run_id}/clusters-with-articles",
    response_model=list[ClusterWithArticles],
    operation_id="list_clusters_with_articles_for_run",
)
async def list_clusters_with_articles(
    analysis_run: ExistingClusteringRun,
    relevancy_filter: RelevancyFilter = "all",
    n_articles: int = 5,
):
    """List all clusters with their top N articles for a specific analysis run"""

    clusters = Cluster.find(
        Cluster.session_id == analysis_run.id,
        Cluster.workspace_id == analysis_run.workspace_id,
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


def _get_default_analysis_params(
    workspace: Workspace,
    analysis_type: AnalysisType,
) -> AnalysisParams:
    match analysis_type:
        case "clustering":
            return ClusteringAnalysisParams(
                hdbscan_settings=workspace.hdbscan_settings,
            )
        case "report":
            return ReportAnalysisParams()

    raise ValueError(
        f"Analysis type {analysis_type} not supported to create a default params"
    )


@router.post(
    "/",
    response_model=AnalysisRun,
    operation_id="create_analysis_run",
)
async def create_analysis_run(
    workspace: ExistingWorkspace,
    run_create: AnalysisRunCreate,
):
    """Create a new pending analysis run"""
    assert workspace.id

    params = (
        _get_default_analysis_params(workspace, run_create.analysis_type)
        if run_create.params is None
        else run_create.params
    )

    run = AnalysisRun(
        workspace_id=workspace.id,
        data_start=run_create.data_start,
        data_end=run_create.data_end,
        analysis_type=run_create.analysis_type,
        params=params,
    )

    return await run.insert()
