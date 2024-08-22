from enum import Enum


class Language(str, Enum):
    DE = "de"
    EN = "en"
    FR = "fr"

    def __str__(self) -> str:
        return str(self.value)
