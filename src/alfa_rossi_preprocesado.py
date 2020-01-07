#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script para pre-procesar los datos de time-stamping para el método de a-Rossi.

Lee los archivos y genera las historias pedidas.
alfa_rossi_preprocesado() es la función principal.
"""

import numpy as np
import matplotlib.pyplot as plt

import sys
sys.path.append('../')

from modules.io_modules import read_timestamp_list

plt.style.use('paper')


def corrige_roll_over(datas_con_rollover):
    """
    Corrige el roll-over en los datos adquiridos

    El roll-over se produce por la resolución finita del contador utilizado.
    Esta corrección se basa en el casteo que hace python: al usar np.diff()
    hace un roll-over para mantenerse en el tipo de dato original. Al usar
    np.sumsum() pasa al siguiente tipo de datos más grande uint64.

    Parámetros
    ----------
        datas_con_rollover : list of numpy.ndarray
            Cada elemento de la lista son los datos leídos del archivo

    Resultados
    ----------
        data_sin_rollover : list of numpy.ndarray
            Cada elemento son los datos con roll-over corregido

    """
    data_sin_rollover = []
    for i, data in enumerate(datas_con_rollover):
        print('Corrigiendo roll-over del archivo [{}]'.format(i))
        print('Tipo de dato inicial: {}'.format(data.dtype))
        # Obtengo los tiempos entre pulsos
        _dts = np.diff(data)
        # Sumo todos los intervalos
        _data_acum = np.cumsum(_dts)
        # Agrego el primer punto como t=0
        _data_acum = np.insert(_data_acum, 0, 0)
        print('Tipo de dato final {}'.format(_data_acum.dtype))
        print('-' * 50)
        data_sin_rollover.append(_data_acum)

    return data_sin_rollover


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


def separa_en_historias_lista(time_stamped_datas, N_historias):
    """ Wrapper de `separa_en_historias` para ser aplicado en listas """
    historias_list = []
    for t_s_data in time_stamped_datas:
        historias_list.append(separa_en_historias(t_s_data, N_historias))
    return historias_list


def convierte_dtype_historias(historias):
    """
    De ser posible, convierte al tipo de dato de menor tamaño posible

    Se asume que todas las historias tendrán el mismo dtype
    """

    # Asumo que todas las historias tienen el mismo tipo de datos
    # (vienen de un mismo numpy array)
    in_dtype = historias[0].dtype
    print('Convirtiendo tipo de datos de las historias')
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
    print('-' * 50)

    return new_historias


def convierte_dtype_historias_lista(list_historias):
    """ Wrapper de `convierte_dtype_historias` para aplicarlo en listas """

    new_list_historias = []
    for i, historias in enumerate(list_historias):
        print("Archivo [{}]".format(i))
        new_list_historias.append(convierte_dtype_historias(historias))
    return new_list_historias


def inspeccion_historias(historias, tb=12.5e-9):
    """
    Verifica los datos separados en historias

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
    print('-' * 50)
    return pulsos_historia, tiempos_historia


def inspeccion_historias_list(list_historias, tb=12.5e-9):
    """ Wrapper de `inspeccion_historias` para aplicarlo en listas """

    lista_pulsos_historia = []
    lista_tiempos_historia = []
    for i, historias in enumerate(list_historias):
        print('Inspección del archivo [{}]'.format(i))
        _pulsos, _tiempos = inspeccion_historias(historias, tb)
        lista_pulsos_historia.append(_pulsos)
        lista_tiempos_historia.append(_tiempos)
    return lista_pulsos_historia, lista_tiempos_historia


def alfa_rossi_preprocesado(nombres, Nhist, tb):
    """
    Función que genera las historias para todos los archivos leídos

    Hace las correcciones del roll-over y busca el menor tipo de dato con que
    pueden ser guardadas las historias.

    Parámetros
    ----------
        nombres : list of strings
            Nombres de los archivos con los datos de timestamping
        Nhist : integer
            Cantidad de historias
        tb : float
            Tiempo de duración de cada pulso de reloj

    Resultados
    ----------
        data_historias : list of list of numpy.ndarray
            Para cada archivo leido se genera una lista con las Nhist creadas.
            Cada historia podrá tener formato uint32, uint64 o float64
            dependiendo del tamaño.
        data_sin_rollover : list of numpy.ndarray
            Cada elemento son los datos leidos con el roll-over corregido.
            Sólo está para debuggear.
        data_con_rollover : list of numpy.ndarray
            Cada elemento son los datos leidos directamente del archivo.
            Sólo está para debuggear.
    """
    # Se leen los datos del archivo
    data_con_rollover, _header = read_timestamp_list(nombres)
    # Se corrige el roll-over
    data_sin_rollover = corrige_roll_over(data_con_rollover)
    # Separe el vector con los tiempos en historias
    data_historias = separa_en_historias_lista(data_sin_rollover, Nhist)
    # Busca el tipo de dato de menor tamaño
    data_historias = convierte_dtype_historias_lista(data_historias)
    # Para verificar cómo quedó todo (opcional)
    inspeccion_historias_list(data_historias, tb)

    return data_historias, data_sin_rollover, data_con_rollover


if __name__ == '__main__':

    # -------------------------------------------------------------------------
    # Parámetros de entrada
    # -------------------------------------------------------------------------
    # Archivos a leer
    nombres = [
              '../datos/medicion04.a.inter.D1.bin',
              '../datos/medicion04.a.inter.D2.bin',
              ]
    Nhist = 100
    tb = 12.5e-9
    # -------------------------------------------------------------------------
    data_bloques, data_sin_ro, data_con_ro = \
        alfa_rossi_preprocesado(nombres, Nhist, tb)

    fig1, ax1 = plt.subplots(1, 1)
    ax1.plot(data_con_ro[0], 'k.')
    ax1.plot(data_sin_ro[0], 'r.')
    for data in data_bloques[0]:
        ax1.plot(data, 'b.')

    plt.show()
