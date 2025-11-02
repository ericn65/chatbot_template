from enum import Enum
from typing import Any

import pandas as pd


def _get_column_info(df: pd.DataFrame) -> dict[str, str]:
    """
    Return column names and their data types as a dictionary.

    Parameters
    ----------
    df : pd.DataFrame
        The dataframe to analyse.

    Returns
    -------
    column_info : dict[str, str]
        A dictionary mapping column names to their data types.
    """
    return {col: str(dtype) for col, dtype in df.dtypes.items()}


def _get_basic_stats(df: pd.DataFrame) -> dict[str, Any]:
    """
    Return basic statistics about the dataframe.

    Parameters
    ----------
    df : pd.DataFrame
        The dataframe to analyse.

    Returns
    -------
    stats : dict[str, Any]
        A dictionary with basic information about the dataset.
    """
    return {
        "n_rows": len(df),
        "n_columns": len(df.columns),
        "missing_values": int(df.isna().sum().sum()),
        "duplicated_rows": int(df.duplicated().sum()),
        "memory_usage_MB": round(df.memory_usage(deep=True).sum() / (1024**2), 2),
    }


def _get_value_counts(
    df: pd.DataFrame, max_unique: int = 10
) -> dict[str, dict[Any, int]]:
    """
    Return value counts for categorical or low-cardinality columns.

    Parameters
    ----------
    df : pd.DataFrame
        The dataframe to analyse.
    max_unique : int
        Maximum number of unique values to consider as 'low-cardinality'.

    Returns
    -------
    value_counts : dict[str, dict[Any, int]]
        Dictionary with columns and their value counts (only if few unique values).
    """
    value_counts: dict[str, dict[Any, int]] = {}
    for col in df.columns:
        unique_vals = df[col].nunique(dropna=True)
        if unique_vals <= max_unique:
            counts = df[col].value_counts(dropna=False).to_dict()
            value_counts[col] = counts
    return value_counts


def _get_numeric_summary(df: pd.DataFrame) -> dict[str, dict[str, float]]:
    """
    Return basic numeric summaries (mean, std, min, max) for numeric columns.

    Parameters
    ----------
    df : pd.DataFrame
        The dataframe to analyse.

    Returns
    -------
    summary : dict[str, dict[str, float]]
        A dictionary mapping numeric columns to their summary statistics.
    """
    numeric_summary: dict[str, dict[str, float]] = {}
    for col in df.select_dtypes(include="number").columns:
        desc = df[col].describe()
        numeric_summary[col] = {
            "mean": float(desc["mean"]),
            "std": float(desc["std"]),
            "min": float(desc["min"]),
            "max": float(desc["max"]),
        }
    return numeric_summary


def analyse_data(df: pd.DataFrame, max_unique: int = 10) -> dict[str, Any]:
    """
    Orchestrator that runs quick data analysis and returns structured info.

    Parameters
    ----------
    df : pd.DataFrame
        The dataframe to analyse.
    max_unique : int, optional
        Maximum number of unique values for which value counts are shown.

    Returns
    -------
    analysis : dict[str, Any]
        Dictionary containing column info, stats, and summaries.
    """
    return {
        "basic_stats": _get_basic_stats(df),
        "column_info": _get_column_info(df),
        "numeric_summary": _get_numeric_summary(df),
        "value_counts": _get_value_counts(df, max_unique=max_unique),
    }


def _enum_to_dict(enum_cls: type[Enum]) -> dict[str, Any]:
    """
    Convert an Enum class into a mapping dictionary {name.lower(): value}.

    Parameters
    ----------
    enum_cls : Type[Enum]
        The Enum class to convert.

    Returns
    -------
    mapping : dict[str, Any]
        Lowercased mapping of Enum names to their values.
    """
    return {member.name.lower(): member.value for member in enum_cls}


def _map_column_to_enum(
    df: pd.DataFrame,
    column: str,
    enum_cls: type[Enum],
    new_column: str | None = None,
    case_insensitive: bool = True,
    default_value: Any | None = None,
) -> pd.DataFrame:
    """
    Map categorical string column values to numeric or alias values from an Enum.

    Parameters
    ----------
    df : pd.DataFrame
        Input dataframe.
    column : str
        Name of the column to map.
    enum_cls : Type[Enum]
        Enum containing possible mappings.
    new_column : str, optional
        Name for the new mapped column. If None, overwrites original column.
    case_insensitive : bool, optional
        Whether to lower-case string values before mapping. Default = True.
    default_value : Any, optional
        Value to assign when a mapping is not found. Default = None.

    Returns
    -------
    df : pd.DataFrame
        DataFrame with the column mapped.
    """
    if column not in df.columns:
        raise ValueError(f"Column '{column}' not found in dataframe.")

    mapping = _enum_to_dict(enum_cls)

    def mapper(x: Any) -> Any:
        if isinstance(x, str):
            key = x.lower().strip() if case_insensitive else x.strip()
            return mapping.get(key, default_value)
        return mapping.get(str(x).lower(), default_value)

    mapped = df[column].map(mapper)

    if new_column:
        df[new_column] = mapped
    else:
        df[column] = mapped

    return df


def _inverse_map_enum_to_labels(
    df: pd.DataFrame, column: str, enum_cls: type[Enum], new_column: str | None = None
) -> pd.DataFrame:
    """
    Convert numeric Enum values back to human-readable labels.

    Parameters
    ----------
    df : pd.DataFrame
        Input dataframe.
    column : str
        Column containing Enum numeric codes.
    enum_cls : Type[Enum]
        Enum used for decoding.
    new_column : str, optional
        Name for decoded column (defaults to overwriting input column).

    Returns
    -------
    df : pd.DataFrame
        DataFrame with decoded column.
    """
    reverse_map = {v.value: v.name.capitalize() for v in enum_cls}
    decoded = df[column].map(reverse_map)

    if new_column:
        df[new_column] = decoded
    else:
        df[column] = decoded

    return df


def encode_column(
    df: pd.DataFrame,
    column: str,
    enum_cls: type[Enum],
    new_column: str | None = None,
    default_value: Any | None = None,
) -> pd.DataFrame:
    """
    Orchestrator to encode a column using an Enum.

    Parameters
    ----------
    df : pd.DataFrame
        The dataframe to process.
    column : str
        The column name to encode.
    enum_cls : Type[Enum]
        Enum that defines valid values.
    new_column : str, optional
        Name for the encoded column.
    default_value : Any, optional
        Value for unmapped categories.

    Returns
    -------
    df : pd.DataFrame
        Dataframe with encoded column added or replaced.
    """
    return _map_column_to_enum(
        df=df,
        column=column,
        enum_cls=enum_cls,
        new_column=new_column,
        default_value=default_value,
    )


def decode_column(
    df: pd.DataFrame, column: str, enum_cls: type[Enum], new_column: str | None = None
) -> pd.DataFrame:
    """
    Orchestrator to decode a column of Enum values back to human-readable labels.

    Parameters
    ----------
    df : pd.DataFrame
        The dataframe to analyse.
    column : str
        The desired column to understand.
    enum_cls : type[Enum]
        The ENUM to codify.
    new_column : str, Optional
        The new column to add.

    Returns
    -------
    data : pd.DataFrame
        The data after decoding an enum.
    """
    return _inverse_map_enum_to_labels(df, column, enum_cls, new_column)
