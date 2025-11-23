import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import PrecisionRecallDisplay, RocCurveDisplay


def plot_confusion_matrix(cm, labels):
    """Plot confusion matrix as heatmap."""
    plt.figure(figsize=(6, 5))
    sns.heatmap(
        cm, annot=True, fmt="d", cmap="Blues", xticklabels=labels, yticklabels=labels
    )
    plt.title("Confusion Matrix")
    plt.tight_layout()


def plot_roc_curve(y_true, y_prob):
    """Plot ROC curve."""
    RocCurveDisplay.from_predictions(y_true, y_prob)
    plt.title("ROC Curve")
    plt.tight_layout()


def plot_precision_recall(y_true, y_prob):
    """Plot Precision-Recall curve."""
    PrecisionRecallDisplay.from_predictions(y_true, y_prob)
    plt.title("Precision-Recall Curve")
    plt.tight_layout()


def plot_pred_vs_true(y_true, y_pred):
    """Scatter: predicted vs true values."""
    plt.figure(figsize=(6, 5))
    sns.scatterplot(x=y_true, y=y_pred)
    plt.xlabel("True Values")
    plt.ylabel("Predicted")
    plt.title("Predicted vs True")
    plt.tight_layout()


def plot_residuals(y_true, y_pred):
    """Plot histogram of residual errors."""
    residuals = y_true - y_pred
    plt.figure(figsize=(6, 5))
    sns.histplot(residuals, kde=True)
    plt.title("Residual Distribution")
    plt.tight_layout()


def plot_forecast_series(y_true, y_pred):
    """Plot time series comparison of actual vs predicted."""
    plt.figure(figsize=(10, 4))
    plt.plot(y_true.index, y_true, label="True")
    plt.plot(y_pred.index, y_pred, label="Predicted")
    plt.legend()
    plt.title("Forecast vs Actual")
    plt.tight_layout()
