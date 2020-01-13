#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Lee los archivos escritos con los datos del procesamiento con alfa-Rossi.

Lee el archivo [nombre]_ros_dat con todas las historias.
Lee el archivo [nombre].ros con el promedio entre historias.

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
        nombre : string
            Camino y nombre del archivo a leer (*_ros.dat)

    Resultados
    ----------
        historias : numpy ndarray
            Array en 2D donde cada columna es una de las historias calculadas
        tau : numpy array
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


def arossi_lee_historias_promedio(nombre):
    """
    Lee el archivo que contiene a todas el promedio de historias de alfa-Rossi

    El archivo que lee fue escrito con `escribe_datos_promedio()' en el script
    `alfa_rossi_escritura.py`

    Busca los datos en función de la línea anterior que lo describe (es
    búsqueda literal). Salvo las historias.

    Los promedios se leen con numpy.loadtxt() salteando las líneas anteriores.

    Parametros
    ----------
        nombre : string
            Camino y nombre del archivo a leer (*_ros.dat)

    Resultados
    ----------
        P_tau_mean : numpy array
           Curva promedio de la probabilidad P(tau) de alfa-Rossi
        P_tau_std : numpy array
           Desvío estándar de la probabilidad promedio P(tau) de alfa-Rossi
        tau : numpy array
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
                'N_trig_mean' : Cantidad de triggers promedio
                'N_trig_std' : Desvío de la cantidad de triggers promedio

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
                    R_mean = np.float64(next(f).rstrip())
                elif line.startswith('# Desvío estándar de la tasa'):
                    R_std = np.float64(next(f).rstrip())
                elif line.startswith('# Cantidad de triggers promedio'):
                    N_trig_mean = np.float64(next(f).rstrip())
                elif line.startswith('# Desvío estándar de la cantidad de'):
                    N_trig_std = np.float64(next(f).rstrip())
                    break
            parametros_dic = {'dt': dt, 'dt_max': dt_max, 'N_bins': N_bins,
                              'tb': tb, 'N_hist': N_hist, 'R_mean': R_mean,
                              'R_std': R_std, 'N_trig_mean': N_trig_mean,
                              'N_trig_std': N_trig_std}
            # Se leen todas las historias
            _data = np.loadtxt(nombre, skiprows=28)
            tau = _data[:, 0]
            P_tau_mean = _data[:, 1]
            P_tau_std = _data[:, 2]
    except IOError as err:
        print('No se pudo leer el archivo: ' + nombre)
        raise err
        sys.exit()

    return P_tau_mean, P_tau_std, tau, parametros_dic


if __name__ == '__main__':

    # -------------------------------------------------------------------------
    # Prueba arossi_lee_historias_completas()
    #
    """
    # Archivo a leer
    nombre = './resultados_arossi/medicion04.a.inter.D1_cov.ros'

    historias, tau, param_dic = arossi_lee_historias_completas(nombre)
    for key in param_dic.keys():
        print('{}: {}'.format(key, param_dic.get(key)))
    print(tau)
    print(historias)
    """

    # -------------------------------------------------------------------------
    # Prueba arossi_lee_historias_promedio()
    #
    # Archivo a leer
    nombre = './resultados_arossi/medicion04.a.inter.D1.ros'

    P, P_std, tau, param_dic = arossi_lee_historias_promedio(nombre)
    for key in param_dic.keys():
        print('{}: {}'.format(key, param_dic.get(key)))
    print(np.column_stack((tau, P, P_std)))
