from enum import Enum


class RelevancyFilter(str, Enum):
    ALL = "all"
    IRRELEVANT = "irrelevant"
    RELEVANT = "relevant"
    UNKNOWN = "unknown"

    def __str__(self) -> str:
        return str(self.value)
