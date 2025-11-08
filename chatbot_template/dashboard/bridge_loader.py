from io import BytesIO, StringIO
from pathlib import Path
from typing import IO, cast

import pandas as pd

from chatbot_template.utils.teacher.data_loaders import load_data
from chatbot_template.utils.teacher.enums import DataTypesEnum


def load_generic_data(
    mode: DataTypesEnum,
    path: str | Path | IO[bytes] | None = None,
    **kwargs,
) -> pd.DataFrame:
    """
    Loads generic data using the system from the main utils library to adapt on
    dashboard.

    Parameters
    ----------
    mode : DataTypesEnum
        The different types of data that can be loaded on the system and the desired
        for the actual study.
    path : str | Path | None
        The path to the data to use. Default = None.
    **kwargs
        More arguments desired to send on load_data.

    Returns
    -------
    dash_loaded_data : pd.DataFrame
        The loaded data for the dashboard.
    """
    if isinstance(path, BytesIO | StringIO):
        if mode == DataTypesEnum.CSV:
            return pd.read_csv(path)
        elif mode == DataTypesEnum.EXCEL:
            return pd.read_excel(path)
        elif mode == DataTypesEnum.JSON:
            return pd.read_json(path)
        else:
            raise ValueError(f"Unsupported mode for in-memory buffer: {mode}")

    path_cast = cast(str | Path | None, path)
    dash_loaded_data = load_data(mode=mode, path_to_data=path_cast, **kwargs)
    return dash_loaded_data


def clean_dataframe(dash_loaded_data: pd.DataFrame) -> pd.DataFrame:
    """
    Normalizes the dataframe without assuming a specific structure.

    Parameters
    ----------
    dash_loaded_data : pd.DataFrame
        The data to clean.

    Returns
    -------
    cleaned_dash_loaded_data : pd.DataFrame
        The cleaned data.
    """
    cleaned_dash_loaded_data = dash_loaded_data.copy()
    for col in cleaned_dash_loaded_data.select_dtypes(include="object").columns:
        cleaned_dash_loaded_data[col] = (
            cleaned_dash_loaded_data[col].astype(str).str.strip()
        )
    return cleaned_dash_loaded_data
