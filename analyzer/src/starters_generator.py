from langchain.chat_models.base import BaseChatModel
from langchain import hub
from pydantic import BaseModel, Field
from shared.language import Language
from shared.models import ClusterOverview, ClusteringSession, Starters, Workspace
from langchain_core.runnables import Runnable, RunnableLambda
import logging


logger = logging.getLogger(__name__)


class ChatStartersGenInput(BaseModel):
    """Input for the chat starters generation."""

    n: int = Field(..., gt=0, le=4)
    data: list[ClusterOverview] = Field(...)
    language: Language


class QuestionsOutput(BaseModel):
    questions: list[str]


ChatStartersChain = Runnable[ChatStartersGenInput, QuestionsOutput]


class ChatStartersGenerator:
    """This class is responsible for generating questions (starters) about the collected data, so they can be used as starters in the chatbot."""

    def __init__(self, llm: BaseChatModel):
        self.llm = llm
        self.chain = self._create_chain()

    def _create_chain(self) -> ChatStartersChain:
        prompt = hub.pull("questions-gen")
        structured_llm = self.llm.with_structured_output(QuestionsOutput)
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
        )

    def get_chain(self) -> ChatStartersChain:
        return self.chain

    async def abatch(self, inputs: list[ChatStartersGenInput]) -> list[QuestionsOutput]:
        return await self.chain.abatch(inputs)

    async def ainvoke(self, input: ChatStartersGenInput) -> QuestionsOutput:
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

        # find last ClusteringSession of workspace
        last_session = (
            await ClusteringSession.find(
                ClusteringSession.workspace_id == workspace.id,
            )
            .sort(-ClusteringSession.data_end)  # type: ignore
            .first_or_none()
        )

        if not last_session:
            logger.info(f"No clustering sessions found for workspace {workspace.id}")
            return

        # get biggest N clusters of session

        clusters = await last_session.get_sorted_clusters(limit=n)

        if not clusters:
            logger.info(f"No clusters found for workspace {workspace.id}")
            return

        # get overviews of clusters
        overviews = [cluster.overview for cluster in clusters if cluster.overview]

        if not overviews:
            logger.warn(f"No overviews found for workspace {workspace.id}")
            return

        input = ChatStartersGenInput(n=n, data=overviews, language=workspace.language)

        output = await self.ainvoke(input)

        assert workspace.id and last_session.id

        starters = await Starters(
            workspace_id=workspace.id,
            session_id=last_session.id,
            starters=output.questions,
        ).save()

        logger.info(f"Generated {len(output.questions)} chat starters. {starters.id=}")
