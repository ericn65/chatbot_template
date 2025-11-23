import pandas as pd

from chatbot_template.utils.teacher.evaluate import evaluate_regression
from chatbot_template.utils.teacher.forecasting import train_regression_model


def main():
    """
    Execute training procedure:
    - Load data.
    - Train model.
    - Save model.
    - Evaluate predictions.
    """
    df = pd.read_csv("data/train.csv")  # <-- adjust path as needed

    # Split between features & labels
    feature_cols = ["lag_1", "lag_7", "temperature", "promo"]
    label_col = "target"

    model, preds = train_regression_model(
        features=df[feature_cols],
        labels=df[label_col],
        model_path="models/rf_forecast.pkl",
        split_factor=0.8,
    )

    print("Model saved to models/rf_forecast.pkl")

    test_idx = int(len(df) * 0.8)
    y_test = df[label_col].iloc[test_idx:]

    metrics = evaluate_regression(y_test, preds)
    print("Evaluation metrics:", metrics)


if __name__ == "__main__":
    main()
