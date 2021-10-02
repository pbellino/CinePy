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
    Compaara la solución obtenida con scipy.integrate.ode frente a la solución
    analítica.

    Se prueba un salto instantáneo en reactividad, sin fuente.
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
    rho_t = rho_f * np.ones_like(t)
    rho_t[ t<=t0 ] = rho_i
    # Fuente en función del tiempo
    Q_t = Q_f * np.ones_like(t)
    Q_t[t <= t0] = Q_i

    n_analitica = solucion_analitica_Ia(t, rho_f, t0, n0, constants)

    # Definición de la reactividad 
    def rho(t):
        if t > t0:
            return rho_f
        elif t <= t0:
            return rho_i

    # Definición de la fuente 
    def S(t):
        if  t >= t0:
            return Q_f
        elif t < t0:
            return Q_i

    # Si se quieren usar valore numéricos para rho(t) se interpola
    # Es bastante más lento que usar una función
    from scipy.interpolate import interp1d
    t_discrete = t
    rho_discrete = np.array([rho(k) for k in t])
    _f = interp1d(t_discrete, rho_discrete, fill_value="extrapolate",
                   kind='linear', assume_sorted=True)
    rho_1 = lambda x: _f(x)
    # Usando sólo al interpolador de numpy (más rápido que el anterior)
    rho_2 = lambda x: np.interp(x, t_discrete, rho_discrete)

    # Resuelve con scipy.integrate.ode
    #t_ode, n_ode, _ = direct_pk_ODE_solver(rho_2, n0, dt, tmax, constants, S)
    t_ode, n_ode, _ = direct_pk_ODE_solver(rho, n0, dt, tmax, constants, S)

    # Graficación
    fig, ax = plt.subplots(3, 1, figsize=(8,7), sharex=True)

    ax[0].plot(t, n_analitica, 'o', label='Analitica')
    ax[0].plot(t_ode, n_ode, '.-', label='direct_pk_ODE_solver')
    ax[0].set_ylabel('n(t)')
    ax[0].legend()

    ax[1].plot(t, rho_t, 'o')
    ax[1].set_ylabel(r'$\$$(t)')

    ax[2].plot(t, Q_t, 'o')
    ax[2].set_ylabel(r'Q(t)')
    ax[2].set_xlabel('Tiempo [s]')

    fig.tight_layout()
    plt.show()
