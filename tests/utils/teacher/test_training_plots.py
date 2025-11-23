import pandas as pd

from chatbot_template.utils.teacher.training_plots import plot_pred_vs_true


def test_plot_pred_vs_true_runs():
    """Test the runs of predictions vs. true."""
    y_true = pd.Series([1, 2, 3])
    y_pred = pd.Series([1, 2, 3])
    plot_pred_vs_true(y_true, y_pred)
    assert True
