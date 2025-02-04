from enum import Enum


class AnalysisRunCreateAnalysisType(str, Enum):
    CLUSTERING = "clustering"
    REPORT = "report"

    def __str__(self) -> str:
        return str(self.value)
