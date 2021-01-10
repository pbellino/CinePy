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
                                          ajuste_afey_delayed, grafica_Nk, \
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
    # grafica_historias_afey(nombre)
    # plt.show()
    # quit()
    folder = 'resultados_afey'

    nombres = {
            'bounching': folder + '/times.D1_var.fey',
               'choice': folder + '/times.D1_var_choice.fey',
                 'skip': folder + '/times.D1_var_skip.fey',
                  'mca': folder + '/times.D1_var_mca.fey',
              }
    # -------------------------------------------------------------------------
    #
    # myfig = grafica_afey(nombres)
    #
    # ax = myfig.get_axes()[0]
    # ax.set_title(u'Un título')
    # plt.show()
    #
    # ------------------------------------------------------------------------

    Nk_res = {}
    results = {}
    for key, nombre in nombres.items():
        print(key,nombre)

        # Camino absoluto del archivo que se quiere leer
        abs_nombre = os.path.join(script_dir, nombre)
        tau, Y, std_Y, num_hist, tasas = lee_fey(abs_nombre)
        # Puntos para cada tau por batch
        Nk = lee_Nk(nombre.rstrip('fey') + 'Nk')

        _, val, teo = ajuste_afey(tau, Y, std_Y, [400, 10, 0], vary=[1, 1, 0],
                                  Nk=Nk, tasa=tasas, verbose=False, plot=False,
                                  conf_int=False)
        results[key] = val

        Nk_res[key] = (tau, Nk)
        #
        #_, val, teo = ajuste_afey_delayed(tau, Y, std_Y, [500, 1, 0, 1],
        #                                    vary=[1, 1, 0, 1])
        print(2*'\n')
        [print("Estimados: {:.4e} - Teóricos: {:.4e}".format(va, te))
                for va, te in zip(val, teo)]
        # ajuste_afey_nldtime(tau, Y, std_Y)

        # Análisis de incertezas
        if False:
            var_teo_exac = teo_variance_berglof_exacta(Y, Nk, tasas[0], tau)
            rel_teo_exac = 100 * np.sqrt(var_teo_exac / num_hist) / Y
            var_teo_pacilio = teo_variance_pacilio(Y, Nk, tasas[0], tau)
            rel_teo_pacilio = 100 * np.sqrt(var_teo_pacilio / num_hist) / Y

            fig8, ax8 = plt.subplots(1, 1)
            ax8.plot(tau, 100 * std_Y / Y, '.', label='Estimated')
            ax8.set_xlabel(r'$\tau$ [s]]')
            ax8.set_ylabel(r'$\sigma_{\bar Y}/\bar Y (\tau)$ [%]')

            ax8.plot(tau, rel_teo_exac, 'k', lw=2, label='Ordendorf')
            ax8.plot(tau, rel_teo_pacilio, 'g', lw=2, label='Pacilio')
            ax8.grid(True)
            ax8.legend(loc='best')

            plt.show()

    fig, axs = plt.subplots(3, 1, sharex=True)
    for key, result in results.items():
        for res, ax in zip(result, axs):
            ax.errorbar([key], res.n, yerr=res.s, fmt='s')
    varis = [r"$\alpha$ [1/s]", r"$\epsilon$", r"$F$ [1/s]"]

    # Gráfico valores teóricos
    x_teo = np.linspace(-0.1, len(result)+0.1, 100)
    y_teo = np.ones(np.shape(x_teo))
    for ax, var, te in zip(axs, varis, teo):
        ax.set_ylabel(var)
        ax.plot(x_teo, te * y_teo, 'k', lw=2)
        # ax.set_ylim(te * 0.95, te * 1.15)

    plt.tight_layout()

    # Gráfica de Nk vs tau
    grafica_Nk(Nk_res)

    plt.show()


