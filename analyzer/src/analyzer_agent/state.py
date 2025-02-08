from typing import Annotated, NotRequired
import operator
from typing_extensions import TypedDict
import anthropic
from .types import TopicBlueprint
from shared.models import Article, Topic


class AgenticTopicsState(TypedDict):
    articles: list[Article]
    language: str
    workspace_description: str
    topic_blueprints: list[TopicBlueprint]
    topic_blueprints_raw_anthropic_responses: Annotated[
        list[anthropic.types.Message], operator.add
    ]
    topics: Annotated[list[Topic], operator.add]
    summary: str


class StateInput(TypedDict):
    articles_ids: NotRequired[list[str]]
    articles: NotRequired[list[Article]]
    language: str
    workspace_description: str


class WriteTopicState(TypedDict):
    articles: list[Article]
    language: str
    workspace_description: str
    topic_blueprint: TopicBlueprint
