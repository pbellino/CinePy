#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np

import sys
sys.path.append('../')

from modules.io_modules import read_bin_dt

a, header = read_bin_dt('../datos/nucleo_01.D1.bin')
for line in header:
    print(line)
print('-'*50)

# Construyo los valores que se van a comparar con la referencia
leido0 = len(a)
# 10 datos intermedios
leido1 = a[45000-1:45010-1]
# Los últimos 10 datos
leido2 = a[-10:]

# Se abre el archivo con los valores de referencias
referencia = []
with open('resultados_octave.dat','r') as f:
    for line in f:
        if not line.startswith('#'):
            referencia.append(line.rstrip('\n'))

refe0 = int(referencia[1])
refe1 = [int(x) for x in referencia[2].split()]
refe2 = [int(x) for x in referencia[3].split()]

if refe0==leido0:
    print('La cantidad de datos leidos es correcta: {}'.format(leido0))
if all(refe1==leido1):
    print('Los datos de 45000 a 45009 son correctos: {}'.format(leido1))
if all(refe2==leido2):
    print('Los últimos 10 datos leidos son correctos: {}'.format(leido2))
