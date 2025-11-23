from typing import Any

import numpy as np
import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    mean_absolute_error,
    mean_squared_error,
    precision_score,
    r2_score,
    recall_score,
    roc_auc_score,
)

# =========================================================
#   CLASSIFICATION METRICS
# =========================================================


def evaluate_classification(
    y_true: pd.Series,
    y_pred: pd.Series,
    y_prob: pd.Series | None = None,
    average: str = "weighted",
) -> dict[str, Any]:
    """
    Evaluate a classification model.

    Parameters
    ----------
    y_true : pd.Series
        True labels.
    y_pred : pd.Series
        Predicted labels.
    y_prob : pd.Series, optional
        Predicted probabilities (required for ROC-AUC).
    average : str
        Averaging method for multi-class classification.
        Options: 'micro', 'macro', 'weighted'.

    Returns
    -------
    dict
        Dictionary with evaluation metrics.
    """
    metrics = {
        "accuracy": accuracy_score(y_true, y_pred),
        "precision": precision_score(y_true, y_pred, average=average, zero_division=0),
        "recall": recall_score(y_true, y_pred, average=average, zero_division=0),
        "f1_score": f1_score(y_true, y_pred, average=average, zero_division=0),
        "confusion_matrix": confusion_matrix(y_true, y_pred),
        "classification_report": classification_report(
            y_true, y_pred, output_dict=False
        ),
    }

    # ROC-AUC only valid for binary or one-vs-rest
    if y_prob is not None:
        try:
            metrics["roc_auc"] = roc_auc_score(y_true, y_prob, multi_class="ovr")
        except Exception:
            metrics["roc_auc"] = None

    return metrics


# =========================================================
#   REGRESSION METRICS
# =========================================================


def evaluate_regression(y_true: pd.Series, y_pred: pd.Series) -> dict[str, float]:
    """
    Evaluate a regression model.

    Parameters
    ----------
    y_true : pd.Series
        True regression values.
    y_pred : pd.Series
        Predicted regression values.

    Returns
    -------
    dict
        Dictionary with regression metrics.
    """
    mae = mean_absolute_error(y_true, y_pred)
    mse = mean_squared_error(y_true, y_pred)
    rmse = np.sqrt(mse)

    # avoid division by zero in MAPE
    mape = np.mean(np.abs((y_true - y_pred) / np.maximum(y_true, 1e-9))) * 100

    return {
        "MAE": mae,
        "MSE": mse,
        "RMSE": rmse,
        "R2": r2_score(y_true, y_pred),
        "MAPE (%)": mape,
    }
