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
        relevant=True,
        irrelevancy_reason=None,
    )
    assert evaluation.relevant == True  # noqa: E712
    assert evaluation.irrelevancy_reason is None


def test_cluster_evaluation_valid_irrelevant():
    evaluation = ClusterEvaluation(
        justification="This cluster is not relevant.",
        relevant=False,
        irrelevancy_reason="Off-topic content",
    )
    assert evaluation.relevant == False  # noqa: E712
    assert evaluation.irrelevancy_reason == "Off-topic content"


def test_cluster_evaluation_invalid_relevant_with_reason():
    with pytest.raises(ValidationError) as exc_info:
        ClusterEvaluation(
            justification="This should fail.",
            relevant=True,
            irrelevancy_reason="This shouldn't be here",
        )
    assert "irrelevancy_reason must be None when relevant is True" in str(
        exc_info.value
    )


def test_cluster_evaluation_invalid_irrelevant_without_reason():
    with pytest.raises(ValidationError) as exc_info:
        ClusterEvaluation(
            justification="This should fail.", relevant=False, irrelevancy_reason=None
        )
    assert "irrelevancy_reason must not be None when relevant is False" in str(
        exc_info.value
    )


def test_cluster_evaluation_irrelevancy_reason_optional_when_relevant():
    evaluation = ClusterEvaluation(
        justification="This is relevant without specifying irrelevancy_reason.",
        relevant=True,
    )
    assert evaluation.relevant == True  # noqa: E712
    assert evaluation.irrelevancy_reason is None


def test_cluster_evaluation_justification_required():
    with pytest.raises(ValidationError) as exc_info:
        ClusterEvaluation(relevant=True)  # type: ignore
    assert "Field required" in str(exc_info.value)
    assert "justification" in str(exc_info.value)


def test_cluster_evaluation_relevant_required():
    with pytest.raises(ValidationError) as exc_info:
        ClusterEvaluation(justification="Missing relevant field")  # type: ignore
    assert "Field required" in str(exc_info.value)
    assert "relevant" in str(exc_info.value)
