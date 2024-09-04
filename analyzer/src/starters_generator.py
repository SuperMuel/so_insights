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
    """This class is responsible for generating questions (starters) about the collected data, so they can be used as starters in the chatbot."""

    def __init__(self, llm: BaseChatModel):
        self.llm = llm
        self.chain = self._create_chain()

    def _create_chain(self) -> ChatStartersChain:
        prompt = hub.pull("questions-gen")
        structured_llm = self.llm.with_structured_output(_QuestionsOutput)
        return (
            RunnableLambda(
                lambda input: {
                    "n": input.n,
                    "data": "\n\n".join(
                        [f"**{o.title}**\n{o.summary}" for o in input.data]
                    ),
                    "language": input.language.to_full_name(),
                }
            )
            | prompt
            | structured_llm
        ).with_config(run_name="conversation_starters_chain")

    def get_chain(self) -> ChatStartersChain:
        return self.chain

    async def abatch(
        self, inputs: list[ConversationStartersGenerationInput]
    ) -> list[_QuestionsOutput]:
        return await self.chain.abatch(inputs)

    async def ainvoke(
        self, input: ConversationStartersGenerationInput
    ) -> _QuestionsOutput:
        return await self.chain.ainvoke(input)

    async def generate_starters_for_workspace(
        self,
        workspace: Workspace,
        n: int = 4,
    ) -> None:
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
            logger.warn(f"No overviews found for workspace {workspace.id}")
            return

        input = ConversationStartersGenerationInput(
            n=n, data=overviews, language=workspace.language
        )

        output = await self.ainvoke(input)

        assert workspace.id
        starters = await Starters(
            workspace_id=workspace.id,
            starters=output.questions,
        ).save()

        logger.info(f"Generated {len(output.questions)} chat starters. {starters.id=}")
