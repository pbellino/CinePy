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


def arossi_grafica_historias(nombres):
    """
    Grafica todas las historias de los archivos indicados.

    Son los archivos grabados con escribe_datos_completos().

    Parámetros
    ----------
        nombres : (list of) strings
            Camino completo del archivo *_ros.dat que contiene los datos de
            todas las historias. PUede ser sólo un string o una lista.

    Resultados
    ----------
        figs : (list of) fig handler
            Referencia a cada figura. Si `nombres` era una lista, entonces figs
            también lo será. Permite modificar parámetros fuera de la función.
    """

    if isinstance(nombres, list):
        _es_lista = True
    else:
        _es_lista = False
        nombres = [nombres]

    figs = []
    for nombre in nombres:
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
        figs.append(fig)
        print('-'*80)

    if not _es_lista:
        figs = figs[0]
    return figs


def arossi_grafica_promedio(nombres):
    """
    Grafica la curva P(tau) de los archivos indicados.

    Son los archivos grabados con escribe_datos_promedio().

    Parámetros
    ----------
        nombres : (list of) strings
            Camino completo del archivo *.dat que contiene los datos de los
            promedios de las historias. PUede ser sólo un string o una lista.

    Resultados
    ----------
        fig : fig handler
            Referencia a la figura. Permite modificar parámetros de la figura
            fuera de la función.
    """

    if not isinstance(nombres, list):
        nombres = [nombres]

    fig, ax = plt.subplots(1, 1)
    for nombre in nombres:
        print('Se lee el archivo : {}'.format(nombre))
        # Lectrua del archivo
        P_mean, P_std, tau, parametros = arossi_lee_historias_promedio(nombre)

        for key in parametros.keys():
            print('{} : {}'.format(key,  parametros.get(key)))

        # Graficación
        label_str = os.path.split(nombre)
        ax.errorbar(tau, P_mean, yerr=P_std, label=label_str, fmt='-.', lw=0.5,
                    elinewidth=0.5, marker='.')
        ax.set_xlabel('Tiempo [s]')
        ax.set_ylabel(r'P($\tau$)')
        fig.tight_layout()
        print('-'*80)

    return fig


if __name__ == '__main__':

    # -------------------------------------------------------------------------
    # Gráfico de historias
    # -------------------------------------------------------------------------
    # Archivos a leer
    nombres = ['./resultados_arossi/medicion04.a.inter.D1_ros.dat',
               './resultados_arossi/medicion04.a.inter.D2_ros.dat']

    figs = arossi_grafica_historias(nombres)

    # figs[1].axes[0].set_xlabel('Nuevo nombre')

    # -------------------------------------------------------------------------
    # Gráfico de promedio
    # -------------------------------------------------------------------------
    # Archivos a leer
    nombres = ['./resultados_arossi/medicion04.a.inter.D1.ros',
               './resultados_arossi/medicion04.a.inter.D2.ros']

    figs = arossi_grafica_promedio(nombres)

    plt.show()
