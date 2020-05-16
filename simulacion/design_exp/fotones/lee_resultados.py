#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script para leer los resultados de cada corrida
TODO
"""

import glob
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
import sys
sys.path.append('../../../')
from modules.io_modules import lee_tally_E_card
sns.set()


if __name__ == '__main__':

    folders = glob.glob("case_*")
    folders.sort()

    parent = os.getcwd()

    radios = []
    # Fotones de 2.22MeV en los detectores
    results_1 = []
    results_2 = []
    # Espectro de las particulas que salen del balde
    espectros_n = []
    espectros_p = []
    for folder in folders[0::5]:
        os.chdir(folder)
        datos, nombre, bins = lee_tally_E_card(folder + '.o')
        # Se normaliza el espectro por el ancho del bin, para todos
        for nom, data in datos.items():
            # Guardo los resultados para gammas de 2.22MeV
            if nom == '14':
                indx = (data[:, 0] > 2.20) & (data[:, 0] <= 2.24)
                # Obtengo incerteza
                _std_val = data[indx, 1] * data[indx, 2]
                # Propago la suma de los bines
                _std_suma = np.sqrt(np.sum(_std_val**2))
                _val_suma = np.sum(data[indx, 1])
                results_1.append([_val_suma, _std_suma])
            elif nom == '24':
                indx = (data[:, 0] > 2.20) & (data[:, 0] <= 2.24)
                # Obtengo incerteza
                _std_val = data[indx, 1] * data[indx, 2]
                # Propago la suma de los bines
                _std_suma = np.sqrt(np.sum(_std_val**2))
                _val_suma = np.sum(data[indx, 1])
                results_2.append([_val_suma, _std_suma])

            # Normalizo los espectros
            bin_limits = bins[nom]
            # Calcula ancho del bin
            bin_width = np.diff(bin_limits, axis=1)[:, 0]
            # Normalizo el valor del histograma
            data[:, 1] = data[:, 1] / bin_width

        espectros_n.append(datos['11'])
        espectros_p.append(datos['21'])
        # Lectura de los parámetros de la simulación
        with open('info_valores.txt', 'r') as f:
            for line in f:
                if line.startswith('@r_balde@'):
                    radios.append(line.split()[-1])
                    break
        os.chdir(parent)

    # -------------------------------------------------------------------------
    #
    # Escribe los valores leídos
    # Separedor de columnas
    sep = 4*' '
    # Encabezado
    encabezado = '# Radio balde [cm]' + sep + 'Tasa_reac' + sep + 'Error rel\n'
    files_out = ['resultados_1.dat', 'resultados_2.dat']
    res_list = [results_1, results_2]
    for res, arch in zip(res_list, files_out):
        with open(arch, 'w') as f:
            f.write(encabezado)
            for rad, val in zip(radios, res):
                f.write(rad + sep + str(val[0]) + sep + str(val[1]) + '\n')

    # -------------------------------------------------------------------------
    #
    # Graficas de espectros de partículas que salen del balde
    fig1, ax = plt.subplots(1, 1, figsize=(8, 6))
    for esp_n, rad in zip(espectros_n, radios):
        eng = esp_n[:, 0]
        val = esp_n[:, 1]
        std_val = esp_n[:, 1] * esp_n[:, 2]
        ax.errorbar(eng, val, yerr=std_val, fmt='.-', label=str(rad))
        ax.set_xlabel('Energía neutrón [MeV]')
        ax.set_ylabel('Número / MeV / (fis. esp)')
        ax.set_xscale('log')
        ax.set_yscale('log')
        ax.set_title('Espectro de neutrones que salen del balde')
        ax.legend(title='Radio balde [cm]', ncol=2)

    fig2, ax = plt.subplots(1, 1, figsize=(8, 6))
    for esp_p, rad in zip(espectros_p, radios):
        eng = esp_p[:, 0]
        val = esp_p[:, 1]
        std_val = esp_p[:, 1] * esp_p[:, 2]
        ax.errorbar(eng, val, yerr=std_val, fmt='.-', label=str(rad))
        ax.set_xlabel('Energía fotón [MeV]')
        ax.set_ylabel('Número / MeV / (fis. esp)')
        ax.set_xscale('log')
        ax.set_yscale('log')
        ax.set_title('Espectro de fotones que salen del balde')
        ax.legend(title='Radio balde [cm]', ncol=2)

    fig1.savefig('espectros_neutrones.png')
    fig2.savefig('espectros_fotones.png')

    plt.show()
