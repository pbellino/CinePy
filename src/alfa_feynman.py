#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np
import itertools
import datetime
import os

import sys
sys.path.append('../')

from modules.io_modules import lee_bin_datos_dt
from modules.estadistica import agrupa_datos


def calcula_alfa_feynman_input(datos, numero_de_historias, dt_base, dt_maximo):
    """
    Genera la lista con historias y parámetros para la técnica de agrupamiento
    """

    print('='*50)
    print('    Parámetros del método alfa-Feynman')
    print('='*50)
    print('*Datos de entrada:')
    print('\tNúmero de historias: {}'.format(numero_de_historias))
    print('\tInervalo temporal de los datos: {} s'.format(dt_base))
    print('\tIntervalo temporal máximo de cada historia: {} s'.format(dt_maximo))
    print('*Datos derivados:')
    datos_totales = len(datos)
    print('\tDatos totales: {}'.format(datos_totales))
    datos_por_historia = datos_totales // numero_de_historias
    print('\tDatos por historia: {}'.format(datos_por_historia))
    maximos_int_para_agrupar = int(dt_maximo / dt_base)
    print('\tNumero máximo de intervalos para agrupar: {}'.format(maximos_int_para_agrupar))
    print('='*50)

    def _datos_por_intervalo(datos_por_historia, maximos_int_para_agrupar):
        """
        Dato usados para hacer estadística para cada intervalo agrupado

        Para ser usado como corrección en el ajuste teórico. Como esto se
        agregó la final, los datos son guardados en un archivo con
        extensión *.Nk. El nombre de dicho archivo se lee del archivo
        "archivos_leidos.tmp". Se graba uno para cada detector, aunque en
        verdad son los mismos datos. Esto es por si en un futuro se necesita
        diferenciarlos

        """
        N_k = [datos_por_historia // i for i in
               range(1, maximos_int_para_agrupar + 1)]
        nombres_archivos = []
        with open('archivos_leidos.tmp', 'r') as f:
            for line in f:
                _nom = line.split('/')[-1]
                _nom = _nom.rsplit('.', 1)
                nombres_archivos.append('resultados/' + _nom[-2] + '.Nk')
        header = u'Cantidad de datos utilizados para hacer estadística ' + \
                 u'con cada intervalo dt.\ne usa para corregir la ' + \
                 u'función teórica durante el ajuste'
        for nombre in nombres_archivos:
            np.savetxt(nombre, N_k, fmt='%.i', header=header)

        return None

    _datos_por_intervalo(datos_por_historia, maximos_int_para_agrupar)

    # Se dividen todos los datos en historias
    historias = np.split(datos[0:datos_por_historia*numero_de_historias],
                         numero_de_historias)
    return historias, maximos_int_para_agrupar, datos_por_historia


def agrupamiento_historia_cov(arg_tupla):
    """ Técnica de agrupamientto para el método de la covarianza """

    historia, maximos, datos_x_hist = arg_tupla
    det1 = historia[0]
    det2 = historia[1]
    Y_k1 = []
    Y_k2 = []
    Y_k12 = []
    for i in range(1, maximos+1):
        _partes = datos_x_hist // i
        _indice_exacto = _partes * i
        _matriz1 = det1[0:_indice_exacto].reshape(_partes, i)
        _matriz2 = det2[0:_indice_exacto].reshape(_partes, i)
        _intervalos1 = _matriz1.sum(axis=1, dtype='uint32')
        _intervalos2 = _matriz2.sum(axis=1, dtype='uint32')
        _cov = np.cov(_intervalos1, _intervalos2)
        Y_k1.append(_cov[0, 0] / np.mean(_intervalos1) - 1)
        Y_k2.append(_cov[1, 1] / np.mean(_intervalos2) - 1)
        Y_k12.append(_cov[0, 1] / np.sqrt(np.mean(_intervalos1)
                                          * np.mean(_intervalos2)))
    return Y_k1, Y_k2, Y_k12


def agrupamiento_historia(arg_tupla):
    """ Técnica de agrupamiento para una historia """

    historia, maximos, datos_x_hist = arg_tupla
    Y_k = []
    for i in range(1, maximos+1):
        _partes = datos_x_hist // i
        _indice_exacto = _partes * i
        _matriz = historia[0:_indice_exacto].reshape(_partes, i)
        _intervalos = _matriz.sum(axis=1, dtype='uint32')
        Y_k.append(np.var(_intervalos, ddof=1) / np.mean(_intervalos) - 1)
    return Y_k


