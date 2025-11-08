import streamlit as st

from chatbot_template.utils.teacher.enums import DataTypesEnum

from .bridge_loader import clean_dataframe, load_generic_data
from .visualizations import generate_plot


def show_dashboard(config):
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
        df = load_generic_data(mode=mode_map.get(ext, DataTypesEnum.CSV), path=uploaded)
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


def config_plot_types(df):
    from .registry import PLOT_TYPES

    # Filtramos tipos de gráfico válidos según el DF
    for name in PLOT_TYPES:
        yield name
