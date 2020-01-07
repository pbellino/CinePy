#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
TODO
"""

import numpy as np
import matplotlib.pyplot as plt

from alfa_rossi_preprocesado import alfa_rossi_preprocesado
import sys
sys.path.append('../')


plt.style.use('paper')


if __name__ == '__main__':

    # -------------------------------------------------------------------------
    # Parámetros de entrada
    # -------------------------------------------------------------------------
    # Archivos a leer
    nombres = [
              '../datos/medicion04.a.inter.D1.bin',
              '../datos/medicion04.a.inter.D2.bin',
              ]
    Nhist = 100
    tb = 12.5e-9
    # -------------------------------------------------------------------------
    data_bloques, _, _ = alfa_rossi_preprocesado(nombres, Nhist, tb)

