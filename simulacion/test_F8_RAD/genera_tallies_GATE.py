#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script para facilitar la escritura del archivo de entrada de MCNP cuando se
quiere calcula la distribución de alfa-Rossi utilizando tally F8 con GATES.
"""

import os.path
import numpy as np


def genera_tallies(archivo_tallies, def_tallies, *args, **kargs):
    """
    Genera los tallies F8 con los GATES sucesivos para obtener la RAD

    Parámetros
    ----------
        archivo_tallies : string
            Nombre del archivo donde se guardaran las tallies

        def_tallies : dict
            Diccionario con los parámetros que se utilizarán para construir
            las tallies. Las claves deben ser:
                'id_det' : string
                    ZAID del elemento donde se quiere analizar las capturas
                    (helio-3, boro-10, etc).
                'celdas_detector' : string
                    Celda en donde se analizarán las capturas (detector)
                'gate_width' : float (en segundos)
                    Ancho de la ventana temporal (es el bin en el histogama de
                    la distribución de alfa-Rossi).
                'gate_maxim' : float (en segundos)
                    Es el máximo tiempo que se analizará para cada trigger.
                    Haciendo `gate_maxim` / `gate_width` se obtiene el número
                    de bines de la distribución.
    """
    try:
        id_det = def_tallies['id_det']
        celdas_detector = def_tallies['celdas_detector']
        gate_width_s = def_tallies['gate_width']
        gate_maxim_s = def_tallies['gate_maxim']
    except KeyError:
        print('No se especificaron todos los datos para las tallies')
        quit()

    # Convierto gates de segundos a shakes
    gate_width = gate_width_s * 1e8
    gate_maxim = gate_maxim_s * 1e8
    # Construyo vector de gates
    pd_gates = np.arange(0, gate_maxim, gate_width)
    N_bins = np.int(gate_maxim / gate_width)
    print('Distribución de a-Rossi con {} bins'.format(N_bins))

    with open(archivo_tallies, 'w') as f:
        f.write('c ' + '-'*40 + '\n')
        f.write('c Definición de las tallies con GATE\n')
        f.write('c ' + '-'*40 + '\n')
        # Tally sin GATE
        f.write('FC0008 Capturas en He3 - Sin GATE\n')
        f.write('F0008:n {}\n'.format(celdas_detector))
        f.write('FT0008 CAP {} \n'.format(id_det))
        f.write('c\n')
        # Tallies con GATE
        for i, pd_gate in enumerate(pd_gates, 1):
            f.write('FC{:03d}8 Capturas en He3 - PD={:.2e}s GW={:.1e}s\n'.format(i, pd_gate/1e8, gate_width/1e8))
            f.write('F{:03d}8:n {}\n'.format(i, celdas_detector))
            f.write('FT{:03d}8 CAP {} GATE {} {}\n'.format(i, id_det, pd_gate,
                                                           gate_width))
            f.write('c\n')
        f.write('c Fin de las tallies con gate\n')
        f.write('c ' + '-'*40 + '\n')
    print('Se generó el archivo de tallies: ' + archivo_tallies)
    return None


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
