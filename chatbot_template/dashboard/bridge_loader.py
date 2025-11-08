from pathlib import Path

import pandas as pd

from chatbot_template.utils.teacher.data_loaders import load_data
from chatbot_template.utils.teacher.enums import DataTypesEnum


def get_default_data(path: str | Path) -> pd.DataFrame:
    """
    Loads in the specified route for the dashboard the desired data using the main
    utils data loader.

    Returns
    -------
    data_loaded : pd.DataFrame
        The data to use as a DataFrame.
    """
    data_path = Path(__file__).resolve().parents[1] / "chatbot_template" / "data" / path
    df = load_data(mode=DataTypesEnum.CSV, path_to_data=data_path)
    df["Valor"] = pd.to_numeric(df["Valor"], errors="coerce")
    df = df.dropna(subset=["Valor"])
    return df


def load_uploaded_data(file: str) -> pd.DataFrame:
    """
    Loads the data if a user has added information as an accepted archive and loads it
    to compute it here.

    Parameters
    ----------
    file : str
        A 'csv' file uploaded by a user in the dashboard.

    Returns
    -------
    user_data_laoded : pd.DataFrame
        The data uploaded by the user loaded in the program as a DataFrame.
    """
    df = pd.read_csv(file)
    df["Valor"] = pd.to_numeric(df["Valor"], errors="coerce")
    df = df.dropna(subset=["Valor"])
    return df
