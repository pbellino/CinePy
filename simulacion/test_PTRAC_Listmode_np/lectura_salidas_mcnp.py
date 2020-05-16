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
from modules.simulacion_modules import agrega_tiempo_de_fuente, \
                                       lee_nps_entrada, read_PTRAC_estandar


if __name__ == '__main__':

    archivo_entrada = 'input'
    archivo_n = 'neutrones_bin.p'
    archivo_p = 'fotones_bin.p'

    # Se lee la cantidad de eventos de fuente del archivo de entrada de MCNP
    nps = lee_nps_entrada(archivo_entrada)
    # Se leen los datos en binario
    print('Leyendo arhvo de neutrones....')
    datos_n, header_n = read_PTRAC_CAP_bin(archivo_n)
    print('Leyendo arhvo de fotones....')
    datos_p = read_PTRAC_estandar(archivo_p, 'bin', ['sur'])

    if False:
        print('-'*50)
        print('Datos en binario')
        print('-'*50)
        for dato in datos_n:
            print(dato)

    # Se agrega el tiempo del evento de fuente [1/s]
    tasa = 100

    print('Se simularon {} fisiones espontáneas'.format(nps))
    print('El Cf252 generó (promedio) {} neutrones de fuente'.format(3.75*nps))
    print('La tasa de eventos agregada es {} 1/s'.format(tasa))
    print('El tiempo total de la simulación será: {} s'.format(nps / tasa))

    archivo_times_n = 'times_listmode_n.dat'
    archivo_times_p = 'times_listmode_p.dat'
    times_n, cells_n, nps_hist_n = agrega_tiempo_de_fuente(tasa, nps, datos_n,
                                                           archivo_times_n)
    times_p, cells_p, nps_hist_p = agrega_tiempo_de_fuente(tasa, nps, datos_p,
                                                           archivo_times_p)

    t_0 = min(times_n[0], times_p[0])
    times_n -= t_0
    times_p -= t_0
    print('Tiempo total simulado de neutrones: {} s'.format(times_n[-1]))
    print('Tiempo total simulado de fotones: {} s'.format(times_p[-1]))

    # Para debuggear
    np.savetxt('historia_n.dat', nps_hist_n, fmt='%i')
    np.savetxt('historia_p.dat', nps_hist_p, fmt='%i')

    if False:
        print('-'*50)
        print('Tiempos absolutos:')
        [print(t) for t in times_n]

