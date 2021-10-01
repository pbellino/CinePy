#!/usr/bin/env python3

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
sns.set()

import sys
sys.path.append('/home/pablo/CinePy')

from constantes.lectura import lee_constantes_retardados
from constantes.constantes_reactores import RA3
from modules.point_kinetics.direct_kinetic_solver import cinetica_directa
from modules.point_kinetics.reactimeter import reactimetro
from modules.point_kinetics.soluciones_analiticas import rho_analitica_01


if __name__ == "__main__":

    """
    Script para probar point_kinetics.direct_kinetic_solver comparándo su
    resultado con la n(t) dada por una función analítica. La n(t) debe ser
            n(t) = n0 exp(-omega (t-t0))

    Se asume que hasta t0 el reactor está crítico y estacionario.
    Sin fuente de neutrones
    """

    # Delayed neutron constants 
    b, lam , beta = lee_constantes_retardados('Tuttle')
    # Reduced generation time
    Lambda_red = RA3.LAMBDA_REDUCIDO

    constantes = b, lam, Lambda_red

    # Simulated neutron density
    n0 = 10
    omega = -1e-2
    tmax = 800
    t0 = 200
    Npunt= 10000
    t = np.linspace(0.0, tmax, Npunt)
    n_analitica = n0 * np.exp(omega * (t-t0))
    n_analitica[t<t0] = n0

    rho_test = rho_analitica_01(t, t0, omega, constantes)

    dt = t[1] - t[0]
    n_num, t_num = cinetica_directa(rho_test, n0, dt, lam, b, Lambda_red, 0)

    # Graficación
    fig, ax = plt.subplots(2, 1, figsize=(7,6), sharex=True)
    ax[0].plot(t, rho_test, '.-', label="Analítica")
    ax[0].set_yscale('linear')
    ax[0].set_ylabel(r'$\$$(t)')
    ax[0].legend()

    ax[1].plot(t_num, n_num, 'o', label='Analítica')
    ax[1].plot(t, n_analitica, '.-', label='Numérica')
    ax[1].set_ylabel('n(t)')
    ax[1].set_xlabel('Tiempo [s]')
    ax[1].legend()

    fig.tight_layout()

    plt.show()
