from enum import Enum

_FULL_NAMES = {
    "xa-ar": "Arabia",
    "xa-en": "Arabia (en)",
    "ar-es": "Argentina",
    "au-en": "Australia",
    "at-de": "Austria",
    "be-fr": "Belgium (fr)",
    "be-nl": "Belgium (nl)",
    "br-pt": "Brazil",
    "bg-bg": "Bulgaria",
    "ca-en": "Canada",
    "ca-fr": "Canada (fr)",
    "ct-ca": "Catalan",
    "cl-es": "Chile",
    "cn-zh": "China",
    "co-es": "Colombia",
    "hr-hr": "Croatia",
    "cz-cs": "Czech Republic",
    "dk-da": "Denmark",
    "ee-et": "Estonia",
    "fi-fi": "Finland",
    "fr-fr": "France",
    "de-de": "Germany",
    "gr-el": "Greece",
    "hk-tzh": "Hong Kong",
    "hu-hu": "Hungary",
    "in-en": "India",
    "id-id": "Indonesia",
    "id-en": "Indonesia (en)",
    "ie-en": "Ireland",
    "il-he": "Israel",
    "it-it": "Italy",
    "jp-jp": "Japan",
    "kr-kr": "Korea",
    "lv-lv": "Latvia",
    "lt-lt": "Lithuania",
    "xl-es": "Latin America",
    "my-ms": "Malaysia",
    "my-en": "Malaysia (en)",
    "mx-es": "Mexico",
    "nl-nl": "Netherlands",
    "nz-en": "New Zealand",
    "no-no": "Norway",
    "pe-es": "Peru",
    "ph-en": "Philippines",
    "ph-tl": "Philippines (tl)",
    "pl-pl": "Poland",
    "pt-pt": "Portugal",
    "ro-ro": "Romania",
    "ru-ru": "Russia",
    "sg-en": "Singapore",
    "sk-sk": "Slovak Republic",
    "sl-sl": "Slovenia",
    "za-en": "South Africa",
    "es-es": "Spain",
    "se-sv": "Sweden",
    "ch-de": "Switzerland (de)",
    "ch-fr": "Switzerland (fr)",
    "ch-it": "Switzerland (it)",
    "tw-tzh": "Taiwan",
    "th-th": "Thailand",
    "tr-tr": "Turkey",
    "ua-uk": "Ukraine",
    "uk-en": "United Kingdom",
    "us-en": "United States",
    "ue-es": "United States (es)",
    "ve-es": "Venezuela",
    "vn-vi": "Vietnam",
    "wt-wt": "No region",
}


class Region(str, Enum):
    ARABIA = "xa-ar"
    ARABIA_EN = "xa-en"
    ARGENTINA = "ar-es"
    AUSTRALIA = "au-en"
    AUSTRIA = "at-de"
    BELGIUM_FR = "be-fr"
    BELGIUM_NL = "be-nl"
    BRAZIL = "br-pt"
    BULGARIA = "bg-bg"
    CANADA = "ca-en"
    CANADA_FR = "ca-fr"
    CATALAN = "ct-ca"
    CHILE = "cl-es"
    CHINA = "cn-zh"
    COLOMBIA = "co-es"
    CROATIA = "hr-hr"
    CZECH_REPUBLIC = "cz-cs"
    DENMARK = "dk-da"
    ESTONIA = "ee-et"
    FINLAND = "fi-fi"
    FRANCE = "fr-fr"
    GERMANY = "de-de"
    GREECE = "gr-el"
    HONG_KONG = "hk-tzh"
    HUNGARY = "hu-hu"
    INDIA = "in-en"
    INDONESIA = "id-id"
    INDONESIA_EN = "id-en"
    IRELAND = "ie-en"
    ISRAEL = "il-he"
    ITALY = "it-it"
    JAPAN = "jp-jp"
    KOREA = "kr-kr"
    LATVIA = "lv-lv"
    LITHUANIA = "lt-lt"
    LATIN_AMERICA = "xl-es"
    MALAYSIA = "my-ms"
    MALAYSIA_EN = "my-en"
    MEXICO = "mx-es"
    NETHERLANDS = "nl-nl"
    NEW_ZEALAND = "nz-en"
    NORWAY = "no-no"
    PERU = "pe-es"
    PHILIPPINES = "ph-en"
    PHILIPPINES_TL = "ph-tl"
    POLAND = "pl-pl"
    PORTUGAL = "pt-pt"
    ROMANIA = "ro-ro"
    RUSSIA = "ru-ru"
    SINGAPORE = "sg-en"
    SLOVAK_REPUBLIC = "sk-sk"
    SLOVENIA = "sl-sl"
    SOUTH_AFRICA = "za-en"
    SPAIN = "es-es"
    SWEDEN = "se-sv"
    SWITZERLAND_DE = "ch-de"
    SWITZERLAND_FR = "ch-fr"
    SWITZERLAND_IT = "ch-it"
    TAIWAN = "tw-tzh"
    THAILAND = "th-th"
    TURKEY = "tr-tr"
    UKRAINE = "ua-uk"
    UNITED_KINGDOM = "uk-en"
    UNITED_STATES = "us-en"
    UNITED_STATES_ES = "ue-es"
    VENEZUELA = "ve-es"
    VIETNAM = "vn-vi"
    NO_REGION = "wt-wt"

    def get_full_name(self):
        return _FULL_NAMES.get(self.value, self.value)
