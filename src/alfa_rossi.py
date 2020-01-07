#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
TODO
"""

import numpy as np
import matplotlib.pyplot as plt
import timeit

from alfa_rossi_preprocesado import alfa_rossi_preprocesado
import sys
sys.path.append('../')


plt.style.use('paper')


def arossi_una_historia_I(data, dt_s, dtmax_s, tb):
    """
    TODO
    dt, dtmax, tb en unidades de segundo
    """
    # Es más cómodo trabajar en unidades de pulso
    dt = np.uint64(dt_s / tb)
    print('dt=', dt)
    dtmax = np.uint64(dtmax_s / tb)
    print('dtmax=', dtmax)
    N_bin = np.uint64(dtmax/dt)
    print('N_bin=', N_bin)
    # Primero selecciona hasta qué indice se puede recorrer `data`
    t_tot_hist = data[-1]   # Tiempo total de la historia
    # Busca el último pulso que puede ser utilizado como trigger
    # en base a lo que dura cada barrido (dtmax)
    ind_max_hist = np.searchsorted(data, t_tot_hist - dtmax, side='right')
    # Creo el vector donde todos los pulsos servirán como triggers
    data_ok = data[:ind_max_hist]
    N_triggers = data_ok.size
    print('Cantidad total de triggers', N_triggers)
    print('last data_ok', data_ok[-1], 'en', ind_max_hist)

    # Recorro todos los triggers
    aaa = []
    bbb = []
    ccc = []
    sump=0
    for i, pulso in enumerate(data_ok):
        # Busco el bloque que voy a binear para este trigger
        i_max = np.searchsorted(data, pulso + dtmax, side='right')
        # Construyo el bloque y fijo t=0 en el trigger
        data_bin = data[i:i_max] - data[i]
        # Cuento los pulsos en cada bin
        p_hist = np.bincount(data_bin // dt)
        # Como np.bincount binea sólo hasta np.amax()+1, completo con
        # ceros el resto de los bines (hasta llenar los N_bin)
        n_pad = np.int64(N_bin-p_hist.size)
        p_hist_completa = np.pad(p_hist, (0, n_pad), mode='constant')
        sump = sump+p_hist_completa[0]
        aaa.append([i, i_max])
        bbb.append(data_bin)
        ccc.append(p_hist_completa)
    # Como np.bincount() cuenta al pulso de trigger, se lo resto
    p_hist_completa[0] = p_hist_completa[0] - N_triggers
    print('suma',sump)
    # print(aaa[0:10])
    # print(bbb[0:10])
    # TODO: ver bien las salidas que se necesitan antes de seguir
    return ccc


if __name__ == '__main__':

    # -------------------------------------------------------------------------
    # Parámetros de entrada
    # -------------------------------------------------------------------------
    # Archivos a leer
    nombres = [
              '../datos/medicion04.a.inter.D1.bin',
              '../datos/medicion04.a.inter.D2.bin',
              ]
    # Cantidad de historias
    Nhist = 100
    # Tiempo base del contador [s]
    tb = 12.5e-9
    dt_s = 0.5e-3
    dtmax_s = 50e-3
    # -------------------------------------------------------------------------
    data_bloques, _, _ = alfa_rossi_preprocesado(nombres, Nhist, tb)

    a = arossi_una_historia_I(data_bloques[0][0], dt_s, dtmax_s, tb)
    a = np.asarray(a)
    acum = np.sum(a, axis=0)
    fig1, ax1 = plt.subplots(1,1)
    ax1.plot(acum,'.')
    plt.show()
    quit()
    print(a)
    for i in a:
        print(i[-1])

    # for blo in data_bloques[0]:
    #     print(blo.size)
    # x = data_bloques[0][0]
    # print(x)

    #print( timeit.timeit(sorted, number=500) )

