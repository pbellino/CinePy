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


def agrega_tiempo_de_fuente(tasa, datos, filename):
    """
    Agrega los tiempos de fuente al tiempo registrado en el PTRAC

    Se asume una distribución exponencial de tiempos entre eventos y se lo
    suma a todas las capturas que provienen de una misma historia

    Parámetros
    ----------

        tasa : double [1/s]
            Tasa de eventos de fuente (fisiones espontáneas) por segundo. Se
            debe calcular en base a la actividad de la fuente.

        datos : list of list
            Los datos leídos del archivo PTRAC, tal cual se obtienen con la
            función `read_PTRAC_CAP_bin()`

        filename : string
            Nombre del archivo donde se guardarán los tiempos.

    Resultados
    ----------

        times : numpy array
            Lista ordenada de los tiempos de captura. Contados todos a partir
            del primero (ie times[0]=0)
        cells : numpy_array
            Celda en donde se produjo la captura. Sirve para diferenciar
            distintos detectores.
        nps : numpy array
            Lista que identifica a cuál historia pertenece cada captura. En
            principio  no tiene mucha utilidad

    Cada elemento de estos tres vectores hace referencia a una captura.

    Ejemplo: times[3], cells[3] y nps[3] hacen referencia al tiempo de captura
    del times[3] del cuarto pulso que se produjo en la celda cells[3] y que
    pertenece a la historia nps[3]
    """

    # Convierto a array de numpy
    datos = np.asarray(datos)
    # Ordeno por historia para después buscar más fácil
    datos = datos[datos[:, 0].argsort()]
    # Número de historia de cada evento
    nps = np.asarray(datos[:, 0], dtype='int64')
    # Cantidad de historias totales
    num_hist = len(set(nps))
    # Tiempos del PTRAC en segundos
    times = np.asarray(datos[:, 1], dtype='float64') * 1e-8
    # Celda donde se produjo la captura
    cells = np.asarray(datos[:, 2], dtype='int64')

    # Se generan número con distribución exponencial
    beta = 1.0 / tasa
    # Genero los tiempos para cada evento de fuente
    np.random.seed(313131)
    src_time = np.cumsum(np.random.exponential(beta, num_hist))
    for n, t in zip(set(nps), src_time):
        indx_min = np.searchsorted(nps, n, side='left')
        indx_max = np.searchsorted(nps, n, side='right')
        times[indx_min:indx_max] += t

    # Ordeno los tiempos y mantengo asociado el numero de historia y la celda
    _temp = np.stack((nps, times, cells), axis=-1)
    # Ordeno para tiempos crecientes
    _temp_sorted = _temp[_temp[:, 1].argsort()]
    # Vuelvo a separar
    nps = _temp_sorted[:, 0]
    times = _temp_sorted[:, 1]
    cells = _temp_sorted[:, 2]
    # Pongo en cero al primer pulso
    times -= times[0]

    # Se guardan los datos del tiempo
    np.savetxt(filename, times, fmt='%.12E')

    return times, cells, cells


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
