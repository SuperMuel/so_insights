import asyncio
from typing import Any

from src.article_evaluator import ArticleEvaluator
from src.analyzer_agent.graph import graph
import logging
from shared.models import (
    AnalysisRun,
    AnalysisType,
    Cluster,
    ClusterEvaluation,
    ClusteringAnalysisResult,
    ClusteringRunEvaluationResult,
    AgenticAnalysisResult,
    Workspace,
)

from src.analyzer_agent.state import AgenticTopicsState, StateInput
from src.analyzer_settings import analyzer_settings
from datetime import datetime, timezone


from beanie import BulkWriter, PydanticObjectId
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


async def _fetch_articles_from_date_range(
    workspace_id: PydanticObjectId, data_start: datetime, data_end: datetime
) -> list[Article]:
    return await Article.find(
        Article.workspace_id == workspace_id,
        Article.date >= data_start,
        Article.date <= data_end,
    ).to_list()


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
        article_evaluator: ArticleEvaluator,
        cluster_evaluator: ClusterEvaluator,
        starters_generator: ConversationStartersGenerator,
        clustering_summarizer: ClusteringAnalysisSummarizer,
    ):
        self.vector_repository = vector_repository
        self.clustering_engine = clustering_engine
        self.overview_generator = overview_generator
        self.article_evaluator = article_evaluator
        self.cluster_evaluator = cluster_evaluator
        self.starters_generator = starters_generator
        self.clustering_analysis_summarizer = clustering_summarizer

    async def handle_run(self, run: AnalysisRun) -> AnalysisRun:
        """
        Handles a run based on its analysis type.
        """

        match run.analysis_type:
            case AnalysisType.CLUSTERING:
                return await self.handle_clustering_run(run)
            case AnalysisType.AGENTIC:
                return await self.handle_agentic_run(run)

        raise ValueError(f"Unknown analysis type: {run.analysis_type}")

    async def _evaluate_articles_if_needed(
        self, articles: list[Article]
    ) -> list[Article]:
        """
        Evaluates articles that don't have an evaluation yet. Saves the evaluations in the database and returns the updated articles.

        Args:
            articles: List of articles to evaluate if needed

        Returns:
            The input list of articles, with evaluations added where needed
        """
        not_evaluated = [article for article in articles if not article.evaluation]

        if not not_evaluated:
            logger.info("No articles to evaluate")
            return articles

        assert (
            len(set(article.workspace_id for article in not_evaluated)) == 1
        ), "All articles must be from the same workspace"

        workspace = await Workspace.get(articles[0].workspace_id)
        if not workspace:
            raise ValueError("Workspace not found")

        logger.info(f"Evaluating {len(not_evaluated)} articles")

        evaluations = await self.article_evaluator.evaluate_articles(
            not_evaluated, workspace.description
        )

        # Update articles with their evaluations
        async with BulkWriter() as bulk_writer:
            for article, evaluation in zip(not_evaluated, evaluations):
                article.evaluation = evaluation
                await article.save(bulk_writer=bulk_writer)

        # Create a mapping of updated articles
        article_map = {article.id: article for article in articles}
        for article in not_evaluated:
            article_map[article.id] = article

        logger.info(f"Updated {len(not_evaluated)} articles with evaluations")

        # Return list with updated articles in original order
        return [article_map[article.id] for article in articles]

    async def _assign_first_images_to_topics(
        self, topics: list[Any], relevant_articles: list[Article]
    ) -> None:
        """
        Given a list of topics and relevant articles, concurrently fetches the first valid image for
        each topic based on the articles associated to it and assigns it to the topic.

        Args:
            topics: List of topics each having an `articles_ids` attribute.
            relevant_articles: List of articles to search for a valid image.
        """
        logger.info(f"Assigning first images to {len(topics)} topics")
        topics_with_no_image = [topic for topic in topics if not topic.first_image]
        logger.info(f"Assigning first images to {len(topics_with_no_image)} topics")

        image_tasks = [
            get_first_valid_image(
                [
                    article
                    for article in relevant_articles
                    if article.id in topic.articles_ids
                ]
            )
            for topic in topics_with_no_image
        ]
        first_images = await asyncio.gather(*image_tasks)

        for topic, first_image in zip(topics_with_no_image, first_images):
            if first_image:
                topic.first_image = first_image

        found_images = [
            first_image for first_image in first_images if first_image is not None
        ]
        logger.info(f"Found {len(found_images)} images")

    async def handle_agentic_run(self, run: AnalysisRun) -> AnalysisRun:
        """
        Processes an agentic run from start to finish.

        Performs the following steps:
        1. Validates run type and state
        2. Retrieves workspace and articles
        3. Generates topics using LangGraph
        4. Updates run status and result

        Args:
            run (AnalysisRun): The run to be processed.

        Returns:
            AnalysisRun: The updated run after processing.

        Raises:
            ValueError: If the run is not a report run or workspace not found.
        """
        if run.analysis_type != AnalysisType.AGENTIC:
            raise ValueError(f"Run {run.id} is not an agentic run")

        logger.info(f"Handling agentic run '{run.id}'")
        try:
            assert run.status in [Status.pending, Status.running]

            if run.status == Status.pending:
                run.status = Status.running

            run.session_start = datetime.now(tz=timezone.utc)
            await run.save()

            workspace = await Workspace.get(run.workspace_id)
            if not workspace:
                raise ValueError("Workspace not found")

            articles = await _fetch_articles_from_date_range(
                run.workspace_id, run.data_start, run.data_end
            )

            if not articles:
                raise ValueError("No articles found.")

            logger.info(f"Found {len(articles)} articles.")

            articles = await self._evaluate_articles_if_needed(articles)

            assert all(article.evaluation for article in articles)

            relevant_articles = [
                article
                for article in articles
                if article.evaluation
                and (
                    article.evaluation.relevance_level == "relevant"
                    or article.evaluation.relevance_level == "somewhat_relevant"
                )
            ]

            if not relevant_articles:
                raise ValueError("No relevant articles found")

            logger.info(f"Found {len(relevant_articles)} relevant articles")

            input: StateInput = {
                "articles": relevant_articles,
                "articles_ids": [
                    str(article.id) for article in relevant_articles if article.id
                ],
                "workspace_description": workspace.description,
                "language": workspace.language,
            }

            result_dict: AgenticTopicsState = await graph.ainvoke(input)  # type: ignore
            topics = result_dict["topics"]

            await self._assign_first_images_to_topics(topics, relevant_articles)

            # Generate a summary
            relevant_articles_ids = [
                article.id for article in relevant_articles if article.id
            ]
            assert len(relevant_articles_ids) == len(relevant_articles)

            result = AgenticAnalysisResult(
                topics=topics,
                summary=result_dict["summary"],
                relevant_articles_ids=relevant_articles_ids,
            )

            run.result = result
            run.status = Status.completed
            run.session_end = datetime.now(tz=timezone.utc)
            await run.save()

            logger.info(f"Report run '{run.id}' finished successfully.")

            try:
                await self.starters_generator.generate_new_conversation_starters(
                    workspace, run
                )
            except Exception as e:
                logger.exception(
                    f"Error generating conversation starters for report run {run.id}",
                    exc_info=e,
                )

        except Exception as e:
            logger.exception(f"Error handling report run: {e}")
            run.status = Status.failed
            run.error = str(e)
            run.session_end = datetime.now(tz=timezone.utc)
            await run.save()

        return run

    async def handle_clustering_run(self, run: AnalysisRun) -> AnalysisRun:
        """
        Processes a clustering run from start to finish.

        Performs the following steps:
        1. Retrieves articles and their vector representations
        2. Executes clustering
        3. Generates cluster overviews
        4. Evaluates clusters
        5. Generates conversation starters and clustering summary

        Handles exceptions and updates clustering status accordingly.

        Args:
            run (AnalysisRun): The run to be processed.

        Returns:
            AnalysisRun: The updated run after processing.

        Raises:
            ValueError: If the run is not a clustering run.
        """

        if run.analysis_type != AnalysisType.CLUSTERING:
            raise ValueError(f"Run {run.id} is not a clustering run")

        try:
            assert run.status in [
                Status.pending,
                Status.running,
            ]  # Run can already be set to be running to avoid multiple processing

            if run.status == Status.pending:
                run.status = Status.running

            run.session_start = datetime.now(tz=timezone.utc)

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

            data_loading_time_s = (
                datetime.now(tz=timezone.utc) - run.session_start
            ).total_seconds()

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
            await self.cluster_evaluator.evaluate_clustering_run(run)

            await self.update_relevancy_counts(run)

            try:
                await asyncio.gather(
                    self.starters_generator.generate_new_conversation_starters(
                        workspace, run
                    ),
                    self.clustering_analysis_summarizer.generate_summary_for_clustering_run(
                        run
                    ),
                )
            except Exception as e:
                logger.exception(
                    f"Error generating conversation starters or summary for clustering run {run.id}",
                    exc_info=e,
                )

            logger.info(
                f"Clustering run '{run.id}' finished. Found {run.result.clusters_count} clusters."
            )

            run.status = Status.completed
            run.session_end = datetime.now(tz=timezone.utc)
            await run.save()

        except Exception as e:
            logger.exception(f"Error handling clustering run: {e}")
            run.status = Status.failed
            run.error = str(e)
            run.session_end = datetime.now(tz=timezone.utc)
            await run.save()

        return run

    async def update_relevancy_counts(self, run: AnalysisRun):
        """
        Updates the relevancy counts for a clustering run based on cluster evaluations.

        Calculates and sets the counts for highly relevant, somewhat relevant, and irrelevant
        clusters in the clustering run.

        Args:
            run (AnalysisRun): The run to update.

        Raises:
            ValueError: If the run is not a clustering run or has no result.
        """

        if run.analysis_type != AnalysisType.CLUSTERING:
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
