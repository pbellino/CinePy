#!/usr/bin/env python3

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
sns.set()
import sys
sys.path.append('/home/pablo/CinePy')

from constantes.lectura import lee_constantes_retardados
from modules.point_kinetics.soluciones_analiticas import solucion_analitica_Ia
from modules.point_kinetics.soluciones_numericas import direct_pk_ODE_solver


if __name__ == "__main__":

    """
    Compara el valor de la solución analítica con la solución numérica de
    scipy.integrate.ode
    """

    from constantes.constantes_reactores import RA3 as REACTOR

    # Delayed neutron constants 
    b, lam , beta = lee_constantes_retardados('Tuttle')
    # Reduced generation time
    Lambda_red = REACTOR.LAMBDA_REDUCIDO

    constants = b, lam, Lambda_red

    # Cantidad de puntos
    Npunt = 10000
    # Paso de integración
    dt = 0.001
    # Vector temporal
    t = dt * np.arange(0, Npunt)
    tmax = t[-1]

    # Cambio en reactividad (en dólares)
    rho_i = 0
    rho_f = -1
    # Cambio en la Fuente de neutrones
    Q_i = 0
    Q_f = 0
    # Tiempo del salto instantáneo
    t0 = 2
    # Valor inicial
    n0 = 5
    # Reactividad en función del tiempo
    reactividad = rho_f * np.ones_like(t)
    reactividad[t<=t0] = rho_i

    n_analitica = solucion_analitica_Ia(t, rho_f, t0, n0, constants)

    # Definición de la reactividad 
    def rho(t):
        if t >= t0:
            return rho_f
        elif t < t0:
            return rho_i

    # Definición de la fuente 
    def S(t):
        _vect = np.zeros(len(b) +1)
        if  t >=t0:
            _vect[0] = Q_f
        elif t < t0:
            _vect[0] = Q_i
        return _vect

    # Resuelve con scipy.integrate.ode
    t_ode, n_ode, _ = direct_pk_ODE_solver(rho, n0, dt, tmax, constants, S)

    # Graficación
    fig, ax = plt.subplots(2, 1, figsize=(7,6), sharex=True)
    ax[0].plot(t, reactividad, 'o', label="Original")
    ax[0].set_ylabel(r'$\$$(t)')

    ax[1].plot(t, n_analitica, 'o', label='analítica_Ia')
    ax[1].plot(t_ode, n_ode, '.-', label='scipy.integrate.ode')
    ax[1].set_ylabel('n(t)')
    ax[1].set_xlabel('Tiempo [s]')
    ax[1].legend()

    fig.tight_layout()
    plt.show()
