#!/usr/bin/env python3

cimport cython
import numpy as np
from libc.math cimport exp

@cython.boundscheck(False)
@cython.wraparound(False)
def reactimetro(double[:] n, time_input, double[:] lam, double[:] b, double Lstar, Q_in=0.0):
    """
    Solves numerically the inverse kinetics equation to get the reactivity as a function of time

    Parameters:
    -----------
        n : np.array (float)
            Neutron density
        time_input : float or np.array (float)
            If float: Time interval separation (dt) between each point in n
            If array: Time vector with same length as n
        lam : np.array (float)
            Decay constants of delayed precursors
        b : np.array (float)
            Delayed neutron fraction (beta_i / beta) (nuclear or effective)
        Lstar : float
            Reduced reproduction time (Lambda / beta_effective)
        Q_in : float or np.array (float)
            Strength of the neutron source. If it is not a constant, it should satisfy len(Q_in)=len(n)

    Returns:
    --------
        rho : np.array (float)
            Reactivity as a function of time
        t : np.array(float)
            Time vector
        D : np.array (float)
            Auxiliary variable only used in the inverse kinetic method to obtain neutron source strength
    """

    cdef int Nr, Ng, k, j
    cdef double[:] rho, Q, D, t_view, e_precomputed
    cdef double[:,:] c
    cdef double dt_k, e_j
    cdef bint is_uniform_dt = False
    cdef double uniform_dt = 0.0

    # Number of points and groups
    Nr = n.shape[0]
    Ng = lam.shape[0]

    # Handle time input
    if np.isscalar(time_input):
        is_uniform_dt = True
        uniform_dt = float(time_input)
        t_array = np.arange(0, Nr, dtype=np.float64) * uniform_dt
        t_view = t_array

        # Pre-compute exponentials for uniform dt case
        e_precomputed_array = np.zeros(Ng, dtype=np.float64)
        e_precomputed = e_precomputed_array
        for j in range(Ng):
            e_precomputed[j] = exp(-lam[j] * uniform_dt)
    else:
        t_array = np.asarray(time_input, dtype=np.float64)
        if t_array.shape[0] != Nr:
            raise ValueError('Time vector must have the same length as neutron density array')
        t_view = t_array
        is_uniform_dt = False
        # Dummy array for non-uniform case
        e_precomputed_array = np.zeros(1, dtype=np.float64)
        e_precomputed = e_precomputed_array

    # Initialize arrays
    c_array = np.zeros((Ng, Nr), dtype=np.float64)
    c = c_array
    rho_array = np.zeros(Nr, dtype=np.float64)
    rho = rho_array
    D_array = np.zeros(Nr, dtype=np.float64)
    D = D_array

    # Handle Q_in
    if np.isscalar(Q_in):
        Q_array = np.full(Nr, float(Q_in), dtype=np.float64)
        Q = Q_array
    else:
        Q_array = np.asarray(Q_in, dtype=np.float64)
        if Q_array.shape[0] != Nr:
            raise ValueError('El vector Q no tiene el mismo tamaño que n')
        Q = Q_array

    # Initial conditions
    for k in range(Ng):
        c[k, 0] = n[0] * b[k] / lam[k] / Lstar

    if n[0] != 0.0:
        rho[0] = -Lstar * Q[0] / n[0]
    else:
        rho[0] = 0.0

    # Main loop with optimization for uniform dt
    for k in range(1, Nr):
        if is_uniform_dt:
            dt_k = uniform_dt
        else:
            dt_k = t_view[k] - t_view[k-1]

        D[k] = (n[k] - n[k-1]) / dt_k

        for j in range(Ng):
            if is_uniform_dt:
                e_j = e_precomputed[j]
            else:
                e_j = exp(-lam[j] * dt_k)

            c[j, k] = (c[j, k-1] * e_j +
                      b[j] / lam[j] / Lstar *
                      (n[k-1] * (1.0 - e_j) -
                       (1.0 - e_j) * (n[k] - n[k-1]) / lam[j] / dt_k +
                       n[k] - n[k-1]))
            # As in LabVIEW
            # D[k] -= lam[j] * c[j, k-1]
            D[k] -= lam[j] * c[j, k]
        # As in LabVIEW
        # rho[k] = 1 + Lstar * (D[k] - Q[k]) / n[k-1]
        # As it should be
        rho[k] = 1.0 + Lstar * (D[k] - Q[k]) / n[k]

    return np.asarray(rho_array), np.asarray(t_array), np.asarray(D_array)

