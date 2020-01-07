#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" TODO """

import numpy as np
import matplotlib.pyplot as plt
import uncertainties as unc

import sys
sys.path.append('../')

from modules.io_modules import read_timestamp
from modules.estadistica import rate_from_timestamp

plt.style.use('paper')


def genera_tiempos_entre_pulsos(nombres, unidad='pulsos', t_base=12.5e-9):
    """
    Calcula el tiempo entre pulsos para los datos especificados.

    Lo calcula directamente cno numpy.diff(). Recordar que lo hace sobre los
    datos sin corrección del roll-over y en uint32. Se aprovecha que la resta
    en python hace un nuevo roll-over para mantenerse dentro de uint32.

    Parámetros
    ----------
    nombres : lista de strings
        Nombre de los archivos que se quieren leer

    unidad : string, opcional
        Se especifica las unidades para el tiempo
        'pulsos' : (default) Unidades de pulsos de reloj utilizado
        'tiempo' : segundos (utiliza el valor de `t_base`)

    t_base: float, opcional
        Periodo del reloj utilizado para contar. Para el sistema NI se
        utiliza un reloj de 80MHz, por lo cual t_base=12.5e-9s.

    Resultados
    ----------
    tiempo_entre_pulsos : list of numpy.ndarray
        Cada elemento es la lista con tiempos entre pulsos.
        De acuerdo a la unidad de tiempo seleccionada `unidad` el tipo de
        dato será:
            `unidad`='pulsos': uint32
            `unidad'='tiempo': float64

    unidad : string
        Unidad utilizada para el tiempo. La misma para todos los archivos.
        Se pone como salida para utilizarla en los gráficos.

    Se graba el gráfico en un archivo llamado `nombre'_hist.png

    """

    tiempo_entre_pulsos = []
    for nombre in nombres:
        _data, _header = read_timestamp(nombre)
        _dts = np.diff(_data)
        if unidad == 'tiempo':
            print('Tiempo expresado en [s] con numpy.ndarray de float64')
            _dts = np.float64(_dts*t_base)
        elif unidad == 'pulsos':
            pass
        else:
            print('Se especificó mal la unidades de tiempo')
            print('Se toma `pulsos`')
            unidad = 'pulsos'
        tiempo_entre_pulsos.append(_dts)
    return (tiempo_entre_pulsos, unidad)


def separa_en_historias(time_stamped_data, N_historias):
    """
    Separa los datos de tiempo entre pulsos en historias.

    Lo hace considerando que cada historia tendrá (estadísticamente) la misma
    duración temporal.
    Podría haberse separado por cantidad de pulsos.

    Parámetros
    ----------
        time_stamped_data : numpy nd.array
            Datos con los tiempos de lelgada de cada pulso.
            Ya debe tener corregido el roll-over
        N_historias : integer
            Cantidad de historias en que se quiere separar los datos

    Resultados
    ----------
        historias : list of numpy array
            Cada elemento es una historia. Todas comienzan en t=0.
    """
    _t_maximo = time_stamped_data[-1]
    # Tiempo que durará cada historia (estadísticamente, pues no necesariamente
    # habrá un pulso al tiempo calculado
    _t_historia = _t_maximo / N_historias
    # Cada historia pasa a estar caracterizado por un mismo número (0,1,...,99)
    _bloques = time_stamped_data // _t_historia
    # Busca los índices en donde se cambian de historia (cambia el número con
    # que están caracterizadas)
    _index_historias = np.where(_bloques[:-1] != _bloques[1:])[0]
    # Sumo uno para que sea más fácil aplicar el slice
    _index_historias += 1
    # Controla que haya pulsos en todas las historias
    # En un proceso estacionario debería suceder siempre
    if _index_historias.size < N_historias - 1:
        print('Hay historias que no tienen pulsos. Revisar')
        quit()
    # Índices del comienzo de cada historia
    # (Se aagrega 0 al comienzo para definir la primer historia)
    _index_start = np.insert(_index_historias, 0, 0)
    # Índices del final de cada historia
    # Se agrega al final el índice máximo que para definir la última historia)
    _index_end = np.insert(_index_historias, _index_historias.size,
                           time_stamped_data.size)
    # Se construyen las historias en una lista
    historias = []
    for start, end in zip(_index_start, _index_end):
        # Todas comenzarán en t=0
        historia = time_stamped_data[start:end] - time_stamped_data[start]
        historias.append(historia)

    return historias


