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
