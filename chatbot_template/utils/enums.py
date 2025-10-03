from enum import StrEnum, auto


class WorkflowError(StrEnum):
    """Types of error that could appear in the workflow."""

    LANG_NOT_SUPPORTED = auto()
    INVALID_NUMBER = auto()
    NOT_AUDIO = auto()
    UNKNOWNN_STATE = auto()
    AUDIO_TOO_SHORT = auto()