def convierte_dtype_historias(historias):
    """
    De ser posible, convierte al tipo de dato de menor tamaño posible

    Se asume que todas las historias tendrán el mismo dtype
    """

    # Asumo que todas las historias tienen el mismo tipo de datos
    # (vienen de un mismo numpy array)
    in_dtype = historias[0].dtype
    print('Tipo de datos originales : {}'.format(in_dtype))
    # Máximo valor de cada historias
    _hist_max = []
    for historia in historias:
        _hist_max.append(historia[-1])
    _hist_max = np.asarray(_hist_max)
    # Fuerzo a que todas las historias tengan el mismo tipo de datos.
    # Se podría optimizar relajando esta condición.
    if all(_hist_max < 2**32):
        _new_dtype = 'uint32'
    elif all(_hist_max < 2**64):
        _new_dtype = 'uint64'
    else:
        _new_dtype = 'float64'
    # Se hace la conversión
    new_historias = []
    for historia in historias:
        new_historias.append(np.asarray(historia, dtype=_new_dtype))
    print('Tipo de dato convrtido: {}'.format(_new_dtype))
    return new_historias


def inspeccion_historias(historias, tb=12.5e-9):
    """
    Verificar los datos separados en historias

    Parámetros
    ---------
        historias : list of numpy.ndarray
        tb : double
            Tiempo de cada pulso de reloj utilizado

    Resultados
    ----------
        pulsos_historia : list
            Cantidad de pulsos de cada historia
        tiempos_historia : list
            Duración de cada historia (utilizando tb para convertir)
    """

    pulsos_historia = []    # Cantidad de pulsos en cada historia
    tiempos_historia = []   # Duranción de cada historia
    for historia in historias:
        pulsos_historia.append(historia.size)
        tiempos_historia.append(historia[-1])
    # Cantidad total de pulsos
    _pul_tot = np.sum(pulsos_historia)
    print('Pulsos totales : {}'.format(_pul_tot))
    # Duración de cada historia en unidades de tb
    _mean_t = np.mean(tiempos_historia) * tb
    _std_t = np.std(tiempos_historia) * tb
    print('Duración de cada historia: {} +/- {}'.format(_mean_t, _std_t))
    print('(Utilizando {} como unidad temporal)'.format(tb))
    return pulsos_historia, tiempos_historia


if __name__ == '__main__':

    # -------------------------------------------------------------------------
    # Parámetros de entrada
    # -------------------------------------------------------------------------
    # Archivos a leer
    nombres = [
              '../datos/medicion04.a.inter.D1.bin',
              # '../datos/medicion04.a.inter.D2.bin',
              ]
    unidad = 'pulsos'
    yscale = 'log'
    # -------------------------------------------------------------------------

    # Se generan los tiempos entre pulsos
    tiempos, unidad = genera_tiempos_entre_pulsos(nombres, unidad)

    _data, _header = read_timestamp(nombres[0])
    _data_new = np.cumsum(tiempos[0])
    _data_new = np.insert(_data_new, 0, 0)
    print('-'*50)
    print(type(_data_new[0]))
    print(len(_data_new))
    print(_data_new[0])
    print(_data_new[-1])
    print(_data_new[121122-1:121132-1])

    # -------------------------------------------------------------------------
    # Separe el vector con los tiempos en historias
    _data_bloq = separa_en_historias(_data_new, 100)
    # Busca el tipo de dato más pequeño
    _data_bloq = convierte_dtype_historias(_data_bloq)

    quit()

    fig1, ax1 = plt.subplots(1, 1)
    ax1.plot(_data, 'k.')
    for data in _data_bloq:
        ax1.plot(data, 'r.')
    pulsos_tot, tiempos_hist = inspeccion_historias(_data_bloq)

    plt.show()
