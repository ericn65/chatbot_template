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
