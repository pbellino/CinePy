#!/usr/bin/env python3

"""
Script para probar la corrección del roll over al procesar los datos
provenientes de una DAQ que haya adquirido enteros de 32 bits
"""

import sys
import numpy as np
sys.path.append('/home/pablo/CinePy')

from modules.alfa_rossi_preprocesamiento import corrige_roll_over

tiempos_raw = [2**32-1, 0]
resultado_teorico = [np.asarray([0, 1], dtype=np.uint64)]
tiempos_tarjeta = np.asarray(tiempos_raw, dtype=np.uint32)

print(f"Tiempos originales: {tiempos_tarjeta}")

tiempos_list = [tiempos_tarjeta]

tiempos_corregidos = corrige_roll_over(tiempos_list)

print(80*'-')
print(f"Tiempos corregidos: {tiempos_corregidos}")
print(80*'-')

assert all(tiempos_corregidos[0] == resultado_teorico[0])
