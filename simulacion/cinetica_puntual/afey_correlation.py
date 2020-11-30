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
    nombre = "resultados_afey/times.D1_var.dat"
    nombre = "resultados_afey/times.D1_var_choice.dat"
    nombre = "resultados_afey/times.D1_var_mca.dat"


    vec_temp, data, num_hist, tasas = lee_historias_completas(nombre)
    coef = np.corrcoef(data)
    np.fill_diagonal(coef, np.nan)
    ax = sns.heatmap(coef)
    ax.invert_yaxis()

    fig, ax1 =  plt.subplots(1, 1)
    ax1.hist(coef.flatten(), bins=50)
    plt.show()
    quit()
    grafica_historias_afey(nombre)
    plt.show()

