#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np
import matplotlib.pyplot as plt
from lmfit import Minimizer, Parameters, report_fit

import seaborn as sns
sns.set()
plt.style.use('paper')

import sys
sys.path.append('../')

from modules.funciones import alfa_feynman_lin_dead_time


def ajuste_afey(tau, Y, std_Y):
    """
    Ajuste no lineal de la curva de alfa-Feynman

    Se ajustan los datos de  Y vs tau con incerteza de stt_Y
    Se utiliza el paquete lmfit para realizar el ajuste

    """

    def residual(params, tau, data=None, sigma=None):
        parvals = params.valuesdict()
        alfa = parvals['alfa']
        amplitud = parvals['amplitud']
        offset = parvals['offset']

        model = alfa_feynman_lin_dead_time(tau, alfa, amplitud, offset)

        if data is None:
            return model
        if sigma is None:
            return model - data
        return (model - data) / sigma

    # Se definen los parámetros del ajuste
    params = Parameters()
    params.add('alfa', value=300, min=0)
    params.add('amplitud', value=1, min=0)
    params.add('offset', value=1)
    # Se define la minimización
    minner = Minimizer(residual, params,
                       fcn_args=(tau,),
                       fcn_kws={'data': Y, 'sigma': std_Y}
                       )
    # Se realiza la minimización
    # Se puede usar directamente la función minimize como wrapper de Minimizer
    result = minner.minimize(method='leastsq')
    report_fit(result)

    best_fit = Y + result.residual * std_Y

    fig, (ax0, ax1) = plt.subplots(2, sharex=True,
                                   gridspec_kw={'height_ratios': [3, 1]},
                                   )

    ax0.errorbar(tau, Y, yerr=std_Y, fmt='k.', elinewidth=4,
                 label='measurement')
    ax0.plot(tau, best_fit, 'r', zorder=3, label='fit')
    ax0.set_ylabel(r'$Y(\tau)$')

    # Invierto el orden de las leyendas
    handles, labels = ax0.get_legend_handles_labels()
    ax0.legend(handles[::-1], labels[::-1], loc='best')

    ax1.plot(tau, result.residual, 'k')
    ax1.set_xlabel(r'$\tau$ [ms]')
    ax1.set_ylabel(r'Residuals')
    fig.subplots_adjust(hspace=0.1)

    return None


def simula_afey(alfa, amplitud, offset):
    """
    Función para simular la curva de alfa-Feynman

    TODO: hacer que las incertezas sean distintas para cada punto
          buscar el modelo teórico que describe std_Y vs tau

    """

    dt_min = 50e-6
    dt_max = 50e-3
    N_tau = 200
    desv_std = 0.2
    # Intervalos temporales
    tau = np.linspace(dt_min, dt_max, N_tau)
    # Función de alfa-Feynman simulada
    Y = alfa_feynman_lin_dead_time(tau, alfa, amplitud, offset)
    # Se le agrega error gaussiano de media nula
    Y = Y + np.random.normal(loc=0.0, scale=desv_std, size=np.shape(tau))
    # Incertezas de cada punto
    std_Y = desv_std * np.ones(np.shape(tau))
    return tau, Y, std_Y


if __name__ == '__main__':

    # TODO: se usa 'ajuste_afey' de este script, pero se podría llamar
    #       directamente al módulo ../src/analisis_alfa_feynman

    tau, Y, std_Y = simula_afey(350, 5, 0.5)
    ajuste_afey(tau, Y, std_Y)

    plt.show()
