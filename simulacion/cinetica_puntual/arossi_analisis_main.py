#!/usr/bin/env python3

"""
Grafica las curvas P(tau) para cada historia y la del promeio.

Ajuste no lineal de la curva P(tau) promedio

TODO: Falta organizar cómo se almacenan los resultados del ajuste. Falta hacer
que se ajusten una lista de curvas. Falta propagar errores para obtener el
resto de los parámetros cinéticos (usar paquete uncertainties).
"""

import numpy as np
import matplotlib.pyplot as plt

import sys
sys.path.append('/home/pablo/CinePy')

from modules.alfa_rossi_lectura import arossi_lee_historias_completas, \
                                       arossi_lee_historias_promedio
from modules.alfa_rossi_analisis import arossi_grafica_historias, \
                                        arossi_grafica_promedio, \
                                        arossi_ajuste_1exp,  \
                                        arossi_ajuste_2exp


if __name__ == '__main__':

    # -------------------------------------------------------------------------
    # Gráfico de historias
    # -------------------------------------------------------------------------
    # Archivos a leer

    nombres = [
               './resultados_arossi/times_listmode_n_corr_ros.dat',
               ]

    # figs = arossi_grafica_historias(nombres)

    # figs[1].axes[0].set_xlabel('Nuevo nombre')

    # -------------------------------------------------------------------------
    # Gráfico de promedio
    # -------------------------------------------------------------------------
    # Archivos a leer
    nombres = [
               './resultados_arossi/times.D1.ros',
               ]

    figs = arossi_grafica_promedio(nombres)

    # -------------------------------------------------------------------------
    # Ajuste de la curva
    # -------------------------------------------------------------------------
    # Archivos a leer
    P_ini = [1e-3, 1, 1e-3, 1, 0]
    for nombre in nombres:
        P, P_std, tau, parametros = arossi_lee_historias_promedio(nombre)
        # arossi_ajuste_1exp(tau, P, P_std)
        fig = arossi_ajuste_2exp(tau[1:], P[1:], P_std[1:], P_ini)
        fig.suptitle(nombre.split('/')[-1])
    plt.show()
    #
