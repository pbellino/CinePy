#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script para verificar que read_timestam esté leyendo bien.

Se compara con las lecturas que hace el script de Octave/Matlab, cuyos
resultados fueron previamente guardados en el archivo llamado
'resultados_timestamp_octave.dat'
"""

import sys
sys.path.append('../')

from modules.io_modules import read_timestamp

a, header = read_timestamp('../datos/medicion04.a.inter.D1.bin')
for line in header:
    print(line)
print('-'*50)

# Construyo los valores que se van a comparar con la referencia
leido0 = len(a)
# 10 datos intermedios (donde hay un roll-over)
leido1 = a[121122-1:121132-1]
# Los últimos 10 datos
leido2 = a[-10:]

# Se abre el archivo con los valores de referencias
referencia = []
with open('resultados_timestamp_octave.dat', 'r') as f:
    for line in f:
        if not line.startswith('#'):
            referencia.append(line.rstrip('\n'))

refe0 = int(referencia[1])
refe1 = [int(x) for x in referencia[2].split()]
refe2 = [int(x) for x in referencia[3].split()]

if refe0 == leido0:
    print('La cantidad de datos leidos es correcta: {}'.format(leido0))
if all(refe1 == leido1):
    print('Los datos de 121122 a 121132 son correctos: {}'.format(leido1))
if all(refe2 == leido2):
    print('Los últimos 10 datos leidos son correctos: {}'.format(leido2))
