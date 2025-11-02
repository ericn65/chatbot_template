import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


class DataVisualizer:
    """
    Generic data visualizer capable of plotting different types
    of charts depending on data types and user input.
    """

    def __init__(self, data: pd.DataFrame):
        if not isinstance(data, pd.DataFrame):
            raise TypeError("data must be a pandas DataFrame.")
        self.data = data.copy()

    # -------------------------------------------
    # 🔹 Basic distribution plot
    # -------------------------------------------
    def plot_distribution(self, column: str, bins: int = 20):
        """
        Plots the distribution of our data.

        Parameters
        ----------
        column : str
            The columns to get and anayse.
        bins : int
            The number of points we want to add as distributions.
        """
        if column not in self.data.columns:
            raise ValueError(f"Column '{column}' not found.")
        if not pd.api.types.is_numeric_dtype(self.data[column]):
            raise TypeError(f"Column '{column}' must be numeric.")
        plt.figure(figsize=(7, 5))
        sns.histplot(self.data[column], bins=bins, kde=True)
        plt.title(f"Distribution of {column}")
        plt.xlabel(column)
        plt.ylabel("Frequency")
        plt.tight_layout()
        plt.show()

    # -------------------------------------------
    # 🔹 Boxplot by category
    # -------------------------------------------
    def plot_boxplot(self, category_col: str, numeric_col: str):
        """
        Plots a boxplot for different stuff.

        Parameters
        ----------
        category_cols : str
            The different categories for the columns.
        numeric_col : str
            The different numerics.
        """
        if (
            category_col not in self.data.columns
            or numeric_col not in self.data.columns
        ):
            raise ValueError("Invalid columns provided.")
        plt.figure(figsize=(8, 5))
        sns.boxplot(x=self.data[category_col], y=self.data[numeric_col])
        plt.title(f"{numeric_col} by {category_col}")
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()

    # -------------------------------------------
    # 🔹 Correlation matrix
    # -------------------------------------------
    def plot_correlation_matrix(self):
        """Plots correlation matrices."""
        numeric_df = self.data.select_dtypes(include="number")
        if numeric_df.empty:
            raise ValueError("No numeric columns available for correlation.")
        corr = numeric_df.corr()
        plt.figure(figsize=(8, 6))
        sns.heatmap(corr, annot=True, cmap="coolwarm", fmt=".2f")
        plt.title("Correlation Matrix")
        plt.tight_layout()
        plt.show()

    # -------------------------------------------
    # 🔹 Scatter plot between two numeric columns
    # -------------------------------------------
    def plot_scatter(self, x_col: str, y_col: str, hue: str | None = None):
        """
        Plots scatter maps for different data.

        Parameters
        ----------
        x_col : str
            The name of the x-axis columns.
        y_col : str
            The name of the y-axis columns.
        hue : str, Optional
            The hue. Default = None.
        """
        if x_col not in self.data.columns or y_col not in self.data.columns:
            raise ValueError("Invalid columns provided.")
        plt.figure(figsize=(7, 5))
        sns.scatterplot(data=self.data, x=x_col, y=y_col, hue=hue)
        plt.title(f"{y_col} vs {x_col}")
        plt.tight_layout()
        plt.show()

    # -------------------------------------------
    # 🔹 Bar chart for categories
    # -------------------------------------------
    def plot_by_category(self, category_col: str, numeric_col: str):
        """
        Plots by categories.

        Parameters
        ----------
        category_col : str
            The type of category column.
        numeric_col : str
            The numeric columns.
        """
        if (
            category_col not in self.data.columns
            or numeric_col not in self.data.columns
        ):
            raise ValueError("Invalid columns provided.")
        grouped = (
            self.data.groupby(category_col)[numeric_col]
            .mean()
            .sort_values(ascending=False)
        )
        plt.figure(figsize=(8, 5))
        sns.barplot(x=grouped.index, y=grouped.values)
        plt.title(f"Average {numeric_col} by {category_col}")
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()

    # -------------------------------------------
    # 🔹 Time series line plot
    # -------------------------------------------
    def plot_time_series(self, date_col: str, value_col: str, freq: str | None = None):
        """
        Plots a time series.

        Parameters
        ----------
        date_col : str
            Any kind of data with columns.
        value_col : str
            The value of the columns.
        freq : str | None
            The frequency of the value on a column.
        """
        if date_col not in self.data.columns or value_col not in self.data.columns:
            raise ValueError("Invalid columns provided.")
        data = self.data.copy()
        data[date_col] = pd.to_datetime(data[date_col], errors="coerce")
        if freq:
            data = data.resample(freq, on=date_col)[value_col].mean().reset_index()
        plt.figure(figsize=(9, 5))
        sns.lineplot(data=data, x=date_col, y=value_col)
        plt.title(f"Time Series of {value_col} over {date_col}")
        plt.tight_layout()
        plt.show()

    def auto_visualize(self):
        """Decides which one to use before anything else."""
        for col in self.data.columns:
            if pd.api.types.is_numeric_dtype(self.data[col]):
                self.plot_distribution(col)
            elif pd.api.types.is_datetime64_any_dtype(self.data[col]):
                self.plot_time_series(
                    col, self.data.select_dtypes(include="number").columns[0]
                )
