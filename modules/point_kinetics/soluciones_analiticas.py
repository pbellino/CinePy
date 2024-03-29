#!/usr/bin/env python3

import numpy as np


def in_hour_equation(omega, rho, constants):
    """
    Ecuación in-hour f(w) - rho

    Se escribe de esta manera para pasarla al algoritmo que busca los zeros.

    Si se quiere evaluar rho para un dado omega se puede hacer:
        >>> in_hour_equation(omega, 0, constantes)

    Parameters
    ----------
        omega : float
            Independant variable
        rho : float
            Reactivity (in dolars)
        constants : touple or list (b, lambda, L*)
            b (list), lambda (list), reduced Lambda (float)
            b_i = beta_i / beta_eff
            L* = L/beta_eff
    """
    b, lam, Lambda_red = constants
    _sum = np.sum( b / (lam + omega))
    return omega * Lambda_red + omega * _sum - rho


def solucion_in_hour_equation(rho, constants):
    """
    Resuelve la ecuación in-hour para un valor de rho

    TODO: revisar los problemas numéricos que aparecen al incluir fotoneutrones

    Parameters
    ----------
        rho : float
            Reactivity (in dolars)
        constants : touple or list (b, lambda, L*)
            b (list), lambda (list), reduced Lambda (float)
            b_i = beta_i / beta_eff
            L* = L/beta_eff

    Returns
    -------
        roots : numpy array
            Array with the zeros of the in-hour equaation
            roots[0] is the biggest root

    """
    from scipy.optimize import brentq

    _, lam, _ = constants
    fac = 3e-15
    lam_ini = -lam[::-1] * (1 - fac)
    lam_fin = -lam[::-1] * (1 + fac)
    ome_ini = np.insert(lam_ini, 0, -1e+10)
    ome_fin = np.append(lam_fin, 1e+10)

    roots = []
    for ini, fin in zip(ome_ini, ome_fin):
        roots.append(brentq(in_hour_equation, ini, fin,
                     args=(rho, constants)))
    return np.array(roots)


def solucion_analitica_Ia(t, rho, t0, n0, constantes):
    """
    Función analítica para un salo en reactividad de rho en un reactor
    inicialmente crítico estacionario. Sin fuente de neutrones.

    Parámetros
    ----------
          t : np array of floats
            Tiempos donde se evalúa la solución
        rho : float
            Reactividad insertada
        t0 : float
            Tiempo donde se produce el saalto
        n0 : float
            Valor inicial de la densidad neutrónica
        constantes : touple or list (b, lambda, L*)
            b (list), lambda (list), reduced Lambda (float)
            b_i = beta_i / beta_eff
            L* = L/beta_eff

    Resultados
    ----------
        n : numpy array
            Solución de la densidad neutrónica n(t)

    """
    b, lam, Lambda_red = constantes
    # Coeficientes de las exponenciales
    roots = solucion_in_hour_equation(rho, constantes)
    B = []
    for root in roots:
        # Conviene expresarlo así en lugar de poner $/omega
        # para evitar problemas cuando $=0
        _numerador = Lambda_red + np.sum(b / (root + lam))
        B.append(_numerador / (Lambda_red + np.sum(b*lam/(root+lam)**2)))
    # Suma de exponenciales para t>=t0
    n_pos = 0.
    for root, amp in zip(roots, B):
        n_pos += amp * np.exp(root*(t[t >= t0] - t0))
    n_pos *= n0
    # Constante para t<t0
    n_pre = n0 * np.ones(np.shape(t[t < t0]))

    return np.concatenate((n_pre, n_pos))


def solucion_analitica_IIa(t, t0, n0, Qf, constantes):
    """
    Función analítica para un salto en la fuente en t0 desde Q=0 hasta Q=Qf
    en un reactor crítico, inicialmente estacionario, donde no se modifica
    la reactividad.

    Parámetros
    ----------
          t : np array of floats
            Tiempos donde se evalúa la solución
        t0 : float
            Tiempo donde se produce el saalto
        n0 : float
            Valor inicial de la densidad neutrónica
        Qf : Valor de la fuente de neutrones para t>=t0
        constantes : touple or list (b, lambda, L*)
            b (list), lambda (list), reduced Lambda (float)
            b_i = beta_i / beta_eff
            L* = L/beta_eff

    Resultados
    ----------
        n : numpy array
            Solución de la densidad neutrónica n(t)

    """
    b, lam, Lambda_red = constantes
    # Coeficientes de las exponenciales
    roots = solucion_in_hour_equation(0.0, constantes)
    B = []
    for root in roots[:-1]:
        B.append(1.0 / root**2 / ( -np.sum(b/(root+lam)**2)))
    # Suma de exponenciales para t>=t0
    n_pos = 0.
    for root, amp in zip(roots[:-1], B):
        n_pos += amp * np.exp(root*(t[t >= t0] - t0))
    n_pos += np.sum(b / lam**2) / (Lambda_red + np.sum(b / lam))**2
    n_pos += (t[t >= t0] -t0) / np.sum(b / lam)
    n_pos *= Lambda_red * Qf
    n_pos += n0
    # Constante para t<t0
    n_pre = n0 * np.ones(np.shape(t[t < t0]))

    return np.concatenate((n_pre, n_pos))


