from enum import Enum


class UrlToMarkdownConversionExtractionMethod(str, Enum):
    FIRECRAWL = "firecrawl"
    JINA = "jina"

    def __str__(self) -> str:
        return str(self.value)
