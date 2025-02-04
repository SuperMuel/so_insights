from enum import Enum


class AnalysisType(str, Enum):
    CLUSTERING = "clustering"
    REPORT = "report"

    def __str__(self) -> str:
        return str(self.value)
