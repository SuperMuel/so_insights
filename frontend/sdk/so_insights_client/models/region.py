from enum import Enum


class Region(str, Enum):
    AR_ES = "ar-es"
    AT_DE = "at-de"
    AU_EN = "au-en"
    BE_FR = "be-fr"
    BE_NL = "be-nl"
    BG_BG = "bg-bg"
    BR_PT = "br-pt"
    CA_EN = "ca-en"
    CA_FR = "ca-fr"
    CH_DE = "ch-de"
    CH_FR = "ch-fr"
    CH_IT = "ch-it"
    CL_ES = "cl-es"
    CN_ZH = "cn-zh"
    CO_ES = "co-es"
    CT_CA = "ct-ca"
    CZ_CS = "cz-cs"
    DE_DE = "de-de"
    DK_DA = "dk-da"
    EE_ET = "ee-et"
    ES_ES = "es-es"
    FI_FI = "fi-fi"
    FR_FR = "fr-fr"
    GR_EL = "gr-el"
    HK_TZH = "hk-tzh"
    HR_HR = "hr-hr"
    HU_HU = "hu-hu"
    ID_EN = "id-en"
    ID_ID = "id-id"
    IE_EN = "ie-en"
    IL_HE = "il-he"
    IN_EN = "in-en"
    IT_IT = "it-it"
    JP_JP = "jp-jp"
    KR_KR = "kr-kr"
    LT_LT = "lt-lt"
    LV_LV = "lv-lv"
    MX_ES = "mx-es"
    MY_EN = "my-en"
    MY_MS = "my-ms"
    NL_NL = "nl-nl"
    NO_NO = "no-no"
    NZ_EN = "nz-en"
    PE_ES = "pe-es"
    PH_EN = "ph-en"
    PH_TL = "ph-tl"
    PL_PL = "pl-pl"
    PT_PT = "pt-pt"
    RO_RO = "ro-ro"
    RU_RU = "ru-ru"
    SE_SV = "se-sv"
    SG_EN = "sg-en"
    SK_SK = "sk-sk"
    SL_SL = "sl-sl"
    TH_TH = "th-th"
    TR_TR = "tr-tr"
    TW_TZH = "tw-tzh"
    UA_UK = "ua-uk"
    UE_ES = "ue-es"
    UK_EN = "uk-en"
    US_EN = "us-en"
    VE_ES = "ve-es"
    VN_VI = "vn-vi"
    WT_WT = "wt-wt"
    XA_AR = "xa-ar"
    XA_EN = "xa-en"
    XL_ES = "xl-es"
    ZA_EN = "za-en"

    def __str__(self) -> str:
        return str(self.value)