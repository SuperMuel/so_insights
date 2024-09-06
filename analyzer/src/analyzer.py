import asyncio
from datetime import datetime


from beanie import PydanticObjectId
from beanie.operators import Exists
from shared.models import (
    Article,
    Cluster,
    ClusterEvaluation,
    ClusteringSession,
    Status,
    Workspace,
)

import logging

from src.analyzer_settings import AnalyzerSettings
from src.evaluator import ClusterEvaluator
from src.cluster_overview_generator import ClusterOverviewGenerator
from src.clustering_engine import ClusteringEngine
from src.session_summary_generator import SessionSummarizer
from src.starters_generator import ConversationStartersGenerator
from src.util import get_first_valid_image
from src.vector_repository import PineconeVectorRepository

logger = logging.getLogger(__name__)

settings = AnalyzerSettings()


def id_to_str(id: PydanticObjectId | None) -> str:
    if not id:
        raise ValueError("id is None")
    return str(id)


class Analyzer:
    def __init__(
        self,
        vector_repository: PineconeVectorRepository,
        clustering_engine: ClusteringEngine,
        overview_generator: ClusterOverviewGenerator,
        cluster_evaluator: ClusterEvaluator,
        starters_generator: ConversationStartersGenerator,
        session_summarizer: SessionSummarizer,
    ):
        self.vector_repository = vector_repository
        self.clustering_engine = clustering_engine
        self.overview_generator = overview_generator
        self.evaluator = cluster_evaluator
        self.starters_generator = starters_generator
        self.session_summarizer = session_summarizer

    async def handle_session(self, session: ClusteringSession) -> ClusteringSession:
        try:
            assert session.status in [
                Status.pending,
                Status.running,
            ]  # Session can already be set to be running to avoid multiple processing

            if session.status == Status.pending:
                session.status = Status.running

            session.session_start = datetime.now()

            await session.save()

            logger.info(f"Handling clustering session '{session.id}'")

            workspace = await Workspace.get(session.workspace_id)
            if not workspace:
                raise ValueError("Workspace not found")

            all_articles = await Article.find(
                Article.workspace_id == session.workspace_id,
                Article.date >= session.data_start,
                Article.date <= session.data_end,
            ).to_list()

            logger.info(f"Found {len(all_articles)} articles.")

            if len(all_articles) > 10_000:
                logger.warning("High number of articles!")

            if not all_articles:
                raise ValueError("No articles found.")

            if len(all_articles) < settings.MIN_ARTICLES_FOR_CLUSTERING:
                raise ValueError("Not enough articles to cluster.")

            vectors = self.vector_repository.fetch_vectors(
                [id_to_str(article.id) for article in all_articles],
                namespace=id_to_str(session.workspace_id),
            )

            data_loading_time_s = (
                datetime.now() - session.session_start
            ).total_seconds()

            logger.info(f"Fetched {len(vectors)} vectors.")

            clustering_result = self.clustering_engine.perform_clustering(
                vectors, hdbscan_settings=workspace.hdbscan_settings
            )

            logger.info(
                f"Clustering finished. Found {len(clustering_result.clusters)} clusters."
            )

            session.articles_count = len(all_articles)
            session.clusters_count = len(clustering_result.clusters)
            session.noise_articles_ids = [
                PydanticObjectId(article.id) for article in clustering_result.noise
            ]
            session.noise_articles_count = len(clustering_result.noise)
            session.clustered_articles_count = sum(
                len(cluster.articles) for cluster in clustering_result.clusters
            )
            session.metadata.update(
                {
                    "algorithm": "hdbscan",
                    "min_cluster_size": workspace.hdbscan_settings.min_cluster_size,
                    "min_samples": workspace.hdbscan_settings.min_samples,
                    "data_loading_time_s": data_loading_time_s,
                    "clustering_time_s": clustering_result.clustering_duration_s,
                }
            )
            await session.save()

            assert session.id

            clusters = []
            for cluster_result in clustering_result.clusters:
                articles_ids = [
                    PydanticObjectId(article.id) for article in cluster_result.articles
                ]
                cluster: Cluster = await Cluster(
                    workspace_id=session.workspace_id,
                    session_id=session.id,
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
            await self.overview_generator.generate_overviews_for_session(session)

            logger.info(f"Evaluating {len(clusters)} clusters.")
            await self.evaluator.evaluate_session(session)

            await self.update_relevancy_counts(session)

            await asyncio.gather(
                self.starters_generator.generate_starters_for_workspace(workspace),
                self.session_summarizer.generate_summary_for_session(session),
            )

            logger.info(
                f"Clustering session '{session.id}' finished. Found {session.clusters_count} clusters."
            )

            session.status = Status.completed
            session.session_end = datetime.now()
            await session.save()

        except Exception as e:
            logger.exception(f"Error handling clustering session: {e}")
            session.status = Status.failed
            session.error = str(e)
            session.session_end = datetime.now()
            await session.save()

        return session

    async def update_relevancy_counts(self, session: ClusteringSession):
        evaluated_clusters = await Cluster.find(
            Cluster.session_id == session.id,
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

        session.relevant_clusters_count = relevant_clusters_count
        session.somewhat_relevant_clusters_count = somewhat_relevant_clusters_count
        session.irrelevant_clusters_count = irrelevant_clusters_count

        await session.save()
