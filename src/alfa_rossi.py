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


def grafica_histograma_interarrivals(tiempo_entre_pulsos, *args, **kargs):
    """
    Grafica el histograma de tiempo entre pulsos

    Parámetros
    ----------
    tiempo_entre_pulsos : numpy array
        Vector con los tiempo entre pulsos

    unidad : string
        Unidad utilizada para `tiempo_entre_pulsos`

    nbins : int
        Cantidad de bines para el histograma

    yscale : string
        Escala para el eje y ('linear', 'log')

    nombre : string
        Nombre para la leyenda que identifica la curva

    """
    if kargs is not None:
        unidad = kargs.get('unidad', 'pulsos')
        nbins = kargs.get('nbins', 1000)
        yscale = kargs.get('yscale', 'linear')
        nombre = kargs.get('nombre', 'Datos')

    h_coun, h_bin = np.histogram(tiempo_entre_pulsos, bins=nbins, density=True)
    fig1, ax1 = plt.subplots(1, 1)
    # Genero vector de bins centrados
    center_bin = h_bin[:-1] + np.diff(h_bin)
    ax1.plot(center_bin, h_coun, '.')
    ax1.set_yscale(yscale)
    # Asigno unidades a los bines
    if unidad == 'tiempo':
        xscale = r'Tiempo [s]'
    elif unidad == 'pulsos':
        xscale = r'Pulsos'
    else:
        print('No se reconoce la unidad temporal')
        xscale = 'Desconocido'
    ax1.set_xlabel(xscale)
    ax1.set_ylabel(u'Densidad de probabilidad')
    ax1.set_title('Histograma de tiempo entre pulsos')
    ax1.legend([nombre], loc='best')
    ax1.grid('True')
    ax1.ticklabel_format(style='sci', axis='x', scilimits=(0, 0),
                         useMathText=True)

    # Tasa de cuentas
    _R, _R_std = rate_from_timestamp(tiempo_entre_pulsos)
    R = unc.ufloat(_R, _R_std)
    str_R = r'R = (${:1.2uL}$) cps'.format(R)
    bbox_props = dict(boxstyle='Round', fc='w')
    ax1.annotate(str_R, xy=(0.3, 0.8), bbox=bbox_props, size=15,
                 xycoords='axes fraction')
    # Graba el archivo
    fig1.savefig(nombre + '_hist.png')
    # Imprime en pantalla
    print('-' * 50)
    print('Nombre: ' + nombre)
    print('R = ' + str(R))
    print('-' * 50)
    return None


def separa_en_historias(time_stamped_data, N_historias):
    """
    TODO
    """
    _t_maximo = time_stamped_data[-1]
    print(_t_maximo)
    # Tiempo que durará cada historia
    _t_historia = _t_maximo / N_historias
    _bloques = time_stamped_data // _t_historia
    _index_historias = np.where(_bloques[:-1] != _bloques[1:])
    print(_index_historias)
    print(len(_index_historias[0]))
    # return _data_bloques


if __name__ == '__main__':

    # -------------------------------------------------------------------------
    # Parámetros de entrada
    # -------------------------------------------------------------------------
    # Archivos a leer
    nombres = [
              '../datos/medicion04.a.inter.D1.bin',
              #'../datos/medicion04.a.inter.D2.bin',
              ]
    unidad = 'pulsos'
    nbins = 10000
    yscale = 'log'
    # -------------------------------------------------------------------------
    # Para la leyenda del gráfico
    archivos = []
    for nombre in nombres:
        archivos.append(nombre.rsplit('/')[-1])

    # Se generan los tiempos entre pulsos
    tiempos, unidad = genera_tiempos_entre_pulsos(nombres, unidad)

    _data, _header = read_timestamp(nombres[0])
    _data_new = np.cumsum(tiempos[0])
    _data_new=np.insert(_data_new, 0, 0)
    print(type(_data_new[0]))
    print(len(_data_new))
    print(_data_new[0])
    print(_data_new[-1])
    print(_data_new[121122-1:121132-1])

    _data_bloq = separa_en_historias(_data_new, 100)

    fig1, ax1 = plt.subplots(1, 1)
    ax1.plot(_data, 'k.')
    ax1.plot(_data_bloq, 'r.')
    #ax1.plot(_data_new, 'r.')

    plt.show()
