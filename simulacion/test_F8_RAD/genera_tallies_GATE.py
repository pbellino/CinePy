#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script para facilitar la escritura del archivo de entrada de MCNP cuando se
quiere calcula la distribución de alfa-Rossi utilizando tally F8 con GATES.
"""

import os.path
import sys

sys.path.append('../../')
from modules.simulacion_modules import genera_tallies


def genera_archivo_completo(arch_sin_tallies, arch_tallies, arch_final):
    """
    Concatena dos archivos y escribe el resultado en un tercero.
    """
    _arch_fin_i = arch_final

    i = 1
    while True:
        if os.path.exists(_arch_fin_i):
            _arch_fin_i = arch_final + '_' + str(i).zfill(2)
            i += 1
        else:
            break
    arch_final = _arch_fin_i
    archivos = [arch_sin_tallies, arch_tallies]
    with open(arch_final, 'w') as fo:
        for archivo in archivos:
            with open(archivo, 'r') as fi:
                fo.write(fi.read())
    print('Se generó el archivo completo: ' + arch_final)
    return None


if __name__ == '__main__':

    nombre_archivo_tallies = 'solo_tallies'
    # nombre_archivo_sin_tallies = 'input_sin_tallies.i'
    # nombre_archivo_completo = 'test_F8_RAD.i'

    def_tallies = {
                   'id_det': '5010 3006',
                   'celdas_detector': '102',
                   'gate_width': 1e-10,
                   'gate_maxim': 1e-9,
                   }

    genera_tallies(nombre_archivo_tallies, def_tallies)

    # genera_archivo_completo(nombre_archivo_sin_tallies,
    #                         nombre_archivo_tallies,
    #                         nombre_archivo_completo,
    #                         )
