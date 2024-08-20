from datetime import datetime
import aiohttp


from beanie import PydanticObjectId
from pydantic import HttpUrl
from shared.models import Article, Cluster, ClusteringSession, Workspace

import logging

from src.evaluator import ClusterEvaluator
from src.cluster_overview_generator import ClusterOverviewGenerator
from src.clustering_engine import ClusteringEngine
from src.vector_repository import PineconeVectorRepository

logger = logging.getLogger(__name__)


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
    ):
        self.vector_repository = vector_repository
        self.clustering_engine = clustering_engine
        self.overview_generator = overview_generator
        self.evaluator = cluster_evaluator

    async def analyse(
        self, workspace: Workspace, data_start: datetime, data_end: datetime
    ):
        session_start = datetime.now()
        assert workspace.id
        logger.info(
            f"Analyzing workspace '{workspace.name}' on period {data_start} -> {data_end}"
        )

        all_articles = await Article.find(
            Article.workspace_id == workspace.id,
            Article.date >= data_start,
            Article.date <= data_end,
        ).to_list()

        logger.info(f"Found {len(all_articles)} articles.")

        if len(all_articles) > 10_000:
            logger.warn("High number of articles !")

        if not all_articles:
            logger.warn("No articles found. Skipping clustering. No session created.")
            return

        vectors = self.vector_repository.fetch_vectors(
            [id_to_str(article.id) for article in all_articles],
            namespace=id_to_str(workspace.id),
        )

        data_loading_time_s = (datetime.now() - session_start).total_seconds()

        logger.info(f"Fetched {len(vectors)} vectors.")

        clustering_result = self.clustering_engine.perform_clustering(vectors)

        logger.info(
            f"Clustering finished. Found {len(clustering_result.clusters)} clusters."
        )

        session: ClusteringSession = await ClusteringSession(
            session_start=session_start,
            session_end=datetime.now(),
            workspace_id=workspace.id,
            data_start=data_start,
            data_end=data_end,
            articles_count=len(all_articles),
            clusters_count=len(clustering_result.clusters),
            noise_articles_ids=[
                PydanticObjectId(article.id) for article in clustering_result.noise
            ],
            noise_articles_count=len(clustering_result.noise),
            clustered_articles_count=sum(
                len(cluster.articles) for cluster in clustering_result.clusters
            ),
            metadata={
                "algorithm": "hdbscan",
                "min_cluster_size": self.clustering_engine.min_cluster_size,
                "min_samples": self.clustering_engine.min_samples,
                "data_loading_time_s": data_loading_time_s,
                "clustering_time_s": clustering_result.clustering_duration_s,
            },
        ).insert()

        assert session.id

        clusters = []

        for cluster_result in clustering_result.clusters:
            articles_ids = [
                PydanticObjectId(article.id) for article in cluster_result.articles
            ]
            cluster: Cluster = await Cluster(
                workspace_id=workspace.id,
                session_id=session.id,
                articles_ids=articles_ids,
                articles_count=len(cluster_result.articles),
                first_image=await get_first_valid_image(
                    [article for article in all_articles if article.id in articles_ids]
                ),
            ).insert()

            clusters.append(cluster)

        logger.info(f"Generating overviews for {len(clusters)} clusters.")
        await self.overview_generator.generate_overviews_for_session(session)

        logger.info(f"Evaluating {len(clusters)} clusters.")

        await self.evaluator.evaluate_session(session)

        logger.info(
            f"Clustering session '{session.id}' finished. Found {session.clusters_count} clusters."
        )


async def get_first_valid_image(articles: list[Article]) -> HttpUrl | None:
    timeout = aiohttp.ClientTimeout(total=5)  # 5 seconds timeout for the entire request
    async with aiohttp.ClientSession(timeout=timeout) as session:
        for article in articles:
            if not article.image:
                continue
            try:
                async with session.head(str(article.image)) as response:
                    if response.status == 200:
                        content_type = response.headers.get("Content-Type", "")
                        if content_type.startswith("image/"):
                            return article.image
            except aiohttp.ClientError:
                continue  # Move to the next article if there's an error
    return None
