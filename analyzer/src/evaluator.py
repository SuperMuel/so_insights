import logging
from typing import Annotated, Sequence
from pydantic import BaseModel, StringConstraints
from shared.models import (
    Cluster,
    ClusterEvaluation,
    ClusterOverview,
    Workspace,
    ClusteringSession,
)
from langchain_core.runnables import Runnable, RunnableLambda

from langchain import hub
from langchain_core.language_models.chat_models import BaseChatModel
from src.analyzer_settings import analyzer_settings


logger = logging.getLogger(__name__)

_NotEmptyStr = Annotated[str, StringConstraints(min_length=5, strip_whitespace=True)]


class ClusterEvaluationInput(BaseModel):
    """
    Represents a request for cluster evaluation.

    Attributes:
        workspace_description (_NotEmptyStr): Description of the workspace.
        cluster_overview (ClusterOverview): Overview of the cluster to be evaluated.
    """

    workspace_description: _NotEmptyStr
    cluster_overview: ClusterOverview

    def to_chain_input(self) -> dict[str, str]:
        return {
            "description": self.workspace_description,
            "title": self.cluster_overview.title,
            "summary": self.cluster_overview.summary,
        }


EvaluationChain = Runnable[ClusterEvaluationInput, ClusterEvaluation]


def get_workspace_description(Workspace: Workspace) -> str:
    return f"**{Workspace.name}**\n{Workspace.description}"


# TODO : Refactor this class to separate evaluation logic from database operations.
class ClusterEvaluator:
    """
    Evaluates clusters of articles to determine their relevance and importance within a workspace context.

    Uses an LLM to assess each cluster's content against the workspace's focus and goals.

    The evaluator can process clusters in batches for efficiency and provides logging of evaluation statistics.
    This evaluation is crucial for prioritizing and filtering clusters, ensuring that the most relevant
    information is highlighted for the users.

    Attributes:
        llm (BaseChatModel): The language model used for evaluations.
        prompt: The prompt template used to guide the language model's evaluation.
        structured_llm: A version of the language model configured to output structured ClusterEvaluation objects.
        chain (EvaluationChain): The complete evaluation pipeline, from input formatting to structured output.
    """

    def __init__(self, llm: BaseChatModel):
        self.llm = llm
        self.prompt = hub.pull(analyzer_settings.CLUSTER_EVAL_PROMPT_REF)
        self.structured_llm = llm.with_structured_output(ClusterEvaluation)
        self.chain: EvaluationChain = (
            RunnableLambda(ClusterEvaluationInput.to_chain_input)
            | self.prompt
            | self.structured_llm
        ).with_config(run_name="cluster_eval_chain")

    async def _generate_cluster_eval(self, cluster: Cluster) -> ClusterEvaluation:
        """
        Generates an evaluation for a single cluster.

        Note : Logs cluster_id and workspace_id as metadata.
        """

        assert cluster.overview, "Cluster must have an overview"

        workspace = await Workspace.get(cluster.workspace_id)
        assert workspace

        return await self.chain.ainvoke(
            ClusterEvaluationInput(
                workspace_description=get_workspace_description(workspace),
                cluster_overview=cluster.overview,
            ),
            config={
                "metadata": {
                    "cluster_id": cluster.id,
                    "workspace_id": cluster.workspace_id,
                }
            },
        )

    async def _get_clusters_evaluations(
        self,
        clusters: Sequence[Cluster],
        session_id: str | None,
    ) -> list[ClusterEvaluation]:
        """
        Generates evaluations for a sequence of clusters.

        This method processes multiple clusters in batch, ensuring they all belong
        to the same workspace and have overviews.

        Args:
            clusters (Sequence[Cluster]): The clusters to be evaluated.
            session_id (str | None): The ID of the clustering session, only for logging purposes.

        Returns:
            list[ClusterEvaluation]: A list of evaluation results for the clusters.
        """

        if not clusters:
            return []

        workspace = await Workspace.get(clusters[0].workspace_id)
        assert workspace

        assert set(cluster.workspace_id for cluster in clusters) == {
            workspace.id
        }, "All clusters must belong to the same workspace"

        assert all(
            cluster.overview for cluster in clusters
        ), "All clusters must have an overview"

        return await self.chain.abatch(
            [
                ClusterEvaluationInput(
                    workspace_description=get_workspace_description(workspace),
                    cluster_overview=cluster.overview,  # type: ignore
                )
                for cluster in clusters
            ],
            config={
                "metadata": {
                    "workspace_id": workspace.id,
                    **({"session_id": session_id} if session_id else {}),
                }
            },
        )

    async def evaluate_clusters(
        self,
        clusters: Sequence[Cluster],
        session_id: str | None = None,
    ) -> None:
        """
        Evaluates a sequence of clusters and updates their evaluation data.

        Args:
            clusters (Sequence[Cluster]): The clusters to be evaluated.
            session_id (str | None): The ID of the clustering session, only for logging purposes.

        Note:
            This method updates the clusters in the database with their evaluations. But it should be refactored
            to separate the evaluation logic from the database operations. This class should focus on generating
            the evaluations, not updating the models.
        """

        if not clusters:
            logger.info("No clusters to evaluate.")
            return

        logger.info(f"Evaluating {len(clusters)} clusters...")
        evaluations = await self._get_clusters_evaluations(
            clusters,
            session_id,
        )

        for cluster, evaluation in zip(clusters, evaluations):
            cluster.evaluation = evaluation
            await cluster.save()

        nb_high = len(
            [e for e in evaluations if e.relevance_level == "highly_relevant"]
        )
        nb_medium = len(
            [e for e in evaluations if e.relevance_level == "somewhat_relevant"]
        )
        nb_low = len([e for e in evaluations if e.relevance_level == "not_relevant"])

        logging.info(
            f"Found {nb_high} highly relevant, {nb_medium} somewhat relevant and {nb_low} not relevant clusters."
        )

        confidence_avg = sum([e.confidence_score for e in evaluations]) / len(
            evaluations
        )

        logging.info(f"Average confidence score: {confidence_avg:.2f}")

    async def evaluate_session(self, session: ClusteringSession) -> None:
        """
        Evaluates all clusters associated with a given clustering session.

        This method retrieves all clusters for the specified session,
        evaluates them, and updates their evaluation data in the database.

        Args:
            session (ClusteringSession): The clustering session whose clusters are to be evaluated.
        """

        clusters = await session.get_sorted_clusters()

        if not clusters:
            logger.info("No clusters found for the given session.")
            return

        await self.evaluate_clusters(
            clusters,
            session_id=str(session.id) if session.id else None,
        )
