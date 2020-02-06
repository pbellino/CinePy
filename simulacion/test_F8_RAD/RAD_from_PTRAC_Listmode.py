#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Comparación de la distribución alfa-Rossi obtenida con las tallies F8 y PTRAC
"""

import numpy as np
import sys

sys.path.append('../../')
from modules.io_modules import lee_tally_F8_RAD
from modules.simulacion_modules import RAD_sin_accidentales


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
