#!/usr/bin/env python3

import numpy as np

import sys
sys.path.append('/home/pablo/CinePy')

from modules.alfa_rossi_preprocesamiento import alfa_rossi_preprocesamiento
from modules.estadistica import timestamp_to_timewindow
from modules.alfa_feynman_procesamiento import metodo_alfa_feynman


if __name__ == '__main__':

    import matplotlib.pyplot as plt

    # -------------------------------------------------------------------------
    # Parámetros de entrada
    # -------------------------------------------------------------------------
    # Archivos de lista de tiempos a leer
    nombres = [
              './simulacion/times.D1.gz',
              ]
    # Conversión listmode a ventana temporal
    dt_base = 5e-5            # intervalo base para binnear la lista de tiempos
    # Técnica de agrupamiento
    numero_de_historias = 50  # Historias que se promediarán
    dt_maximo = 1e-2          # másimo intervalo temporal para cada historia
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
        # plt.plot(x*dt_base, y, 's-', label=nom.split('/')[-1])
        # plt.xlabel(r"$t$ [s] ")
        # plt.ylabel(r"$N$ [pulsos]")
        leidos.append((y, dt_base))
    # plt.legend()
    # plt.title(r"$\Delta t_{{base}}$: {:.2e} s".format(dt_base))
    # plt.show()
    # -------------------------------------------------------------------------

    calculos = [
               # 'var_serie',
               'var_paralelo',
               'var_paralelo_choice',
               'var_paralelo_skip',
               'var_paralelo_mca',
               # 'cov_paralelo',
               # 'sum_paralelo',
                ]

    # Parámetros extras para el cálculo mca y choice
    extra = {'skip_mca':0,
             'method_mca':'A_over_k',
             'fraction':0.10,
             'corr_time':dt_maximo*2,
            }
    for calculo in calculos:
        Y_historias = metodo_alfa_feynman(leidos, numero_de_historias,
                                          dt_maximo, calculo, nombres, **extra)