def calcula_alfa_feynman(datos, numero_de_historias, dt_base, dt_maximo):
    """
    Método de alfa-Feynman con la técnica de agrupamiento. En serie.

    """
    # Se generan historias y datos para la técnia de agrupamiento
    historias, maximos_int_para_agrupar, datos_por_historia =  \
        calcula_alfa_feynman_input(datos, numero_de_historias, dt_base,
                                   dt_maximo)
    # Se aplica la técnica de agrupamiento
    Y_historias = []
    for j, historia in enumerate(historias):
        Y_k = agrupamiento_historia((historia, maximos_int_para_agrupar,
                                     datos_por_historia))
        Y_historias.append(Y_k)
        print('Historia: {}'.format(j+1))
    return Y_historias


def wrapper_lectura(nombres, int_agrupar):
    """
    Función para leer los datos y agrupar intervalos

    También escribe el archivo 'archivos_leidos.tmp' con los nombres de los
    archivos leidos 'nombre'.

    Parametros
    ----------
    nombre : lista de strings
        El camino y nombre de los archivos para leer
    int_agrupar : entero
        Cantidad de datos que se quieren agrupar antes del procesamiento

    Resultados
    ----------
    agrupado_y_dt: lista de tuplas
        Por cada archivo leido se obtiene una tupla con
        (datos_agrupados, dt_agrupado) donde
        datos_agrupados : lista de array numpy
            Array con los datos leidos de cuentas en cada dt,
            y agrupados en "int_agrupar" intervalos consecutivos.
        dt_agrupado : float
            dt de cada intervalo luego de agrupar
            dt_agrupado = (dt_base * int_agrupar )

    """
    def _escribe_nombres_leidos(nombres):
        """ Escribe los nombres de los archivos leidos """

        filename = 'archivos_leidos.tmp'
        try:
            os.remove(filename)
        except OSError:
            pass
        with open(filename, 'a') as f:
            for nombre in nombres:
                f.write(nombre + '\n')

    _results = lee_bin_datos_dt(nombres)

    # Tamaños de los datos adquiridos
    tamanos = [len(result[0]) for result in _results]
    # Busco el tamaño mínimo para unificar el tamaño del resto
    tamano_minimo = np.min(tamanos)

    agrupado_y_dt = []
    for dato, dt in _results:
        # Todos tendrán el mismo tamaño (obligatorio para calcular cov)
        dato = dato[0:tamano_minimo]
        # Se agrupan los datos originales de la adquisición
        agrupado_y_dt.append(agrupa_datos(dato, int_agrupar, dt))

    _escribe_nombres_leidos(nombres)
    return agrupado_y_dt


def afey_varianza_serie(leidos, numero_de_historias, dt_maximo):
    """
    Metodo de alfa-Feynman aplicado variance to mean, en serie.

    Ver el DocString de "metodo_alfa_feynman" para parametros y resultados.

    """

    Y_historias = []
    for leido in leidos:
        a, dt_base = leido
        Y_historias.append(calcula_alfa_feynman(a, numero_de_historias,
                                                dt_base, dt_maximo))
    return Y_historias, dt_base


def agrupa_argumentos(a, b, c):
    """ Función para construir argumentos como tuplas al paralelizar """
    return zip(a, itertools.repeat(b), itertools.repeat(c))


def afey_varianza_paralelo(leidos, numero_de_historias, dt_maximo):
    """
    Metodo de alfa-Feynman aplicado variance to mean, en paralelo.

    Ver el DocString de "metodo_alfa_feynman" para parametros y resultados.

    """

    Y_historias = []
    for leido in leidos:
        a, dt_base = leido
        historias, max_int, datos_x_hist = \
            calcula_alfa_feynman_input(a, numero_de_historias, dt_base,
                                       dt_maximo)
        # Se corre con todos los procesadores disponibles
        num_proc = mp.cpu_count()
        pool = mp.Pool(processes=num_proc)
        print('Se utilizan {} procesos'.format(num_proc))
        # Argumento de 'agrupamiento_historia' como tupla
        arg_tupla = agrupa_argumentos(historias, max_int, datos_x_hist)
        Y_historias.append(pool.map(agrupamiento_historia, arg_tupla))
    return Y_historias, dt_base


