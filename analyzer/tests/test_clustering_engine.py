from unittest.mock import patch
import numpy as np
from pydantic import ValidationError
import pytest
from shared.models import HdbscanSettings
from src.clustering_engine import ClusterResult, ClusteringEngine, ClusteringResult
from src.vector_repository import ArticleEmbedding


### Cluster result


def test_cluster_result_with_mismatched_embedding_dimensions():
    center = [0.1, 0.2, 0.3]
    articles = [
        ArticleEmbedding(id="1", embedding=[0.1, 0.2]),
        ArticleEmbedding(id="2", embedding=[0.4, 0.5]),
        ArticleEmbedding(id="3", embedding=[0.7, 0.8, 0.9]),  # Mismatched dimension
    ]

    # Assert that ValidationError is raised
    with pytest.raises(expected_exception=ValidationError):
        ClusterResult(id=1, center=center, articles=articles)


def test_cluster_validation_sorted():
    center = [0.0, 0.0, 0.0]
    articles = [
        ArticleEmbedding(id="1", embedding=[1.0, 1.0, 1.0]),
        ArticleEmbedding(id="2", embedding=[2.0, 2.0, 2.0]),
        ArticleEmbedding(id="3", embedding=[3.0, 3.0, 3.0]),
    ]

    cluster = ClusterResult(id=0, center=center, articles=articles)
    assert len(cluster.articles) == 3
    assert [a.id for a in cluster.articles] == ["1", "2", "3"]


def test_cluster_validation_unsorted():
    center = [0.0, 0.0, 0.0]
    articles = [
        ArticleEmbedding(id="3", embedding=[3.0, 3.0, 3.0]),
        ArticleEmbedding(id="1", embedding=[1.0, 1.0, 1.0]),
        ArticleEmbedding(id="2", embedding=[2.0, 2.0, 2.0]),
    ]

    cluster = ClusterResult(id=0, center=center, articles=articles)
    assert len(cluster.articles) == 3
    assert [a.id for a in cluster.articles] == ["1", "2", "3"]


def test_cluster_validation_empty():
    center = [0.0, 0.0, 0.0]
    articles = []

    with pytest.raises(ValueError) as exc_info:
        ClusterResult(id=0, center=center, articles=articles)

    assert "A cluster must contain at least one article" in str(exc_info.value)


def test_cluster_validation_single_article():
    center = [0.0, 0.0, 0.0]
    articles = [ArticleEmbedding(id="1", embedding=[1.0, 1.0, 1.0])]

    cluster = ClusterResult(id=0, center=center, articles=articles)
    assert len(cluster.articles) == 1
    assert cluster.articles[0].id == "1"


def test_cluster_validation_same_distance():
    center = [0.0, 0.0, 0.0]
    articles = [
        ArticleEmbedding(id="1", embedding=[1.0, 1.0, 1.0]),
        ArticleEmbedding(id="2", embedding=[1.0, 1.0, 1.0]),
        ArticleEmbedding(id="3", embedding=[1.0, 1.0, 1.0]),
    ]

    cluster = ClusterResult(id=0, center=center, articles=articles)
    assert len(cluster.articles) == 3
    assert set(a.id for a in cluster.articles) == {"1", "2", "3"}


def test_cluster_validation_mixed_distances():
    center = [0.0, 0.0, 0.0]
    articles = [
        ArticleEmbedding(id="3", embedding=[3.0, 3.0, 3.0]),
        ArticleEmbedding(id="1", embedding=[1.0, 1.0, 1.0]),
        ArticleEmbedding(id="4", embedding=[4.0, 4.0, 4.0]),
        ArticleEmbedding(id="2", embedding=[2.0, 2.0, 2.0]),
    ]

    cluster = ClusterResult(id=0, center=center, articles=articles)
    assert len(cluster.articles) == 4
    assert [a.id for a in cluster.articles] == ["1", "2", "3", "4"]


### ClusteringResult


def test_clustering_result_valid():
    clusters = [
        ClusterResult(
            id=1,
            center=[0.1, 0.2, 0.3],
            articles=[
                ArticleEmbedding(id="1", embedding=[0.1, 0.2, 0.3]),
                ArticleEmbedding(id="2", embedding=[0.4, 0.5, 0.6]),
            ],
        ),
        ClusterResult(
            id=2,
            center=[0.7, 0.8, 0.9],
            articles=[ArticleEmbedding(id="3", embedding=[0.7, 0.8, 0.9])],
        ),
    ]
    noise = [ArticleEmbedding(id="4", embedding=[1.0, 1.1, 1.2])]

    # Create ClusteringResult
    result = ClusteringResult(clusters=clusters, noise=noise, clustering_duration_s=1.5)

    # Assert
    assert len(result.clusters) == 2
    assert len(result.noise) == 1
    assert result.clustering_duration_s == 1.5


