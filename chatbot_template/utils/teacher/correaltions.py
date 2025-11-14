import pandas as pd
import seaborn as sns
from matplotlib import pyplot as plt
from scipy.stats import kendalltau, pearsonr, spearmanr

from chatbot_template.utils.teacher.enums import CorrelationsEnums


def correlation_matrix(
    data: pd.DataFrame,
    metodo: CorrelationsEnums = CorrelationsEnums.PEARSON,
    columnas: list[str] | None = None,
    heatmap: bool = True,
) -> pd.DataFrame:
    """
    Compute a correlation matrix for the given DataFrame.

    Parameters
    ----------
    df : pd.DataFrame
        Input dataframe.
    metodo : CorrelationMethods
        Correlation method to compute (PEARSON, SPEARMAN, KENDALL).
    columnas : list of str, optional
        List of columns to include. If None, all numeric columns are used.
    heatmap : bool
        If True, a heatmap is displayed.

    Returns
    -------
    pd.DataFrame
        The correlation matrix for the selected columns.
    """
    if columnas is not None:
        data = data[columnas]

    corr = data.corr(method=metodo.value)

    if heatmap:
        plt.figure(figsize=(7, 5))
        sns.heatmap(corr, cmap="coolwarm", annot=True, fmt=".2f")
        plt.title(f"Correlation Matrix ({metodo.value})")
        plt.tight_layout()
        plt.show()

    return corr


def correlation_between(
    data: pd.DataFrame,
    col1: str,
    col2: str,
    metodo: CorrelationsEnums = CorrelationsEnums.PEARSON,
    plot: bool = True,
) -> float:
    """
    Compute the correlation between two columns.

    Parameters
    ----------
    df : pd.DataFrame
        Input dataframe.
    col1 : str
        First column name.
    col2 : str
        Second column name.
    metodo : CorrelationMethods
        Correlation method to compute (PEARSON, SPEARMAN, KENDALL).
    plot : bool
        If True, a scatter plot is displayed.

    Returns
    -------
    float
        Correlation value between col1 and col2.
    """
    corr = data[[col1, col2]].corr(method=metodo.value).iloc[0, 1]

    if plot:
        plt.figure(figsize=(6, 4))
        plt.scatter(data[col1], data[col2])
        plt.xlabel(col1)
        plt.ylabel(col2)
        plt.title(f"{metodo.value.capitalize()} Correlation: {corr:.3f}")
        plt.grid(True)
        plt.tight_layout()
        plt.show()

    return corr


def correlation_pvalue_matrix(
    df: pd.DataFrame, method: CorrelationsEnums = CorrelationsEnums.PEARSON
) -> pd.DataFrame:
    """
    Computes a matrix of p-values for pairwise correlations.

    Parameters
    ----------
    df : pd.DataFrame
        Numerical dataframe.
    method : CorrelationMethods
        Correlation method.

    Returns
    -------
    pd.DataFrame
        Matrix of p-values.
    """
    cols = df.columns
    pvals = pd.DataFrame(index=cols, columns=cols, dtype=float)

    for c1 in cols:
        for c2 in cols:
            if method is CorrelationsEnums.PEARSON:
                _, p = pearsonr(df[c1], df[c2])
            elif method is CorrelationsEnums.SPEARMAN:
                _, p = spearmanr(df[c1], df[c2])
            else:
                _, p = kendalltau(df[c1], df[c2])
            pvals.loc[c1, c2] = p

    return pvals


def correlation_with_pvalue(
    df: pd.DataFrame,
    col1: str,
    col2: str,
    method: CorrelationsEnums = CorrelationsEnums.PEARSON,
) -> tuple[float, float]:
    """
    Compute both correlation and p-value between two columns.

    Parameters
    ----------
    df : pd.DataFrame
        Input DataFrame.
    col1 : str
        First numeric column.
    col2 : str
        Second numeric column.
    method : CorrelationMethods
        Correlation method to use (PEARSON, SPEARMAN, KENDALL).

    Returns
    -------
    tuple[float, float]
        (correlation_value, p_value)
    """
    x = df[col1]
    y = df[col2]

    if method is CorrelationsEnums.PEARSON:
        corr, p = pearsonr(x, y)
    elif method is CorrelationsEnums.SPEARMAN:
        corr, p = spearmanr(x, y)
    else:  # KENDALL
        corr, p = kendalltau(x, y)

    return corr, p
