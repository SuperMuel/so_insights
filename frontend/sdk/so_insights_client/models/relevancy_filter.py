from enum import Enum


class RelevancyFilter(str, Enum):
    ALL = "all"
    HIGHLY_RELEVANT = "highly_relevant"
    NOT_RELEVANT = "not_relevant"
    SOMEWHAT_RELEVANT = "somewhat_relevant"
    UNKNOWN = "unknown"

    def __str__(self) -> str:
        return str(self.value)
