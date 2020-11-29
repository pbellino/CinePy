#!/usr/bin/env python3

"""
Script para analizar la correlación que existe para un dado T_i en el método de
alfa-Feynman.

Se debe seleccionar el T_i (dt_base) que se quiera analizar. Esta correlación
es previa al método de agrupamiento, aparece al tomar varios T_i consecutivos
para obtener el <T_i> de cada historia.
"""

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os

import sys
sys.path.append('/home/pablo/CinePy')

from modules.estadistica import timestamp_to_timewindow
from modules.alfa_rossi_preprocesamiento import alfa_rossi_preprocesamiento
from modules.alfa_feynman_procesamiento import calcula_alfa_feynman_input


if __name__ == '__main__':
    # -------------------------------------------------------------------------
    # Parámetros de entrada
    # -------------------------------------------------------------------------
    # Archivos de lista de tiempos a leer
    nombres = [
              './simulacion/times.D1.gz',
              ]
    # Conversión listmode a ventana temporal
    dt_base = 5e-1            # intervalo base para binnear la lista de tiempos
    # dt_base = 5e-1            # intervalo base para binnear la lista de tiempos
    # Técnica de agrupamiento
    numero_de_historias =50000 # Historias que se promediarán
    dt_maximo = 5e+1          # másimo intervalo temporal para cada historia
    # -------------------------------------------------------------------------
    #
    # Lectura de archivo de lista de tiempos
    _, datos, _ = alfa_rossi_preprocesamiento(nombres, 1, 1, 'ascii')
    # Conversión de lista de tiempos a ventana temporal 
    binned, time_win = timestamp_to_timewindow(datos, dt_base, 'segundos',
                                               'pulsos', 1)
    # Armo la estructura de datos que necesito para procesar los datos
    leidos = []
    for x, y in zip(time_win, binned):
        leidos.append((y, dt_base))
    # -------------------------------------------------------------------------

    histo, _, _ = calcula_alfa_feynman_input(binned[0], numero_de_historias,
                                             dt_base, dt_maximo)
    histo = np.asarray(histo)
    print(type(histo), np.shape(histo))

    coef = np.corrcoef(histo.T)
    np.fill_diagonal(coef, np.nan)
    ax = sns.heatmap(coef)
    ax.invert_yaxis()

    fig, ax1 =  plt.subplots(1, 1)
    ax1.hist(coef.flatten(), bins=50)
    plt.show()

