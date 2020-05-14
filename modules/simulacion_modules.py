#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np
from mcnptools import Ptrac
from modules.alfa_rossi_procesamiento import arossi_una_historia_I
from modules.io_modules import read_PTRAC_CAP_bin


def genera_tallies(archivo_tallies, def_tallies, *args, **kargs):
    """
    Genera los tallies F8 con los GATES sucesivos para obtener la RAD

    Parámetros
    ----------
        archivo_tallies : string
            Nombre del archivo donde se guardaran las tallies

        def_tallies : dict
            Diccionario con los parámetros que se utilizarán para construir
            las tallies. Las claves deben ser:
                'id_det' : string
                    ZAID del elemento donde se quiere analizar las capturas
                    (helio-3, boro-10, etc).
                'celdas_detector' : string
                    Celda en donde se analizarán las capturas (detector)
                'gate_width' : float (en segundos)
                    Ancho de la ventana temporal (es el bin en el histogama de
                    la distribución de alfa-Rossi).
                'gate_maxim' : float (en segundos)
                    Es el máximo tiempo que se analizará para cada trigger.
                    Haciendo `gate_maxim` / `gate_width` se obtiene el número
                    de bines de la distribución.
    """
    try:
        id_det = def_tallies['id_det']
        celdas_detector = def_tallies['celdas_detector']
        gate_width_s = def_tallies['gate_width']
        gate_maxim_s = def_tallies['gate_maxim']
    except KeyError:
        print('No se especificaron todos los datos para las tallies')
        quit()

    # Convierto gates de segundos a shakes
    gate_width = gate_width_s * 1e8
    gate_maxim = gate_maxim_s * 1e8
    # Construyo vector de gates
    pd_gates = np.arange(0, gate_maxim, gate_width)
    N_bins = np.int(gate_maxim / gate_width)
    print('Distribución de a-Rossi con {} bins'.format(N_bins))

    with open(archivo_tallies, 'w') as f:
        f.write('c ' + '-'*40 + '\n')
        f.write('c Definición de las tallies con GATE\n')
        f.write('c ' + '-'*40 + '\n')
        # Tally sin GATE
        f.write('FC0008 Capturas en He3 - Sin GATE\n')
        f.write('F0008:n {}\n'.format(celdas_detector))
        f.write('FT0008 CAP {} \n'.format(id_det))
        f.write('c\n')
        # Tallies con GATE
        for i, pd_gate in enumerate(pd_gates, 1):
            f.write('FC{:03d}8 Capturas en He3 - PD={:.2e}s GW={:.1e}s\n'.format(i, pd_gate/1e8, gate_width/1e8))
            f.write('F{:03d}8:n {}\n'.format(i, celdas_detector))
            f.write('FT{:03d}8 CAP {} GATE {} {}\n'.format(i, id_det, pd_gate,
                                                           gate_width))
            f.write('c\n')
        f.write('c Fin de las tallies con gate\n')
        f.write('c ' + '-'*40 + '\n')
    print('Se generó el archivo de tallies: ' + archivo_tallies)
    return None


