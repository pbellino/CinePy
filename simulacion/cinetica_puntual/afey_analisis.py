#!/usr/bin/env python3

import numpy as np
import matplotlib.pyplot as plt
import os

import sys
sys.path.append('/home/pablo/CinePy')

from modules.io_modules import lee_fey
from modules.alfa_feynman_analisis import teo_variance_berglof, grafica_afey, \
                                          ajuste_afey_nldtime, ajuste_afey, \
                                          grafica_historias_afey, lee_Nk, \
                                          ajuste_afey_2exp, ajuste_afey_3exp, \
                                          ajuste_afey_delayed, \
                                          ajuste_afey_2exp_delayed, \
                                          teo_variance_berglof_exacta, \
                                          teo_variance_pacilio


if __name__ == '__main__':

    # Carpeta donde se encuentra este script
    # Lo uso por si quiero llamarlo desde otro dierectorio
    script_dir = os.path.dirname(__file__)
    # -------------------------------------------------------------------------
    # Gráfico de las historias
    # -------------------------------------------------------------------------
    # nombre = 'resultados_afey/times.D1_var_mca.dat'
    # #nombre = 'resultados_afey/times.D1_var.dat'
    # #nombre = 'resultados_afey/times.D1_var.dat'
    # nombre = 'resultados_afey/times.D1_var_choice.dat'
    # nombre = 'resultados_afey/times.D1_var_skip.dat'
    # grafica_historias_afey(nombre)
    # plt.show()
    # quit()

    nombres = [
     #         'resultados_afey/times.D1_var.fey',
     #         'resultados_afey/times.D1_var_choice.fey',
               'resultados_afey/times.D1_var_skip.fey',
     #         'resultados_afey/times.D1_var_mca.fey',
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
    tau, Y, std_Y, num_hist, tasas = lee_fey(abs_nombre)
    print(std_Y / Y * 100)
    Nk = lee_Nk(nombre.rstrip('fey') + 'Nk')
    var_teo = teo_variance_berglof(Y, Nk)
    var_teo_exac = teo_variance_berglof_exacta(Y, Nk, tasas[0], tau)
    var_teo_pacilio = teo_variance_pacilio(Y, Nk, tasas[0], tau)

    _, val, teo = ajuste_afey(tau, Y, std_Y, [400, 10, 0], vary=[1, 1, 0],
                               Nk=Nk)
    #
    #_, val, teo = ajuste_afey_delayed(tau, Y, std_Y, [500, 1, 0, 1],
    #                                    vary=[1, 1, 0, 1])
    print(2*'\n')
    [print("Estimados: {:.4e} - Teóricos: {:.4e}".format(va, te))
            for va, te in zip(val, teo)]
    # ajuste_afey_2exp(tau, Y, std_Y)
    # ajuste_afey_3exp(tau, Y, std_Y)
    # ajuste_afey_2exp_delayed(tau, Y, std_Y, [0.5, 1, 0, 3, 1, 1])
    # ajuste_afey_nldtime(tau, Y, std_Y)

    fig8, ax8 = plt.subplots(1, 1)
    ax8.plot(tau, num_hist*std_Y**2, '.', label='Estimated variance')
    ax8.set_xlabel(r'$\tau$ [s]')
    ax8.set_ylabel(r'Var[Y($\tau$)]')

    ax8.plot(tau, var_teo, 'r', lw=2, label='Teoretical variance')
    ax8.plot(tau, var_teo_exac, 'k', lw=2, label='Teoretical variance exact')
    ax8.plot(tau, var_teo_pacilio, 'g', lw=2, label='Teoretical variance pacilio')
    ax8.grid(True)
    ax8.legend(loc='best')

    plt.show()
