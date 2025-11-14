from enum import Enum, StrEnum, auto


class WorkflowError(StrEnum):
    """Types of error that could appear in the workflow."""

    INVALID_USER = auto()
    INVALID_PASSWORD = auto()
    ANSWER_NON_EXITENT = auto()
    NON_EXISTENT_PARAMETER = auto()
    LOGIN_ERROR = auto()
    INVALID_NUMBER = auto()
    NOT_AUDIO = auto()
    UNKNOWN_STATE = auto()
    AUDIO_TOO_SHORT = auto()


class AudioFeatureType(Enum):
    """Supported audio feature representations."""

    RAW = auto()
    STFT = auto()
    MEL = auto()
    MFCC = auto()


class TextFeatureType(Enum):
    """Available text feature extraction modes."""

    BASIC = auto()
    LEXICAL = auto()
    LIWC_SIM = auto()


class DataTypesEnum(Enum):
    """Available data types to extract."""

    CSV = auto()
    JSON = auto()
    SQL = auto()
    EXCEL = auto()
    OTHER = auto()


class CountryEnums(Enum):
    """Available countries in our data."""

    SPAIN = 0
    ARGENTINA = 1
    ITALY = 2
    MOROCCO = 3
    ECUADOR = 4
    ROMANIA = 5
    UK = 6
    GERMAN = 7
    FRANCE = 8
    ALGERIA = 9
    SENEGAL = 10
    USA = 11
    BOLIVIA = 12
    PERU = 13
    CHILE = 14
    GREECE = 15
    RUSSIA = 16
    SWEEDEN = 17
    ISRAEL = 18


class CorrelationsEnums(StrEnum):
    """Class to deal with different correlations."""

    PEARSON = "pearson"
    SPEARMAN = "spearman"
    KENDALL = "kendall"
