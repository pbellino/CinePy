#!/usr/bin/env python
# -*- coding: utf-8 -*-

import matplotlib.pyplot as plt

import sys
sys.path.append('../')

from modules.io_modules import lee_historias_completas, lee_fey

import seaborn as sns
sns.set()
plt.style.use('paper')


def grafica_historias_afey(nombre):
    """
    Grafica todas las historias guardadas en el archivo 'nombre'

    Parametros
    ----------
    nombres : lista de strings
        Camino y nombre del archivo .dat que contiene a todas las historias

    Resultados
    ----------
    fig :
        Referencia por si se quiere guardar el gráfico

    """

    vec_t, historias = lee_historias_completas(nombre)

    fig = plt.figure(1)
    ax = fig.add_subplot(1, 1, 1)

    # Se itera sobre cada historia
    for historia in historias.T:
        ax.plot(vec_t, historia)

    ax.set_xlabel(r'$\Delta$ t [s]')
    ax.set_ylabel(r'Y($\Delta$ t)')
    ax.set_title('{} historias leidas del archivo: {}'.format(
       historias.shape[1], nombre))
    ax.grid(True)
    # plt.show()

    return fig


def grafica_afey(nombres):
    """
    Grafica todas la curva promedio y su desvio de los archivos 'nombres'

    Parametros
    ----------
    nombres : lista de strings
        Camino y nombre del archivo .fey con el valor medio y desvío de Y(Dt)

    Resultados
    ----------
    fig :
        Referencia por si se quiere guardar el gráfico

    """

    fig = plt.figure(1)
    ax = fig.add_subplot(1, 1, 1)
    for nombre in nombres:
        vec_t, Y, std_Y = lee_fey(nombre)

        ax.errorbar(vec_t, Y, yerr=std_Y, fmt='.',
                    label=nombre.rsplit('/')[-1])

    ax.set_xlabel(r'$\Delta$ t [s]')
    ax.set_ylabel(r'Y($\Delta$ t)')
    ax.legend(loc='best')
    ax.grid(True)
    # plt.show()

    return fig


if __name__ == '__main__':

    # ---------------------------------------------------------------------------------
    # Parámetros de entrada
    # ---------------------------------------------------------------------------------
    # Archivos a leer
    nombre = 'resultados/nucleo_01.D1D2_cov.dat'
    grafica_historias_afey(nombre)
    plt.show()
    nombre = 'resultados/nucleo_01.D1.fey'
    nombres = ['resultados/nucleo_01.D1.fey',
               'resultados/nucleo_01.D2.fey',
               ]
    # ---------------------------------------------------------------------------------

    myfig = grafica_afey(nombres)

    ax = myfig.get_axes()[0]
    ax.set_title(u'Un título')
    plt.show()
