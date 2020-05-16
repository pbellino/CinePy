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
                 label=r'Detector 1 NaI')
    ax1.errorbar(radio_2, tasa_reac_2, yerr=std_tasa_reac_2, fmt='.',
                 label=r'Detector 2 NaI')
    ax1.set_xlabel('Radio balde con agua [cm]')
    ax1.set_ylabel('Flujo de partíulas en el detector [1 /cm$^2$ / FE]')
    ax1.ticklabel_format(style='sci', axis='y', scilimits=(0, 0),
                         useMathText=True)
    ax1.set_title('Fotones con energías entre 2.20 y 2.24 MeV')
    # ax1.set_yscale('log')
    ax1.legend()
    # fig1.savefig('graficos.png')
    plt.show()
