#!/usr/bin/env python3

import numpy as np

import sys
sys.path.append('../')

from modules.alfa_feynman_procesamiento import wrapper_lectura, \
                                               metodo_alfa_feynman


if __name__ == '__main__':


    # -------------------------------------------------------------------------
    # Parámetros de entrada
    # -------------------------------------------------------------------------
    # Archivos a leer
    nombres = [
              '../datos/nucleo_01.D1.bin',
              '../datos/nucleo_01.D2.bin',
              ]
    # Intervalos para agrupar los datos adquiridos
    int_agrupar = 5
    # Técnica de agrupamiento
    numero_de_historias = 100  # Historias que se promediarán
    dt_maximo = 50e-3          # másimo intervalo temporal para cada historia
    # -------------------------------------------------------------------------
    # Lectura y agrupamiento
    leidos = wrapper_lectura(nombres, int_agrupar)
    # -------------------------------------------------------------------------

    calculos = [
                'var_paralelo',
                'cov_paralelo',
                'sum_paralelo',
                ]

    for calculo in calculos:
        Y_historias = metodo_alfa_feynman(leidos, numero_de_historias,
                                          dt_maximo, calculo)
        for Y_historia in Y_historias:
            print(np.array(Y_historia)[9, :])
