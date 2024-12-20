from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_core.language_models.chat_models import BaseChatModel
from langchain import hub
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
from src.analyzer_settings import analyzer_settings
from langchain_core.runnables import Runnable, RunnableLambda
import logging


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
    """
    Generates overviews for clusters of articles using an LLM.

    This class handles the process of formatting articles, fetching the prompt from langsmith hub,
    and generating titles and summaries for clusters.

    Note : These methods also updates the cluster objects with the generated overviews or error messages, but
    we should consider moving these somewhere else. This class should be focused on generating the overviews, not
    updating the models.
    """

    def __init__(
        self,
        llm: BaseChatModel,
        max_articles: int = analyzer_settings.OVERVIEW_GENERATION_MAX_ARTICLES,
    ):
        """
        Initialize the ClusterOverviewGenerator.

        Args:
            llm (BaseChatModel): The language model to use for generating overviews.
            max_articles (int): Maximum number of articles to provide to the LLM for generating the overview.
        """

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

        assert all([article.id in cluster.articles_ids for article in articles])
        articles = sorted(
            articles,
            key=lambda x: cluster.articles_ids.index(x.id),  # type:ignore
        )

        # Assert that the articles are in the same order as the cluster, to get most relevant articles first
        assert [article.id for article in articles] == cluster.articles_ids

        return SetOfUniqueArticles(articles).limit(self.max_articles)

    async def _get_formatted_articles(self, cluster: Cluster) -> str:
        unique_articles = await self._get_articles(cluster)
        return self._format_articles(unique_articles)

    async def _get_language(self, cluster: Cluster) -> Language:
        workspace = await Workspace.get(cluster.workspace_id)
        assert workspace
        return workspace.language

    def _create_chain(self) -> Runnable[Cluster, ClusterOverviewOutput]:
        prompt = hub.pull(analyzer_settings.ARTICLES_OVERVIEW_PROMPT_REF)
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
        max_concurrency: int = analyzer_settings.OVERVIEW_GENERATION_MAX_CONCURRENCY,
    ) -> None:
        """
        Generate overviews for multiple clusters concurrently, then update the cluster
        objects with the generated overviews or error messages.

        Args:
            clusters (list[Cluster]): List of clusters to generate overviews for.
            max_concurrency (int): Maximum number of concurrent overview generations.

        Raises:
            RuntimeError: If overview generation fails for any clusters.
        """

        if not clusters:
            logger.warning("Empty clusters list, skipping overview generation")
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

        exceptions = [
            overview for overview in overviews if isinstance(overview, Exception)
        ]

        if exceptions:
            raise RuntimeError(
                f"Failed to generate overviews for {len(exceptions)} clusters."
            )

        logger.info(f"Finished generating overviews for {len(clusters)} clusters.")

    async def generate_overviews_for_session(
        self,
        session: ClusteringSession,
        max_concurrency: int = analyzer_settings.OVERVIEW_GENERATION_MAX_CONCURRENCY,
        only_missing: bool = False,
    ) -> None:
        """
        Generate overviews for all clusters in a clustering session.

        Args:
            session (ClusteringSession): The clustering session to process.
            max_concurrency (int): Maximum number of concurrent overview generations.
            only_missing (bool): If True, only generate overviews for clusters without existing overviews.
        """

        logger.info(f"Generating overviews for session {session.id}")
        clusters = await Cluster.find(Cluster.session_id == session.id).to_list()
        logger.info(f"Found {len(clusters)} clusters")

        if only_missing:
            clusters = [cluster for cluster in clusters if not cluster.overview]
            logger.info(f"Found {len(clusters)} clusters without overviews")

        await self.generate_overviews(clusters, max_concurrency=max_concurrency)
        logger.info(f"Finished generating overviews for session {session.id}")
