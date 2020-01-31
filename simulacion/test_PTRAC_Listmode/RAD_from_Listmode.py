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

    archivo = 'ptrac_CAP_asc'

    # Se leen los datos
    datas, header = read_PTRAC_CAP_asc(archivo)

    for data in datas:
        print(data)
    '''
    # Se ordena de acuerdo a tiempo creciente
    new_data_sorted = new_data[new_data[:, 1].argsort()]
    # Separo los datos
    nps = new_data_sorted[:, 0].astype('int')
    time = new_data_sorted[:, 1]*1e-8
    cell = new_data_sorted[:, 2].astype('int')
    num = new_data_sorted[:, 3].astype('int')

    # Pongo en cero al primer pulso
    time -= time[0]
    print('Tiempo', time)
    # Datos del histograma
    dt_s = 1e-11
    dtmax_s = 1e-10
    tb = 1
    # Construyo la distribución de a-Rossi
    P_historia, _, N_trig, P_trig = arossi_una_historia_I(time, dt_s,
                                                          dtmax_s, tb)

    print(N_trig)
    print(P_trig)
    print(P_trig.sum(axis=0))
    '''
    # Leo el archivo PTRAC en binario

    archivo = 'ptrac_CAP_bin'

    datos, header = read_PTRAC_CAP_bin(archivo)

    for dato in datos:
        print(dato)