def afey_covarianza_paralelo(leidos, numero_de_historias, dt_maximo):
    """
    Metodo de alfa-Feynman aplicado la covarianza entre detectores, en paralelo.

    Solo se toman los primeros dos elementos de leidos.

    Ver el DocString de "metodo_alfa_feynman" para parametros y resultados.

    """

    if len(leidos) < 2:
        print('='*50)
        print('Para calcular la covarianza se necesita especifiar dos detectores')
        print('Se sale del programa')
        print('='*50)
        quit()
    elif len(leidos) > 2:
        print('='*50)
        print('Se calcula la covarianza con los primeros dos archivos especificados')
        print('='*50)

    # Daatos de ambos detectores
    datos = [leido[0] for leido in leidos]
    dt_base = leidos[0][1] # Asumo que serán iguales, tomo arbitrariamente el det1

    hist1, max_int, datos_x_hist = \
        calcula_alfa_feynman_input(datos[0], numero_de_historias, dt_base,
                                   dt_maximo)
    hist2, max_int, datos_x_hist = \
        calcula_alfa_feynman_input(datos[1], numero_de_historias, dt_base,
                                   dt_maximo)
    historias = zip(hist1, hist2)

    arg_tupla = agrupa_argumentos(historias, max_int, datos_x_hist)
    # Se corre con todos los procesadores disponibles
    num_proc = mp.cpu_count()
    pool = mp.Pool(processes=num_proc)
    print('Se utilizan {} procesos'.format(num_proc))
    _Y_det = pool.map(agrupamiento_historia_cov, arg_tupla)
    # Ordeno salida para obtener una lista de Y similar a los otros casos
    # [Y_var1, Y_var2, Y_cov12]
    Y_historias = []
    for i in range(3):
        Y_historias.append(np.array(_Y_det)[:, i, :])
    return Y_historias, dt_base


def afey_suma_paralelo(leidos, numero_de_historias, dt_maximo):
    """
    Metodo de alfa-Feynman aplicado a la suma de detectores, en paralelo.

    Se suman los elementos de leidos

    Ver el DocString de "metodo_alfa_feynman" para parametros y resultados.

    """

    historias = []
    for leido in leidos:
        a, dt_base = leido
        _hist, max_int, datos_x_hist = \
            calcula_alfa_feynman_input(a, numero_de_historias, dt_base,
                                       dt_maximo)
        historias.append(_hist)

    historias = np.array(historias)
    # Se suman las historias de los detectores
    historias_sumadas = np.sum(historias, axis=0)
    num_proc = mp.cpu_count()
    pool = mp.Pool(processes=num_proc)
    print('Se utilizan {} procesos'.format(num_proc))
    arg_tupla = agrupa_argumentos(historias_sumadas, max_int, datos_x_hist)
    # Lo pongo comom lista de un elemento para homogenizar el formato
    return [pool.map(agrupamiento_historia, arg_tupla)], dt_base


def promedia_historias(Y_historias):
    """
    Hace estadística sobre todas las historias para cada detector

    Calcula el valor medio y la desviación estandar del valor medio como
        sig_mean(Y) = sig(Y) / sqrt(N)

    Parametros
    ----------
        Y_historias : lista de numpy ndarray
            Un array por cada detector. La estadistica se realiza sin
            iterar sobre los elementos, usando axis=1.
    Resultados
    ----------
        mean_Y_historias : numpy ndarray
            Valor medio de Y_historias para cada detector
        std_mean_Y_historias : numpy ndarray
            Desviación estandar del promedio para cada detector

    """

    mean_Y_historias = np.mean(Y_historias, axis=1)
    std_mean_Y_historias = np.std(Y_historias, axis=1, ddof=1) / \
        np.sqrt(np.shape(Y_historias)[1])
    return mean_Y_historias, std_mean_Y_historias


