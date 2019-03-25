#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np
import matplotlib.pyplot as plt

import sys
sys.path.append('../')

from modules.io_modules import lee_historias_completas

plt.style.use('paper')


def grafica_historias_afey(nombre):
    """
    Grafica todas las historias guardadas en el archivo 'nombre'

    Parametros
    ----------
    nombres : lista de strings
        Camino y nombre del archivo .dat que contiene a todas las historias

    """

    vec_t, historias = lee_historias_completas(nombre)

    fig1 = plt.figure(1)
    ax1 = fig1.add_subplot(1, 1, 1)

    # Se itera sobre cada historia
    for historia in historias.T:
        ax1.plot(vec_t, historia)

    ax1.set_xlabel(r'$\Delta$ t [s]')
    ax1.set_ylabel(r'Y($\Delta$ t)')
    ax1.set_title('{} historias leidas del archivo: {}'.format(
        historias.shape[1], nombre))
    ax1.grid(True)

    plt.show()


if __name__ == '__main__':

    # ---------------------------------------------------------------------------------
    # Parámetros de entrada
    # ---------------------------------------------------------------------------------
    # Archivos a leer
    nombres = 'resultados/nucleo_01.D1D2_cov.dat'
    # ---------------------------------------------------------------------------------

    grafica_historias_afey(nombres)
