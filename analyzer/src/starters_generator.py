from typing import Any
from langchain.chat_models.base import BaseChatModel
from langchain import hub
from pydantic import BaseModel, Field
from shared.language import Language
from shared.models import (
    AnalysisRun,
    AnalysisType,
    ReportAnalysisResult,
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
    formatted_data: str = Field(
        ...,
        description="Formatted data to use as input for the chat starters generation.",
    )
    language: Language
    workspace_description: str


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
                "data": input.formatted_data,
                "language": input.language.to_full_name(),
                "workspace_description": input.workspace_description,
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

    async def generate_new_conversation_starters(
        self,
        workspace: Workspace,
        run: AnalysisRun,
        n: int = 4,
    ) -> None:
        """
        Generates and saves conversation starters for a specific workspace.

        Uses the last report or the largest relevant clusters of the analysis run
        to create engaging questions tailored to the workspace's content and language.

        Args:
            workspace (Workspace): The workspace for which to generate starters.
            run (AnalysisRun): The analysis run to use to generate starters.
            n (int): The maximum number of starters to generate (default: 4).
        """

        assert n > 0
        logger.info(
            f"Generating chat starters for workspace {workspace.id} ({workspace.name}) with analysis run {run.id}"
        )

        match run.analysis_type:
            case AnalysisType.CLUSTERING:
                clusters = await run.get_largest_clusters(
                    relevance_level="highly_relevant", limit=n
                )
                if not clusters:
                    logger.warning(
                        f"No relevant clusters found for the analysis run {run.id}"
                    )
                    return
                overviews = [c.overview for c in clusters if c.overview]
                data = "\n\n".join([f"**{o.title}**\n{o.summary}" for o in overviews])
                logger.info(
                    f"Using {len(overviews)} overviews of {len(clusters)} clusters for starters generation"
                )
            case AnalysisType.AGENTIC:
                assert run.result is not None and isinstance(
                    run.result, ReportAnalysisResult
                )
                data = run.result.report_content
                logger.info(
                    f"Using {len(data)} characters of report content for starters generation"
                )

        input = ConversationStartersGenerationInput(
            n=n,
            formatted_data=data,
            language=workspace.language,
            workspace_description=workspace.description,
        )

        output = await self.ainvoke(
            input,
            metadata={
                "workspace_id": workspace.id,
                "analysis_run_id": run.id,
            },
        )

        assert workspace.id
        starters = await Starters(
            workspace_id=workspace.id,
            starters=output.questions,
        ).save()

        logger.info(f"Generated {len(output.questions)} chat starters. {starters.id=}")
