from beanie.operators import In
from langchain_core.output_parsers import StrOutputParser
from langchain.chat_models.base import BaseChatModel
from langchain.chat_models import init_chat_model
from langchain import hub
from langchain_anthropic import ChatAnthropic
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
    article_to_anthropic_document,
    extract_body_with_citations,
    extract_title_and_body,
    anthropic_response_to_markdown,
    anthropic_response_to_markdown_with_citations,
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

body_llm = init_chat_model("gemini-2.0-flash-001", model_provider="google_genai")


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


ANTHROPIC_WRITE_TOPIC_PROMPT = """You are an AI agent tasked with writing a concise, informative, and engaging body for a specific topic based on a collection of articles. Your writing will be part of a system that provides targeted information to clients interested in specific domains. The goal is to create easy-to-read and ultra-targeted content about the latest news, trends, and advancements in the client's domain of interest.

The final report will be written in {language}, even if the collected articles are in multiple languages.

The audience is interested in the following research interest :
<research_interest>
{research_interest}
</research_interest>

Your task is to write the body of the following topic blueprint :
<topic_blueprint>
{topic_blueprint}
</topic_blueprint>

1. Analyze the topic_blueprint, paying close attention to the title, description, and quotes provided.

2. Review the articles and identify the most relevant information related to the topic. 

3. Write a coherent and informative body for the topic, adhering to the following guidelines:
   - Keep the content focused on the specific topic and relevant to the workspace_description.
   - Use clear and concise language.
   - Use specific examples, data points, and details from the articles to support your points. Avoid general statements or vague summaries

4. Style and tone: **Concise and Targeted**
   - Write in an objective, informative tone.
   - Write a concise and easy-to-read body for the topic. Aim for impactful summaries rather than lengthy prose.
   - Do not fear using jargon or technical language: the audience is familiar with their domain.
   - Do not write introduction, transitions or conclusions.
   - Use Markdown formatting : bullet points, bold... but no tables.  

5. Output format : 
    - Write your reasoning under <scratchpad> tags. 
    - Write the final title for the topic under <title> tags. 
    - Write the final body for the topic under <body> tags.
"""


async def _write_topic_body_anthropic(
    state: WriteTopicState, supporting_articles: list[Article]
):
    llm = ChatAnthropic(model_name="claude-3-5-haiku-latest")  # type: ignore

    prompt = ANTHROPIC_WRITE_TOPIC_PROMPT.format(
        research_interest=state["workspace_description"],
        topic_blueprint=format_topic_blueprint(state["topic_blueprint"]),
        language=state["language"],
    )

    messages = [
        {
            "role": "user",
            "content": [
                *[
                    article_to_anthropic_document(article)
                    for article in supporting_articles
                    if article.content or article.body
                ],
                {"type": "text", "text": prompt},
            ],
        }
    ]

    response = await llm.ainvoke(messages)

    body_with_citations, article_ids = anthropic_response_to_markdown_with_citations(
        response, state["articles"]
    )

    title, body = anthropic_response_to_markdown(response)

    topic = Topic(
        title=title,
        body=body,
        body_with_links=body_with_citations,
        articles_ids=[article.id for article in supporting_articles if article.id],
    )

    return {"topics": [topic]}


async def _write_topic_body_other(
    llm: BaseChatModel, state: WriteTopicState, supporting_articles: list[Article]
):
    prompt = hub.pull(analyzer_settings.WRITE_TOPIC_PROMPT_REF)

    chain = (prompt | llm | StrOutputParser()).with_config(
        run_name="write_topic_body",
    )

    response = await chain.ainvoke(
        {
            "articles": format_articles(supporting_articles),
            "language": state["language"],
            "research_interest": state["workspace_description"],
            "topic_blueprint": format_topic_blueprint(state["topic_blueprint"]),
        }
    )

    title, body = extract_title_and_body(response)
    body_with_citations = extract_body_with_citations(response)

    topic = Topic(
        title=title,
        body=body,
        body_with_links=body_with_citations,
        articles_ids=[article.id for article in supporting_articles if article.id],
    )

    return {"topics": [topic]}


@traceable
async def write_topic_body(state: WriteTopicState):
    logger.info(f"Writing topic body {state['topic_blueprint'].title}")

    all_articles = state["articles"]
    supporting_articles = [
        all_articles[idx - 1]
        for idx in state["topic_blueprint"].supporting_articles_idxs
    ]

    if analyzer_settings.USE_ANTHROPIC_CITATIONS:
        return await _write_topic_body_anthropic(state, supporting_articles)
    else:
        return await _write_topic_body_other(body_llm, state, supporting_articles)


async def generate_summary(state: AgenticTopicsState):
    logger.info("Generating summary")

    prompt = hub.pull(analyzer_settings.BIG_SUMMARY_PROMPT_REF)

    chain = (prompt | body_llm | StrOutputParser()).with_config(
        run_name="generate_summary",
    )

    topics_str = ("\n" * 5).join(
        [f"**{topic.title}**\n{topic.body}" for topic in state["topics"]]
    )

    response = await chain.ainvoke(
        {
            "news_topics": topics_str,
            "language": state["language"],
        }
    )

    return {"summary": response}


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
graph_builder.add_node("generate_summary", generate_summary)

graph_builder.add_edge(START, "get_articles")
graph_builder.add_edge("get_articles", "generate_topic_blueprints")
graph_builder.add_conditional_edges(
    "generate_topic_blueprints",
    continue_to_write_topic_body,  # type: ignore
    ["write_topic_body"],
)
graph_builder.add_edge("write_topic_body", "generate_summary")
graph_builder.add_edge("generate_summary", END)

graph = graph_builder.compile()


async def create_graph():
    mongo_client = get_client(analyzer_settings.MONGODB_URI.get_secret_value())
    await my_init_beanie(mongo_client)

    return graph
