from unittest.mock import MagicMock
from src.vector_repository import PineconeVectorRepository, ArticleEmbedding


def test_fetch_vectors():
    # Mock the GRPCIndex
    mock_index = MagicMock()

    # Sample data
    ids = ["id1", "id2", "id3"]
    namespace = "test_namespace"
    mock_response = {
        "vectors": {
            "id1": {"id": "id1", "values": [0.1, 0.2, 0.3]},
            "id2": {"id": "id2", "values": [0.4, 0.5, 0.6]},
            "id3": {"id": "id3", "values": [0.7, 0.8, 0.9]},
        }
    }

    # Configure the mock to return the sample data
    mock_index.fetch.return_value = mock_response

    # Create an instance of PineconeVectorRepository with the mock index
    repository = PineconeVectorRepository(mock_index)

    # Call the method under test
    result = repository.fetch_vectors(ids, namespace)

    # Expected result
    expected_result = [
        ArticleEmbedding(id="id1", embedding=[0.1, 0.2, 0.3]),
        ArticleEmbedding(id="id2", embedding=[0.4, 0.5, 0.6]),
        ArticleEmbedding(id="id3", embedding=[0.7, 0.8, 0.9]),
    ]

    # Assertions
    assert result == expected_result
    mock_index.fetch.assert_called_with(ids, namespace=namespace)


def test_fetch_vectors_with_batches():
    mock_index = MagicMock()

    # Create 1500 IDs to ensure at least one full batch and one partial batch
    ids = [f"id{i}" for i in range(1500)]
    namespace = "test_namespace"

    def mock_fetch(batch_ids, namespace):
        return {
            "vectors": {
                id: {"id": id, "values": [float(id[2:])] * 3} for id in batch_ids
            }
        }

    mock_index.fetch.side_effect = mock_fetch

    repository = PineconeVectorRepository(mock_index)
    result = repository.fetch_vectors(ids, namespace)

    # Verify results
    assert len(result) == 1500
    assert all(isinstance(item, ArticleEmbedding) for item in result)
    assert result[0] == ArticleEmbedding(id="id0", embedding=[0.0, 0.0, 0.0])
    assert result[-1] == ArticleEmbedding(
        id="id1499", embedding=[1499.0, 1499.0, 1499.0]
    )

    # Verify batching
    assert mock_index.fetch.call_count == 2
    mock_index.fetch.assert_any_call(ids[:1000], namespace=namespace)
    mock_index.fetch.assert_any_call(ids[1000:], namespace=namespace)
