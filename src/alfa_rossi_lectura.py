#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
TODO
Escribe los resultados del procesamiento con el método de alfa-Rossi.

Genera el archivo [nombre]_ros_dat con todas las historias.
Genera el archivo [nombre].ros con el promedio entre historias.

Toma os resultados provenientes de `alfa_rossi_procesamiento()` que está en el
script `alfa_rossi_procesamiento.py`.
"""

import numpy as np

import sys
sys.path.append('../')


def arossi_lee_historias_completas(nombre):
    """
    Lee el archivo que contiene a todas las historias de alfa-Rossi

    El archivo que lee fue escrito con `escribe_datos_completos()' en el script
    `alfa_rossi_escritura.py`

    Busca los datos en función de la línea anterior que lo describe (es
    búsqueda literal). Salvo las historias.

    Las historias se leen con numpy.loadtxt() salteando las líneas anteriores.

    Parametros
    ----------
        nombre: string
            Camino y nombre del archivo a leer (*_ros.dat)

    Resultados
    ----------
        historias: numpy ndarray
            Array en 2D donde cada columna es una de las historias calculadas
        tau: numpy array
            Vector temporal con los tau (bines centrados)
        parametros_dic : dictionary
            Diccionario con el resto de los parámetros leidos.
                'dt': Duración del bin [s]
                'dt_max' : Máximo bin analizado [s]
                'N_bins' : Cantidad de bines por trigger (dt_max / dt)
                'tb' : Tiempo de los pulsos utilizado para contar [s]
                'N_hist' : Cantidad de historias
                'N_trigg' : Cantidad de triggers en cada historia (numpy array)
                'R_mean' : Tasa de cuentas en cada historia (numpy array)
                'R_std' : Desvío del promedio en cada historia (numpy array)

    """

    try:
        with open(nombre, 'r') as f:
            # Se lee el dt
            for line in f:
                if line.startswith('# Duración del bin (dt)'):
                    dt = np.double(next(f).rstrip())
                elif line.startswith('# Máximo bin analizado'):
                    dt_max = np.float64(next(f).rstrip())
                elif line.startswith('# Puntos analizados por trigger'):
                    N_bins = np.uint32(next(f).rstrip())
                elif line.startswith('# Tiempo base del contador'):
                    tb = np.float64(next(f).rstrip())
                elif line.startswith('# Número de historias'):
                    N_hist = np.uint32(next(f).rstrip())
                elif line.startswith('# Tasa de cuentas'):
                    next(f)
                    R_mean = np.float64(next(f).rstrip().split(' '))
                elif line.startswith('# Desvío estándar del promedio'):
                    next(f)
                    R_std = np.float64(next(f).rstrip().split(' '))
                elif line.startswith('# Cantidad de triggers'):
                    next(f)
                    N_trigg = np.uint32(next(f).rstrip().split(' '))
                    break
            parametros_dic = {'dt': dt, 'dt_max': dt_max, 'N_bins': N_bins,
                              'tb': tb, 'N_hist': N_hist, 'N_trigg': N_trigg,
                              'R_mean': R_mean, 'R_std': R_std}
            # Se leen todas las historias
            _data = np.loadtxt(nombre, skiprows=30)
            tau = _data[:, 0]
            historias = _data[:, 1:]
    except IOError as err:
        print('No se pudo leer el archivo: ' + nombre)
        raise err
        sys.exit()

    return historias, tau, parametros_dic


if __name__ == '__main__':

    # -------------------------------------------------------------------------
    # Parámetros de entrada
    # -------------------------------------------------------------------------
    # Archivo a leer
    nombre = './resultados_arossi/medicion04.a.inter.D1_ros.dat'

    historias, tau, param_dic = arossi_lee_historias_completas(nombre)
    keys = ['dt', 'dt_max', 'N_bins', 'tb', 'N_hist']
    for key in param_dic.keys():
        print('{}: {}'.format(key, param_dic.get(key)))
    print(tau)
    print(historias)

    # -------------------------------------------------------------------------
