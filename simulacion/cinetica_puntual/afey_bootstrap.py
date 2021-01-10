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

    nombres = [
     #        'resultados_afey/times.D1_var.fey',
     #        'resultados_afey/times.D1_var_choice.fey',
              'resultados_afey/times.D1_var_skip.fey',
     #        'resultados_afey/times.D1_var_mca.fey',
              ]

    N_bs = 1000
    # ------------------------------------------------------------------------
    nombre = nombres[0]
    # Camino absoluto del archivo que se quiere leer
    abs_nombre = os.path.join(script_dir, nombre)

    np.random.seed(1)
    params = []
    if True:
        for i in range(N_bs):
            tau, Y, std_Y, num_hist, tasas = lee_fey(abs_nombre)

            Nk = lee_Nk(nombre.rstrip('fey') + 'Nk')
            data_size = np.size(tau)
            ind_bs = np.random.randint(0, data_size, size=data_size)
            tau_bs = tau[ind_bs]
            Y_bs = Y[ind_bs]
            std_Y_bs = std_Y[ind_bs]

            _, val, teo = ajuste_afey(tau_bs, Y_bs, std_Y_bs, [500, 1, 0],
                                      vary=[1, 1, 0], verbose=False,
                                      plot=False, conf_int=False, Nk=Nk)
            params.append(val)

        alfas, efis = [], []
        for param in params:
            alfas.append(param[0].n)
            efis.append(param[1].n)
        alfas = np.asarray(alfas)
        efis = np.asarray(efis)

        np.save('alfas', alfas)
        np.save('efis', efis)

    alfas = np.load('alfas.npy')
    efis = np.load('efis.npy')

    fig, ax = plt.subplots(1,2)
    ax[0].hist(alfas, 20)
    ax[1].hist(efis, 20)

    fig, ax = plt.subplots(1,1)
    h = ax.hist2d(alfas, efis, 100, density=False)
    ax.plot(420, 0.04, 'bo', markersize=8)
    fig.colorbar(h[3], ax=ax)
    #plt.hist(efis, 20)
    # [print("Estimados: {} - Teóricos: {}".format(va, te)) 
    #        for va, te in zip(val, teo)]
    alfa_m = np.mean(alfas)
    alfa_std = np.std(alfas)

    efi_m = np.mean(efis)
    efi_std = np.std(efis)

    print(alfa_m, alfa_std)
    print(efi_m, efi_std)

    plt.show()
