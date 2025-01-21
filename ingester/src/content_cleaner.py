import logging

from langchain import hub
from langchain.chat_models import init_chat_model
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import Runnable

from shared.content_fetching_models import ArticleContentCleanerOutput
from src.ingester_settings import ingester_settings

logger = logging.getLogger(__name__)


ArticleContentCleanerChain = Runnable[str, ArticleContentCleanerOutput]


class ArticleContentCleaner:
    """
    Cleans the markdown content of an article using an LLM.
    """

    def __init__(self, llm: BaseChatModel | None = None):
        self.llm = llm or init_chat_model(ingester_settings.CONTENT_CLEANER_MODEL)
        self.chain = self._create_chain()

    @classmethod
    def _parse_output(cls, output: str) -> ArticleContentCleanerOutput:
        """
        Parses the output of the article content cleaner LLM.

        Assuming the LLM output format is:

        ```md
        # Article title

        <cleaned markdown article content>
        ```
        """

        lines = output.split("\n")
        title = lines[0].strip("# ")
        cleaned_markdown = "\n".join(lines[1:]).strip()

        return ArticleContentCleanerOutput(
            title=title, cleaned_markdown=cleaned_markdown
        )

    def _create_chain(self) -> ArticleContentCleanerChain:
        """
        Creates the LangChain chain for article content cleaning.
        """
        prompt = hub.pull(ingester_settings.ARTICLE_CONTENT_CLEANER_PROMPT_REF)

        return (prompt | self.llm | StrOutputParser() | self._parse_output).with_config(
            run_name="article_content_cleaner_chain"
        )

    def get_chain(self) -> ArticleContentCleanerChain:
        """
        Returns the LangChain chain for article content cleaning.
        """
        return self.chain

    async def clean_article_content(
        self, raw_markdown_content: str, metadata: dict = {}
    ) -> ArticleContentCleanerOutput:
        """
        Cleans the markdown content of an article.

        Args:
            markdown (str): The markdown content to clean.

        Returns:
            ArticleContentCleanerOutput: The cleaned markdown content.
        """

        logger.info("Cleaning article content...")

        return await self.chain.ainvoke(
            raw_markdown_content, config={"metadata": metadata}
        )
