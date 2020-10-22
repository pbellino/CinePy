#!/usr/bin/env python3

"""
Script para procesar los datos con el método de alfa-Rossi

La función principal es `alfa_rossi_procesamiento()`

Toma la salida de la función `alfa_rossi_preprocesamiento()` que está en
el script `alfa_rossi_preprocesamiento.py`.

TODO: Puede tene problemas de memoria para ciertos parámetros dt y dtmax. Para
aplicaciones en reactores no sucede, quizá para otras aplicaciones haya que
optimizar el manejo de memoria.

OJO: La función numpy.bincount() parace tener un bug cuando trabaja con uint64.
Trata de castear a in64 y no puede. Trabajando con un tb=12.5e-9s, el límite
rondaría los 3600 años. Pero si se llegara a reducir mucho el tb podría
molestar. Suena bastante improbable igual.
"""

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import multiprocessing as mp
import itertools
import time
import os

import sys
sys.path.append('../')

from modules.alfa_rossi_preprocesamiento import alfa_rossi_preprocesamiento
from modules.estadistica import rate_from_timestamp

sns.set()
plt.style.use('paper')


def arossi_una_historia_I(data, dt_s, dtmax_s, tb, trigs='compute'):
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
        trigs : str ("compute", "all")
            Indicación para saber cuántos triggers utilizarp por historia.
            "compute" : Calcula cuál debe ser el último trigger para que todos
            los binnes de la distribución tengan la misma estadística (es el
            comportamiento original).
            "all" : usa todos los triggers. Se agregó para procesar los datos
            de coincidencias sin accidentales a través de la PTRAC.

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
            Tasa de cuenta promedio y desvío del promedio en la historia
            (está dividida por raiz(N)).
        N_triggers : int
            Cantidad de pulsos que se utilizaron como triggers
        P_trigger : list of list of numpy array
            Son las cuentas directas obtenidas en cada trigger.
            Están sin normalizar. Se utiliza para debuggear.
            Quizá sirva para aplicar otros métodos de multiplicidad

    """
    # Es más cómodo trabajar en unidades de pulso
    dt = np.float(dt_s / tb)
    # print('dt=', dt)
    dtmax = np.float64(dtmax_s / tb)
    # print('dtmax=', dtmax)
    N_bin = np.int(dtmax / dt)
    # print('N_bin=', N_bin)
    # Primero selecciona hasta qué indice se puede recorrer `data`
    t_tot_hist = data[-1]   # Tiempo total de la historia
    # Busca el último pulso que puede ser utilizado como trigger
    # en base a lo que dura cada barrido (dtmax)
    if trigs == "compute":
        # Para que todos tengan la misma estadística
        ind_max_hist = np.searchsorted(data, t_tot_hist - dtmax, side='right')
        # Creo el vector donde todos los pulsos servirán como triggers
        data_ok = data[:ind_max_hist]
        # Tasa de cuentas y desvío de la historia
        R_historia = rate_from_timestamp(np.diff(data_ok)*tb)
    elif trigs == "all":
        # Si una historia es una cadena de fisión, tomo todos los triggers
        data_ok = data[:-1]
        # No normalizo si cada historia es una cadena de fisión
        # Fijo entonces una tasa unitaria y desvío nulo para identificarlo
        R_historia = (1, 0)
    # Cantidad de triggers en data_ok
    N_triggers = data_ok.size
    # Recorro todos los triggers
    P_trigger = []
    for i, trigger in enumerate(data_ok):
        # Busco el bloque que voy a binear para este trigger
        # Es importante que sea side=`left` para evitar que si existe un
        # pulso en dtmax sea contado como un bin extra
        i_max = np.searchsorted(data, trigger + dtmax, side='left')
        # Construyo el bloque y fijo t=0 en el trigger
        data_bin = (data[i:i_max] - data[i]) // dt
        # Cuento los pulsos en cada bin
        # Debo forzar 'int64' porque a veces hay problemas (bug)
        p_hist = np.bincount(data_bin.astype('int64'), minlength=N_bin)
        # Como np.bincount() cuenta al pulso del trigger, se lo resto
        p_hist[0] -= 1
        P_trigger.append(p_hist)
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
    data, dt_s, dtmax_s, tb, trigs = arg_tupla
    return arossi_una_historia_I(data, dt_s, dtmax_s, tb, trigs)


def alfa_rossi_procesamiento(data_bloques, dt_s, dtmax_s, tb, trigs='compute'):
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
        trigs : str ("compute", "all")
            Indicación para saber cuántos triggers utilizarp por historia.
            "compute" : Calcula cuál debe ser el último trigger para que todos
            los binnes de la distribución tengan la misma estadística (es el
            comportamiento original).
            "all" : usa todos los triggers. Se agregó para procesar los datos
            de coincidencias sin accidentales a través de la PTRAC.

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
                                 itertools.repeat(tb),
                                 itertools.repeat(trigs),
                                 )
        _res = _pool.map(wrapper_arossi_una_historia_I, argumentos_wrapper)
        _res = np.asarray(_res)
        results_detectores.append(_res)
        print('-' * 50)
    return results_detectores


def arossi_inspecciona_resultados(resultados, nombres, N_hist, dt_s, dtmax_s):
    """
    Grafica los resultados obtenidos con `arossi_historias`

    Los parámetros de entrada son los mismos que en arossi_historias.

    """

    # Nombres para identificar archivos
    nombres_lab = []
    for nombre in nombres:
        nombres_lab.append(os.path.split(nombre)[-1])

    # Gráficos de triggers y tasa de cuentas para cada historia
    fig1, axs = plt.subplots(2, 1, sharex='col')
    # Vector con los números de historias
    hist = np.linspace(1, N_hist, N_hist, dtype=int)
    # Grafico todos los archivos
    for i, resultado in enumerate(resultados):
        R = np.asarray(list(resultado[:, 1]))
        axs[0].errorbar(hist, R[:, 0], yerr=R[:, 1], fmt='.', elinewidth=0.5,
                        lw=0, label=nombres_lab[i])
        Trig = resultado[:, 2]
        axs[1].plot(hist, Trig, '.', label=nombres_lab[i])

    axs[0].set_ylabel('Tasa de cuentas [cps]')
    axs[1].set_ylabel('# triggers')
    axs[1].set_xlabel('Historias')

    for ax in axs:
        ax.grid(True)
        ax.legend(loc='best')

    # Gráfico de la curva de alfa-Rossi
    # Vector temporal
    tau = np.linspace(0, dtmax_s, int(dtmax_s / dt_s), endpoint=False)
    # Lo hago centrado en el bin
    tau += dt_s / 2
    fig3, ax1 = plt.subplots(1, 1)
    # Grafica todos los archivos leidos en el mismo gráfico
    for i, resultado in enumerate(resultados):
        historias = resultado[:, 0]
        # Grafica todas las historias
        fig2, ax0 = plt.subplots(1, 1)
        ax0.plot(tau, np.asarray(list((historias))).transpose(),
                 lw=0.5, marker='.', label='Historias')
        ax0.set_xlabel(r'TIempo [s]')
        ax0.set_ylabel(r'P($\tau$)')
        handles, labels = ax0.get_legend_handles_labels()
        ax0.legend([handles[0]], [labels[0]], loc='best')
        ax0.set_title(nombres_lab[i])
        fig2.tight_layout()
        # Grafica el promedio entre historias
        P_mean = np.mean(historias)
        P_std = np.std(historias, ddof=1) / np.sqrt(N_hist)
        ax1.errorbar(tau, P_mean, yerr=P_std, fmt='.', elinewidth=0.5,
                     lw=0, label=nombres_lab[i])

    ax1.set_xlabel(r'Tiempo [s]')
    ax1.set_ylabel(r'P($\tau$)')
    ax1.ticklabel_format(style='sci', axis='x', scilimits=(0, 0))
    ax1.set_title(r'Curvas promediadas entre historias')
    ax1.grid(True)
    ax1.legend(loc='best')
    fig3.tight_layout()
    ax1.set_yscale('log')

    plt.show()

    return None


if __name__ == '__main__':

    # -------------------------------------------------------------------------
    # Parámetros de entrada
    # -------------------------------------------------------------------------
    # Archivos a leer
    nombres = [
               # '../datos/medicion04.a.inter.D1.bin',
               # '../datos/medicion04.a.inter.D2.bin',
               '../datos/medicion04.a.inter.D1.txt',
              ]
    tipo = 'ascii'
    # Cantidad de historias
    Nhist = 200
    # Tiempo base del contador [s]
    if tipo == 'binario':
        tb = 12.5e-9
    elif tipo == 'ascii':
        tb = 1.0
    # Tiempos en segundos
    dt_s = 0.5e-3
    dtmax_s = 50e-3

    # -------------------------------------------------------------------------
    # Para probar `arossi_historias()'
    # -------------------------------------------------------------------------
    data_bloq, _, _ = alfa_rossi_preprocesamiento(nombres, Nhist, tb,
                                                  formato_datos=tipo)
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
    resultados = alfa_rossi_procesamiento(data_bloq, dt_s, dtmax_s, tb)
    tf = time.time()
    print('Tiempo paralelo: {} s'.format(tf-t0))

    # Se grafican resultados
    arossi_inspecciona_resultados(resultados, nombres, Nhist, dt_s, dtmax_s)

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
