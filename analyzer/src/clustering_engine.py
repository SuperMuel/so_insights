import logging
from collections import defaultdict
from datetime import UTC, datetime
from typing import Self

from src.vector_repository import ArticleEmbedding
import hdbscan
import numpy as np
from pydantic import BaseModel, Field, model_validator
from sklearn.metrics.pairwise import euclidean_distances
from shared.models import HdbscanSettings

logger = logging.getLogger(__name__)


class ClusterResult(BaseModel):
    """
    Represents the result of a single cluster in the clustering process.

    Attributes:
        id (int): Unique identifier for the cluster.
        center (list[float]): The centroid of the cluster.
        articles (list[ArticleEmbedding]): Articles in the cluster, sorted by distance to the center.
    """

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

    @model_validator(mode="after")
    def validate_embedding_dimensions(self) -> Self:
        if not self.articles:
            raise ValueError("A cluster must contain at least one article")

        center_dim = len(self.center)
        for article in self.articles:
            if len(article.embedding) != center_dim:
                raise ValueError(
                    f"Mismatched embedding dimensions. Expected {center_dim}, got {len(article.embedding)}"
                )

        return self


class ClusteringResult(BaseModel):
    """
    Represents the overall result of the clustering process.

    Attributes:
        clusters (list[ClusterResult]): List of clusters found, sorted by size in descending order.
        noise (list[ArticleEmbedding]): List of articles not assigned to any cluster.
        clustering_duration_s (float): Duration of the clustering process in seconds.
    """

    clusters: list[ClusterResult]
    noise: list[ArticleEmbedding]
    clustering_duration_s: float = Field(
        ..., description="Duration of clustering in seconds", ge=0
    )

    @model_validator(mode="after")
    def sort_clusters(self) -> Self:
        self.clusters.sort(key=lambda cluster: len(cluster.articles), reverse=True)
        return self


class ClusteringEngine:
    """
    Handles the clustering process for articles using the HDBSCAN algorithm.
    """

    def _get_hdbscan(self, hdbscan_settings: HdbscanSettings) -> hdbscan.HDBSCAN:
        return hdbscan.HDBSCAN(
            **hdbscan_settings.model_dump(exclude_none=True, exclude_unset=True)
        )

    @staticmethod
    def get_cluster_center(points: np.ndarray) -> np.ndarray:
        """
        Calculates the center of a cluster given its points.

        Args:
            points (np.ndarray): Array of points in the cluster.

        Returns:
            np.ndarray: The center point of the cluster.
        """

        return np.mean(points, axis=0)

    @staticmethod
    def get_closest_points(
        points: np.ndarray, center: np.ndarray, n: int = 5
    ) -> list[int]:
        """
        Finds the indices of the n closest points to a given center.

        Args:
            points (np.ndarray): Array of points to search.
            center (np.ndarray): The center point to measure distance from.
            n (int, optional): Number of closest points to return.

        Returns:
            list[int]: Indices of the n closest points.
        """

        distances = euclidean_distances([center], points)[0]  # type:ignore
        return np.argsort(distances)[:n].tolist()

    def perform_clustering(
        self,
        articles: list[ArticleEmbedding],
        hdbscan_settings: HdbscanSettings,
    ) -> ClusteringResult:
        """
        Performs clustering on the given articles using HDBSCAN.

        Args:
            articles (list[ArticleEmbedding]): List of articles to cluster.
            hdbscan_settings (HdbscanSettings): Configuration for the HDBSCAN algorithm.

        Returns:
            ClusteringResult: The result of the clustering process, including clusters and noise.
        """

        logger.info("Performing clustering...")
        matrix = np.array([article.embedding for article in articles])

        start_time = datetime.now(UTC)
        cluster_labels = self._get_hdbscan(hdbscan_settings).fit_predict(matrix)
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
