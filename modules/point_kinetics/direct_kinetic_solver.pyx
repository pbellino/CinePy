#!/usr/bin/env python3

cimport cython
import numpy as np

@cython.boundscheck(False)
@cython.wraparound(False)
def cinetica_directa(double[:] rho, double n_0, double dt, double[:] lam, double[:] b, double Lstar, Q_in=0.0):
    """
    Solves numercally the inverse kinetics equation to get the reactivity as a function of time

    Parameters:
    -----------
        rho : np.array (float)
            Reactivity as a function of time (in dolars)
        n_0 : float
            Initial neutron density (at t=0)
        dt : float
            Time interval separation between each point in rho
        lam : np.array (float)
            Decay consants of delayed precursors
        b : np.array (float)
            Delayed neutron fracction (beta_i / beta) (nuclear or effective)
        Lstar : float
            Reduced reproduction time (Lambda / beta_effective)
        Q_in : float or np.array (float)
            Strenght of the neutron source. If it is not a constast, it should satisfy len(Q_in)=len(rho)

    Returns:
    --------
        n : np.array (float)
            Neutron density
        t : np.array(float)
            Time
    """

    cdef int Nr, Ng, k, j
    cdef double _suma_1, _suma_2, _suma_3, _temp
    cdef double[:] n, Q, e, t
    cdef double[:,:] c

    # Number of points
    Nr = np.size(rho)
    # Number of delayed neutron groups
    Ng = np.size(lam)
    # Precursors concentrations
    c = np.zeros((Ng, Nr))
    # Neutron density
    n = np.zeros(Nr)
    n[0] = n_0
    # Initially, precursors at equilibrium
    for k in range(Ng):
        c[k, 0] = n[0] * b[k] / lam[k] / Lstar
    if np.size(Q_in) == 1:
        Q = Q_in * np.ones_like(n)
    elif np.size(Q_in) != Nr:
        raise ValueError('El vector Q no tiene el mismo tamaño que n')

    # Initial reactivity
    if Q[0] == 0.0:
        # Reactor is critical
        rho[0] = 0.0
    else:
        # Reactor is subcritical
        rho[0] = - Lstar * Q[0] / n[0]

    e = np.zeros(Ng)
    for j in range(Ng):
        e[j] = np.exp(-lam[j] * dt)
    for k in range(1, Nr):
        _suma_1, _suma_2, _suma_3 = 0, 0, 0
        for j in range(Ng):
            _temp = b[j] * (1- e[j]) / lam[j]
            _suma_1 += _temp * (1 + lam[j] * dt)
            _suma_2 += lam[j] * c[j, k-1] * e[j]
            _suma_3 += _temp
        n[k] = ( n[k-1] * ( 1- Lstar / dt - _suma_1 / dt) - Lstar * _suma_2) / (rho[k] - Lstar / dt - _suma_3 / dt)
    t = np.arange(0, Nr) * dt

    return np.asarray(n), np.asarray(t)
