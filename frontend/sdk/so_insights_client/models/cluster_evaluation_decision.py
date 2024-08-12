from enum import Enum


class ClusterEvaluationDecision(str, Enum):
    EXCLUDE = "exclude"
    INCLUDE = "include"

    def __str__(self) -> str:
        return str(self.value)
