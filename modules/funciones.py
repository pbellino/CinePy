#!/usr/bin/env python3

"""
Funciones utilizadas para relizar ajustes de datos experimentales
"""

import numpy as np


# ----------------------------------------------------------------------------
# Funciones de ajuste para alfa-Feynman
# ----------------------------------------------------------------------------


def func_aux(x):
    """ Función auxiliar para construir las funciones de alfa-Feynman """
    return 1 - (1 - np.exp(-x)) / x


def alfa_feynman(tau, alfa, amplitud):
    """
    Función del método de alfa-Feynman teórica

    No tiene ninguna corrección

    Y(tau) = amplitud * [1 - (1 - exp(-alfa*tau) ) / (alfa*tau)]

    donde:
        amplitud = epsilon*Diven/(alfa^2 Lambda^2)

    """
    return amplitud * func_aux(alfa*tau)


def alfa_feynman_lin_dead_time_Nk(tau, alfa, amplitud, offset, Nk):
    """
    Función del método de alfa-Feynman teórica teniendo en cuenta el número
    finito de intervalos utilizados y tiempo muerto (lineal)


    Y(tau) = amplitud * [1 - (1 - exp(-alfa*tau) ) / (alfa*tau)]x
           - amplitud * [1 - (1 - exp(-alfa*tau*Nk) ) / (alfa*tau*Nk)] / Nk

    donde:
        amplitud = epsilon*Diven/(alfa^2 Lambda^2)
            siendo epsilong la eficiencia y Lambda el tiempo entre
            reproducciones
        offset = 2 R d
            siendo R la tasa de cuentas y d el tiempo muerto
    """
    return amplitud*(func_aux(alfa*tau) - func_aux(alfa*tau*Nk) / Nk) \
            - offset * (Nk-1) / Nk - 1 / Nk


def alfa_feynman_lin_dead_time(tau, alfa, amplitud, offset):
    """
    Función del método de alfa-Feynman con tiempo muerto (lineal)

    Corrección lineal debido al tiempo muerto de la función de alfa-Feynman

    Y(tau) = amplitud * [1 - (1 - exp(-alfa*tau) ) / (alfa*tau)] - offset

    donde:
        amplitud = epsilon*Diven/(alfa^2 Lambda^2)
            siendo epsilong la eficiencia y Lambda el tiempo entre
            reproducciones
        offset = 2 R d
            siendo R la tasa de cuentas y d el tiempo muerto
    """
    return alfa_feynman(tau, alfa, amplitud) - offset


def alfa_feynman_dos_exp(tau, alfa, amplitud, offset, alfa_2, amplitud_2):
    """
    Función de alfa-Feynman teniendo en cuenta dos exponenciales

    Para considerar efectos espaciales se agrega una exponencial más al
    método estandar. Se mantiene la corrección lineal del tiempo muerto.

    """
    Y = amplitud * func_aux(alfa*tau) - offset \
        + amplitud_2 * func_aux(alfa_2*tau)
    return Y


def alfa_feynman_dos_exp_delayed(tau, alfa, amplitud, offset, slope, alfa_2,
                                 amplitud_2):
    """
    Función de alfa-Feynman teniendo en cuenta dos exponenciales

    Para considerar efectos espaciales se agrega una exponencial más al
    método estandar. Se mantiene la corrección lineal del tiempo muerto.

    """
    Y = amplitud * func_aux(alfa*tau) - offset \
        + amplitud_2 * func_aux(alfa_2*tau) + slope * tau
    return Y


def alfa_feynman_tres_exp(tau, alfa, amplitud, offset, alfa_2, amplitud_2,
                          alfa_3, amplitud_3):
    """
    Función de alfa-Feynman teniendo en cuenta tres exponenciales

    Para considerar efectos espaciales se agrega una exponencial más al
    método estandar. Se mantiene la corrección lineal del tiempo muerto.

    """
    Y = amplitud * func_aux(alfa*tau) - offset \
        + amplitud_2 * func_aux(alfa_2*tau) \
        + amplitud_3 * func_aux(alfa_3*tau)
    return Y


