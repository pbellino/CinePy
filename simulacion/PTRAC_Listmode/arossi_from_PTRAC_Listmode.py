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
from modules.io_modules import read_PTRAC_CAP_bin
from modules.simulacion_modules import agrega_tiempo_de_fuente, \
                                       lee_nps_entrada


if __name__ == '__main__':

    archivo_entrada = 'Cf252_H2O.i'
    archivo_bin = 'ptrac'

    # Se lee la cantidad de eventos de fuente del archivo de entrada de MCNP
    nps = lee_nps_entrada(archivo_entrada)

    # Se leen los datos en binario
    datos, header = read_PTRAC_CAP_bin(archivo_bin)

    '''
    print('-'*50)
    print('Datos en binario')
    print('-'*50)
    for dato in datos:
        print(dato)
    '''

    # Se agrega el tiempo del evento de fuente [1/s]
    tasa = 10

    print('Se simularon {} fisiones espontáneas'.format(nps))
    print('El Cf252 generó (promedio) {} neutrones de fuente'.format(3.75*nps))
    print('La tasa de eventos agregada es {} 1/s'.format(tasa))
    print('El tiempo total de la simulación será: {} s'.format(nps / tasa))
    archivo = 'times_listmode.dat'
    times, nps_cap, cells = agrega_tiempo_de_fuente(tasa, nps, datos, archivo)
    print('El tiempo total simulado fue: {} s'.format(times[-1]))

    '''
    print('-'*50)
    print('Tiempos absolutos:')
    [print(t) for t in times]
    '''

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
