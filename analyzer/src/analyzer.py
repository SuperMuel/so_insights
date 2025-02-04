import asyncio
import logging
from shared.models import (
    AnalysisRun,
    Cluster,
    ClusterEvaluation,
    ClusteringAnalysisResult,
    ClusteringRunEvaluationResult,
    Workspace,
)

from src.analyzer_settings import analyzer_settings
from datetime import datetime


from beanie import PydanticObjectId
from beanie.operators import Exists
from shared.models import (
    Article,
    Status,
)


from src.cluster_evaluator import ClusterEvaluator
from src.cluster_overview_generator import ClusterOverviewGenerator
from src.clustering_engine import ClusteringEngine
from src.clustering_analysis_generator import ClusteringAnalysisSummarizer
from src.starters_generator import ConversationStartersGenerator
from src.util import get_first_valid_image
from src.vector_repository import PineconeVectorRepository

logger = logging.getLogger(__name__)


def id_to_str(id: PydanticObjectId | None) -> str:
    if not id:
        raise ValueError("id is None")
    return str(id)


class Analyzer:
    """
    Orchestrates the entire analysis process for clustering runs, including
    data retrieval, clustering, overview generation, evaluation, and summarization.
    """

    def __init__(
        self,
        vector_repository: PineconeVectorRepository,
        clustering_engine: ClusteringEngine,
        overview_generator: ClusterOverviewGenerator,
        cluster_evaluator: ClusterEvaluator,
        starters_generator: ConversationStartersGenerator,
        clustering_summarizer: ClusteringAnalysisSummarizer,
    ):
        self.vector_repository = vector_repository
        self.clustering_engine = clustering_engine
        self.overview_generator = overview_generator
        self.evaluator = cluster_evaluator
        self.starters_generator = starters_generator
        self.clustering_analysis_summarizer = clustering_summarizer

    async def handle_run(self, run: AnalysisRun) -> AnalysisRun:
        """
        Handles a run based on its analysis type.
        """

        match run.analysis_type:
            case "clustering":
                return await self.handle_clustering_run(run)
            case "report":
                return await self.handle_report_run(run)

        raise ValueError(f"Unknown analysis type: {run.analysis_type}")

    async def handle_report_run(self, run: AnalysisRun) -> AnalysisRun:
        """
        Processes a report run from start to finish.
        """

        # check run type
        if run.analysis_type != "report":
            raise ValueError(f"Run {run.id} is not a report run")

        raise NotImplementedError("Report runs are not implemented yet")

    async def handle_clustering_run(self, run: AnalysisRun) -> AnalysisRun:
        """
        Processes a clustering run from start to finish.

        Performs the following steps:
        1. Retrieves articles and their vector representations
        2. Executes clustering
        3. Generates cluster overviews
        4. Evaluates clusters
        5. Generates conversation starters and session summary

        Handles exceptions and updates session status accordingly.

        Args:
            run (AnalysisRun): The run to be processed.

        Returns:
            AnalysisRun: The updated run after processing.

        Raises:
            ValueError: If the run is not a clustering run.
        """

        if run.analysis_type != "clustering":
            raise ValueError(f"Run {run.id} is not a clustering run")

        try:
            assert run.status in [
                Status.pending,
                Status.running,
            ]  # Session can already be set to be running to avoid multiple processing

            if run.status == Status.pending:
                run.status = Status.running

            run.session_start = datetime.now()

            await run.save()

            logger.info(f"Handling clustering run '{run.id}'")

            workspace = await Workspace.get(run.workspace_id)
            if not workspace:
                raise ValueError("Workspace not found")

            all_articles = await Article.find(
                Article.workspace_id == run.workspace_id,
                Article.date >= run.data_start,
                Article.date <= run.data_end,
            ).to_list()

            logger.info(f"Found {len(all_articles)} articles.")

            if len(all_articles) > 10_000:
                logger.warning("High number of articles!")

            if not all_articles:
                raise ValueError("No articles found.")

            if len(all_articles) < analyzer_settings.MIN_ARTICLES_FOR_CLUSTERING:
                raise ValueError("Not enough articles to cluster.")

            vectors = self.vector_repository.fetch_vectors(
                [id_to_str(article.id) for article in all_articles],
                namespace=id_to_str(run.workspace_id),
            )

            data_loading_time_s = (datetime.now() - run.session_start).total_seconds()

            logger.info(f"Fetched {len(vectors)} vectors.")

            clustering_result = self.clustering_engine.perform_clustering(
                vectors, hdbscan_settings=workspace.hdbscan_settings
            )

            logger.info(
                f"Clustering finished. Found {len(clustering_result.clusters)} clusters."
            )

            run.result = ClusteringAnalysisResult(
                articles_count=len(all_articles),
                clusters_count=len(clustering_result.clusters),
                noise_articles_ids=[
                    PydanticObjectId(article.id) for article in clustering_result.noise
                ],
                noise_articles_count=len(clustering_result.noise),
                clustered_articles_count=sum(
                    len(cluster.articles) for cluster in clustering_result.clusters
                ),
                data_loading_time_s=data_loading_time_s,
                clustering_time_s=clustering_result.clustering_duration_s,
            )

            await run.save()

            assert run.id

            # Create clusters
            clusters = []
            for cluster_result in clustering_result.clusters:
                articles_ids = [
                    PydanticObjectId(article.id) for article in cluster_result.articles
                ]
                cluster: Cluster = await Cluster(
                    workspace_id=run.workspace_id,
                    session_id=run.id,
                    articles_ids=articles_ids,
                    articles_count=len(cluster_result.articles),
                    first_image=await get_first_valid_image(
                        [
                            article
                            for article in all_articles
                            if article.id in articles_ids
                        ]
                    ),
                ).insert()
                clusters.append(cluster)

            logger.info(f"Generating overviews for {len(clusters)} clusters.")
            await self.overview_generator.generate_overviews_for_clustering_run(run)

            logger.info(f"Evaluating {len(clusters)} clusters.")
            await self.evaluator.evaluate_clustering_run(run)

            await self.update_relevancy_counts(run)

            await asyncio.gather(
                self.starters_generator.generate_starters_for_workspace(workspace),
                self.clustering_analysis_summarizer.generate_summary_for_clustering_run(
                    run
                ),
            )

            logger.info(
                f"Clustering run '{run.id}' finished. Found {run.result.clusters_count} clusters."
            )

            run.status = Status.completed
            run.session_end = datetime.now()
            await run.save()

        except Exception as e:
            logger.exception(f"Error handling clustering run: {e}")
            run.status = Status.failed
            run.error = str(e)
            run.session_end = datetime.now()
            await run.save()

        return run

    async def update_relevancy_counts(self, run: AnalysisRun):
        """
        Updates the relevancy counts for a clustering run based on cluster evaluations.

        Calculates and sets the counts for highly relevant, somewhat relevant, and irrelevant
        clusters in the session.

        Args:
            run (AnalysisRun): The run to update.

        Raises:
            ValueError: If the run is not a clustering run or has no result.
        """

        if run.analysis_type != "clustering":
            raise ValueError(f"Run {run.id} is not a clustering run")

        if not run.result:
            raise ValueError(f"Run {run.id} has no result")

        assert isinstance(run.result, ClusteringAnalysisResult)

        evaluated_clusters = await Cluster.find(
            Cluster.session_id == run.id,
            Exists(Cluster.evaluation),
            Cluster.evaluation != None,  # noqa: E711
        ).to_list()

        evaluations: list[ClusterEvaluation] = [
            cluster.evaluation for cluster in evaluated_clusters if cluster.evaluation
        ]

        relevant_clusters_count = len(
            [
                evaluation
                for evaluation in evaluations
                if evaluation.relevance_level == "highly_relevant"
            ]
        )
        somewhat_relevant_clusters_count = len(
            [
                evaluation
                for evaluation in evaluations
                if evaluation.relevance_level == "somewhat_relevant"
            ]
        )
        irrelevant_clusters_count = len(
            [
                evaluation
                for evaluation in evaluations
                if evaluation.relevance_level == "not_relevant"
            ]
        )

        assert (
            relevant_clusters_count
            + somewhat_relevant_clusters_count
            + irrelevant_clusters_count
            == len(evaluations)
        )

        assert isinstance(run.result, ClusteringAnalysisResult)

        evaluation = ClusteringRunEvaluationResult(
            relevant_clusters_count=relevant_clusters_count,
            somewhat_relevant_clusters_count=somewhat_relevant_clusters_count,
            irrelevant_clusters_count=irrelevant_clusters_count,
        )

        run.result.evaluation = evaluation

        logger.info(
            f"Updated relevancy counts for clustering run '{run.id}'. Evaluation: {evaluation}"
        )

        await run.save()
