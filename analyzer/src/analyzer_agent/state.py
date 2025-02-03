from typing import Annotated
import operator
from typing_extensions import TypedDict
import anthropic
from .types import Section
from shared.models import Article


class ReportState(TypedDict):
    articles: list[Article]
    language: str
    workspace_description: str
    sections: list[Section]
    sections_raw_anthropic_responses: Annotated[
        list[anthropic.types.Message], operator.add
    ]
    final_report_md: str


class StateInput(TypedDict):
    articles_ids: list[str] | None
    articles: list[Article] | None
    language: str
    workspace_description: str


class WriteSectionState(TypedDict):
    articles: list[Article]
    language: str
    workspace_description: str
    section: Section
