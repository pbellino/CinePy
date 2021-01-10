#!/usr/bin/env python3

import numpy as np
import matplotlib.pyplot as plt

import sys
sys.path.append('/home/pablo/CinePy')

from modules.alfa_rossi_preprocesamiento import alfa_rossi_preprocesamiento
from modules.estadistica import timestamp_to_timewindow
from modules.alfa_feynman_procesamiento import metodo_alfa_feynman


if __name__ == '__main__':

    n_b = 15
    dt_maximos = 8e-3 * np.linspace(1, n_b, n_b)
    [print(f"{k:.4e}") for k in dt_maximos]
    #quit()

    # -------------------------------------------------------------------------
    # Parámetros de entrada
    # -------------------------------------------------------------------------
    # Archivos de lista de tiempos a leer
    nombres = [
              './simulacion/times.D1.gz',
              ]
    # Conversión listmode a ventana temporal
    dt_base = 6e-4            # intervalo base para binnear la lista de tiempos
    # Técnica de agrupamiento
    numero_de_historias = 50  # Historias que se promediarán
    # -------------------------------------------------------------------------
    #
    # Lectura de archivo de lista de tiempos
    _, datos, _ = alfa_rossi_preprocesamiento(nombres, 1, 1, 'ascii')
    # Conversión de lista de tiempos a ventana temporal 
    binned, time_win = timestamp_to_timewindow(datos, dt_base, 'segundos',
                                               'pulsos', 1)
    print(np.shape(binned[0]))
    # Armo la estructura de datos que necesito para procesar los datos
    leidos = []
    for x, y, nom in zip(time_win, binned, nombres):
        leidos.append((y, dt_base))
    # -------------------------------------------------------------------------
    calculos = [
               'var_paralelo',
               'var_paralelo_choice',
               'var_paralelo_skip',
               'var_paralelo_mca',
                ]

    # Cálculos para cada dt_maximo
    for dt_maximo in dt_maximos:
        # Parámetros extras para el cálculo mca y choice
        extra = {'skip_mca': 0,
                 'method_mca':'A_over_k',
                 'fraction': 0.25,
                 'corr_time': dt_maximo*2,
                 'carpeta_resultados': "barrido/{:.2e}".format(dt_maximo),
                }
        for calculo in calculos:
            Y_historias = metodo_alfa_feynman(leidos, numero_de_historias,
                                              dt_maximo, calculo, nombres,
                                              **extra)

