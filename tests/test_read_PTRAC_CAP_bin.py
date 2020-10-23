#!/usr/bin/env python3

"""
Test para la versión optimizada de la función read_PTRAC_CAP_bin()
"""

import sys

sys.path.append('/home/pablo/CinePy/')
from modules.io_modules import read_PTRAC_CAP_bin, read_PTRAC_CAP_bin_obsoleta


if __name__ == '__main__':

    archivo_n = 'in_sdef_n.p'

    datos_n, header_n = read_PTRAC_CAP_bin(archivo_n)
    datos_n_obs, header_n = read_PTRAC_CAP_bin_obsoleta(archivo_n)

    print(datos_n_obs == datos_n)
