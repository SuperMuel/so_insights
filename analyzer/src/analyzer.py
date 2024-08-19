from datetime import datetime

from beanie import PydanticObjectId
from pydantic import HttpUrl
from shared.models import Article, Cluster, ClusteringSession, Workspace

import logging

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
    ):
        self.vector_repository = vector_repository
        self.clustering_engine = clustering_engine
        self.overview_generator = overview_generator

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

        for cluster_result in clustering_result.clusters:  # TODO : parallelize
            articles_ids = [
                PydanticObjectId(article.id) for article in cluster_result.articles
            ]
            cluster: Cluster = await Cluster(
                workspace_id=workspace.id,
                session_id=session.id,
                articles_ids=articles_ids,
                articles_count=len(cluster_result.articles),
                first_image=await get_first_image(
                    [article for article in all_articles if article.id in articles_ids]
                ),
            ).insert()

            try:
                logger.info(f"Generating overview for cluster {cluster.id}")
                overview = await self.overview_generator.generate_overview(
                    cluster=cluster
                )
                cluster.title = overview.title
                cluster.summary = overview.summary
            except Exception as e:
                logger.error(
                    f"Failed to generate overview for cluster {cluster.id}: {e}"
                )
                cluster.overview_generation_error = str(e)
            await cluster.save()

        logger.info(
            f"Clustering session '{session.id}' finished. Found {session.clusters_count} clusters."
        )


async def get_first_image(articles: list[Article]) -> HttpUrl | None:
    for article in articles:
        if article.image:
            return article.image
    return None
