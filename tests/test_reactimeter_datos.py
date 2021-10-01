#!/usr/bin/env python3

import numpy as np
import matplotlib.pyplot as plt
import os
import seaborn as sns
sns.set()

import sys
sys.path.append('/home/pablo/CinePy')

from modules.point_kinetics.reactimeter import reactimetro
from modules.point_kinetics.io_modules import lee_reactimetro
from constantes.lectura import lee_constantes_retardados
from constantes.constantes_reactores import RA3

if __name__ == "__main__":

    archivos = [
                "E01_potencia_cajas.AI.D1.bin",
               ]

    for archivo in archivos:
        n, rho, t, sdn, dt, head = lee_reactimetro(archivo)

    ind = t < 700
    n = n[ind]
    rho = rho[ind]
    t = t[ind]
    sdn = sdn[ind]

    # Delayed neutron constants 
    b, lam , beta = lee_constantes_retardados('Tuttle')
    # Reduced generation time
    Lambda_red = RA3.LAMBDA_REDUCIDO
    # dt read from header of data file
    for line in head:
        if line.startswith(b"Frecuencia sampleo procesamiento"):
            dt = line.split()[-1]
            dt = 1 / float(dt)

    rho_r, t_r, _ = reactimetro(n, dt, lam, b, Lambda_red)

    fig1, ax = plt.subplots(2, 1, sharex=True)
    ax[0].plot(t, n/n[0], label="Acquired")
    ax[1].plot(t, rho, label="Acquired")
    ax[0].set_ylabel('Voltage [V]')

    ax[1].set_xlabel('Time [s]')
    ax[1].set_ylabel('Reactivity [$]')

    ax[1].plot(t_r, rho_r, label="Reactimeter")

    # ax[1].legend(loc="upper center", ncol=2, bbox_to_anchor=(0.5, 1.35))
    ax[1].legend(loc="upper center", ncol=2)

    fig1.tight_layout()
    plt.show()

