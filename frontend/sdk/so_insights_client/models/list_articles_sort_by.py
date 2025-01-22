from enum import Enum


class ListArticlesSortBy(str, Enum):
    DATE = "date"
    FOUND_AT = "found_at"

    def __str__(self) -> str:
        return str(self.value)
