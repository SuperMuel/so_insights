from pydantic import ValidationError
import pytest
from beanie import init_beanie
from mongomock_motor import AsyncMongoMockClient
from make_it_sync import make_sync
from shared.models import Cluster, ClusterEvaluation


@pytest.fixture(autouse=True)
def my_fixture():
    client = AsyncMongoMockClient()

    make_sync(init_beanie)(
        document_models=[Cluster],
        database=client.get_database(name="db"),  # type:ignore
    )
    yield


def test_cluster_evaluation_valid_relevant():
    evaluation = ClusterEvaluation(
        justification="This cluster is relevant.",
        relevance_level="highly_relevant",
        confidence_score=0.9,
    )
    assert evaluation.justification == "This cluster is relevant."
    assert evaluation.relevance_level == "highly_relevant"
    assert evaluation.confidence_score == 0.9


def test_confidence_score_between_0_and_1():
    with pytest.raises(ValidationError):
        ClusterEvaluation(
            justification="This should fail.",
            relevance_level="highly_relevant",
            confidence_score=1.1,
        )
