#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script para verificar que `arossi_una_historia_I` esté trabajando bien.

Se compara con las lecturas que hace el script de Octave/Matlab, cuyos
resultados fueron previamente guardados en el archivo llamado
'resultados_historia_arossi.dat'

En Octave no se separó por historias, por lo cual sólo es válido comparar los
triggers de la primer historia obtenida en python.
"""

import numpy as np
import sys
sys.path.append('../')
sys.path.append('../src')

from src.alfa_rossi_preprocesado import alfa_rossi_preprocesado
from src.alfa_rossi import arossi_una_historia_I

archivo = 'medicion04.a.inter.D1.bin'
nombres = ['../datos/' + archivo]
Nhist = 100
tb = 12.5e-9
dt_s = 0.5e-3
dtmax_s = 50e-3

# Para comparar con la referencia:
dt = np.int(dt_s / tb)
dtmax = np.int(dtmax_s / tb)
N_bin = np.int(dtmax_s / dt_s)

# Se lee archvo y generan las historias
data_bloques, _, _ = alfa_rossi_preprocesado(nombres, Nhist, tb)

# Selecciono el primer archivo y la primer historia
data = data_bloques[0][0]
historia_1 = arossi_una_historia_I(data, dt_s, dtmax_s, tb)

# Se lee el trigger #1
leido_1 = historia_1[0]
# Se lee el trigger #26
leido_26 = historia_1[25]
# Se lee el trigger #77
leido_77 = historia_1[76]

# Se abre el archivo con los valores de referencias
referencia = []
with open('resultados_historia_arossi.dat', 'r') as f:
    for line in f:
        if not line.startswith('#'):
            referencia.append(line.rstrip('\n'))

refe0 = referencia[0]   # Nombre de archivo
refe1 = int(referencia[1])  # dt
refe2 = int(referencia[2])  # N_bin
refe4 = [int(x) for x in referencia[3].split(',')]  # trigger #1
refe5 = [int(x) for x in referencia[4].split(',')]  # trigger #26
refe6 = [int(x) for x in referencia[5].split(',')]  # trigger #77

# Se hacen las comparaciones
print('-' * 50)
if refe0 == archivo:
    print('Se analiza el archivo: {}'.format(archivo))
else:
    print('Se está leyendo un archivo diferente al de referencia')
    print('Referencia : ' + refe0)
    quit()
if refe1 != dt:
    print('No coinciden los dt')
    quit()
if refe2 != N_bin:
    print('No coinciden los N_bin')
    quit()
if all(refe4 != leido_1):
    print('El trigger #1 no coincide')
    quit()
if all(refe5 != leido_26):
    print('El trigger #26 no coincide')
    quit()
if all(refe6 != leido_77):
    print('El trigger #77 no coincide')
    quit()
print('Todas las comparaciones resultaron correctas')
print('-' * 50)
