import pandas as pd
import numpy as np

df = pd.read_csv("scripts/data_filtering/data_poblacion.csv")


def filter_by_column(df, column_name: str):
    """
    Filtra el DataFrame para incluir solo las filas donde el valor en 'column_name' es verdadero.
    """
    filtered_df = df[column_name]
    return filtered_df

def datos_paises(df):

    dataframe = df

    df.loc[:, "Population", "country"]


def filtro_poblacion_pais(pais, df):
    "Filtro que te da el número de habitantes de un país específico."
   

nombre_columna = "Mercado_de_invierno_2024"
filter_by_columna= filter_by_column(df,nombre_columna)

print(filter_by_columna)