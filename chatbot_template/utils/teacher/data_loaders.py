from pathlib import Path
from typing import Any

import pandas as pd
from requests import Session

from chatbot_template.utils.teacher.enums import DataTypesEnum


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


def tag_df_with_metadata(
    data: pd.DataFrame,
    new_data_name: str,
    new_data: Any,
) -> pd.DataFrame:
    """
    Tag an existing DataFrame (already loaded) with year and optional metadata.

    Parameters
    ----------
    data : pd.DataFrame
        The dataframe to tag.
    new_data_name : str
        The name of the metadata to mix and add information. Name of a column.
    new_data : Any
        The specified generic metadata for one column common between same year metadata.
        eg. new_data = year : int = 2024 if new_data_name: str = year.

    Returns
    -------
    df : pd.DataFrame
        Tagged dataframe.
    """
    df_copy = data.copy()
    df_copy[new_data_name] = new_data

    return df_copy


def safe_concat_dataframes(
    dataframes: list[pd.DataFrame],
    reset_index: bool = True,
) -> pd.DataFrame:
    """
    Safely concatenate multiple DataFrames, ensuring identical columns.

    Parameters
    ----------
    dataframes : list[pd.DataFrame]
        List of already computed DataFrames to concatenate.
    reset_index : bool, optional
        Whether to reset index after concatenation. Default = True.

    Returns
    -------
    combined_df : pd.DataFrame
        Concatenated DataFrame.

    Raises
    ------
    ValueError
        If any DataFrame has different columns (names or order).
    TypeError
        If a non-DataFrame object is passed in the list.
    """
    if not dataframes:
        raise ValueError("No DataFrames provided for concatenation.")

    if not all(isinstance(df, pd.DataFrame) for df in dataframes):
        raise TypeError("All elements in 'dataframes' must be pandas DataFrames.")

    reference_cols = list(dataframes[0].columns)

    for i, df in enumerate(dataframes[1:], start=2):
        if list(df.columns) != reference_cols:
            raise ValueError(
                f"DataFrame #{i} has different columns.\n"
                f"Expected: {reference_cols}\n"
                f"Got: {list(df.columns)}"
            )

    combined_df = pd.concat(dataframes, ignore_index=reset_index)
    if reset_index:
        combined_df.reset_index(drop=True, inplace=True)  # noqa: PD002

    return combined_df


def save_dataframe_to_csv(
    data: pd.DataFrame, output_path: str | Path, index: bool = False
) -> Path:
    """
    Save the combined dataframe to CSV.

    Parameters
    ----------
    df : pd.DataFrame
        The dataframe to save.
    output_path : str | Path
        Destination CSV file path.
    index : bool, optional
        Whether to include the index in the output file. Default = False.

    Returns
    -------
    output_path : Path
        Path to the saved file.
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    data.to_csv(output_path, index=index)
    return output_path
