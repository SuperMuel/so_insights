import logging
from collections import defaultdict
from datetime import UTC, datetime
from typing import Self

from src.vector_repository import ArticleEmbedding
import hdbscan
import numpy as np
from pydantic import BaseModel, Field, model_validator
from sklearn.metrics.pairwise import euclidean_distances

logger = logging.getLogger(__name__)


class ClusterResult(BaseModel):
    id: int
    center: list[float]
    articles: list[ArticleEmbedding] = Field(
        ...,
        description="Articles in the cluster sorted by their distance to the cluster center",
    )

    @model_validator(mode="after")
    def sort_articles(self) -> Self:
        if not self.articles:
            raise ValueError("A cluster must contain at least one article")

        center = np.array(self.center)
        embeddings = np.array([article.embedding for article in self.articles])
        distances = euclidean_distances([center], embeddings)[0]  # type:ignore
        sorted_indices = np.argsort(distances)
        self.articles = [self.articles[i] for i in sorted_indices]

        return self


class ClusteringResult(BaseModel):
    clusters: list[ClusterResult]
    noise: list[ArticleEmbedding]
    clustering_duration_s: float = Field(
        ..., description="Duration of clustering in seconds"
    )


class ClusteringEngine:
    def __init__(self, min_cluster_size: int, min_samples: int):
        self.min_cluster_size = min_cluster_size
        self.min_samples = min_samples

        self.clusterer = hdbscan.HDBSCAN(
            min_cluster_size=self.min_cluster_size,
            min_samples=self.min_samples,
        )

    @staticmethod
    def get_cluster_center(points: np.ndarray) -> np.ndarray:
        return np.mean(points, axis=0)

    @staticmethod
    def get_closest_points(
        points: np.ndarray, center: np.ndarray, n: int = 5
    ) -> list[int]:
        distances = euclidean_distances([center], points)[0]  # type:ignore
        return np.argsort(distances)[:n].tolist()

    def perform_clustering(self, articles: list[ArticleEmbedding]) -> ClusteringResult:
        logger.info("Performing clustering...")
        matrix = np.array([article.embedding for article in articles])

        start_time = datetime.now(UTC)
        cluster_labels = self.clusterer.fit_predict(matrix)
        end_time = datetime.now(UTC)

        logger.info(
            f"Clustering completed in {(end_time - start_time).total_seconds():.2f} seconds"
        )

        clusters_dict: dict[int, list[ArticleEmbedding]] = defaultdict(list)
        noise_articles: list[ArticleEmbedding] = []

        for article, label in zip(articles, cluster_labels):
            if label == -1:
                noise_articles.append(article)
            else:
                clusters_dict[label].append(article)

        clusters: list[ClusterResult] = []

        for cluster_id, cluster_articles in clusters_dict.items():
            cluster_embeddings = np.array(
                [article.embedding for article in cluster_articles]
            )
            center = self.get_cluster_center(cluster_embeddings)

            clusters.append(
                ClusterResult(
                    id=cluster_id, center=center.tolist(), articles=cluster_articles
                )
            )

        return ClusteringResult(
            clusters=clusters,
            noise=noise_articles,
            clustering_duration_s=(end_time - start_time).total_seconds(),
        )