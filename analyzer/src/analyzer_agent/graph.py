from typing import Any
from beanie.operators import In
from dotenv import load_dotenv
from langchain import hub
from src.article_evaluator import format_articles
from src.analyzer_settings import analyzer_settings
from langgraph.graph import StateGraph, START, END
from langgraph.types import Send
import anthropic
from langsmith import traceable
from shared.models import Article, Topic
from shared.db import get_client, my_init_beanie
from beanie import PydanticObjectId
from src.analyzer_agent.types import TopicBlueprint, TopicsBlueprints
from src.analyzer_agent.utils import (
    response_to_markdown,
    response_to_markdown_with_citations,
)
from src.analyzer_agent.state import AgenticTopicsState, StateInput, WriteTopicState
from langchain_openai import ChatOpenAI
import logging


logger = logging.getLogger(__name__)

outline_LLM = ChatOpenAI(
    model="o3-mini",
    reasoning_effort="medium",
    max_retries=3,
)

client = anthropic.Anthropic()
# ANTHROPIC_MODEL = "claude-3-5-sonnet-latest"
ANTHROPIC_MODEL = "claude-3-5-haiku-latest"


async def get_articles(state: StateInput):
    articles, articles_ids = state.get("articles"), state.get("articles_ids")

    if not articles_ids and not articles:
        raise ValueError("Either articles_ids or articles must be provided")

    if articles:
        return  # no update

    assert articles_ids

    ids = []
    # if element is multiline, split it
    for element in articles_ids:
        if "\n" in element:
            ids.extend(element.split("\n"))
        else:
            ids.append(element)
    # strip all ids
    ids = [id.strip() for id in ids]
    assert all(isinstance(id, str) for id in ids)

    # Convert ids to PydanticObjectId
    ids = [PydanticObjectId(id) for id in ids]

    articles = await Article.find_many(In(Article.id, ids)).to_list()
    if not articles:
        raise ValueError("No articles found")

    logger.info(f"Found {len(articles)} articles")

    return {"articles": articles}


async def generate_topic_blueprints(state: StateInput):
    logger.info("Generating topics plans")
    assert (articles := state.get("articles"))

    prompt = hub.pull(analyzer_settings.TOPICS_BLUEPRINTS_PROMPT_REF)
    structured_llm = outline_LLM.with_structured_output(TopicsBlueprints)

    chain = (prompt | structured_llm).with_config(
        run_name="generate_topic_blueprints",
    )

    blueprints = await chain.ainvoke(
        {
            "articles": format_articles(articles),
            "language": state["language"],
            "workspace_description": state["workspace_description"],
        }
    )
    assert isinstance(blueprints, TopicsBlueprints)

    logger.info(f"Generated topic blueprints with {len(blueprints.topics)} topics")

    return {"topic_blueprints": blueprints.topics}


def article_to_anthropic_document(article: Article) -> dict[str, Any]:
    assert (
        article.content or article.body
    ), "An Anthropic document must have non-empty data, but the article provided had empty content and body"

    return {
        "type": "document",
        "source": {
            "type": "text",
            "media_type": "text/plain",
            "data": article.content or article.body,
        },
        "title": article.title,
        "citations": {"enabled": True},
    }


def format_topic_blueprint(topic_blueprint: TopicBlueprint):
    return f"""
    Title: {topic_blueprint.title}
    Description: {topic_blueprint.description}
    Quotes examples:
    {
        "\n".join(
            [
                f"- {quote.text}" for quote in topic_blueprint.supporting_quotes
            ]
        )
    }
    """


@traceable
def write_topic_body(state: WriteTopicState):
    logger.info(f"Writing topic body {state['topic_blueprint'].title}")
    prompt = hub.pull(analyzer_settings.WRITE_TOPIC_PROMPT_REF).format(
        articles=format_articles(state["articles"]),
        research_interest=state["workspace_description"],
        topic_blueprint=format_topic_blueprint(state["topic_blueprint"]),
        language=state["language"],
    )

    response = client.messages.create(
        model=ANTHROPIC_MODEL,
        max_tokens=4096,
        messages=[
            {
                "role": "user",
                "content": [
                    *[
                        article_to_anthropic_document(article)
                        for article in state["articles"]
                        if article.content or article.body
                    ],  # type: ignore
                    {"type": "text", "text": prompt},
                ],
            }
        ],
    )

    markdown_with_citations, article_ids = response_to_markdown_with_citations(
        response, state["articles"]
    )

    markdown = response_to_markdown(response)

    topic = Topic(
        title=state["topic_blueprint"].title,
        body=markdown,
        body_with_links=markdown_with_citations,
        articles_ids=[article.id for article in article_ids if article.id],
    )

    return {"topics": [topic]}


def continue_to_write_topic_body(state: AgenticTopicsState):
    assert all(isinstance(topic, TopicBlueprint) for topic in state["topic_blueprints"])

    return [
        Send(
            "write_topic_body",
            {
                "articles": state["articles"],
                "language": state["language"],
                "workspace_description": state["workspace_description"],
                "topic_blueprint": topic,
            },
        )
        for topic in state["topic_blueprints"]
    ]


graph_builder = StateGraph(AgenticTopicsState, input=StateInput)

graph_builder.add_node("get_articles", get_articles)
graph_builder.add_node("generate_topic_blueprints", generate_topic_blueprints)
graph_builder.add_node("write_topic_body", write_topic_body)

graph_builder.add_edge(START, "get_articles")
graph_builder.add_edge("get_articles", "generate_topic_blueprints")
graph_builder.add_conditional_edges(
    "generate_topic_blueprints",
    continue_to_write_topic_body,  # type: ignore
    ["write_topic_body"],
)
graph_builder.add_edge("write_topic_body", END)

graph = graph_builder.compile()


async def create_graph():
    mongo_client = get_client(analyzer_settings.MONGODB_URI.get_secret_value())
    await my_init_beanie(mongo_client)

    return graph
