from typing import Any
from langchain.chat_models.base import BaseChatModel
from langchain import hub
from pydantic import BaseModel, Field
from shared.language import Language
from shared.models import (
    ClusterOverview,
    Starters,
    Workspace,
)
from langchain_core.runnables import Runnable, RunnableLambda
import logging

from src.analyzer_settings import analyzer_settings


logger = logging.getLogger(__name__)


class ConversationStartersGenerationInput(BaseModel):
    """Input for the chat starters generation."""

    n: int = Field(..., gt=0, le=4)
    data: list[ClusterOverview] = Field(...)
    language: Language


class _QuestionsOutput(BaseModel):
    questions: list[str]


ChatStartersChain = Runnable[ConversationStartersGenerationInput, _QuestionsOutput]


class ConversationStartersGenerator:
    """
    Generates engaging questions based on analyzed data to initiate conversations in the chatbot.
    These questions serve as conversation starters, encouraging user interaction with the insights
    derived from the clustering process.
    """

    def __init__(self, llm: BaseChatModel):
        self.llm = llm
        self.chain = self._create_chain()

    def _create_chain(self) -> ChatStartersChain:
        prompt = hub.pull(analyzer_settings.CONVERSATION_STARTERS_PROMPT_REF)
        structured_llm = self.llm.with_structured_output(_QuestionsOutput)

        def _format_input(input: ConversationStartersGenerationInput) -> dict[str, Any]:
            return {
                "n": input.n,
                "data": "\n\n".join(
                    [f"**{o.title}**\n{o.summary}" for o in input.data]
                ),
                "language": input.language.to_full_name(),
            }

        return (RunnableLambda(_format_input) | prompt | structured_llm).with_config(
            run_name="conversation_starters_chain"
        )

    def get_chain(self) -> ChatStartersChain:
        return self.chain

    async def abatch(
        self,
        inputs: list[ConversationStartersGenerationInput],
        metadata: dict[str, Any] = {},
    ) -> list[_QuestionsOutput]:
        """
        Generates conversation starters for multiple inputs in batch.
        """

        return await self.chain.abatch(inputs, config={"metadata": metadata})

    async def ainvoke(
        self,
        input: ConversationStartersGenerationInput,
        metadata: dict[str, Any] = {},
    ) -> _QuestionsOutput:
        """
        Generates conversation starters for a single input asynchronously.
        """

        return await self.chain.ainvoke(input, config={"metadata": metadata})

    async def generate_starters_for_workspace(
        self,
        workspace: Workspace,
        n: int = 4,
    ) -> None:
        """
        Generates and saves conversation starters for a specific workspace.

        Processes the most recent and relevant cluster overviews to create
        engaging questions tailored to the workspace's content and language.

        Args:
            workspace (Workspace): The workspace for which to generate starters.
            n (int): The number of starters to generate (default: 4).
        """

        assert n > 0
        logger.info(
            f"Generating chat starters for workspace {workspace.id} ({workspace.name})"
        )

        sessions = await workspace.get_sorted_sessions().to_list()
        if not sessions:
            logger.info(f"No clustering sessions found for workspace {workspace.id}")
            return

        overviews: list[ClusterOverview] = []

        for session in sessions:
            clusters = await session.get_sorted_clusters(
                relevance_level="highly_relevant"
            )
            _overviews = [c.overview for c in clusters if c.overview]
            overviews.extend(_overviews[: n - len(overviews)])

            if len(overviews) >= n:
                break

        if not overviews:
            logger.warning(f"No overviews found for workspace {workspace.id}")
            return

        input = ConversationStartersGenerationInput(
            n=n, data=overviews, language=workspace.language
        )

        output = await self.ainvoke(input, metadata={"workspace_id": workspace.id})

        assert workspace.id
        starters = await Starters(
            workspace_id=workspace.id,
            starters=output.questions,
        ).save()

        logger.info(f"Generated {len(output.questions)} chat starters. {starters.id=}")
