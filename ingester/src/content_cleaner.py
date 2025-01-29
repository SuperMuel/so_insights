import logging

from langchain import hub
from langchain.chat_models import init_chat_model
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import Runnable, RunnableLambda

from shared.content_fetching_models import ArticleContentCleanerOutput
from src.ingester_settings import ingester_settings

logger = logging.getLogger(__name__)


ArticleContentCleanerChain = Runnable[str, ArticleContentCleanerOutput]


class ArticleContentCleaner:
    """
    Cleans the markdown content of an article using an LLM.
    """

    def __init__(
        self,
        llm: BaseChatModel | None = None,
        retry_llm: BaseChatModel | None = None,
    ):
        self.llm = llm or init_chat_model(ingester_settings.CONTENT_CLEANER_MODEL)
        self.retry_llm = retry_llm or init_chat_model(
            ingester_settings.CONTENT_CLEANER_RETRY_MODEL
        )
        self.chain = self._create_chain()

    @staticmethod
    def _parse_str_output(completion: str) -> ArticleContentCleanerOutput:
        """
        Parse the LLM output which should be in XML-style format.

        The LLM output should be in one of these formats:

        For successful cleaning:
        ```
        <title>The title of the article</title>
        <content>
        The markdown formatted content of the article
        </content>
        ```

        For errors:
        ```
        <error>The error message</error>
        ```
        """
        import re

        INVALID_OUTPUT_ERROR_MESSAGE = """The output format is invalid.

If you successfully extracted and cleaned the article, present the result in the following format:
```
<title>The title of the article</title>
<content>
The markdown formatted content of the article
</content>
```

If you encountered any issues that prevented you from cleaning the article, present an error message in the following format:
```
<error>The error message</error>
```
"""

        completion = completion.strip()

        # Check for error first
        error_match = re.search(
            r"<error>(.*?)</error>", completion, re.IGNORECASE | re.DOTALL
        )
        if error_match:
            return ArticleContentCleanerOutput(error=error_match.group(1).strip())

        # Extract title and content
        title_match = re.search(r"<title>(.*?)</title>", completion, re.DOTALL)
        if not title_match:
            raise ValueError(INVALID_OUTPUT_ERROR_MESSAGE)
        title = title_match.group(1).strip()

        content_match = re.search(r"<content>(.*?)</content>", completion, re.DOTALL)
        if not content_match:
            raise ValueError(INVALID_OUTPUT_ERROR_MESSAGE)

        content = content_match.group(1).strip()

        return ArticleContentCleanerOutput(
            title=title,
            cleaned_article_content=content,
        )

    def _create_chain(self) -> ArticleContentCleanerChain:
        """
        Creates the LangChain chain for article content cleaning.
        """
        prompt = hub.pull(ingester_settings.ARTICLE_CONTENT_CLEANER_PROMPT_REF)

        return (
            prompt
            | self.llm
            | StrOutputParser()
            | RunnableLambda(self._parse_str_output)
        ).with_config(run_name="article_content_cleaner_chain")

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