def agrega_tiempo_de_fuente(tasa, nps, datos, filename):
    """
    Agrega los tiempos de fuente al tiempo registrado en el PTRAC

    Se asume una distribución exponencial de tiempos entre eventos y se lo
    suma a todas las capturas que provienen de una misma historia

    Parámetros
    ----------

        tasa : double [1/s]
            Tasa de eventos de fuente (fisiones espontáneas) por segundo. Se
            debe calcular en base a la actividad de la fuente.

        nps : int
            Cantidad de eventos de fuente (fisiones espontáneas) generadas en
            MCNP

        datos : list of list
            Los datos leídos del archivo PTRAC. El formato debe ser:
                1er columna -> El número de historia (nps)
                2da columna -> Los tiempos registrados
                3ra columna -> La celda donde se registró
            Si hay más columnas son ignoradas.

        filename : string
            Nombre del archivo donde se guardarán los tiempos.

    Resultados
    ----------

        times : numpy array
            Lista ordenada de los tiempos de captura.
        cells : numpy_array
            Celda en donde se produjo la captura. Sirve para diferenciar
            distintos detectores.
        nps_hist : numpy array
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
    nps_hist = np.asarray(datos[:, 0], dtype='int64')
    # Cantidad de historias totales detectadas
    # num_hist_tot = np.unique(nps_hist).shape[0]
    # Tiempos del PTRAC en segundos
    times = np.asarray(datos[:, 1], dtype='float64') * 1e-8
    # Celda donde se produjo la captura
    cells = np.asarray(datos[:, 2], dtype='int64')

    # Se generan número con distribución exponencial
    beta = 1.0 / tasa
    # Genero los tiempos para cada evento de fuente
    np.random.seed(313131)
    # Tiempo para todos los eventos de fuente
    src_time_tot = np.cumsum(np.random.exponential(beta, nps))
    # Tiempo sólo para los eventos que contribuyeron en el PTRAC
    # - Esto lo comento para conservar la relación entre el tiempo generado
    # - y la histroria cuando quiero procesar neutrones y fotones
    # src_time = np.random.choice(src_time_tot, size=num_hist_tot,
    #                        replace=False)
    src_time = src_time_tot[np.unique(nps_hist)-1]
    for n, t in zip(np.unique(nps_hist), src_time):
        indx_min = np.searchsorted(nps_hist, n, side='left')
        indx_max = np.searchsorted(nps_hist, n, side='right')
        times[indx_min:indx_max] += t

    # Ordeno los tiempos y mantengo asociado el numero de historia y la celda
    _temp = np.stack((nps_hist, times, cells), axis=-1)
    # Ordeno para tiempos crecientes
    _temp_sorted = _temp[_temp[:, 1].argsort()]
    # Vuelvo a separar
    nps_hist = _temp_sorted[:, 0]
    times = _temp_sorted[:, 1]
    cells = _temp_sorted[:, 2]
    # Pongo en cero al primer pulso
    # times -= times[0]

    # Se guardan los datos del tiempo
    np.savetxt(filename, times, fmt='%.12E')

    return times, cells, nps_hist


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


def lee_nps_entrada(nombre):
    """
    Lee la cantidad de historias simuladas desde el archivo de entrada de MCNP
    """
    with open(nombre, 'r') as f:
        for line in f:
            if line.startswith('NPS'):
                return int(float(line.split()[-1]))
        print('No se pudo leer la cantidad nps del archivo: ' + nombre)


def read_PTRAC_estandar(archivo, tipo):
    """
    Función para leer archivo PTRAC estandar de MCNP

    Parametros
    ----------
        archivo : string
            Nombre del archivo que se quiere leer
        tipo : string ('asc', 'bin')
            Tipo del archivo PTRAC. ASCII o binario ('asc' o 'bin')

    """

    Nbatch = 1000
    if tipo == 'bin':
        p = Ptrac(archivo, Ptrac.BIN_PTRAC)
    elif tipo == 'asc':
        p = Ptrac(archivo, Ptrac.ASC_PTRAC)
    else:
        raise NameError('Tipo de archivo no reconocido.' +
                        'Debe ser "bin" o "asc"')

    # Se obtienen las historias
    hists = p.ReadHistories(Nbatch)

    data = []
    while hists:
        # Loop en las historias
        for h in hists:
            # Número de historia
            numero_nps = h.GetNPS().NPS()
            # Loop en los eventos
            for e in range(h.GetNumEvents()):
                event = h.GetEvent(e)
                data.append([
                              numero_nps,
                              event.Get(Ptrac.TIME),
                              int(event.Get(Ptrac.CELL)),
                              event.Type(),
                              ]
                            )

                # if event.Type() == Ptrac.SUR:
                #    print(event.Get(Ptrac.X))

        hists = p.ReadHistories(Nbatch)
    return data


if __name__ == "__main__":
    pass
