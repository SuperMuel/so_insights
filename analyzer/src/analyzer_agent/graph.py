from typing import Any
from beanie.operators import In
from langchain import hub
from src.article_evaluator import format_articles
from src.analyzer_settings import analyzer_settings
from langgraph.graph import StateGraph, START, END
from langgraph.types import Send
import anthropic
from langsmith import traceable
from shared.models import Article
from shared.db import get_client, my_init_beanie
from beanie import PydanticObjectId
from src.analyzer_agent.types import Section, ReportOutline
from src.analyzer_agent.utils import responses_to_markdown_with_citations
from src.analyzer_agent.state import ReportState, StateInput, WriteSectionState
from langchain_openai import ChatOpenAI
import logging

logger = logging.getLogger(__name__)

outline_LLM = ChatOpenAI(
    model="o3-mini",
    reasoning_effort="medium",
    max_retries=3,
)

client = anthropic.Anthropic()
ANTHROPIC_MODEL = "claude-3-5-sonnet-latest"
ANTHROPIC_MODEL_FALLBACK = "claude-3-5-haiku-latest"


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


async def generate_outline(state: StateInput):
    logger.info("Generating outline")
    assert (articles := state.get("articles"))

    prompt = hub.pull(analyzer_settings.REPORT_OUTLINE_PROMPT_REF)
    structured_llm = outline_LLM.with_structured_output(ReportOutline)

    chain = (prompt | structured_llm).with_config(
        run_name="generate_outline",
    )

    outline_result = await chain.ainvoke(
        {
            "articles": format_articles(articles),
            "language": state["language"],
            "workspace_description": state["workspace_description"],
        }
    )

    logger.info(f"Generated outline with {len(outline_result.sections)} sections")

    assert isinstance(outline_result, ReportOutline)

    return {"sections": outline_result.sections}


def article_to_anthropic_document(article: Article) -> dict[str, Any]:
    return {
        "type": "document",
        "source": {"type": "text", "media_type": "text/plain", "data": article.content},
        "title": article.title,
        "citations": {"enabled": True},
    }


@traceable
def write_section(state: WriteSectionState):
    logger.info(f"Writing section {state['section'].title}")
    prompt = """You are an expert report writer. Your task is to write a section of a report based on a collection of articles that relate to a specific research interest.

The final report will be written in {language}, even if the collected articles are in multiple languages.

The audience is interested in the following research interest : 
{research_interest}

The sections's title is : 
{section_title}

The sections's description is : 
{section_description}

Please write this section only, without the title. If you need to add headers, start with h2.
Write the section inside <section> tags.

Use concrete details over general statements.""".format(
        research_interest=state["workspace_description"],
        section_title=state["section"].title,
        section_description=state["section"].description,
        language=state["language"],
    )

    response = client.messages.create(
        model=ANTHROPIC_MODEL,
        max_tokens=1024,
        messages=[
            {
                "role": "user",
                "content": [
                    *[
                        article_to_anthropic_document(article)
                        for article in state["articles"]
                    ],  # type: ignore
                    {"type": "text", "text": prompt},
                ],
            }
        ],
    )

    return {"sections_raw_anthropic_responses": [response]}


def continue_to_write_section(state: ReportState):
    assert all(isinstance(section, Section) for section in state["sections"])

    return [
        Send(
            "write_section",
            {
                "articles": state["articles"],
                "language": state["language"],
                "workspace_description": state["workspace_description"],
                "section": section,
            },
        )
        for section in state["sections"]
    ]


def combine_sections(state: ReportState):
    logger.info("Combining sections")
    sections = state["sections"]
    assert len(sections) == len(state["sections_raw_anthropic_responses"])

    written_sections = responses_to_markdown_with_citations(
        state["sections_raw_anthropic_responses"], state["articles"]
    )
    assert len(sections) == len(written_sections)

    return {
        "final_report_md": "\n\n".join(
            [
                f"# {section.title}\n\n{written_section}"
                for section, written_section in zip(sections, written_sections)
            ]
        )
    }


graph_builder = StateGraph(ReportState, input=StateInput)

graph_builder.add_node("get_articles", get_articles)
graph_builder.add_node("generate_sections", generate_outline)
graph_builder.add_node("write_section", write_section)
graph_builder.add_node("combine_sections", combine_sections)


graph_builder.add_edge(START, "get_articles")
graph_builder.add_edge("get_articles", "generate_sections")
graph_builder.add_conditional_edges(
    "generate_sections",
    continue_to_write_section,  # type: ignore
    ["write_section"],
)
graph_builder.add_edge("write_section", "combine_sections")
graph_builder.add_edge("combine_sections", END)

graph = graph_builder.compile()


async def create_graph():
    mongo_client = get_client(analyzer_settings.MONGODB_URI.get_secret_value())
    await my_init_beanie(mongo_client)

    return graph
