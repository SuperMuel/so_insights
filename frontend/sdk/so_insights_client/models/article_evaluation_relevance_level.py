from enum import Enum


class ArticleEvaluationRelevanceLevel(str, Enum):
    NOT_RELEVANT = "not_relevant"
    RELEVANT = "relevant"
    SOMEWHAT_RELEVANT = "somewhat_relevant"

    def __str__(self) -> str:
        return str(self.value)
