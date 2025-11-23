import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

from chatbot_template.utils.teacher.evaluate import evaluate_regression
from chatbot_template.utils.teacher.predictor import (
    load_model,
    predict_with_model,
)
from chatbot_template.utils.teacher.training_plots import (
    plot_forecast_series,
    plot_pred_vs_true,
    plot_residuals,
)


def run_evaluation_dashboard():
    """Launch the evaluation dashboard for pretrained models."""
    st.title("🧪 Model Evaluation Dashboard")

    # Load the trained model
    model_path = st.text_input("Path to trained model (.pkl)", "trained_rf_model.pkl")

    if not model_path:
        st.stop()

    try:
        model = load_model(model_path)
        st.success("Model loaded successfully.")
    except Exception as e:
        st.error(f"Could not load model: {e}")
        st.stop()

    # Upload data for prediction
    uploaded_file = st.file_uploader("Upload CSV with feature data", type=["csv"])

    if uploaded_file is None:
        st.info("Upload a feature dataset to evaluate model.")
        return

    data = pd.read_csv(uploaded_file)
    st.subheader("Preview of Input Data")
    st.dataframe(data.head())

    feature_cols = st.multiselect("Select feature columns", data.columns)

    if st.button("Run Predictions"):
        if not feature_cols:
            st.error("You must select feature columns.")
            return

        preds = predict_with_model(model, data[feature_cols])

        st.subheader("Predictions")
        st.write(preds)

        if "target" in data.columns:
            st.subheader("Evaluation Metrics")
            y_true = data["target"]
            metrics = evaluate_regression(y_true, preds)
            st.write(metrics)

            # Plots
            st.subheader("Pred vs True")
            fig1 = plt.figure()
            plot_pred_vs_true(y_true, preds)
            st.pyplot(fig1)

            st.subheader("Residuals")
            fig2 = plt.figure()
            plot_residuals(y_true, preds)
            st.pyplot(fig2)

            st.subheader("Forecast vs Actual")
            fig3 = plt.figure()
            plot_forecast_series(y_true, preds)
            st.pyplot(fig3)
