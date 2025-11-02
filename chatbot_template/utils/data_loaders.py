from pathlib import Path

import pandas as pd
from requests import Session

from chatbot_template.utils.enums import DataTypesEnum


def _load_data_csv(path_to_data: str | Path) -> pd.DataFrame:
    """Load data from a CSV file."""
    return pd.read_csv(path_to_data)


def _load_data_excel(
    path_to_data: str | Path, sheet_to_read: int | None = None
) -> pd.DataFrame:
    """Load data from an Excel file."""
    return (
        pd.read_excel(path_to_data, sheet_name=sheet_to_read)
        if sheet_to_read is not None
        else pd.read_excel(path_to_data)
    )


def _load_from_sql(db: Session, query: str) -> pd.DataFrame:
    """Read data from a SQL database using an open session and query."""
    return pd.read_sql(query, db)


def _load_from_json(path_to_data: str | Path) -> pd.DataFrame:
    """Load data from a JSON file."""
    return pd.read_json(path_to_data)


def load_data(
    mode: DataTypesEnum,
    path_to_data: str | Path | None = None,
    db: Session | None = None,
    query: str | None = None,
    sheet_to_read: int | None = None,
) -> pd.DataFrame:
    """
    Orchestrator to load data depending on the DataTypesEnum value.

    Parameters
    ----------
    mode : DataTypesEnum
        The accepted type to read.
    path_to_data : str | Path | None
        Path to the file (required for file-based loaders).
    db : Session | None
        Database session (required for SQL mode).
    query : str | None
        SQL query to execute (required for SQL mode).
    sheet_to_read : int | None
        Sheet index for Excel files (optional).

    Returns
    -------
    data : pd.DataFrame
        The processed data.
    """
    if not isinstance(mode, DataTypesEnum):
        raise TypeError(
            f"mode must be an instance of DataTypesEnum, not {type(mode).__name__}."
        )

    match mode:
        case DataTypesEnum.CSV:
            if path_to_data is None:
                raise ValueError("path_to_data must be provided for CSV mode.")
            return _load_data_csv(path_to_data)

        case DataTypesEnum.EXCEL:
            if path_to_data is None:
                raise ValueError("path_to_data must be provided for EXCEL mode.")
            return _load_data_excel(path_to_data, sheet_to_read=sheet_to_read)

        case DataTypesEnum.JSON:
            if path_to_data is None:
                raise ValueError("path_to_data must be provided for JSON mode.")
            return _load_from_json(path_to_data)

        case DataTypesEnum.SQL:
            if db is None or query is None:
                raise ValueError(
                    "Both db (Session) and query must be provided for SQL mode."
                )
            return _load_from_sql(db, query)

        case _:
            raise NotImplementedError(f"Loading for mode '{mode}' is not implemented.")
