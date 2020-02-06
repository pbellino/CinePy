#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script de prueba para generar la distrubución de alfa-Rossi a partir de la
simulación con PTRAC en modo lista.
"""

import numpy as np
import sys

sys.path.append('../../')
from modules.alfa_rossi_procesamiento import arossi_una_historia_I
from modules.io_modules import read_PTRAC_CAP_bin, read_PTRAC_CAP_asc
from modules.simulacion_modules import agrega_tiempo_de_fuente


if __name__ == '__main__':

    archivo_asc = 'ptrac_CAP_asc'
    archivo_bin = 'ptrac_CAP_bin'

    # Se leen los datos en ascii (debug)
    '''
    datos_ascii, header_ascii = read_PTRAC_CAP_asc(archivo_asc)

    print('-'*50)
    print('Datos en ascii')
    print('-'*50)
    for dato in datos_ascii:
        print(dato)
    '''

    # Se leen los datos en binario
    datos, header = read_PTRAC_CAP_bin(archivo_bin)

    print('-'*50)
    print('Datos en binario')
    print('-'*50)
    for dato in datos:
        print(dato)

    # Se agrega el tiempo del evento de fuente
    tasa = 10
    archivo = 'times_listmode.dat'
    times, nps, cells = agrega_tiempo_de_fuente(tasa, datos, archivo)

    print('-'*50)
    print('Tiempos absolutos:')
    [print(t) for t in times]

    quit()
    # Datos del histograma
    dt_s = 1e-11
    dtmax_s = 1e-10
    tb = 1
    # Construyo la distribución de a-Rossi
    P_historia, _, N_trig, P_trig = arossi_una_historia_I(times, dt_s,
                                                          dtmax_s, tb)

    print(P_trig)
    print(P_trig.sum(axis=0))
