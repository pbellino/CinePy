#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np
from modules.alfa_rossi_procesamiento import arossi_una_historia_I
from modules.io_modules import read_PTRAC_CAP_bin


def agrega_tiempo_de_fuente(tasa, datos, filename):
    """
    Agrega los tiempos de fuente al tiempo registrado en el PTRAC

    Se asume una distribución exponencial de tiempos entre eventos y se lo
    suma a todas las capturas que provienen de una misma historia

    Parámetros
    ----------

        tasa : double [1/s]
            Tasa de eventos de fuente (fisiones espontáneas) por segundo. Se
            debe calcular en base a la actividad de la fuente.

        datos : list of list
            Los datos leídos del archivo PTRAC, tal cual se obtienen con la
            función `read_PTRAC_CAP_bin()`

        filename : string
            Nombre del archivo donde se guardarán los tiempos.

    Resultados
    ----------

        times : numpy array
            Lista ordenada de los tiempos de captura. Contados todos a partir
            del primero (ie times[0]=0)
        cells : numpy_array
            Celda en donde se produjo la captura. Sirve para diferenciar
            distintos detectores.
        nps : numpy array
            Lista que identifica a cuál historia pertenece cada captura. En
            principio  no tiene mucha utilidad

    Cada elemento de estos tres vectores hace referencia a una captura.

    Ejemplo: times[3], cells[3] y nps[3] hacen referencia al tiempo de captura
    del times[3] del cuarto pulso que se produjo en la celda cells[3] y que
    pertenece a la historia nps[3]
    """

    # Convierto a array de numpy
    datos = np.asarray(datos)
    # Ordeno por historia para después buscar más fácil
    datos = datos[datos[:, 0].argsort()]
    # Número de historia de cada evento
    nps = np.asarray(datos[:, 0], dtype='int64')
    # Cantidad de historias totales
    num_hist = len(set(nps))
    # Tiempos del PTRAC en segundos
    times = np.asarray(datos[:, 1], dtype='float64') * 1e-8
    # Celda donde se produjo la captura
    cells = np.asarray(datos[:, 2], dtype='int64')

    # Se generan número con distribución exponencial
    beta = 1.0 / tasa
    # Genero los tiempos para cada evento de fuente
    np.random.seed(313131)
    src_time = np.cumsum(np.random.exponential(beta, num_hist))
    for n, t in zip(set(nps), src_time):
        indx_min = np.searchsorted(nps, n, side='left')
        indx_max = np.searchsorted(nps, n, side='right')
        times[indx_min:indx_max] += t

    # Ordeno los tiempos y mantengo asociado el numero de historia y la celda
    _temp = np.stack((nps, times, cells), axis=-1)
    # Ordeno para tiempos crecientes
    _temp_sorted = _temp[_temp[:, 1].argsort()]
    # Vuelvo a separar
    nps = _temp_sorted[:, 0]
    times = _temp_sorted[:, 1]
    cells = _temp_sorted[:, 2]
    # Pongo en cero al primer pulso
    times -= times[0]

    # Se guardan los datos del tiempo
    np.savetxt(filename, times, fmt='%.12E')

    return times, cells, cells


def RAD_sin_accidentales(nombre, dt_s, dtmax_s):
    """
    Función para obtener la distribución RAD a partir del PTRAC

    El objetivo es comparar con la RAD obtenida con tallies F8 + GATES. Por
    este motivo se deben eliminar las coincidencias accidentales.

    Notar que pueden haber algunas diferencias porque la forma de obtener la
    RAD con las tallies y con los algoritmos míos (arossi_una_historia_I) son
    distintos. Yo obligo a que todos los triggers alcancen el 'dtmax_s'. Las
    tallies F8 en cambio, abren un GATE para cualquier trigger.

    Parámetros
    ----------
        nombre : string
            Nombre del archivo binario PTRAC obtenido con event=CAP

        dt_s : float (segundos)
            Intervalo temporal para cada bin de la distribución

        dtmax : float (segundos)
            Máximo intervalo de la distribución de alfa-Rossi

    Importante
    ----------
        Los valores dt_s y dtmax deben coincidir con los utilizados para
        construir las tallies F8 con GATES sucesivas
    """
    # Leo el archivo binario de PTRAC con event=CAP
    datos, header = read_PTRAC_CAP_bin(nombre)

    # Convierto a array numpy
    datos = np.asarray(datos)
    # Números de historia
    nps = np.asarray(datos[:, 0], dtype='int64')
    # Tiempos
    timestamp = np.asarray(datos[:, 1], dtype='float64') * 1e-8
    # Obtiene los timestamp para una misma historia
    times_historia = []
    for n in set(nps):
        indx = np.where(nps == n)
        # Timestamp por historia y ordenado
        list_by_hist = np.sort(timestamp[indx])
        # Se fija t=0 en el primer pulso
        list_by_hist -= list_by_hist[0]
        times_historia.append(list_by_hist)

    # Datos de la RAD
    historias = []
    for time in times_historia:
        P_historia, _, N_trig, P_trig =  \
            arossi_una_historia_I(time, dt_s, dtmax_s, 1)
        # print(P_trig)
        # Analizo los triggers para no tener que operar sobre P_historia
        # (molesta la normalización en este caso)
        if P_trig.size:
            # Sumo todos trigger
            historias.append(np.sum(P_trig, axis=0))
    # Sumo entre todos los eventos para obtener la distribución de alfa-Rossi
    RAD = np.sum(historias, axis=0)
    return RAD


if __name__ == "__main__":
    pass
