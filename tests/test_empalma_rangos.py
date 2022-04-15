#!/usr/bin/env python3

"""
Prueba de la función para empalmar la evolución de una señal cuando se mide
con un amplificador lineal en distintas décadas
"""

import os
import matplotlib.pyplot as plt
import seaborn as sns
sns.set()

import sys
sys.path.append('/home/pablo/CinePy')

from modules.point_kinetics.io_modules import lee_reactimetro
from modules.handy_tools import empalma_rangos


archivo = os.path.join("..", "datos", "M05_pot.AI.D1.bin")

# Tiempos previos y posteriores a cada salto
t_saltos = [
       (528.4, 529.0),
       (618.6, 619.5),
       (719.8, 720.5),
       (819.7, 820.4),
       ]
# Lee el archivo grabado
n, rho, t, sdn, dt, head = lee_reactimetro(archivo)
# Empalma las evoluciones de cada rango
n_empalmado = empalma_rangos(n, t, t_saltos)
# Grafica
fig, ax = plt.subplots()
ax.plot(t, n, label='medido')
ax.plot(t, n_empalmado, label='empalmado')
ax.legend()
ax.set_xlabel("Tiempo [s]")
ax.set_ylabel("Voltaje [V]")
ax.set_yscale('log')

plt.show()
