from typing import Annotated, NotRequired
import operator
from typing_extensions import TypedDict
import anthropic
from .types import TopicBlueprint
from shared.models import Article, Topic


class ReportState(TypedDict):
    articles: list[Article]
    language: str
    workspace_description: str
    sections: list[TopicBlueprint]
    sections_raw_anthropic_responses: Annotated[
        list[anthropic.types.Message], operator.add
    ]
    final_report_md: str
    topics: list[Topic]


class StateInput(TypedDict):
    articles_ids: NotRequired[list[str]]
    articles: NotRequired[list[Article]]
    language: str
    workspace_description: str


class WriteTopicState(TypedDict):
    articles: list[Article]
    language: str
    workspace_description: str
    topic: TopicBlueprint


class WriteSectionState(TypedDict):
    articles: list[Article]
    language: str
    workspace_description: str
    section: TopicBlueprint
