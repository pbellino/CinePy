#!/usr/bin/env python3

import numpy as np
from scipy.integrate import ode


def direct_pk_ODE_solver(rho, n0, dt, tmax, constants, Q):
    """
    Solver for the direct point kinetic equation using the scipy.ingegrate.ode
    solver.

    Parameters
    ----------
        rho : callable (returns float)
            Reactivity as a function of time (in dolars)
        n0 : float
            Initial value of the neutron density
        dt : float
            Time step
        tmax : float
            Maximun integration time
        constants : touple or list (b, lambda, L*)
            b (list), lambda (list), reduced Lambda (float)
            b_i = beta_i / beta_eff
            L* = L/beta_eff
        Q : callable (returns float)
            Strength of the neutron sources as a function of time.

    Returns
    -------
        t_ode : numpy array
            Times
        n_ode : numpy array
            Neutron density
        c_ode : numpy ndarray
            Delayed neutron precursors

    >>> def rho(t):
    >>>    if t>= 2:
    >>>       return rho_f
    >>>    elif t<= 2:
    >>>       return rho_i
    >>>
    >>> def S(t):
    >>>    if t>= 2:
    >>>       return Q_f
    >>>    elif t<= 2:
    >>>       return Q_i

    """

    b, lam, Lambda_red = constants


    if Q(0) == 0.0:
        if rho(0) != 0:
            n0 = 0
        else:
            n0 = 5
    else:
        if rho(0) >= 0:
            _msg = "Error: el reactor no se encuentra inicialmente \n"
            _msg += "estacionario (S!=0 y rho>=0)"
            raise Exception(_msg)
        else:
            n0 = -Lambda_red * Q(0) / rho(0)

    # Vector fuente (S)
    def source(t):
        _tmp = np.zeros(len(b) + 1)
        _tmp[0] = Q(t)
        return _tmp

    def func_ode(t, X, P, U):
        # Y = A*X + S
        P[0, 0] = (rho(t) - 1) / Lambda_red
        return np.asarray(np.matmul(P, X) + U(t))

    A = np.zeros((7, 7))
    A[1:, 1:] = np.diag(-lam)
    A[0, 1: ] = lam
    A[1:, 0] = b / Lambda_red

    X0 = b / lam / Lambda_red * n0
    X0 = np.insert(X0, 0, n0)

    # ------ Se resuelve utilizando scipy.integrate.ode
    r = ode(func_ode)
    r.set_integrator('dopri5', max_step=dt)
    r.set_initial_value(X0, 0.0)
    r.set_f_params(A, source)

    t_ode = []
    y_ode = []
    while r.successful() and r.t < tmax:
        t_ode.append(r.t)
        y_ode.append(r.y)
        r.integrate(r.t+dt)

    # print(f"Return code : {r.get_return_code()}")

    t_ode = np.asarray(t_ode)
    n_ode = np.asarray(y_ode)[:, 0]
    c_ode = np.asarray(y_ode)[:, 1:]

    return t_ode, n_ode, c_ode


if __name__ == "__main__":
    pass
