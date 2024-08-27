from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_core.language_models.chat_models import BaseChatModel
from langchain import hub
from langsmith import traceable
from shared.language import Language
from shared.models import (
    Article,
    Cluster,
    ClusterOverview,
    ClusteringSession,
    Workspace,
)
from beanie.operators import In
from shared.set_of_unique_articles import SetOfUniqueArticles
from src.analyzer_settings import AnalyzerSettings
from langchain_core.runnables import Runnable, RunnableLambda
import logging

settings = AnalyzerSettings()

logger = logging.getLogger(__name__)


class ClusterOverviewOutput(BaseModel):
    """Output for your title and summary."""

    scratchpad: str = Field(
        ...,
        description="A dense, initial draft of the summary that captures key points and ideas from the articles.",
    )
    forgot: str = Field(
        ...,
        description="A list of important details or points that were initially missed or overlooked in the first draft of the summary.",
    )

    final_summary: str = Field(
        ...,
        description="A comprehensive and cohesive summary that integrates both the initial scratchpad and the details mentioned in the reflection.",
    )
    title: str = Field(
        ...,
        description="A clear, descriptive title that encapsulates the overall theme or subject matter of the cluster.",
    )


class ClusterOverviewGenerator:
    def __init__(
        self,
        llm: BaseChatModel,
        max_articles: int = settings.OVERVIEW_GENERATION_MAX_ARTICLES,
    ):
        self.llm: BaseChatModel = llm
        self.max_articles = max_articles
        self.chain = self._create_chain()

    def _format_article(self, article: Article) -> str:
        return f"<title>{article.title}</title>\n<date>{article.date.strftime('%Y-%m-%d')}</date>\n<body>\n{article.body}\n</body>"

    def _format_articles(self, unique_articles: SetOfUniqueArticles) -> str:
        return "\n\n".join(
            [self._format_article(article) for article in unique_articles]
        )

    async def _get_articles(self, cluster: Cluster) -> SetOfUniqueArticles:
        articles = await Article.find(In(Article.id, cluster.articles_ids)).to_list()
        if not articles:
            raise RuntimeError(f"No articles found for cluster {cluster.id}")
        return SetOfUniqueArticles(articles).limit(self.max_articles)

    async def _get_formatted_articles(self, cluster: Cluster) -> str:
        unique_articles = await self._get_articles(cluster)
        return self._format_articles(unique_articles)

    async def _get_language(self, cluster: Cluster) -> Language:
        workspace = await Workspace.get(cluster.workspace_id)
        assert workspace
        return workspace.language

    def _create_chain(self) -> Runnable[Cluster, ClusterOverviewOutput]:
        prompt = hub.pull("articles_overview")
        structured_llm = self.llm.with_structured_output(ClusterOverviewOutput)

        return (
            {
                "articles": RunnableLambda(self._get_formatted_articles),
                "language": RunnableLambda(self._get_language),
            }
            | prompt
            | structured_llm
        ).with_config(run_name="overview_generation_chain")

    async def generate_overviews(  # TODO : consider moving what updates the models to the analyzer class
        self,
        clusters: list[Cluster],
        max_concurrency: int = settings.OVERVIEW_GENERATION_MAX_CONCURRENCY,
    ) -> None:
        if not clusters:
            logger.warn("Empty clusters list, skipping overview generation")
            return
        logger.info(f"Generating overviews for {len(clusters)} clusters")
        overviews: list[ClusterOverviewOutput | Exception] = await self.chain.abatch(  # type:ignore
            clusters,
            config={"max_concurrency": max_concurrency},
            return_exceptions=True,
        )

        for cluster, overview in zip(clusters, overviews):
            if isinstance(overview, Exception):
                logger.error(
                    f"Failed to generate overview for cluster {cluster.id}: {overview}"
                )
                cluster.overview_generation_error = str(overview)
            else:
                cluster.overview = ClusterOverview(
                    title=overview.title,
                    summary=overview.final_summary,
                    language=await self._get_language(cluster),
                )
                cluster.overview_generation_error = None
            await cluster.save()

        logger.info(f"Finished generating overviews for {len(clusters)} clusters")

    async def generate_overviews_for_session(
        self,
        session: ClusteringSession,
        max_concurrency: int = settings.OVERVIEW_GENERATION_MAX_CONCURRENCY,
        only_missing: bool = False,
    ) -> None:
        logger.info(f"Generating overviews for session {session.id}")
        clusters = await Cluster.find(Cluster.session_id == session.id).to_list()
        logger.info(f"Found {len(clusters)} clusters")

        if only_missing:
            clusters = [cluster for cluster in clusters if not cluster.overview]
            logger.info(f"Found {len(clusters)} clusters without overviews")

        await self.generate_overviews(clusters, max_concurrency=max_concurrency)
        logger.info(f"Finished generating overviews for session {session.id}")


# async def _main():
#     from shared.db import get_client, my_init_beanie
#     from src.analyzer_settings import AnalyzerSettings

#     load_dotenv()

#     logging.basicConfig(
#         level=logging.INFO,
#         format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
#         handlers=[logging.StreamHandler()],
#     )
#     llm = init_chat_model("gpt-4o-mini")

#     # structured_llm = llm.with_structured_output(ClusterOverview)

#     # print(structured_llm.output_schema.schema())

#     settings = AnalyzerSettings()

#     mongo_client = get_client(settings.MONGODB_URI)
#     await my_init_beanie(mongo_client)

#     session = await ClusteringSession.get("66bb8eee8267db888758dd24")
#     assert session
#     clusters = await Cluster.find(Cluster.session_id == session.id).to_list()
#     cluster = clusters[0]

#     generator = ClusterOverviewGenerator(llm=init_chat_model("gpt-4o-mini"))

#     overview = await generator.generate_overview(cluster=cluster)
#     print(overview)

#     # await generator.generate_overviews_for_session(session)


# if __name__ == "__main__":
#     import asyncio

#     asyncio.run(_main())
