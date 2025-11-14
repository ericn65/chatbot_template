# Importar las classes o objetos

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# GenerarNumeroPoblacionTotal()

from data_cleaning import data_cleaners 
from data_filtering import data_filter
from data_visualizers import Data_Visualization # OK
from RnD import RnD

# Preguntar compañeros si tienen una funcion donde dan el resultado en un df

def main():

    # Limpieza --> Preguntar compañeros 
    df = data_cleaners(df)

    # Filtrado --> Preguntar compañeros 
    df = data_filter(df, "age > 30") 

    # visualizar datos con una grafica pasamos datos X, Y
    Data_Visualization.showBarGraphic()

    # Resultado --> Preguntar compañeros Rnd
    Resultado = RnD(df)
    print(Resultado)

if __name__ == "__main__":
     main()