def alfa_feynman_nldtime(tau, alfa, amplitud, t_dead, amplitud_dead):
    Y = - amplitud_dead*(2 - t_dead/tau) \
        + amplitud * ((1-t_dead/tau) * np.exp(-alfa*t_dead)
                      * func_aux(alfa*(tau-t_dead)))
    return Y


def alfa_feynman_lin_dead_time_lin_delayed(tau, alfa, amplitud, offset, slope):
    """
    Función del método de alfa-Feynman con tiempo muerto y retardados

    Corrección lineal debido al tiempo muerto de la función de alfa-Feynman
    junto con la corrección a primer orden debido a los neutrones retardados

    Y(tau) = amplitud * [1 - (1 - exp(-alfa*tau) ) / (alfa*tau)] - offset
             + slope*tau

    donde:
        amplitud = epsilon*Diven/(alfa^2 Lambda^2)
            siendo epsilong la eficiencia y Lambda el tiempo entre
            reproducciones
        offset = 2 R d
            siendo R la tasa de cuentas y d el tiempo muerto
        slope = 1/2 * alfa_delayed * C_8
            (ver paper 'Reactor Noise Experiment...' Kitamura, Journal
            of Nuc. Sci. and Tech.  vol 36,  No 8,  653-660, 1999)
    """
    return alfa_feynman(tau, alfa, amplitud) - offset + slope * tau


# ----------------------------------------------------------------------------
# Funciones de ajuste para alfa-Rossi
# ----------------------------------------------------------------------------

def arossi_1exp(tau, alfa, amplitud, uno):
    """
    Función del método de alfa-Rossi teórica

    No tiene ninguna corrección.

    P(tau) = amplitud * exp(-alfa*tau) + uno

    donde:
        amplitud = epsilon*Diven/(alfa^2 Lambda^2)
        alfa = - ($-beta) / Lambda* [1/s]
        uno  = 1

    `uno` se lo deja como parámetro de ajusta para corroborar que haya
    consistencia. Debe ser igual a la unidad porque se ajusta la probabilidad
    normalizada con la tasa de cuentas. Si no se normalizara la función, esto
    sería equivalente a ajustar la tasa de cuentas (cuando en verdad se la
    puede estimar de forma directa por otros métodos).

    """
    return amplitud * np.exp(-alfa*tau) + uno


def arossi_2exp(tau, alfa_1, amplitud_1, alfa_2, amplitud_2, uno):
    """
    Función del método de alfa-Rossi teórica

    No tiene ninguna corrección.

    P(tau) = amplitud_1 * exp(-alfa_1*tau)
           + amplitud_2 * exp(-alfa_2*tau) + uno


    `uno` se lo deja como parámetro de ajusta para corroborar que haya
    consistencia. Debe ser igual a la unidad porque se ajusta la probabilidad
    normalizada con la tasa de cuentas. Si no se normalizara la función, esto
    sería equivalente a ajustar la tasa de cuentas (cuando en verdad se la
    puede estimar de forma directa por otros métodos).

    """
    P = amplitud_1 * np.exp(-alfa_1*tau) + amplitud_2 * np.exp(-alfa_2*tau) \
        + uno
    return P


if __name__ == '__main__':

    import matplotlib.pyplot as plt

    t = np.linspace(50e-6, 50e-3, 200)
    Y_1 = alfa_feynman(t, 200, 5)
    Y_2 = alfa_feynman_lin_dead_time(t, 200, 5, 0.5)
    Y_3 = alfa_feynman_lin_dead_time_lin_delayed(t, 200, 5, 0.5, 5)
    Y_4 = alfa_feynman_nldtime(t, 200, 5, 10e-6, 0.5)
    plt.plot(t, Y_1, '.', label='alfa_feynman')
    plt.plot(t, Y_2, '.', label='alfa_feynman_lin_dead_time')
    plt.plot(t, Y_3, '.', label='alfa_feynman_lin_dead_time_lin_delayed')
    plt.plot(t, Y_4, '.', label='alfa_feynman_nldtime')
    plt.legend()
    plt.show()