def escribe_archivos_promedios(mean_Y, std_mean_Y, dt_base, calculo):
    """
    Escribe los archivos que contienen el promedio y desvio de las historias
    """

    header = genera_encabezados(dt_base, calculo)
    nombres_archivos = genera_nombre_archivos(mean_Y, calculo)
    # Para diferencia
    for j, nombre in enumerate(nombres_archivos):
        with open(nombre, 'w') as f:
            for line in header:
                f.write(line + '\n')
        with open(nombre, 'ab') as f:
            # Lo ordeno para que quede en dos columnas
            ordenado = [mean_Y[j], std_mean_Y[j]]
            ordenado = np.vstack(ordenado)
            np.savetxt(f, ordenado.T)


def escribe_archivos_completos(Y_historias, dt_base, calculo):
    """
    Escribe los archivos que contienen a todas las historias
    """

    header = genera_encabezados(dt_base, calculo)
    nombres_archivos = genera_nombre_archivos(Y_historias, calculo)
    # Para diferencia
    for j, nombre in enumerate(nombres_archivos):
        # Cambio la extensión para diferenciarlo del promedio
        nombre = nombre.rsplit('.', 1)[0] + '.dat'
        # nombre = nombre+'.gz'
        with open(nombre, 'w') as f:
            for line in header:
                f.write(line + '\n')
        with open(nombre, 'ab') as f:
            np.savetxt(f, np.array(Y_historias[j]).T)
        # TODO: se puede guardar comprimido, pero no es fácil hacer append
        # np.savetxt(_nombre, np.array(Y_historia).T)


def genera_encabezados(dt_base, calculo):
    """ Genera el enabezado + info con el intervalo dt """

    header_str = []
    line_1 = '# Historias completas obtenidas con el método de alfa-Feynman'
    header_str.append(line_1)
    header_str.append('#')

    diccionario_calculo = {
            'var_serie': '# Cáclulo de (var/mean - 1) en serie',
            'var_paralelo': '# Cálculo de (var_i/mean_i - 1) en paralelo',
            'cov_paralelo': '# Cálculo de [cov_12/sqrt(mean_1*mean_2)] en paralelo',
            'sum_paralelo': '# Cálculo de (var/mean - 1) sumando detectores en paralelo',
                      }
    header_str.append(diccionario_calculo.get(calculo))
    header_str.append('#')
    # Fecha y hora
    now = datetime.datetime.now()
    now_str = now.strftime(now.strftime("%d-%m-%Y %H:%M"))
    header_str.append('# Fecha de procesamiento: {}'.format(now_str))
    header_str.append('#')
    header_str.append('# Valor de dt [s]:')
    header_str.append('{}'.format(dt_base))
    header_str.append('#')
    header_str.append('# Cada columna es una historia')
    header_str.append('#')

    return header_str


def genera_nombre_archivos(Y_historias, calculo):
    """
    Genera los nombres de los archivos donde se guardarán los datos

    Parametros
    ----------
        Y_historia : lista de numpy array
            Se lo utiliza solamente para contar la cantidad de curvas Y(dt)
            que se calcularon
            TODO: Se puede pasar directamente len(Y_historias)
        calculo : string
            Tipo de caĺculo utilizado (var, cov o sum)

   Resultados
   ----------
   _final : lista de strings
        Nombre de los archivos donde se guardaran los datos

    """

    # Se guardan en la carpeta 'resultados'
    # Se crea si no existe
    directorio = 'resultados'
    if not os.path.exists(directorio):
        os.makedirs(directorio)
    # Lee el archivo donde se guardaron los nombres (wrapper_lectura)
    nombres_archivos = []
    id_det = []
    with open('archivos_leidos.tmp', 'r') as f:
        for line in f:
            _nom = line.split('/')[-1]
            _nom = _nom.rsplit('.')
            id_det.append(_nom[-2])
            nombres_archivos.append(directorio + '/' + _nom[-3])
    # Para saber si se pidió var, cov o sum
    id_calculo = calculo.split('_')[-2]
    _final = []
    for j in range(len(Y_historias)):
        if id_calculo == 'var':
            _final.append(nombres_archivos[j] + '.' + id_det[j] + '.fey')
        elif id_calculo == 'cov':
            if j != 2:
                _final.append(nombres_archivos[j] + '.' + id_det[j]
                              + '_cov.fey')
            elif j == 2:
                _final.append(nombres_archivos[0] + '.' + ''.join(id_det[0:2])
                              + '_cov.fey')
        elif id_calculo == 'sum':
            _final.append(nombres_archivos[0] + '.' + ''.join(id_det)
                          + '_sum.fey')
        else:
            print('No se reconoce el cálculo')
    return _final


