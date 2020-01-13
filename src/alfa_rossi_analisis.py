#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
TODO
"""

import numpy as np
import matplotlib.pyplot as plt
import os
import seaborn as sns
sns.set()

import sys
sys.path.append('../')

from alfa_rossi_lectura import arossi_lee_historias_completas, \
                               arossi_lee_historias_promedio

plt.style.use('paper')


def arossi_grafica_historias(nombre):
    """
    TODO
    """
    # Lectrua del archivo
    print('Se lee el archivo : {}'.format(nombre))
    historias, tau, parametros = arossi_lee_historias_completas(nombre)

    for key in parametros.keys():
        print('{} : {}'.format(key,  parametros.get(key)))

    # Graficación
    fig, ax = plt.subplots(1, 1)
    ax.plot(tau, historias, marker='.', label='Historias')
    ax.set_xlabel('Tiempo [s]')
    ax.set_ylabel(r'P($\tau$)')
    handles, labels = ax.get_legend_handles_labels()
    ax.legend([handles[0]], [labels[0]], loc='best')
    ax.set_title(os.path.split(nombre)[-1])
    fig.tight_layout()

    return fig


if __name__ == '__main__':

    # -------------------------------------------------------------------------
    # Parámetros de entrada
    # -------------------------------------------------------------------------
    # Archivos a leer
    nombre = './resultados_arossi/medicion04.a.inter.D1_ros.dat'
    # -------------------------------------------------------------------------

    fig1 = arossi_grafica_historias(nombre)

    plt.show()
