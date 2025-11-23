import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

from chatbot_template.utils.teacher.evaluate import evaluate_regression
from chatbot_template.utils.teacher.forecasting import train_regression_model
from chatbot_template.utils.teacher.training_plots import (
    plot_forecast_series,
    plot_pred_vs_true,
    plot_residuals,
)


def run_training_dashboard():
    """
    Launch the model training dashboard interface.

    Allows:
    - Uploading a dataset.
    - Selecting features and labels.
    - Training a RandomForest model.
    - Displaying evaluation metrics and plots.
    """
    st.title("📈 ML Model Training Dashboard")

    uploaded_file = st.file_uploader("Upload CSV file", type=["csv"])

    if uploaded_file is None:
        st.info("Please upload a dataset to continue.")
        return

    data = pd.read_csv(uploaded_file)
    st.subheader("Preview of Data")
    st.dataframe(data.head())

    feature_cols = st.multiselect("Select feature columns", data.columns)
    label_col = st.selectbox("Select target column", data.columns)

    if st.button("Train Model"):
        if not feature_cols:
            st.error("You must select at least one feature column.")
            return

        model, y_pred = train_regression_model(
            features=data[feature_cols],
            labels=data[label_col],
            model_path="trained_rf_model.pkl",
        )

        st.success("Model trained and saved as trained_rf_model.pkl 🎉")

        # Evaluation
        split_idx = int(len(data) * 0.8)
        y_test = data[label_col].iloc[split_idx:]

        metrics = evaluate_regression(y_test, y_pred)
        st.subheader("📊 Evaluation Metrics")
        st.write(metrics)

        # ------------------------ Plots ------------------------
        st.subheader("📌 Predicted vs True")
        fig1 = plt.figure()
        plot_pred_vs_true(y_test, y_pred)
        st.pyplot(fig1)

        st.subheader("📌 Residual Distribution")
        fig2 = plt.figure()
        plot_residuals(y_test, y_pred)
        st.pyplot(fig2)

        st.subheader("📌 Forecast vs Actual")
        fig3 = plt.figure()
        plot_forecast_series(y_test, y_pred)
        st.pyplot(fig3)
