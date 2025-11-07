from __future__ import annotations

from typing import Any, Literal

import numpy as np
import pandas as pd


class DataAggregator:
    """
    Utility class for generic aggregation, filtering, and statistical summaries.
    Works with any DataFrame schema.
    """

    def __init__(self, data: pd.DataFrame):
        if not isinstance(data, pd.DataFrame):
            raise TypeError("data must be a pandas DataFrame.")
        self.data = data.copy()

    # ------------------------------------------------------------------
    # GENERIC STATISTICS
    # ------------------------------------------------------------------
    def get_numeric_summary(self) -> pd.DataFrame:
        """Return a summary with mean, median, std, min, max for all numeric columns."""
        numeric_df = self.data.select_dtypes(include="number")
        if numeric_df.empty:
            raise ValueError("No numeric columns found in the DataFrame.")
        return numeric_df.agg(["mean", "median", "std", "min", "max"]).T

    # ------------------------------------------------------------------
    # GROUPING
    # ------------------------------------------------------------------
    def group_by_and_aggregate(
        self,
        group_col: str,
        agg_map: dict[str, list[str]] | None = None,
    ) -> pd.DataFrame:
        """
        Group the data by a column and perform aggregations.

        Parameters
        ----------
        group_col : str
            The column to group by.
        agg_map : dict[str, list[str]] | None
            Mapping of column -> list of aggregation functions
            (e.g., {"sales": ["mean", "sum"]})

        Returns
        -------
        pd.DataFrame
            Aggregated results.
        """
        if group_col not in self.data.columns:
            raise ValueError(f"Column '{group_col}' not found in DataFrame.")
        if agg_map is None:
            # Default: all numeric columns
            numeric_cols = self.data.select_dtypes(include="number").columns
            agg_map = {
                col: ["mean", "median", "std", "min", "max"] for col in numeric_cols
            }

        grouped = self.data.groupby(group_col).agg(agg_map)
        grouped.columns = ["_".join(col).strip() for col in grouped.columns.to_numpy()]
        grouped = grouped.reset_index()
        return grouped

    # ------------------------------------------------------------------
    # FILTERING
    # ------------------------------------------------------------------
    def filter_by_condition(
        self, column: str, condition: Literal["==", ">", "<", ">=", "<="], value: Any
    ) -> pd.DataFrame:
        """
        Filter the dataframe by a condition on a column.

        Parameters
        ----------
        column : str
            The column to filter.
        condition : str
            Comparison operator as string.
        value : Any
            The value to compare against.

        Returns
        -------
        pd.DataFrame
            Filtered DataFrame.
        """
        if column not in self.data.columns:
            raise ValueError(f"Column '{column}' not found in DataFrame.")

        match condition:
            case "==":
                return self.data[self.data[column] == value]
            case ">":
                return self.data[self.data[column] > value]
            case "<":
                return self.data[self.data[column] < value]
            case ">=":
                return self.data[self.data[column] >= value]
            case "<=":
                return self.data[self.data[column] <= value]
            case _:
                raise ValueError(f"Unsupported condition '{condition}'.")

    # ------------------------------------------------------------------
    # SPLITTING
    # ------------------------------------------------------------------
    def split_by_column(self, column: str) -> dict[Any, pd.DataFrame]:
        """
        Split the DataFrame into multiple DataFrames based on unique values in a column.

        Parameters
        ----------
        column : str
            The column to split by.

        Returns
        -------
        dict[Any, pd.DataFrame]
            Dictionary mapping unique values -> sub-DataFrames.
        """
        if column not in self.data.columns:
            raise ValueError(f"Column '{column}' not found in DataFrame.")

        return {value: df for value, df in self.data.groupby(column)}

    # ------------------------------------------------------------------
    # OUTLIER DETECTION
    # ------------------------------------------------------------------
    def detect_outliers(self, column: str, z_threshold: float = 3.0) -> pd.DataFrame:
        """
        Detect rows with outliers in a numeric column using Z-score.

        Parameters
        ----------
        column : str
            Numeric column to check.
        z_threshold : float
            Z-score threshold to mark as outlier.

        Returns
        -------
        pd.DataFrame
            Subset of rows considered outliers.
        """
        if column not in self.data.columns:
            raise ValueError(f"Column '{column}' not found in DataFrame.")
        if not np.issubdtype(self.data[column].dtype, np.number):
            raise TypeError(f"Column '{column}' must be numeric.")

        z_scores = np.abs(
            (self.data[column] - self.data[column].mean())
            / self.data[column].std(ddof=0)
        )
        return self.data[z_scores > z_threshold]
