from enum import Enum


class SearchProvider(str, Enum):
    DUCKDUCKGO = "duckduckgo"
    RSS = "rss"
    SERPERDEV = "serperdev"

    def __str__(self) -> str:
        return str(self.value)
