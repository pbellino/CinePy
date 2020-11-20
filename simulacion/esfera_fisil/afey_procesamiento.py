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
              './times_listmode_n.D1.dat',
              './times_listmode_p.D2.dat',
              ]
    # Conversión listmode a ventana temporal
    dt_base = 4e-4            # intervalo base para binnear la lista de tiempos
    # Técnica de agrupamiento
    numero_de_historias = 50  # Historias que se promediarán
    dt_maximo = 2e-2          # másimo intervalo temporal para cada historia
    # -------------------------------------------------------------------------
    #
    # Lectura de archivo de lista de tiempos
    _, datos, _ = alfa_rossi_preprocesamiento(nombres, 1, 1, 'ascii')
    # Conversión de lista de tiempos a ventana temporal 
    binned, time_win = timestamp_to_timewindow(datos, dt_base, 'segundos',
                                               'pulsos', 1)
    # Armo la estructura de datos que necesito para procesar los datos
    leidos = []
    for x, y, nom in zip(time_win, binned, nombres):
        plt.plot(x*dt_base, y, 's-', label=nom.split('/')[-1])
        plt.xlabel(r"$t$ [s] ")
        plt.ylabel(r"$N$ [pulsos]")
        leidos.append((y, dt_base))
    plt.legend()
    plt.title(r"$\Delta t_{{base}}$: {:.2e} s".format(dt_base))
    plt.show()
    # -------------------------------------------------------------------------

    calculos = [
               # 'var_serie',
                'var_paralelo',
                'cov_paralelo',
               # 'sum_paralelo',
               # 'pirulo',
                ]

    for calculo in calculos:
        Y_historias = metodo_alfa_feynman(leidos, numero_de_historias,
                                          dt_maximo, calculo, nombres)
        for Y_historia in Y_historias:
            print(np.array(Y_historia)[9, :])
