#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script para leer los resultados de cada corrida
TODO
"""

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import sys
sys.path.append('../../../../')
from modules.io_modules import lee_tally_E_card
sns.set()


if __name__ == '__main__':

    archivos = [
                'input_001.o',
                'input_002.o',
                'input_003.o',
                'input_004.o',
                ]
    labels = [
              'Fuente lin - Sin det - Sin agua',
              'Fuente vol - Sin det - Sin agua',
              'Fuente vol - Con det - Sin agua',
              'Fuente vol - Con det - con agua',
              ]

    tal = '21'
    fig, ax = plt.subplots(1, 1, figsize=(8, 6))
    for archivo, label in zip(archivos, labels):
        datos, nombre, bins = lee_tally_E_card(archivo)
        eng = datos[tal][:, 0]
        val = datos[tal][:, 1]
        std_val = datos[tal][:, 2] * val
        bin_limits = bins[tal]
        # Calcula ancho del bin
        bin_width = np.diff(bin_limits, axis=1)[:, 0]
        # Normalizo con ancho del bin
        val = val / bin_width
        std_val = std_val / bin_width
        ax.errorbar(eng, val, yerr=std_val, fmt='.-', label=label)
        ax.set_xlabel('Energía [MeV]')
        ax.set_ylabel('Valores / MeV')
        ax.set_xscale('log')
        ax.set_yscale('log')

    ax.set_title('Gráfico de la tally ' + tal)
    ax.legend()
    plt.show()
