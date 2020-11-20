#!/usr/bin/env python3

import numpy as np
import matplotlib.pyplot as plt
import os

import sys
sys.path.append('/home/pablo/CinePy')

from modules.io_modules import lee_historias_completas, lee_fey
from modules.funciones import alfa_feynman_lin_dead_time, \
                              alfa_feynman_dos_exp, alfa_feynman_tres_exp, \
                              alfa_feynman_lin_dead_time_lin_delayed, \
                              alfa_feynman_dos_exp_delayed, \
                              alfa_feynman_nldtime
from modules.alfa_feynman_analisis import teo_variance_berglof, grafica_afey, \
                                          ajuste_afey_nldtime, ajuste_afey, \
                                          grafica_historias_afey, lee_Nk, \
                                          ajuste_afey_2exp, ajuste_afey_3exp, \
                                          ajuste_afey_delayed, \
                                          ajuste_afey_2exp_delayed


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
    nombres = ['resultados_afey/times_listmode.D1.fey',
               'resultados_afey/times_listmode.D2.fey',
               ]
    # -------------------------------------------------------------------------
    #
    # myfig = grafica_afey(nombres)
    #
    # ax = myfig.get_axes()[0]
    # ax.set_title(u'Un título')
    # plt.show()
    #
    # ------------------------------------------------------------------------
    nombre = nombres[0]
    # Camino absoluto del archivo que se quiere leer
    abs_nombre = os.path.join(script_dir, nombre)
    tau, Y, std_Y, num_hist, _ = lee_fey(abs_nombre)

    Nk = lee_Nk(nombre.rstrip('fey') + 'Nk')
    var_teo = teo_variance_berglof(Y, Nk)

    ajuste_afey(tau, Y, std_Y)
    # ajuste_afey_2exp(tau, Y, std_Y)
    # ajuste_afey_3exp(tau, Y, std_Y)
    # ajuste_afey_delayed(tau, Y, std_Y)
    # ajuste_afey_2exp_delayed(tau, Y, std_Y)
    # ajuste_afey_nldtime(tau, Y, std_Y)

    fig8, ax8 = plt.subplots(1, 1)
    ax8.plot(tau, num_hist*std_Y**2, '.', label='Estimated variance')
    ax8.set_xlabel(r'$\tau$ [s]')
    ax8.set_ylabel(r'Var[Y($\tau$)]')

    ax8.plot(tau, var_teo, 'r', lw=2, label='Teoretical variance')
    ax8.grid(True)
    ax8.legend(loc='best')

    plt.show()
