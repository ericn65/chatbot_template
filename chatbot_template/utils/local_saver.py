import json
import os
from datetime import datetime


def save_response(
    user_id: str, phase: str, step: int, response: str, audio_path: str | None = None
) -> dict:
    """
    Save the user's response to a local list.

    Parameters
    ----------
    user_id : str
        The unique identifier of the user.
    phase : str
        The current phase of the workflow.
    step : int
        The current step in the phase.
    response : str
        The user's response message.
    audio_path : str | None
        The local path to the audio file if applicable.

    Returns
    -------
    list[dict]
        A list of saved response records.
    """
    record = {
        "user_id": user_id,
        "phase": phase,
        "step": step,
        "response": response,
        "audio_path": audio_path,
    }

    return record


def save_response_to_file(user_id: str, record: dict):
    """
    Saves the user's response record to a local JSON file.

    Parameters
    ----------
    user_id : str
        The unique identifier of the user.
    record : dict
        The response record to save.

    Returns
    -------
    None
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    filename = f"/temp/{user_id}_{timestamp}.json"
    if os.path.exists(filename):
        with open(filename, encoding="utf-8") as f:
            data = json.load(f)
    else:
        data = []
    data.append(record)
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
