from enum import Enum


class AnalysisType(str, Enum):
    AGENTIC = "agentic"
    CLUSTERING = "clustering"

    def __str__(self) -> str:
        return str(self.value)
