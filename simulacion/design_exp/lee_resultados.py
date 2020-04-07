#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script para leer los resultados de cada corrida

Entre en todas las carpetas y lee la salida de MCNP.
Escribe los resultados de cada tally en un archivo distinto.
"""

import os
import glob
import sys
sys.path.append('../../')
from modules.io_modules import lee_tallies


if __name__ == '__main__':

    # Carpetas donde entrará a leer
    folders = glob.glob("case_*")
    folders.sort()

    parent = os.getcwd()

    # Entra en cada carpeta a leer los rsultados de las tallies
    results_1 = []
    results_2 = []
    radios = []
    for folder in folders:
        os.chdir(folder)
        # Lectura de la salida de MCNP
        data, nps, source_neutrons = lee_tallies(folder + '.o')
        results_1.append(data[0])
        results_2.append(data[1])

        # Lectura de los parámetros de la simulación
        with open('info_valores.txt', 'r') as f:
            for line in f:
                if line.startswith('@r_balde@'):
                    radios.append(line.split()[-1])
                    break

        os.chdir(parent)

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
                f.write(rad + sep + val[0] + sep + val[1] + '\n')