def solucion_analitica_IIb(t, t0, rho0, Q0, constantes):
    """
    Función analítica para un salto en la fuente en t0 desde Q=Q0 hasta Q=0
    en un reactor subcrítico, inicialmente estacionario, donde no se modifica
    la reactividad.

    Fundamento del método "source jerk"

    Parámetros
    ----------
          t : np array of floats
            Tiempos donde se evalúa la solución
        t0 : float
            Tiempo donde se produce el saalto
      rho0 : float (negativa)
            Reactividad del reactor
        Qo : Valor inicial de la fuente de neutrones
        constantes : touple or list (b, lambda, L*)
            b (list), lambda (list), reduced Lambda (float)
            b_i = beta_i / beta_eff
            L* = L/beta_eff

    Resultados
    ----------
        n : numpy array
            Solución de la densidad neutrónica n(t)

    """

    b, lam, Lambda_red = constantes
    # Coeficientes de las exponenciales
    roots = solucion_in_hour_equation(rho0, constantes)
    B = []
    for root in roots:
        B.append(1.0 / root / (Lambda_red + np.sum(b * lam/(root + lam)**2)))
    # Suma de exponenciales para t>=t0
    n_pos = 0.
    for root, amp in zip(roots, B):
        n_pos += amp * np.exp(root*(t[t >= t0] - t0))
    n_pos *= - Lambda_red * Q0
    # Constante para t<t0
    n0 = - Lambda_red * Q0 / rho0
    n_pre = n0 * np.ones(np.shape(t[t < t0]))

    return np.concatenate((n_pre, n_pos))


def solucion_analitica_IIc(t, t0, rho0, Qf, constantes):
    """
    Función analítica para un salto en la fuente en t0 desde Q=0 hasta Q=Qf
    en un reactor no crítico, inicialmente sin neutrones, donde no se modifica
    la reactividad.

    Simula la introducción de una fuente en un reactor sin neutrones.

    Si el reactor está crítico, se obtiene el caso IIb.

    Parámetros
    ----------
          t : np array of floats
            Tiempos donde se evalúa la solución
        t0 : float
            Tiempo donde se produce el saalto
      rho0 : float (negativa)
            Reactividad del reactor
        Qf : Valor de la fuente de neutrones
        constantes : touple or list (b, lambda, L*)
            b (list), lambda (list), reduced Lambda (float)
            b_i = beta_i / beta_eff
            L* = L/beta_eff

    Resultados
    ----------
        n : numpy array
            Solución de la densidad neutrónica n(t)

    """

    b, lam, Lambda_red = constantes
    # Coeficientes de las exponenciales
    roots = solucion_in_hour_equation(rho0, constantes)
    B = []
    for root in roots:
        B.append(1.0 / root / (Lambda_red + np.sum(b * lam/(root + lam)**2)))
    # Suma de exponenciales para t>=t0
    n_pos = 0.
    for root, amp in zip(roots, B):
        n_pos += amp * np.exp(root*(t[t >= t0] - t0))
    n_pos += - 1 / rho0
    n_pos *= Lambda_red * Qf
    # Constante para t<t0
    n0 = 0.0
    n_pre = n0 * np.ones(np.shape(t[t < t0]))

    return np.concatenate((n_pre, n_pos))


