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

    # Se agrega el tiempo del evento de fuente [1/s]
    tasa = 10

    print('Se simularon {} fisiones espontáneas'.format(nps))
    print('El Cf252 generó (promedio) {} neutrones de fuente'.format(3.75*nps))
    print('La tasa de eventos agregada es {} 1/s'.format(tasa))
    print('El tiempo total de la simulación será: {} s'.format(nps / tasa))
    archivo = 'times_listmode.dat'
    data_sorted = agrega_tiempo_de_fuente(tasa, nps, datos)

    times = data_sorted[:, 1]
    times -= times[0]
    np.savetxt('times_listmode.dat', times, fmt='%.12E')
    print('El tiempo total simulado fue: {} s'.format(times[-1]))
