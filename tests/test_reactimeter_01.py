#!/usr/bin/env python3

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
sns.set()

import sys
sys.path.append('/home/pablo/CinePy')

from modules.point_kinetics.reactimeter import reactimetro
from modules.point_kinetics.soluciones_analiticas import in_hour_equation, \
            rho_analitica_01
from constantes.lectura import lee_constantes_retardados
from constantes.constantes_reactores import RA3 as REACTOR

if __name__ == "__main__":

    """
    Script para probar modules.point_kinetics.reactimeter.reactimetro con la
    función analítica n(t) = n0 * exp(omega * (t-t0)) cuya reactividad teórica
    es conocida.
    """

    # Delayed neutron constants
    b, lam , beta = lee_constantes_retardados('Tuttle')
    # Reduced generation time
    Lambda_red = REACTOR.LAMBDA_REDUCIDO

    constantes = b, lam, Lambda_red
    # Simulated neutron density
    n0 = 10
    omega = -4e-3
    t0 = 200
    tmax = 800
    Npunt= 50000
    t = np.linspace(0.0, tmax, Npunt)
    n_test = n0 * np.exp(omega * (t-t0))
    n_test[t<=t0] = n0
    # Reactividad teórica
    rho_analitica = rho_analitica_01(t, t0, omega, constantes)

    dt = t[1] - t[0]
    # Reactividad dada por el reactímetro
    rho_r, t_r, _ = reactimetro(n_test, dt, lam, b, Lambda_red)

    # Valor asintótico teórico
    rho_asin = in_hour_equation(omega, 0, constantes)

    fig1, ax = plt.subplots(2, 1, sharex=True)
    ax[0].plot(t, n_test, label="Test")
    ax[0].set_ylabel('Neutron density')

    ax[1].plot(t_r, rho_r, 'o', label="Numeric")
    ax[1].plot(t, rho_analitica, '.-', label="Analitica")
    ax[1].set_xlabel('Time [s]')
    ax[1].set_ylabel('Reactivity [$]')

    ax[1].legend(loc="upper center", ncol=1)

    _msg = "Valor asintótico: {:.6e} (teórico) y {:.6e} (último dato)"
    ax[1].set_title(_msg.format(rho_asin, rho_r[-1]))
    fig1.tight_layout()
    plt.show()

