from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_core.language_models.chat_models import BaseChatModel
from langchain import hub
from langchain.chat_models import init_chat_model
from langsmith import traceable
from shared.models import Article, Cluster, ClusteringSession
from beanie.operators import In
from shared.set_of_unique_articles import SetOfUniqueArticles
from src.analyzer_settings import AnalyzerSettings
from langchain_core.runnables import Runnable, RunnableLambda

settings = AnalyzerSettings()


class ClusterOverview(BaseModel):
    """A title and summary of a cluster of articles"""

    title: str = Field(description="The title of the cluster")
    summary: str = Field(description="A summary of the cluster")
    error: str | None = Field(
        description="An error message if the task could not be completed"
    )
    # TODO :  chain of density


class ClusterOverviewGenerator:
    def __init__(
        self,
        llm: BaseChatModel,
        max_articles: int = settings.OVERVIEW_GENERATION_MAX_ARTICLES,
    ):
        self.llm: BaseChatModel = llm
        self.max_articles = max_articles

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

    def create_chain(self) -> Runnable[Cluster, ClusterOverview]:
        prompt = hub.pull("supermuel/articles_title_summary")
        structured_llm = self.llm.with_structured_output(ClusterOverview)

        return (
            {
                "articles": RunnableLambda(self._get_formatted_articles),
            }
            | prompt
            | structured_llm
        ).with_config(run_name="overview_generation_chain")

    @traceable
    async def generate_overview(
        self,
        cluster: Cluster,
    ) -> ClusterOverview:
        """Generate a title and summary for a cluster of articles."""

        chain = self.create_chain()

        return await chain.ainvoke(cluster)


async def _main():
    from shared.db import get_client, my_init_beanie
    from src.analyzer_settings import AnalyzerSettings

    settings = AnalyzerSettings()

    mongo_client = get_client(settings.MONGODB_URI)
    await my_init_beanie(mongo_client)

    session = await ClusteringSession.get("66bb8eee8267db888758dd24")

    assert session

    clusters = await Cluster.find(Cluster.session_id == session.id).to_list()

    print([cluster.id for cluster in clusters])

    cluster = clusters[0]

    generator = ClusterOverviewGenerator(llm=init_chat_model("gpt-4o-mini"))

    overview = await generator.generate_overview(
        cluster=cluster,
        max_articles=30,
    )

    print(overview)


if __name__ == "__main__":
    import asyncio

    asyncio.run(_main())
