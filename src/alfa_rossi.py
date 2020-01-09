#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
TODO
"""

import numpy as np
import matplotlib.pyplot as plt
import multiprocessing as mp
import itertools
import timeit
import time

from alfa_rossi_preprocesado import alfa_rossi_preprocesado
from modules.estadistica import rate_from_timestamp

import sys
sys.path.append('../')

plt.style.use('paper')


def arossi_una_historia_I(data, dt_s, dtmax_s, tb):
    """
    Aplica el método de a-Rossi (Tipo I) a una historia

    En el código se convierten todos los tiempos a pulsos, mediante tb.

    La función P(tau) de alfa-Rossi programada está normalizada con la tasa
    de cuentas de la historia.

    De todas maneras se puede trabajar con P_trigger que están los datos en
    crudo obtenidos con cada trigger (P_historia es un promedio de ésta)

    Muchas de las magnitudes calculadas en esta función podrían hacerse afuera,
    pero ya que va a ser paralelizada, perferí poner todo acá.

    En la carpeta /tests/ hay un script para verificar que haga lo correcto.

    Parámetros
    ----------
        data : numpy array
            Vector con los tiempos de llegada de pulsos. Originalmente
            pensado para que sea una historia.
        dt_s : double [segundos]
            Duración de cada intervalo del histograma.
        dtmax_s : double [segundos]
            Tiempo total del histograma (N_bin = dtmax_s / dt_s)
        tb : double [segundos]
            Tiempo que dura cada pulso del contador

    Resultados
    ----------
        P_historia : numpy array
            P(tau) normalizada para la historia. La normalización utilizada
            consiste en dividir las cuentas acumuladas de los histogramas para
            cada trigger por:
                1) La cantidad total de triggers `Ǹ_triggers` (np.mean)
                2) El ancho de cada bin `dt_s`
                3) La tasa de cuentas de la historia `R_historia[0]`
            Con esta normalización, la parte no correlacionada vale uno.
        R_historia : tupla (R_promedio, R_desvío)
            Tasa de cuenta promedio y desvío en la historia. El desvío es sin
            dividir por raiz(N)
        N_triggers : int
            Cantidad de pulsos que se utilizaron como triggers
        P_trigger : list of list of numpy array
            Son las cuentas directas obtenidas en cada trigger.
            Están sin normalizar. Se utiliza para debuggear.
            Quizá sirva para aplicar otros métodos de multiplicidad

    """
    # Es más cómodo trabajar en unidades de pulso
    dt = np.int(dt_s / tb)
    # print('dt=', dt)
    dtmax = np.int(dtmax_s / tb)
    # print('dtmax=', dtmax)
    N_bin = np.int(dtmax/dt)
    # print('N_bin=', N_bin)
    # Primero selecciona hasta qué indice se puede recorrer `data`
    t_tot_hist = data[-1]   # Tiempo total de la historia
    # Busca el último pulso que puede ser utilizado como trigger
    # en base a lo que dura cada barrido (dtmax)
    ind_max_hist = np.searchsorted(data, t_tot_hist - dtmax, side='right')
    # Creo el vector donde todos los pulsos servirán como triggers
    data_ok = data[:ind_max_hist]
    # Cantidad de triggers en data_ok
    N_triggers = data_ok.size
    # Tasa de cuentas y desvío de la historia
    R_historia = rate_from_timestamp(np.diff(data_ok)*tb)

    # Recorro todos los triggers
    P_trigger = []
    for i, trigger in enumerate(data_ok):
        # Busco el bloque que voy a binear para este trigger
        # Es importante que sea side=`left` para evitar que si existe un
        # pulso en dtmax sea contado como un bin extra
        i_max = np.searchsorted(data, trigger + dtmax, side='left')
        # Construyo el bloque y fijo t=0 en el trigger
        data_bin = data[i:i_max] - data[i]
        # Cuento los pulsos en cada bin
        p_hist = np.bincount(data_bin // dt)
        # Como np.bincount() cuenta al pulso del trigger, se lo resto
        p_hist[0] -= 1
        # Como np.bincount binea sólo hasta np.amax()+1, completo con
        # ceros el resto de los bines (hasta llenar los N_bin)
        n_pad = np.int(N_bin - p_hist.size)  # Cantidad de ceros que se agregan
        p_hist_completa = np.pad(p_hist, (0, n_pad), mode='constant')
        P_trigger.append(p_hist_completa)
    P_trigger = np.asarray(P_trigger)
    # Calculo la probabilidad normalizada (por dt del bin)
    # Pero más importante: normalizada con la tasa de cuentas (para que la
    # parte no correlacionada sea siempore igual a uno).
    P_historia = np.mean(P_trigger, axis=0) / dt_s / R_historia[0]

    return P_historia, R_historia, N_triggers, P_trigger


def arossi_serial(data_bloques_undet, dt_s, dtmax_s, tb):
    """ Función en serie, sólo para debugg (sólo para un detector)"""
    a = []
    for data in data_bloques_undet:
        a.append(arossi_una_historia_I(data, dt_s, dtmax_s, tb))
    return a


def wrapper_arossi_una_historia_I(arg_tupla):
    """ Wrapper de `arossi_una_historia_I` usada al paralelizar. """
    data, dt_s, dtmax_s, tb = arg_tupla
    return arossi_una_historia_I(data, dt_s, dtmax_s, tb)


def arossi_historias(data_bloques, dt_s, dtmax_s, tb):
    """
    Procesamiento de alfa-Rossi para todos los detectores.

    Los cálculos por detector se hacen en serie. Los cálculos para las
    historia están paralelizados con `multiprocessing`.

    Parámetros
    ----------
        data_bloques : list of numpy ndarray
            Cada elemento de la lista está compuesto por un array con todas
            las historias. Es obtenido a partir de `alfa_rossi_preprocesado.py`
        dt_s : double [segundos]
            Duración de cada intervalo del histograma.
        dtmax_s : double [segundos]
            Tiempo total del histograma (N_bin = dtmax_s / dt_s)
        tb : double [segundos]
            Tiempo que dura cada pulso del contador

    Resultados
    ----------
        results_detectores : lista de numpy ndarray
            Cada elemento de la lista corresponde al resultado de un detector.
            Cada elemento contiene a las salidas de la función
            `wrapper_arossi_una_historia_I`:
                - P_historia : numpy array
                - R_historia : tupla (R_promedio, R_desvío)
                - N_triggers : int
                - P_trigger : list of list of numpy array
            Para más detalle, ver la función `arossi_una_historia_I`

    """
    # Cantidad de procesadores disponibles
    _num_proc = mp.cpu_count()
    _pool = mp.Pool(processes=_num_proc)
    print('Se utilizan {} procesos'.format(_num_proc))
    print('-' * 50)
    results_detectores = []  # Lista para los resultados de cada detector
    # Itero sobre cada detector
    for i, data_un_detector in enumerate(data_bloques):
        print('Procesando al archivo [{}]'.format(i))
        # Construyo el argumento del wrapper en forma de tupla
        argumentos_wrapper = zip(data_un_detector, itertools.repeat(dt_s),
                                 itertools.repeat(dtmax_s),
                                 itertools.repeat(tb))
        _res = _pool.map(wrapper_arossi_una_historia_I, argumentos_wrapper)
        _res = np.asarray(_res)
        results_detectores.append(_res)
        print('-' * 50)
    return results_detectores


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
    # Para probar `arossi_historias()'
    # -------------------------------------------------------------------------
    data_bloq, _, _ = alfa_rossi_preprocesado(nombres, Nhist, tb)
    # En serie
    """
    t0 = time.time()
    a_s = arossi_serial(data_bloques[0], dt_s, dtmax_s, tb)
    tf = time.time()
    print('Tiempo serie: {} s'.format(tf-t0))
    quit()
    """

    # En paralelo
    t0 = time.time()
    a_p = arossi_historias(data_bloq, dt_s, dtmax_s, tb)
    tf = time.time()
    print('Tiempo paralelo: {} s'.format(tf-t0))

    fig1, ax1 = plt.subplots(1, 1)
    m = np.mean(a_p[0][:, 0])
    ax1.plot(m)
    m = np.mean(a_p[1][:, 0])
    ax1.plot(m)

    plt.show()
    quit()
    # Gráficos de triggers y tasa de cuentas para cada historia
    fig1, axs = plt.subplots(2, 1, sharex='col')
    hist = np.linspace(0, Nhist-1, Nhist, dtype=int)
    for i, det in enumerate(a_p):
        R = np.asarray(list(det[:, 1]))
        lab_str = 'Archivo ' + str(i)
        axs[0].errorbar(hist, R[:, 0], yerr=R[:, 1], fmt='.', elinewidth=0.5,
                        lw=0, label=lab_str)
        Trig = det[:, 2]
        axs[1].plot(hist, Trig, '.', label=lab_str)

    axs[0].set_ylabel('Tasa de cuentas [cps]')
    axs[1].set_ylabel('# triggers')
    axs[1].set_xlabel('Historias')

    for ax in axs:
        ax.grid(True)
        ax.legend(loc='best')

    plt.show()

    # -------------------------------------------------------------------------
    # Para probar 'arossi_una_historia_I()'
    # -------------------------------------------------------------------------
    """
    data_bloques, _, _ = alfa_rossi_preprocesado(nombres, Nhist, tb)
    a, _, _, _ = arossi_una_historia_I(data_bloques[0][99], dt_s, dtmax_s, tb)

    fig1, ax1 = plt.subplots(1, 1)
    ax1.plot(a, '.')
    plt.show()

    # print( timeit.timeit(sorted, number=500) )
    """
    # -------------------------------------------------------------------------
