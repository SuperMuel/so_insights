import logging

from langchain import hub
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.runnables import Runnable, RunnableLambda
from pydantic import BaseModel, Field

from shared.models import (
    Article,
    ArticleEvaluation,
)
from src.analyzer_settings import analyzer_settings
from langchain_core.rate_limiters import InMemoryRateLimiter

logger = logging.getLogger(__name__)


def format_articles(articles: list[Article], index_start: int = 1) -> str:
    """Format a list of articles with clear separation and indexing.

    Includes the title, url, published date and content of the article.
    If the content is empty, we use the meta-description instead.

    Args:
        articles: List of articles to format
        index_start: Starting index for article numbering

    Returns:
        Formatted string with all articles
    """
    TEMPLATE = """
<article {index}>

<title>{title}</title>
<url>{url}</url>
<published_date>{published_date}</published_date>

<content>
{content}
</content>

</article {index}>
"""

    formatted_articles = []
    for i, article in enumerate(articles, start=index_start):
        formatted = TEMPLATE.format(
            index=i,
            title=article.title,
            url=article.url,
            published_date=article.date.strftime("%Y-%m-%d"),
            content=article.content or article.body,
        )
        formatted_articles.append(formatted)

    return "\n\n".join(formatted_articles)


class ArticleEvaluationInput(BaseModel):
    articles: list[Article]
    workspace_description: str

    def to_chain_input(self) -> dict[str, str]:
        return {
            "articles": format_articles(self.articles),
            "workspace_description": self.workspace_description,
        }


ArticleEvaluationChain = Runnable[ArticleEvaluationInput, list[ArticleEvaluation]]


class EvaluationsBatch(BaseModel):
    evaluations: list[ArticleEvaluation] = Field(
        ...,
        description="A list of evaluations for each article in the batch, in the same order as the articles were provided.",
    )


class ArticleEvaluator:
    def __init__(self, llm: BaseChatModel, rate_limiter: InMemoryRateLimiter | None):
        self.llm = llm
        self.prompt = hub.pull(analyzer_settings.ARTICLE_EVAL_PROMPT_REF)
        self.structured_llm = llm.with_structured_output(EvaluationsBatch)

        if rate_limiter is None:
            self.rate_limiter = InMemoryRateLimiter(
                requests_per_second=0.5, check_every_n_seconds=0.5, max_bucket_size=10
            )
        else:
            self.rate_limiter = rate_limiter

        self.llm = llm.bind(rate_limiter=self.rate_limiter).with_retry(
            stop_after_attempt=5
        )

        self.chain: ArticleEvaluationChain = (
            RunnableLambda(ArticleEvaluationInput.to_chain_input)
            | self.prompt
            | self.structured_llm
            | RunnableLambda(lambda x: x.evaluations)
        ).with_config(run_name="article_eval_chain")

    async def evaluate_articles(
        self,
        articles: list[Article],
        workspace_description: str,
        batch_size: int = analyzer_settings.ARTICLE_EVAL_BATCH_SIZE,
    ) -> list[ArticleEvaluation]:
        # batch the articles
        inputs = [
            ArticleEvaluationInput(
                articles=articles[i : i + batch_size],
                workspace_description=workspace_description,
            )
            for i in range(0, len(articles), batch_size)
        ]

        results: list[list[ArticleEvaluation]] = await self.chain.abatch(inputs)

        # flatten the results
        return [evaluation for batch in results for evaluation in batch]
