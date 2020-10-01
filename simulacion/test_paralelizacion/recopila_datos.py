#!/usr/bin/env python3

"""
Script para probar cómo  leer y procesar datos de corridas paralelizadas
"""

import numpy as np
import sys
sys.path.append('/home/pablo/CinePy')
from modules.corridas_paralelizadas import run_paralelo
from modules.io_modules import read_PTRAC_CAP_bin
from modules.simulacion_modules import lee_nps_entrada, read_PTRAC_estandar, \
                                       agrega_tiempo_de_fuente, merge_outputs


if __name__ == '__main__':

    # Corridas n + p
    datos_n, datos_p, nps = merge_outputs(dos_corridas=True)
    datos_n_fte = agrega_tiempo_de_fuente(100, nps, datos_n)
    datos_p_fte = agrega_tiempo_de_fuente(100, nps, datos_p)
    print(nps, np.shape(datos_n), np.shape(datos_p))
    print(np.shape(datos_n_fte), np.shape(datos_p_fte))

    # Corridas n
    # datos_n, nps = merge_outputs()
    # datos_n_fte = agrega_tiempo_de_fuente(100, nps, datos_n)
    # print(nps, np.shape(datos_n))
    # print(np.shape(datos_n_fte))
