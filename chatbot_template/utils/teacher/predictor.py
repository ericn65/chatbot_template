import joblib
import pandas as pd
from sklearn.ensemble import RandomForestRegressor


def load_model(model_path: str) -> RandomForestRegressor:
    """
    Load a previously saved ML model using joblib.

    Parameters
    ----------
    model_path : str
        Path to the stored model (.pkl file).

    Returns
    -------
    model
        Loaded ML model.
    """
    return joblib.load(model_path)


def predict_with_model(model, new_features: pd.DataFrame | dict):
    """
    Use a pre-trained model to generate predictions.

    Parameters
    ----------
    model : object
        Pre-trained ML model loaded via joblib.
    new_features : pd.DataFrame or dict
        New feature data to predict on.

    Returns
    -------
    array-like
        Predictions for the given feature set.
    """
    if isinstance(new_features, dict):
        new_features = pd.DataFrame([new_features])

    return model.predict(new_features)
