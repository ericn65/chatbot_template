from enum import StrEnum, auto


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
