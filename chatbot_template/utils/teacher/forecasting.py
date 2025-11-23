import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor


def train_regression_model(
    features: pd.DataFrame,
    labels: pd.Series,
    split_factor: float = 0.8,
    model_path: str = "./models/trained_model.pkl",
) -> tuple[RandomForestRegressor, pd.Series]:
    """
    Train a RandomForest model for forecasting and save it to disk.

    Parameters
    ----------
    features : pd.DataFrame
        Feature matrix (lags, rolling windows, external variables).
    labels : pd.Series
        Target variable.
    split_factor : float
        Proportion of data used for training. Default: 0.8.
    model_path : str
        Path to save the trained model.

    Returns
    -------
    model : RandomForestRegressor
        The trained model object.
    predictions : pd.Series
        Predictions on the test set (for evaluation).
    """
    split = int(len(features) * split_factor)

    X_train = features.iloc[:split]  # noqa: N806
    X_test = features.iloc[split:]  # noqa: N806

    y_train = labels.iloc[:split]
    y_test = labels.iloc[split:]

    model = RandomForestRegressor()
    model.fit(X_train, y_train)

    joblib.dump(model, model_path)

    predictions = pd.Series(model.predict(X_test), index=y_test.index)

    return model, predictions


def train_classifier_model(
    features: pd.DataFrame,
    labels: pd.Series,
    split_factor: float = 0.8,
    model_path: str = "./models/trained_model.pkl",
) -> tuple[RandomForestClassifier, pd.Series]:
    """
    Train a RandomForest model for forecasting classifiers and save it to disk.

    Parameters
    ----------
    features : pd.DataFrame
        Feature matrix (lags, rolling windows, external variables).
    labels : pd.Series
        Target variable.
    split_factor : float
        Proportion of data used for training. Default: 0.8.
    model_path : str
        Path to save the trained model.

    Returns
    -------
    model : RandomForestClassifier
        The trained model object.
    predictions : pd.Series
        Predictions on the test set (for evaluation).
    """
    split = int(len(features) * split_factor)

    X_train = features.iloc[:split]  # noqa: N806
    X_test = features.iloc[split:]  # noqa: N806

    y_train = labels.iloc[:split]
    y_test = labels.iloc[split:]

    model = RandomForestClassifier()
    model.fit(X_train, y_train)

    joblib.dump(model, model_path)

    predictions = pd.Series(model.predict(X_test), index=y_test.index)

    return model, predictions
