from enum import Enum


class AnalysisRunAnalysisType(str, Enum):
    CLUSTERING = "clustering"
    REPORT = "report"

    def __str__(self) -> str:
        return str(self.value)
