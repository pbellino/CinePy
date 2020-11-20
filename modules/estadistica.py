#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np


def agrupa_datos(data, n_datos=1, dt=None):
    '''
    Agrupa los datos de data en n_datos

    Parametros
    ----------
        data : numpy array
            datos que se quieren agrupar
        n_datos : entero
            número de intervalos que se agruparán
        dt : flotante, opcional
            intervalo de tiempo original de 'data'

    Salida
    ------
        datos_agrupados : numpy array
            datos agrupados cada n_datos
        dt_agrupado : flotante, opcional
            Si se especificó dt se devuelve el dt agrupado
            (dt_agrupado = dt*n_datos)

    >>> a = np.array([3, 6, 7, 9, 1])
    >>> agrupa_datos(a, 2)
    Se agrupan 2 intervalos base
    array([ 9, 16], dtype=uint32)
    >>> agrupa_datos(a, 2, 0.3)
    Se agrupan 2 intervalos base
    Intervalo de adquisición agrupado: 0.6 s
    (array([ 9, 16], dtype=uint32), 0.6)
    '''

    data = np.array(data)
    if n_datos == 1:
        if dt is None:
            return data
        else:
            return data, dt
    elif n_datos >= 2:
        print('Se agrupan {} intervalos base'.format(n_datos))
        # Al hacer reshape, el array debe tener el tamaño exacto
        # Se deben obviar los datos sobrantes
        _partes = len(data) // n_datos
        _indice_exacto = _partes * n_datos
        _matriz = data[0:_indice_exacto].reshape(_partes, n_datos)
        datos_agrupados = _matriz.sum(axis=1, dtype='uint32')
        if dt is None:
            return datos_agrupados
        else:
            dt_agrupado = dt * n_datos
            print('Intervalo de adquisición agrupado: {} s'.format(dt_agrupado))
            return datos_agrupados, dt_agrupado


def rate_from_timestamp(tiempo_entre_pulsos):
    """
    Estima la tasa de cuentas e incerteza a partir del tiempo entre pulsos

    Parámetros
    ----------
        tiempo_entre_pulsos : numpy array
            Vector con los tiempos entre pulsos. Cuidado con las unidades.

    Resultados
    ----------
        R_mean : float
            Tasa de cuentas promedio
        R_std : float
            Desviación estandar del promedio de la tasa de cuentas.
            Se calcula con la fórmula de propagación de errores a primer órden.
    """
    # Promedio
    _dt_mean = np.mean(tiempo_entre_pulsos)
    R_mean = 1.0/_dt_mean
    # Desvío
    _dt_std = np.std(tiempo_entre_pulsos, ddof=1) \
        / np.sqrt(len(tiempo_entre_pulsos))
    # Fórmula de propagación de errores a primer orden
    R_std = _dt_std / _dt_mean**2
    return R_mean, R_std


def timestamp_to_timewindow(datos, dt, units_in, units_out, tb):
    """
    Convierte los datos de time-stamp en cantidad de pulsos en dt

    Parámetros
    ----------
        datos : (list of) numpy array
            Datos expresados como tiempos de llegada de cada pulso
        dt : float or int
            Intervalo temporal en que se agruparán los pulsos
        units_in : string ('segundos', 'pulsos')
            Unidad de tiempo de `dt`
        units_out : string ('segundos', 'pulsos')
            Unidad de tiempo que se utilizará para hacer pulsos/dt
        tb : float
            Duración del pulso utilizado para contar

    Resultados
    ----------
        datos_binned : (list of) numpy array
            Pulsos agrupado en el dt
        tiempos: (list of) numpy array
            Cada elemento es un vector temporal asociado a cada bin centrado
            Los elementos están asociados a los elementos de `datos_binnes`,
            conservando el orden.
            (si `units_out` = 'segundos')
            Vector con índices dsde 0 ... Nbin-1 (si `units_out` = 'pulsos')

    >>> a = np.asarray([0, 2, 3, 6, 7, 8, 14])
    >>> y, t = timestamp_to_timewindow(a, 3, 'pulsos', 'pulsos', 1)
    >>> y
    array([2, 1, 3, 0])
    >>> t
    array([0, 1, 2, 3])

    """

    if isinstance(datos, list):
        _es_lista = True
    else:
        _es_lista = False
        datos = [datos]
    # Paso a unidades de pulsos
    if units_in == 'segundos':
        dt = np.float(dt / tb)
    elif units_in == 'pulsos':
        pass
    else:
        print('La unidad de dt_in sólo puede ser "segundos" o "pulsos"')
        quit()

    if units_out not in ['pulsos', 'segundos']:
        print('La unidad de salida sólo puede ser "segundos" o "pulsos"')
        quit()

    datos_binned = []
    tiempos = []
    for dato in datos:
        # --------------------------------------------------------------------
        # No recuerdo si esto era realmente necesario luego de esquivar el bug
        # que tiene numpy.bincount()
        #
        # if dato[-1] <= (2**64 / 2 - 1):
        #     dato = dato.astype(np.int64)
        # else:
        #     print('No se puede aplicar binncount(), buscar otra forma')
        #     quit()
        # --------------------------------------------------------------------
        # Cantidad de bines que se generan
        _Nbin = np.uint64(dato[-1] // dt)
        # Tiempo máximo exacto que voy a tomar respecto al dt_in
        t_exacto = (dato[-1] // dt) * dt
        # Índice del tiempo exacto
        i_exacto = np.searchsorted(dato, t_exacto, side='left')
        _dat = dato[0:i_exacto] // dt
        _bines = np.bincount(_dat.astype('int64'), minlength=_Nbin)
        # _bines = np.bincount(dato[0:i_exacto] // dt, minlength=_Nbin)
        if units_out == 'segundos':
            _bines = _bines / dt / tb
        datos_binned.append(_bines)

        # Construyo vectores temporales para cada vector leido
        tiempo = np.arange(_bines.size)

        if units_out == 'segundos':
            # vector centrado en los bines
            tiempo = tiempo + 0.5
            tiempo = tiempo * dt * tb
        tiempos.append(tiempo)

    # En caso de que no sea una lista
    if not _es_lista:
        datos_binned = datos_binned[0]
        tiempos = tiempos[0]

    return datos_binned, tiempos


if __name__ == "__main__":
    import doctest
    doctest.testmod()
