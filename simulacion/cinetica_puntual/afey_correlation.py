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

    # Carpeta donde se encuentra este script
    # Lo uso por si quiero llamarlo desde otro dierectorio
    script_dir = os.path.dirname(__file__)
    # -------------------------------------------------------------------------
    # Parámetros de entrada
    # -------------------------------------------------------------------------
    # Archivos a leer
    #nombre = "resultados_afey/times.D1_var.dat"
    #nombre = "resultados_afey/times.D1_var_choice.dat"
    nombre = "resultados_afey/times.D1_var_skip.dat"
    #nombre = "resultados_afey/times.D1_var_mca.dat"

    vec_temp, data, num_hist, tasas = lee_historias_completas(nombre)
    coef = np.corrcoef(data)
    np.fill_diagonal(coef, np.nan)
    ax = sns.heatmap(coef, xticklabels=9, yticklabels=9)

    labels = [item.get_text() for item in ax.get_xticklabels()]
    labels = [str(int(item)+1) for item in labels]
    ax.set_xticklabels(labels)
    ax.set_yticklabels(labels, rotation='horizontal')
    ax.set(xlabel=r'$T_i/T_1$', ylabel=r'$T_i/T_1$')
    ax.invert_yaxis()
    ax.set_title('Correlation matrix')
    plt.tight_layout()

    fig, ax1 =  plt.subplots(1, 1)
    ax1 = sns.distplot(coef.flatten(), bins=50, kde=True)
    ax1.set_xlabel("Correlacion coefficients")
    plt.show()

