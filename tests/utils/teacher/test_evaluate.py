import pandas as pd

from chatbot_template.utils.teacher.evaluate import (
    evaluate_classification,
    evaluate_regression,
)


def test_regression_evaluation():
    """Test the regression evaluation."""
    y_true = pd.Series([1, 2, 3])
    y_pred = pd.Series([1, 2, 3])
    metrics = evaluate_regression(y_true, y_pred)
    assert metrics["MAE"] == 0
    assert metrics["R2"] == 1.0


def test_classification_evaluation():
    """Test the classification evaluation."""
    y_true = pd.Series([0, 1, 1, 0])
    y_pred = pd.Series([0, 1, 1, 0])
    metrics = evaluate_classification(y_true, y_pred)
    assert metrics["accuracy"] == 1.0