def solucion_analitica_Ib(t, t0, rho0, rhof, Q0, constantes):
    """
    Función analítica para un salto en la reactividad en t0 desde rho0 hasta
    rhof en un reactor con fuente Q0, inicialmente sin neutrones, donde no se
    modifica la fuente de neutrones.

    rho0 debe ser negativa para que esté inicialmente estacionario

    rhof no puede ser cero


    Parámetros
    ----------
          t : np array of floats
            Tiempos donde se evalúa la solución
        t0 : float
            Tiempo donde se produce el saalto
      rho0 : float (negativa)
            Reactividad del reactor
      rhof : float (!=0)
            Reactividad final
        Qf : Valor de la fuente de neutrones
        constantes : touple or list (b, lambda, L*)
            b (list), lambda (list), reduced Lambda (float)
            b_i = beta_i / beta_eff
            L* = L/beta_eff

    Resultados
    ----------
        n : numpy array
            Solución de la densidad neutrónica n(t)

    """
    b, lam, Lambda_red = constantes
    # Coeficientes de las exponenciales
    roots = solucion_in_hour_equation(rhof, constantes)
    B = []
    for root in roots:
        B.append(1.0 / root / (Lambda_red + np.sum(b * lam/(root + lam)**2)))
    # Suma de exponenciales para t>=t0
    n_pos = 0.
    for root, amp in zip(roots, B):
        n_pos += amp * np.exp(root*(t[t >= t0] - t0))
    n_pos *= (1 - rhof / rho0)
    n_pos += - 1 / rhof
    n_pos *= Lambda_red * Q0
    # Constante para t<t0
    n0 = - Lambda_red * Q0 / rho0
    n_pre = n0 * np.ones(np.shape(t[t < t0]))

    return np.concatenate((n_pre, n_pos))


def solucion_analitica_Ic(t, t0, rho0, Q0, constantes):
    """
    Función analítica para un salto en la reactividad en t0 desde rho0 hasta
    rhof=0 en un reactor con fuente Q0, inicialmente sin neutrones, donde no se
    modifica la fuente de neutrones.

    rho0 debe ser negativa para que esté estacionario inicialmente

    rhof no puede ser cero


    Parámetros
    ----------
          t : np array of floats
            Tiempos donde se evalúa la solución
        t0 : float
            Tiempo donde se produce el saalto
      rho0 : float (negativa)
            Reactividad del reactor
        Qf : Valor de la fuente de neutrones
        constantes : touple or list (b, lambda, L*)
            b (list), lambda (list), reduced Lambda (float)
            b_i = beta_i / beta_eff
            L* = L/beta_eff

    Resultados
    ----------
        n : numpy array
            Solución de la densidad neutrónica n(t)

    """

    b, lam, Lambda_red = constantes
    # Coeficientes de las exponenciales
    roots = solucion_in_hour_equation(0.0, constantes)
    B = []
    for root in roots[:-1]:
        B.append(1.0 / root**2 / ( -np.sum(b/(root+lam)**2)))
    # Suma de exponenciales para t>=t0
    n_pos = 0.
    for root, amp in zip(roots[:-1], B):
        n_pos += amp * np.exp(root*(t[t >= t0] - t0))
    n_pos += np.sum(b / lam**2) / (Lambda_red + np.sum(b / lam))**2
    n_pos += (t[t >= t0] -t0) / np.sum(b / lam)
    n_pos += - 1/ rho0
    n_pos *= Lambda_red * Q0
    # Constante para t<t0
    n0 = - Lambda_red * Q0 / rho0
    n_pre = n0 * np.ones(np.shape(t[t < t0]))

    return np.concatenate((n_pre, n_pos))


def rho_analitica_01(t, t0, omega, constantes):
    """
    Solución analítica de rho(t) para

            n(t) = n0 exp(omega * (t-t0))

    Para un reactor inicialmente crítico y estacionario. Sin fuente de
    neutrones.

    Ver informe Estabilidades para su deducción

    Parameters
    ----------
        t : numpy array
            Time where the reactivity is evaluated
        t0 : float
            Time offset
        omega : float
            Parameter of the test function
        constantes : touple or list (b, lambda, L*)
            b (list), lambda (list), reduced Lambda (float)
            b_i = beta_i / beta_eff
            L* = L/beta_eff

    Returns
    -------
        rho : numpy array
            Reactivity as a function of time

    """
    bs, lams, Lambda_red = constantes
    _sum = 0
    for b, lam in zip(bs, lams):
        _sum += b / (lam + omega) * (1- np.exp((-omega-lam) * t))
    _rho_origin = np.asarray(omega * (Lambda_red + _sum))
    # Corro el resultado hasta t0
    rho = np.zeros_like(t)
    _indx = t >= t0
    rho[_indx] = _rho_origin[0:sum(_indx)]
    return rho


if __name__ == "__main__":

    pass
