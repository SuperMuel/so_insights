from enum import Enum


class ClusterEvaluationRelevanceLevel(str, Enum):
    HIGHLY_RELEVANT = "highly_relevant"
    NOT_RELEVANT = "not_relevant"
    SOMEWHAT_RELEVANT = "somewhat_relevant"

    def __str__(self) -> str:
        return str(self.value)
