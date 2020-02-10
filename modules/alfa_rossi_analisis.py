#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Grafica las curvas P(tau) para cada historia y la del promeio.

Ajuste no lineal de la curva P(tau) promedio

TODO: Falta organizar cómo se almacenan los resultados del ajuste. Falta hacer
que se ajusten una lista de curvas. Falta propagar errores para obtener el
resto de los parámetros cinéticos (usar paquete uncertainties).
"""

import numpy as np
import matplotlib.pyplot as plt
import os
from lmfit import Minimizer, Parameters, report_fit
from scipy.stats import norm
import seaborn as sns

import sys
sys.path.append('../')

from modules.alfa_rossi_lectura import arossi_lee_historias_completas, \
                                       arossi_lee_historias_promedio
from modules.funciones import arossi_1exp, arossi_2exp

sns.set()
plt.style.use('paper')


def arossi_grafica_historias(nombres):
    """
    Grafica todas las historias de los archivos indicados.

    Son los archivos grabados con escribe_datos_completos().

    Parámetros
    ----------
        nombres : (list of) strings
            Camino completo del archivo *_ros.dat que contiene los datos de
            todas las historias. PUede ser sólo un string o una lista.

    Resultados
    ----------
        figs : (list of) fig handler
            Referencia a cada figura. Si `nombres` era una lista, entonces figs
            también lo será. Permite modificar parámetros fuera de la función.
    """

    if isinstance(nombres, list):
        _es_lista = True
    else:
        _es_lista = False
        nombres = [nombres]

    figs = []
    for nombre in nombres:
        # Lectrua del archivo
        print('Se lee el archivo : {}'.format(nombre))
        historias, tau, parametros = arossi_lee_historias_completas(nombre)

        for key in parametros.keys():
            print('{} : {}'.format(key,  parametros.get(key)))

        # Graficación
        fig, ax = plt.subplots(1, 1)
        ax.plot(tau, historias, marker='.', label='Historias')
        ax.set_xlabel('Tiempo [s]')
        ax.set_ylabel(r'P($\tau$)')
        ax.ticklabel_format(style='sci', axis='x', scilimits=(0, 0))
        handles, labels = ax.get_legend_handles_labels()
        ax.legend([handles[0]], [labels[0]], loc='best')
        ax.set_title(os.path.split(nombre)[-1])
        fig.tight_layout()
        figs.append(fig)
        print('-'*80)

    if not _es_lista:
        figs = figs[0]
    return figs


def arossi_grafica_promedio(nombres):
    """
    Grafica la curva P(tau) de los archivos indicados.

    Son los archivos grabados con escribe_datos_promedio().

    Parámetros
    ----------
        nombres : (list of) strings
            Camino completo del archivo *.dat que contiene los datos de los
            promedios de las historias. PUede ser sólo un string o una lista.

    Resultados
    ----------
        fig : fig handler
            Referencia a la figura. Permite modificar parámetros de la figura
            fuera de la función.
    """

    if not isinstance(nombres, list):
        nombres = [nombres]

    fig, ax = plt.subplots(1, 1)
    for nombre in nombres:
        print('Se lee el archivo : {}'.format(nombre))
        # Lectrua del archivo
        P_mean, P_std, tau, parametros = arossi_lee_historias_promedio(nombre)

        for key in parametros.keys():
            print('{} : {}'.format(key,  parametros.get(key)))

        # Graficación
        label_str = os.path.split(nombre)[-1]
        ax.errorbar(tau, P_mean, yerr=P_std, label=label_str, fmt='-.', lw=0.5,
                    elinewidth=0.5, marker='.')
        ax.set_xlabel('Tiempo [s]')
        ax.set_ylabel(r'P($\tau$)')
        ax.ticklabel_format(style='sci', axis='x', scilimits=(0, 0))
        ax.legend(loc='best')
        fig.tight_layout()
        print('-'*80)

    return fig


def arossi_ajuste_1exp(tau, P, P_std):
    """
    Ajusta de P(tau) con una exponencial
    """
    def residual(params, tau, data=None, sigma=None):
        parvals = params.valuesdict()
        alfa = parvals['alfa']
        amplitud = parvals['amplitud']
        uno = parvals['uno']

        model = arossi_1exp(tau, alfa, amplitud, uno)

        if data is None:
            return model
        if sigma is None:
            return model-data
        return (model - data) / sigma

    # Se definen parámetros del ajuste
    params = Parameters()
    params.add('alfa', value=200.0, min=0.0)
    params.add('amplitud', value=1.0, min=0.0)
    params.add('uno', value=1.0, min=0.0)
    # Se define la minimización
    minimi = Minimizer(residual, params,
                       fcn_args=(tau,),
                       fcn_kws={'data': P, 'sigma': P_std}
                       )
    result = minimi.minimize(method='leastsq')
    report_fit(result)

    best_fit = P + result.residual * P_std

    fig, (ax0, ax1) = plt.subplots(2, sharex=True,
                                   gridspec_kw={'height_ratios': [3, 1]},
                                   )

    ax0.errorbar(tau, P, yerr=P_std, fmt='k.', elinewidth=1,
                 label='measurement')
    ax0.plot(tau, best_fit, 'r', zorder=3, label='fit')
    ax0.set_ylabel(r'P($\tau$)')
    ax0.ticklabel_format(style='sci', axis='x', scilimits=(0, 0))
    # Invierte orden de las leyendas
    handles, labels = ax0.get_legend_handles_labels()
    ax0.legend(handles[::-1], labels[::-1], loc='best')
    # Gráfico de los residuos del ajuste
    ax1.plot(tau, result.residual, 'k.')
    ax1.set_xlabel(r'$\tau$ [s]')
    ax1.set_ylabel(r'Residuals')
    fig.subplots_adjust(hspace=0.1)

    # Gráfico del histograma de los residuos
    fig2, ax1 = plt.subplots(1, 1)
    ax1.hist(result.residual, bins=20, density=True, label='Residuals')
    res_mean = np.mean(result.residual)
    res_std = np.std(result.residual)
    x = np.linspace(norm.ppf(0.0001), norm.ppf(0.999), 500)
    ax1.plot(x, norm.pdf(x, loc=res_mean, scale=res_std), 'r-', lw=5,
             alpha=0.6, label='Normal pdf')
    # Invierte orden de las leyendas
    handles, labels = ax1.get_legend_handles_labels()
    ax1.legend(handles[::-1], labels[::-1], loc='best')

    return None


def arossi_ajuste_2exp(tau, P, P_std):
    """
    Ajusta de P(tau) con dos exponenciales
    """
    def residual(params, tau, data=None, sigma=None):
        parvals = params.valuesdict()
        alfa_1 = parvals['alfa_1']
        amplitud_1 = parvals['amplitud_1']
        alfa_2 = parvals['alfa_2']
        amplitud_2 = parvals['amplitud_2']
        uno = parvals['uno']

        model = arossi_2exp(tau, alfa_1, amplitud_1, alfa_2, amplitud_2, uno)

        if data is None:
            return model
        if sigma is None:
            return model-data
        return (model - data) / sigma

    # Se definen parámetros del ajuste
    params = Parameters()
    params.add('alfa_1', value=200.0, min=0.0)
    params.add('amplitud_1', value=1.0, min=0.0)
    params.add('alfa_2', value=800.0, min=0.0)
    params.add('amplitud_2', value=1.0, min=0.0)
    params.add('uno', value=1.0, min=0.0)
    # Se define la minimización
    minimi = Minimizer(residual, params,
                       fcn_args=(tau,),
                       fcn_kws={'data': P, 'sigma': P_std}
                       )
    result = minimi.minimize(method='leastsq')
    report_fit(result)

    best_fit = P + result.residual * P_std

    fig, (ax0, ax1) = plt.subplots(2, sharex=True,
                                   gridspec_kw={'height_ratios': [3, 1]},
                                   )

    ax0.errorbar(tau, P, yerr=P_std, fmt='k.', elinewidth=1,
                 label='measurement')
    ax0.plot(tau, best_fit, 'r', zorder=3, label='fit')
    ax0.set_ylabel(r'P($\tau$)')
    ax0.ticklabel_format(style='sci', axis='x', scilimits=(0, 0))
    # Invierte orden de las leyendas
    handles, labels = ax0.get_legend_handles_labels()
    ax0.legend(handles[::-1], labels[::-1], loc='best')
    # Gráfico de los residuos del ajuste
    ax1.plot(tau, result.residual, 'k.')
    ax1.set_xlabel(r'$\tau$ [s]')
    ax1.set_ylabel(r'Residuals')
    fig.subplots_adjust(hspace=0.1)

    # Gráfico del histograma de los residuos
    fig2, ax1 = plt.subplots(1, 1)
    ax1.hist(result.residual, bins=20, density=True, label='Residuals')
    res_mean = np.mean(result.residual)
    res_std = np.std(result.residual)
    x = np.linspace(norm.ppf(0.0001), norm.ppf(0.999), 500)
    ax1.plot(x, norm.pdf(x, loc=res_mean, scale=res_std), 'r-', lw=5,
             alpha=0.6, label='Normal pdf')
    # Invierte orden de las leyendas
    handles, labels = ax1.get_legend_handles_labels()
    ax1.legend(handles[::-1], labels[::-1], loc='best')

    return None


if __name__ == '__main__':

    # -------------------------------------------------------------------------
    # Gráfico de historias
    # -------------------------------------------------------------------------
    # Archivos a leer

    nombres = ['../src/resultados_arossi/medicion04.a.inter.D1_ros.dat',
               '../src/resultados_arossi/medicion04.a.inter.D2_ros.dat',
               ]

    figs = arossi_grafica_historias(nombres)

    # figs[1].axes[0].set_xlabel('Nuevo nombre')

    # -------------------------------------------------------------------------
    # Gráfico de promedio
    # -------------------------------------------------------------------------
    # Archivos a leer
    nombres = ['../src/resultados_arossi/medicion04.a.inter.D1.ros',
               '../src/resultados_arossi/medicion04.a.inter.D2.ros',
               ]

    figs = arossi_grafica_promedio(nombres)

    # -------------------------------------------------------------------------
    # Ajuste de la curva
    # -------------------------------------------------------------------------
    # Archivos a leer
    nombres = '../src/resultados_arossi/medicion04.a.inter.D1.ros'

    P, P_std, tau, parametros = arossi_lee_historias_promedio(nombres)
    arossi_ajuste_1exp(tau, P, P_std)
    # arossi_ajuste_1exp(tau[2:], P[2:], P_std[2:])
    plt.show()
