#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Comparación de la distribución alfa-Rossi obtenida con las tallies F8 y PTRAC
"""

import numpy as np
import sys

sys.path.append('../../')
from modules.alfa_rossi_procesamiento import arossi_una_historia_I
from modules.io_modules import lee_tally_F8_RAD, read_PTRAC_CAP_bin


def RAD_sin_accidentales(nombre, dt_s, dtmax_s):
    """
    Función para obtener la distribución RAD a partir del PTRAC

    El objetivo es comparar con la RAD obtenida con tallies F8 + GATES. Por
    este motivo se deben eliminar las coincidencias accidentales.

    Notar que pueden haber algunas diferencias porque la forma de obtener la
    RAD con las tallies y con los algoritmos míos (arossi_una_historia_I) son
    distintos. Yo obligo a que todos los triggers alcancen el 'dtmax_s'. Las
    tallies F8 en cambio, abren un GATE para cualquier trigger.

    Parámetros
    ----------
        nombre : string
            Nombre del archivo binario PTRAC obtenido con event=CAP

        dt_s : float (segundos)
            Intervalo temporal para cada bin de la distribución

        dtmax : float (segundos)
            Máximo intervalo de la distribución de alfa-Rossi

    Importante
    ----------
        Los valores dt_s y dtmax deben coincidir con los utilizados para
        construir las tallies F8 con GATES sucesivas
    """
    # Leo el archivo binario de PTRAC con event=CAP
    datos, header = read_PTRAC_CAP_bin(archivo_bin)

    # Convierto a array numpy
    datos = np.asarray(datos)
    # Números de historia
    nps = np.asarray(datos[:, 0], dtype='int64')
    # Tiempos
    timestamp = np.asarray(datos[:, 1], dtype='float64') * 1e-8
    # Obtiene los timestamp para una misma historia
    times_historia = []
    for n in set(nps):
        indx = np.where(nps == n)
        # Timestamp por historia y ordenado
        list_by_hist = np.sort(timestamp[indx])
        # Se fija t=0 en el primer pulso
        list_by_hist -= list_by_hist[0]
        times_historia.append(list_by_hist)

    # Datos de la RAD
    historias = []
    for time in times_historia:
        print(time)
        P_historia, _, N_trig, P_trig =  \
            arossi_una_historia_I(time, dt_s, dtmax_s, 1)
        # print(P_trig)
        # Analizo los triggers para no tener que operar sobre P_historia
        # (molesta la normalización en este caso)
        if P_trig.size:
            # Sumo todos trigger
            historias.append(np.sum(P_trig, axis=0))
    # Sumo entre todos los eventos para obtener la distribución de alfa-Rossi
    RAD = np.sum(historias, axis=0)
    return RAD


if __name__ == '__main__':

    # ------------------------------------------------------------------------
    # RAD con Listmode sacando accidentales
    # ------------------------------------------------------------------------
    #
    archivo_bin = 'ptrac_CAP_bin'

    # Deben coincidir con los especificados en los tallies de MCNP
    # utilizados para obtener la RAD con tallies sucesivos
    dt_s = 1e-10
    dtmax_s = 1e-9

    RAD_from_ptrac = RAD_sin_accidentales(archivo_bin, dt_s, dtmax_s)

    # ------------------------------------------------------------------------
    # RAD con tallies F8 + GATES consecutivos
    # ------------------------------------------------------------------------
    #
    archivo = 'test_F8_RAD.out'
    data, cap_NG, nps = lee_tally_F8_RAD(archivo)
    RAD_from_F8 = data[:, 0] * nps
    tot_cap = cap_NG[0] * nps

    print('-'*50)
    print('RAD con PTRAC sin accidentales: \n\t', RAD_from_ptrac)
    print('-'*50)
    print('RAD con F8 + GATES: \n\t', RAD_from_F8.astype(int))

    print('-'*50)
