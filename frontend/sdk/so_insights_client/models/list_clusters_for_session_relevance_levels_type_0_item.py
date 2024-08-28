from enum import Enum


class ListClustersForSessionRelevanceLevelsType0Item(str, Enum):
    HIGHLY_RELEVANT = "highly_relevant"
    NOT_RELEVANT = "not_relevant"
    SOMEWHAT_RELEVANT = "somewhat_relevant"

    def __str__(self) -> str:
        return str(self.value)
