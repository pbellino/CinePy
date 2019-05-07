#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np
from scipy.stats import norm
import matplotlib.pyplot as plt
import os
from lmfit import Minimizer, Parameters, report_fit

import seaborn as sns
sns.set()
plt.style.use('paper')

import sys
sys.path.append('../')

from modules.io_modules import lee_historias_completas, lee_fey
from modules.funciones import alfa_feynman_lin_dead_time


def grafica_historias_afey(nombre):
    """
    Grafica todas las historias guardadas en el archivo 'nombre'

    Parametros
    ----------
    nombres : lista de strings
        Camino y nombre del archivo .dat que contiene a todas las historias

    Resultados
    ----------
    fig :
        Referencia por si se quiere guardar el gráfico

    """

    vec_t, historias, _ = lee_historias_completas(nombre)

    fig = plt.figure(1)
    ax = fig.add_subplot(1, 1, 1)

    # Se itera sobre cada historia
    for historia in historias.T:
        ax.plot(vec_t, historia)

    ax.set_xlabel(r'$\Delta$ t [s]')
    ax.set_ylabel(r'Y($\Delta$ t)')
    ax.set_title('{} historias leidas del archivo: {}'.format(
       historias.shape[1], nombre))
    ax.grid(True)
    # plt.show()

    return fig


def grafica_afey(nombres):
    """
    Grafica todas la curva promedio y su desvio de los archivos 'nombres'

    Parametros
    ----------
    nombres : lista de strings
        Camino y nombre del archivo .fey con el valor medio y desvío de Y(Dt)

    Resultados
    ----------
    fig :
        Referencia por si se quiere guardar el gráfico

    """

    fig = plt.figure(1)
    ax = fig.add_subplot(1, 1, 1)
    for nombre in nombres:
        vec_t, Y, std_Y, _, _ = lee_fey(nombre)

        ax.errorbar(vec_t, Y, yerr=std_Y, fmt='.',
                    label=nombre.rsplit('/')[-1])

    ax.set_xlabel(r'$\Delta$ t [s]')
    ax.set_ylabel(r'Y($\Delta$ t)')
    ax.legend(loc='best')
    ax.grid(True)
    # plt.show()

    return fig


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

    ax1.plot(tau, result.residual, 'k.')
    ax1.set_xlabel(r'$\tau$ [ms]')
    ax1.set_ylabel(r'Residuals')
    fig.subplots_adjust(hspace=0.1)

    # Graficación del histograma de los residuos
    fig2, ax3 = plt.subplots(1, 1)
    ax3.hist(result.residual, bins=15, density=True, label='Residuals')
    res_mean = np.mean(result.residual)
    res_std = np.std(result.residual)
    x = np.linspace(norm.ppf(0.001), norm.ppf(0.999), 500)
    ax3.plot(x, norm.pdf(x, loc=res_mean, scale=res_std),
             'r-', lw=5, alpha=0.6, label='Normal pdf')
    # Invierto el orden de las leyendas
    handles, labels = ax3.get_legend_handles_labels()
    ax3.legend(handles[::-1], labels[::-1], loc='best')

    return None


def teo_variance_berglof(Y, Nk):
    """ Varianza teórica """
    return 2*(Y+1)**2 / (Nk-1)


def lee_Nk(nombre):
    Nk = np.loadtxt(nombre, dtype=np.uint32)
    return Nk

if __name__ == '__main__':

    # Carpeta donde se encuentra este script
    # Lo uso por si quiero llamarlo desde otro dierectorio
    script_dir = os.path.dirname(__file__)
    # -------------------------------------------------------------------------
    # Parámetros de entrada
    # -------------------------------------------------------------------------
    # Archivos a leer
    # nombre = 'resultados/nucleo_01.D1D2_cov.dat'
    # grafica_historias_afey(nombre)
    # plt.show()
    # nombre = 'resultados/nucleo_01.D1.fey'
    # nombres = ['resultados/nucleo_01.D1.fey',
    #            'resultados/nucleo_01.D2.fey',
    #            ]
    # -------------------------------------------------------------------------
    #
    # myfig = grafica_afey(nombres)
    #
    # ax = myfig.get_axes()[0]
    # ax.set_title(u'Un título')
    # plt.show()
    #
    # ------------------------------------------------------------------------

    nombre = 'resultados/nucleo_01.D2.fey'
    # Camino absoluto del archivo que se quiere leer
    abs_nombre = os.path.join(script_dir, nombre)
    tau, Y, std_Y, num_hist, _ = lee_fey(abs_nombre)

    Nk = lee_Nk(nombre.rstrip('fey') + 'Nk')
    var_teo = teo_variance_berglof(Y, Nk)

    # ajuste_afey(tau, Y, np.sqrt(var_teo/num_hist))
    ajuste_afey(tau, Y, std_Y)
    fig8, ax8 = plt.subplots(1, 1)
    ax8.plot(tau, num_hist*std_Y**2, '.', label='Estimated variance')
    ax8.set_xlabel(r'$\tau$ [ms]')
    ax8.set_ylabel(r'Var[Y($\tau$)]')

    ax8.plot(tau, var_teo, 'r', lw=2, label='Teoretical variance')
    ax8.grid(True)
    ax8.legend(loc='best')

    plt.show()
