import pandas as pd

from chatbot_template.utils.teacher.forecasting import train_regression_model


def test_trainer_runs():
    """Test the trainer models."""
    data = pd.DataFrame(
        {
            "lag_1": [1, 2, 3, 4],
            "lag_7": [1, 2, 3, 4],
            "temp": [10, 11, 12, 13],
            "y": [5, 6, 7, 8],
        }
    )

    model, preds = train_regression_model(
        features=data[["lag_1", "lag_7", "temp"]],
        labels=data["y"],
        split_factor=0.5,
        model_path="test_model.pkl",
    )

    assert len(preds) == 2
