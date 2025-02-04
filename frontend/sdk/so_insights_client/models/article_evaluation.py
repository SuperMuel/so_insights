from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.article_evaluation_relevance_level import ArticleEvaluationRelevanceLevel

T = TypeVar("T", bound="ArticleEvaluation")


@_attrs_define
class ArticleEvaluation:
    """Represents an assessment of an article's quality and relevance to the research interest.

    Attributes:
        justification (str): A brief justification (one to two sentences) explaining why the article was classified with
            the chosen verdict.
        relevance_level (ArticleEvaluationRelevanceLevel): The relevance classification of the article with respect to
            the research interest. Use 'relevant' if the article strongly addresses the research interest,
            'somewhat_relevant' if it partially relates, and 'not_relevant' if it does not relate.
    """

    justification: str
    relevance_level: ArticleEvaluationRelevanceLevel
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        justification = self.justification

        relevance_level = self.relevance_level.value

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "justification": justification,
                "relevance_level": relevance_level,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        d = src_dict.copy()
        justification = d.pop("justification")

        relevance_level = ArticleEvaluationRelevanceLevel(d.pop("relevance_level"))

        article_evaluation = cls(
            justification=justification,
            relevance_level=relevance_level,
        )

        article_evaluation.additional_properties = d
        return article_evaluation

    @property
    def additional_keys(self) -> list[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
