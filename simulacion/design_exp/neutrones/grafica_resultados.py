#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
"""

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
sns.set()


if __name__ == '__main__':

    archivo_1 = 'resultados_1.dat'
    archivo_2 = 'resultados_2.dat'

    datos_1 = np.loadtxt(archivo_1)
    datos_2 = np.loadtxt(archivo_2)

    radio_1 = datos_1[:, 0]
    tasa_reac_1 = datos_1[:, 1]
    std_tasa_reac_1 = datos_1[:, 2] * tasa_reac_1

    radio_2 = datos_2[:, 0]
    tasa_reac_2 = datos_2[:, 1]
    std_tasa_reac_2 = datos_2[:, 2] * tasa_reac_2

    fig1, ax1 = plt.subplots(1, 1)
    ax1.errorbar(radio_1, tasa_reac_1, yerr=std_tasa_reac_1, fmt='.',
                 label=r'$^3$He chico 6NH12.5')
    ax1.errorbar(radio_2, tasa_reac_2, yerr=std_tasa_reac_2, fmt='.',
                 label=r'$^3$He grande 48NH30')
    ax1.set_xlabel('Radio balde con agua [cm]')
    ax1.set_ylabel('Reacciones $^3$He(n,p)$^3$H por FS')
    ax1.ticklabel_format(style='sci', axis='y', scilimits=(0, 0),
                         useMathText=True)
    # ax1.set_yscale('log')
    ax1.legend()
    # fig1.savefig('graficos.png')
    plt.show()
