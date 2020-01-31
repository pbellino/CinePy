#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script de prueba para leer un archivo PTRAC en formato ASCII
"""

import numpy as np
import sys

sys.path.append('../../')
from modules.alfa_rossi_procesamiento import arossi_una_historia_I
from modules.io_modules import read_PTRAC_CAP_bin, read_PTRAC_CAP_asc

if __name__ == '__main__':

    archivo_asc = 'ptrac_CAP_asc'
    archivo_bin = 'ptrac_CAP_bin'

    # Se leen los datos en ascii (debug)
    datos_ascii, header_ascii = read_PTRAC_CAP_asc(archivo_asc)

    print('-'*50)
    print('Datos en ascii')
    print('-'*50)
    for dato in datos_ascii:
        print(dato)

    # Se leen los datos en binario
    datos, header = read_PTRAC_CAP_bin(archivo_bin)

    print('-'*50)
    print('Datos en binario')
    print('-'*50)
    for dato in datos:
        print(dato)

    # Construcción de la distribución de alfa-Rossi a partir de Listmode
    #
    datos = np.asarray(datos)
    # Se ordena de acuerdo a tiempo creciente
    datos_sorted = datos[datos[:, 1].argsort()]
    # Separo los datos de interés
    nps = datos_sorted[:, 0].astype('int')
    time = datos_sorted[:, 1]*1e-8
    cell = datos_sorted[:, 2].astype('int')
    num = datos_sorted[:, 3].astype('int')

    # Pongo en cero al primer pulso
    time -= time[0]
    print('Tiempos: \n', time)
    # Datos del histograma
    dt_s = 1e-11
    dtmax_s = 1e-10
    tb = 1
    # Construyo la distribución de a-Rossi
    P_historia, _, N_trig, P_trig = arossi_una_historia_I(time, dt_s,
                                                          dtmax_s, tb)

    print(P_trig)
    print(P_trig.sum(axis=0))
