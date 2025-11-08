import io
import logging

import pandas as pd
import streamlit as st

from chatbot_template.config.config_dashboard import DashboardConfig
from chatbot_template.utils.teacher.enums import DataTypesEnum

from .bridge_loader import clean_dataframe, load_generic_data
from .registry import PLOT_TYPES
from .visualizations import generate_plot

logger = logging.getLogger(__name__)


def show_dashboard(config: DashboardConfig | None):
    """
    Shows the dashboard and sets all the graphics were desired.

    Parameters
    ----------
    config : DashboardConfig | None
        Checks the configuration process for the dashboard for data and titles.
    """
    if config is None:
        logger.warning(
            "Dashboard config is None — cannot generate personalized dashboard."
        )
        raise ValueError("DashboardConfig is None — dashboard cannot be generated.")

    st.set_page_config(page_title=config.title, layout=config.layout)
    st.title(config.title)

    # Sidebar: carga de datos
    st.sidebar.header("Datos")
    uploaded = st.sidebar.file_uploader(
        "📂 Subir archivo", type=["csv", "json", "xlsx"]
    )
    mode_map = {
        "csv": DataTypesEnum.CSV,
        "json": DataTypesEnum.JSON,
        "xlsx": DataTypesEnum.EXCEL,
    }

    if uploaded:
        ext = uploaded.name.split(".")[-1]
        buffer = io.BytesIO(uploaded.read())
        df = load_generic_data(mode=mode_map.get(ext, DataTypesEnum.CSV), path=buffer)
    elif config.default_data_path:
        df = load_generic_data(mode=DataTypesEnum.CSV, path=config.default_data_path)
    else:
        st.warning("Sube un archivo para continuar.")
        return

    df = clean_dataframe(df)

    # Preview
    st.subheader("📋 Vista previa")
    st.dataframe(df.head())

    # Selección de columnas
    cols = df.columns.tolist()
    x_col = st.selectbox("Eje X", cols)
    y_col = st.selectbox("Eje Y", ["(ninguno)"] + cols)
    y_col = None if y_col == "(ninguno)" else y_col
    plot_type = st.selectbox("Tipo de gráfico", list(config_plot_types(df)))

    # Renderizado
    if st.button("Generar gráfico"):
        fig = generate_plot(df, plot_type, x_col, y_col)
        st.plotly_chart(fig, use_container_width=True)


def config_plot_types(df: pd.DataFrame):
    """
    Returns the type of valid graphics according to the DataFrame content.

    Paramters
    ---------
    df : pd.DataFrame
        Data to show and config plots.
    """
    numeric_cols = df.select_dtypes(include=["number"]).columns
    categorical_cols = df.select_dtypes(exclude=["number"]).columns

    for name in PLOT_TYPES:
        # Ejemplo de lógica básica:
        if name in {"Line", "Scatter", "Box"} and len(numeric_cols) == 0:
            continue  # necesita columnas numéricas
        if name in {"Pie", "Bar"} and len(categorical_cols) == 0:
            continue  # necesita categorías
        yield name
