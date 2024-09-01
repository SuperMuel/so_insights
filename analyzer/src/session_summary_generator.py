from langchain.chat_models.base import BaseChatModel
from langchain import hub
from pydantic import BaseModel
from shared.language import Language
from shared.models import ClusterOverview, ClusteringSession, Workspace
from langchain_core.runnables import Runnable, RunnableLambda
import logging
from langchain_core.output_parsers import StrOutputParser
from src.analyzer_settings import AnalyzerSettings


logger = logging.getLogger(__name__)
settings = AnalyzerSettings()


class SessionSummaryInput(BaseModel):
    """Input for clustering session summary generation."""

    language: Language
    overviews: list[ClusterOverview]


SessionSummaryChain = Runnable[SessionSummaryInput, str]


class SessionSummarizer:
    def __init__(self, llm: BaseChatModel):
        self.llm = llm
        self.chain = self._create_chain()

    def format_overviews(self, overviews: list[ClusterOverview]) -> str:
        assert overviews, "Overviews must not be empty."

        include_summary = (
            len(overviews)
            < settings.INCLUDE_CLUSTER_SUMMARIES_FOR_SESSION_SUMMARY_THRESHOLD
        )

        if include_summary:
            return "\n\n".join(
                [f"**{overview.title}**\n{overview.summary}" for overview in overviews]
            )

        return "\n".join([overview.title for overview in overviews])

    def format_input(self, input: SessionSummaryInput) -> dict:
        return {
            "news_topics": self.format_overviews(input.overviews),
            "language": input.language.to_full_name(),
        }

    def _create_chain(self) -> SessionSummaryChain:
        prompt = hub.pull("big-summary")
        return RunnableLambda(self.format_input) | prompt | self.llm | StrOutputParser()

    def get_chain(self) -> SessionSummaryChain:
        return self.chain

    async def abatch(self, inputs: list[SessionSummaryInput]) -> list[str]:
        return await self.chain.abatch(inputs)

    async def ainvoke(self, input: SessionSummaryInput) -> str:
        return await self.chain.ainvoke(input)

    async def generate_summary_for_session(
        self,
        session: ClusteringSession,
    ) -> None:
        logger.info(f"Generating session summary for session {session.id}.")

        clusters = await session.get_sorted_clusters()

        assert all(
            cluster.overview for cluster in clusters
        ), "All clusters must have overviews."
        assert all(
            cluster.evaluation for cluster in clusters
        ), "All clusters must have evaluations."

        relevant_overviews = [
            c.overview
            for c in clusters
            if c.overview
            and c.evaluation
            and c.evaluation.relevance_level == "highly_relevant"
        ]

        if not relevant_overviews:
            logger.warn(f"No relevant overviews found for session {session.id}")
            return

        workspace = await Workspace.get(session.workspace_id)
        assert workspace

        input = SessionSummaryInput(
            language=workspace.language,
            overviews=relevant_overviews,
        )

        output = await self.ainvoke(input)

        session.summary = output
        await session.save()

        logger.info(f"Generated session summary for session {session.id}.")