def test_clustering_result_sorts_clusters():
    # Prepare test data with unsorted clusters
    clusters = [
        ClusterResult(
            id=1,
            center=[0.1, 0.2, 0.3],
            articles=[ArticleEmbedding(id="1", embedding=[0.1, 0.2, 0.3])],
        ),
        ClusterResult(
            id=2,
            center=[0.7, 0.8, 0.9],
            articles=[
                ArticleEmbedding(id="2", embedding=[0.7, 0.8, 0.9]),
                ArticleEmbedding(id="3", embedding=[0.4, 0.5, 0.6]),
                ArticleEmbedding(id="4", embedding=[1.0, 1.1, 1.2]),
            ],
        ),
    ]

    # Create ClusteringResult
    result = ClusteringResult(clusters=clusters, noise=[], clustering_duration_s=1.5)

    # Assert that clusters are sorted by size in descending order
    assert len(result.clusters[0].articles) > len(result.clusters[1].articles)


def test_clustering_result_empty_clusters_does_not_raise():
    # Test with empty clusters list
    clusters = []
    noise = [ArticleEmbedding(id="1", embedding=[0.1, 0.2, 0.3])]
    result = ClusteringResult(clusters=clusters, noise=noise, clustering_duration_s=1.0)

    assert len(result.clusters) == 0
    assert len(result.noise) == 1


def test_clustering_result_negative_duration():
    # Test with negative clustering duration
    clusters = [
        ClusterResult(
            id=1,
            center=[0.1, 0.2, 0.3],
            articles=[ArticleEmbedding(id="1", embedding=[0.1, 0.2, 0.3])],
        )
    ]

    with pytest.raises(ValidationError):
        ClusteringResult(clusters=clusters, noise=[], clustering_duration_s=-1.0)


def test_clustering_result_with_noise():
    # Test with noise articles
    clusters = [
        ClusterResult(
            id=1,
            center=[0.1, 0.2, 0.3],
            articles=[ArticleEmbedding(id="1", embedding=[0.1, 0.2, 0.3])],
        )
    ]
    noise = [
        ArticleEmbedding(id="2", embedding=[0.4, 0.5, 0.6]),
        ArticleEmbedding(id="3", embedding=[0.7, 0.8, 0.9]),
    ]

    result = ClusteringResult(clusters=clusters, noise=noise, clustering_duration_s=1.0)

    assert len(result.noise) == 2


@pytest.fixture
def clustering_engine():
    return ClusteringEngine()


def test_get_cluster_center():
    points = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
    center = ClusteringEngine.get_cluster_center(points)
    np.testing.assert_array_almost_equal(center, [4, 5, 6])


def test_get_closest_points():
    points = np.array([[1, 1], [2, 2], [3, 3], [4, 4], [5, 5]])
    center = np.array([3, 3])
    closest = ClusteringEngine.get_closest_points(points, center, n=3)
    assert closest == [2, 1, 3]  # Indices of the 3 closest points


def test_perform_clustering(clustering_engine):
    articles = [
        ArticleEmbedding(id="1", embedding=[0, 0]),
        ArticleEmbedding(id="2", embedding=[0.1, 0.1]),
        ArticleEmbedding(id="3", embedding=[1, 1]),
        ArticleEmbedding(id="4", embedding=[1.1, 1.1]),
        ArticleEmbedding(id="5", embedding=[0.5, 0.5]),
    ]
    hdbscan_settings = HdbscanSettings(min_cluster_size=2, min_samples=1)

    result = clustering_engine.perform_clustering(articles, hdbscan_settings)

    assert len(result.clusters) > 0
    assert isinstance(result.clustering_duration_s, float)
    assert result.clustering_duration_s > 0


def test_perform_clustering_with_noise(clustering_engine):
    articles = [
        ArticleEmbedding(id="1", embedding=[0, 0]),
        ArticleEmbedding(id="2", embedding=[0.1, 0.1]),
        ArticleEmbedding(id="3", embedding=[1, 1]),
        ArticleEmbedding(id="4", embedding=[1.1, 1.1]),
        ArticleEmbedding(id="5", embedding=[0.5, 0.5]),
        ArticleEmbedding(id="6", embedding=[10, 10]),  # Noise point
    ]
    hdbscan_settings = HdbscanSettings(min_cluster_size=2, min_samples=1)

    result = clustering_engine.perform_clustering(articles, hdbscan_settings)

    assert len(result.clusters) > 0
    assert len(result.noise) > 0


def test_perform_clustering_empty_input(clustering_engine):
    articles = []
    hdbscan_settings = HdbscanSettings(min_cluster_size=2, min_samples=1)

    with pytest.raises(expected_exception=ValueError):
        clustering_engine.perform_clustering(articles, hdbscan_settings)


def test_hdbscan_settings_passed_to_algorithm(clustering_engine):
    # Mock data for clustering
    articles = [
        ArticleEmbedding(id="1", embedding=[0.1, 0.2]),
        ArticleEmbedding(id="2", embedding=[0.3, 0.4]),
        ArticleEmbedding(id="3", embedding=[0.5, 0.6]),
    ]

    # Define custom HDBSCAN settings
    hdbscan_settings = HdbscanSettings(
        min_cluster_size=2, min_samples=1, cluster_selection_epsilon=0.1
    )

    # Patch the hdbscan.HDBSCAN constructor
    with patch("src.clustering_engine.hdbscan.HDBSCAN") as mock_hdbscan:
        # Call the perform_clustering method
        clustering_engine.perform_clustering(articles, hdbscan_settings)

        # Assert that the HDBSCAN constructor was called once with the expected settings
        mock_hdbscan.assert_called_once_with(
            min_cluster_size=2, min_samples=1, cluster_selection_epsilon=0.1
        )
