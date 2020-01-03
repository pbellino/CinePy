#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np
import matplotlib.pyplot as plt

import sys
sys.path.append('../')

from modules.io_modules import read_timestamp

import seaborn as sns
sns.set()
plt.style.use('paper')


def genera_tiempos_entre_pulsos(nombres, unidad='pulsos', t_base=12.5e-9):
    """
    TODO
    unidades : 'pulsos', 'tiempo'
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


def grafica_histograma_interarrivals(tiempo_entre_pulsos, unidad='pulsos'):
    """
    TODO
    """
    aa, bb = np.histogram(tiempo_entre_pulsos, bins=1000, density=True)
    fig1, ax1 = plt.subplots(1, 1)
    center_bin = bb[:-1] + np.diff(bb)
    ax1.plot(center_bin, aa, '.')
    ax1.set_yscale('log')
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
    ax1.grid('True')
    ax1.ticklabel_format(style='sci', axis='x', scilimits=(0, 0),
                         useMathText=True)
    plt.show()
    return None


if __name__ == '__main__':

    # ---------------------------------------------------------------------------------
    # Parámetros de entrada
    # ---------------------------------------------------------------------------------
    # Archivos a leer
    nombres = [
              '../datos/medicion04.a.inter.D1.bin',
              ]
    # ---------------------------------------------------------------------------------
    unidad = 'tiempo'
    tiempos, uni = genera_tiempos_entre_pulsos(nombres, unidad)
    grafica_histograma_interarrivals(tiempos, uni)
    # grafica_datos_agrupados(nombres)
