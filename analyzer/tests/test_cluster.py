import pytest
from src.clustering_engine import ClusterResult
from src.vector_repository import ArticleEmbedding


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
