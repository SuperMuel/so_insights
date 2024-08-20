import logging
from typing import Annotated, Sequence
from pydantic import BaseModel, StringConstraints
from shared.models import Cluster, ClusterEvaluation, Workspace, ClusteringSession
from langchain_core.runnables import Runnable, RunnableLambda

from langchain import hub
from langchain_core.language_models.chat_models import BaseChatModel


logger = logging.getLogger(__name__)

_NotEmptyStr = Annotated[str, StringConstraints(min_length=5, strip_whitespace=True)]


class ClusterEvaluationRequest(BaseModel):
    workspace_description: _NotEmptyStr
    cluster_title: _NotEmptyStr
    cluster_summary: _NotEmptyStr

    def to_chain_input(self) -> dict[str, str]:
        return {
            "description": self.workspace_description,
            "title": self.cluster_title,
            "summary": self.cluster_summary,
        }


EvaluationChain = Runnable[ClusterEvaluationRequest, ClusterEvaluation]


class ClusterEvaluator:
    def __init__(self, llm: BaseChatModel):
        self.llm = llm
        self.prompt = hub.pull("cluster_eval")
        self.structured_llm = llm.with_structured_output(ClusterEvaluation)
        self.chain: EvaluationChain = (
            RunnableLambda(ClusterEvaluationRequest.to_chain_input)
            | self.prompt
            | self.structured_llm
        ).with_config(run_name="cluster_eval_chain")

    async def evaluate_cluster(self, cluster: Cluster) -> ClusterEvaluation:
        assert cluster.title and cluster.summary, "Cluster must have title and summary"

        workspace = await Workspace.get(cluster.workspace_id)
        assert workspace

        return await self.chain.ainvoke(
            ClusterEvaluationRequest(
                workspace_description=f"**{workspace.name}**\n{workspace.description}",
                cluster_title=cluster.title,
                cluster_summary=cluster.summary,
            )
        )

    async def evaluate_clusters(
        self, clusters: Sequence[Cluster]
    ) -> Sequence[ClusterEvaluation]:
        if not clusters:
            return []

        workspace = await Workspace.get(clusters[0].workspace_id)
        assert workspace

        assert set(cluster.workspace_id for cluster in clusters) == {
            workspace.id
        }, "All clusters must belong to the same workspace"

        assert all(
            cluster.title and cluster.summary for cluster in clusters
        ), "All clusters must have title and summary"

        return await self.chain.abatch(
            [
                ClusterEvaluationRequest(
                    workspace_description=f"**{workspace.name}**\n{workspace.description}",
                    cluster_title=cluster.title,  # type: ignore
                    cluster_summary=cluster.summary,  # type: ignore
                )
                for cluster in clusters
            ]
        )

    async def evaluate_session(self, session: ClusteringSession) -> None:
        clusters = await session.get_sorted_clusters()

        if not clusters:
            logger.info("No clusters found for the given session.")
            return

        logging.info(f"Evaluating {len(clusters)} clusters...")

        evaluations = await self.evaluate_clusters(clusters)

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


# async def _main():
#     from shared.db import get_client, my_init_beanie
#     from src.analyzer_settings import AnalyzerSettings
#     from shared.models import ClusteringSession, Cluster
#     from langchain.chat_models import init_chat_model

#     settings = AnalyzerSettings()

#     mongo_client = get_client(settings.MONGODB_URI)
#     await my_init_beanie(mongo_client)

#     session = await ClusteringSession.get("66bb8eee8267db888758dd24")

#     assert session

#     clusters = await Cluster.find(Cluster.session_id == session.id).to_list()

#     print([cluster.id for cluster in clusters])

#     cluster = clusters[0]

#     generator = ClusterOverviewGenerator(llm=init_chat_model("gpt-4o-mini"))

#     evaluator = Evaluator(
#         llm=init_chat_model("gpt-4o-mini"), overview_generator=generator
#     )

#     evaluation = await evaluator.evaluate_cluster(cluster)

#     print(evaluation)


# if __name__ == "__main__":
#     import asyncio

#     asyncio.run(_main())
