from typing import Any

import pandas as pd

from .registry import PLOT_TYPES


def generate_plot(
    data_to_plot: pd.DataFrame, plot_type: str, x_col: str, y_col: str | None = None
) -> Any:
    """
    Generates a dynamic plot without assuming the different names of columns.

    Parameters
    ----------
    data_to_plot : pd.DataFrame
        The data to plot on the graphics.
    plot_type : str
        The type of plot.
    x_col : str
        The information on the x-axis.
    y_col : str | None
        The information on the y-axis.

    Returns
    -------
    plot_fn : Any
        The plot we are generating.
    """
    if plot_type not in PLOT_TYPES:
        raise ValueError(f"Unsupported plot type: {plot_type}")
    plot_fn = PLOT_TYPES[plot_type]
    return plot_fn(data_to_plot, x_col, y_col)
