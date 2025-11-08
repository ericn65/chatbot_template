import pandas as pd
import plotly.express as px


def _safe_aggregate(
    df: pd.DataFrame, category_col: str, value_col: str | None
) -> tuple:
    """
    Safe way to aggregate data in charts in case plots must missmatch information.

    Parameters
    ----------
    df : pd.DataFrame
        Generic data to safely aggregate.
    category_col : str
        The desired category to plot.
    value_col : str | None
        The value to add.

    Returns
    -------
    grouped, value_col : tuple
        A tuple indicating the grouped data + the value of the column.
    """
    if value_col and value_col in df.columns:
        grouped = df.groupby(category_col)[value_col].sum().reset_index()
    else:
        grouped = df[category_col].value_counts().reset_index()
        grouped.columns = [category_col, "count"]
        value_col = "count"
    return grouped, value_col


PLOT_TYPES = {
    "Bar": lambda df, x, y: px.bar(df, x=x, y=y, title=f"{y} by {x}", color=x),
    "Line": lambda df, x, y: px.line(df, x=x, y=y, title=f"{y} over {x}", markers=True),
    "Scatter": lambda df, x, y: px.scatter(df, x=x, y=y, title=f"{y} vs {x}", color=x),
    "Box": lambda df, x, y: px.box(
        df, x=x, y=y, title=f"Distribution of {y} by {x}", color=x
    ),
    "Histogram": lambda df, x, _: px.histogram(
        df, x=x, title=f"Distribution of {x}", nbins=30
    ),
    "Pie": lambda df, x, y: (
        lambda gdf, vcol: px.pie(
            gdf,
            names=x,
            values=vcol,
            title=f"Proporción de {vcol} por {x}",
            hole=0.3,  # 0.0 = pie, 0.3 = donut
        )
    )(*_safe_aggregate(df, x, y)),
}
