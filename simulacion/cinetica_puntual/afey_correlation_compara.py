#!/usr/bin/env python3

"""
Script para analizar la correlación que se introduce al utilizar el método de
agrupamiento.

"""

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os

import sys
sys.path.append('/home/pablo/CinePy')

from modules.io_modules import lee_historias_completas
from modules.alfa_feynman_analisis import grafica_historias_afey


if __name__ == '__main__':

    # -------------------------------------------------------------------------
    # Parámetros de entrada
    # -------------------------------------------------------------------------
    # Archivos a leer
    nombres = {
               'bounching': "resultados_afey/times.D1_var.dat",
               'choice': "resultados_afey/times.D1_var_choice.dat",
               'skip': "resultados_afey/times.D1_var_skip.dat",
               'MCA': "resultados_afey/times.D1_var_mca.dat",
              }

    fig_c, axs_c = plt.subplots(2, 2, figsize=(9,8), sharex='col',
                                    sharey=True)
    cbar_ax = fig_c.add_axes([.90 , .2, .03, .6])
    fig_h, axs_h = plt.subplots(4, 1, sharex=True)
    i = 0   # Auxiliar para poner la barra de colores a la derecha
    for axc, axh, (key, nom) in zip(axs_c.flat, axs_h, nombres.items()):
        vec_temp, data, num_hist, tasas = lee_historias_completas(nom)
        coef = np.corrcoef(data)
        np.fill_diagonal(coef, np.nan)
        sns.heatmap(coef, xticklabels=9, yticklabels=9, ax=axc,
                         vmin=-0.2, vmax=1, cbar=i==0,
                         cbar_ax=None if i else cbar_ax)

        labels = [item.get_text() for item in axc.get_xticklabels()]
        labels = [str(int(item)+1) for item in labels]
        axc.set_xticklabels(labels)
        axc.set_yticklabels(labels, rotation='horizontal')
        axc.invert_yaxis()
        axc.set_aspect('equal')
        # Gráfico de histogramas
        sns.distplot(coef.flatten(), bins=50, kde=True, ax=axh, label=key)
        axh.legend(loc="upper left")
        i += 1
    axs_h[-1].set_xlabel("Correlacion coefficients")
    for ax in axs_c[1, 0:2]:
        ax.set_xlabel(r'$T_i/T_1$')
    for ax in axs_c[0:2, 0]:
        ax.set_ylabel(r'$T_i/T_1$')
    fig_c.tight_layout(rect=[0, 0, .9, 1])
    fig_h.tight_layout()
    plt.show()