def metodo_alfa_feynman(leidos, numero_de_historias, dt_maximo, calculo):
    """
    Función principal para el método de alfa Feynman

    Aplica el método de alfa-Feynman con agrupamiento. Permite aplicar
    el método de la varianza como la covarianza. También suma distintos
    detectores.
    Se paralelizó con el paquete multirpocessig, donde se toman todos los
    threads dispnibles de la PC.

    Limitaciones: se asume que "leidos" proviene de una misma medición, por
    lo cual los parámetros del método son similares para todos los detectores

    Parametros
    ----------
    leidos : lista de numpy array
        Cada array corresponde a un detector y contiene los pulsos detectados
        en cada intervalo dt (continuos). Si se quiere, previamente se pueden
        reagrupar intervalos.

    numero_de_historias : entero
        Cantidad de historias en que se dividirán los datos "leidos"

    dt_maximo: float
        dt máximo que se quiere alcanzar. Es el útlimo punto de la curva
        de Y(dt) vs dt

    calculo : string
        Indica el tipo de cálculo que se quiere hacer
        'var_serie' : Método variance to mean en serie
            A cada elemento de leidos.
        'var_paralelo' : Método variance to mean paralelo
            A cada elemento de leídos
        'cov_paralelo' : Método de la covarianza en paralelo
            Sólo toma los dos primeros elementos de leidos
        'sum_paralelo' : Suma los datos de todos los detectores
            Sumo todos los datos de leidos

   Resultados
   ----------
    Y_historias : Lista de numpy array
        Cada elemento de la lista es un array de
        (numero_de_historias x numero_datos_por_historia)
        La cantidad de elementos depederá del calculo realizado:
        'var_serie' : Un elemento por cada detector
        'var_paralelo' : Un elemento por cada detector
        'cov_paralelo' : Tres elementos [Y(var1) Y(var2) Y(cov12)]
        'sum_paralelo' : Un elemento
    """

    diccionario_afey = {
            'var_serie': afey_varianza_serie,
            'var_paralelo': afey_varianza_paralelo,
            'cov_paralelo': afey_covarianza_paralelo,
            'sum_paralelo': afey_suma_paralelo,
                      }
    fun_seleccionada = diccionario_afey.get(calculo)
    if fun_seleccionada is None:
        print('El calculo "{}" solicitado no está implementado'.format(calculo))
        print('Se sale del programa')
        quit()
    else:
        Y_historias, dt_base = fun_seleccionada(leidos, numero_de_historias,
                                                dt_maximo)
        # Escribe todas las historias
        escribe_archivos_completos(Y_historias, dt_base, calculo)
        # Calcula estadistica sobre historias
        promedio, desvio = promedia_historias(Y_historias)
        # Escribe promedios y desvios
        escribe_archivos_promedios(promedio, desvio, dt_base, calculo)
        return Y_historias


if __name__ == '__main__':

    import multiprocessing as mp
    import time

    # ---------------------------------------------------------------------------------
    # Parámetros de entrada
    # ---------------------------------------------------------------------------------
    # Archivos a leer
    nombres = [
              '../datos/nucleo_01.D1.bin',
              '../datos/nucleo_01.D2.bin',
              ]
    # Intervalos para agrupar los datos adquiridos
    int_agrupar = 5
    # Técnica de agrupamiento
    numero_de_historias = 100  # Historias que se promediarán
    dt_maximo = 50e-3          # másimo intervalo temporal para cada historia
    # ---------------------------------------------------------------------------------
    # Lectura y agrupamiento
    leidos = wrapper_lectura(nombres, int_agrupar)
    # ---------------------------------------------------------------------------------

    calculos = [
                'var_serie',
                'var_paralelo',
                'cov_paralelo',
                'sum_paralelo',
                'pirulo',
                ]

    for calculo in calculos:
        t0 = time.time()
        Y_historias = metodo_alfa_feynman(leidos, numero_de_historias,
                                          dt_maximo, calculo)
        tf = time.time()
        print('Tiempo para {}: {} s'.format(calculo, tf-t0))
        for Y_historia in Y_historias:
            print(np.array(Y_historia)[9, :])
