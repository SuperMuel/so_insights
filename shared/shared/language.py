from enum import Enum


class Language(str, Enum):
    fr = "fr"
    en = "en"
    de = "de"

    def to_full_name(self) -> str:
        match self:
            case Language.fr:
                return "Français"
            case Language.en:
                return "English"
            case Language.de:
                return "Deutsch"
