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

    archivo = 'input.o'

    datos, nombre, bins = lee_tally_E_card(archivo)

    for nom, data in datos.items():
        eng = data[:, 0]
        val = data[:, 1]
        std_val = data[:, 2] * val
        bin_limits = bins[nom]
        # Calcula ancho del bin
        bin_width = np.diff(bin_limits, axis=1)[:, 0]
        # Normalizo con ancho del bin
        val = val / bin_width
        std_val = std_val / bin_width

        fig, ax = plt.subplots(1, 1, figsize=(8, 6))
        ax.errorbar(eng, val, yerr=std_val, fmt='.')
        ax.set_xlabel('Energía [MeV]')
        ax.set_ylabel('Valores / MeV')
        ax.set_xscale('log')
        ax.set_yscale('log')
        ax.set_title('Gráfico de la tally ' + nom)
    plt.show()
