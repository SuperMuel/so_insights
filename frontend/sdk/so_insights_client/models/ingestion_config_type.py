from enum import Enum


class IngestionConfigType(str, Enum):
    RSS = "rss"
    SEARCH = "search"

    def __str__(self) -> str:
        return str(self.value)
