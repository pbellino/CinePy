#!/usr/bin/env python3

import numpy as np
import itertools
import datetime
import os
import multiprocessing as mp

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

    return agrupado_y_dt


def datos_promedio_Ti_agrupamiento(datos_x_hist, max_int):
    return [datos_x_hist // i for i in range(1, max_int + 1)]


def afey_varianza_serie(leidos, numero_de_historias, dt_maximo, **kwargs):
    """
    Metodo de alfa-Feynman aplicado variance to mean, en serie.

    Ver el DocString de "metodo_alfa_feynman" para parametros y resultados.

    """

    Y_historias = []
    for leido in leidos:
        a, dt_base = leido
        Y_historias.append(calcula_alfa_feynman(a, numero_de_historias,
                                                dt_base, dt_maximo))

    datos_totales = len(a)
    datos_x_hist = datos_totales // numero_de_historias
    max_int = int(dt_maximo / dt_base)

    M_points = datos_promedio_Ti_agrupamiento(datos_x_hist, max_int)

    return Y_historias, dt_base, M_points


def agrupa_argumentos(a, *args):
    """ Función para construir argumentos como tuplas al paralelizar """
    _lst_arg = [itertools.repeat(item) for item in args]
    return zip(a, *_lst_arg)


def afey_varianza_paralelo(leidos, numero_de_historias, dt_maximo, **kwargs):
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

    M_points = datos_promedio_Ti_agrupamiento(datos_x_hist, max_int)

    return Y_historias, dt_base, M_points


def afey_varianza_paralelo_choice(leidos, numero_de_historias, dt_maximo,
        **kwargs):
    """
    Metodo de alfa-Feynman aplicado variance to mean, en paralelo.

    Ver el DocString de "metodo_alfa_feynman" para parametros y resultados.

    """
    # Fracción de puntos que se van a tomar para el promedio
    frac = kwargs.get('fraction')

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

        # Construyo de ante-mano cuántos puntos se elijirán para cada
        # agrupamiento, basado en la fracción especificada
        M_points = []
        for i in range(1, max_int + 1):
            M_points.append(int((datos_x_hist // i) // (1. / frac )))

        # Argumento de 'agrupamiento_historia_choice' como tupla
        arg_tupla = agrupa_argumentos(historias, max_int, datos_x_hist,
                                      M_points)
        Y_historias.append(pool.map(agrupamiento_historia_choice, arg_tupla))
    return Y_historias, dt_base, M_points


def agrupamiento_historia_choice(arg_tupla):
    """
    Técnica de agrupamiento modificada para una historia

    En vez de tomar todos los intervalos sintetizados para el promedio
    se toma una muestra aleatoria. Se toma una fracción `frac` de la cantidad
    total de intervalos para cada dt_i.

    """

    historia, maximos, datos_x_hist, M_points = arg_tupla
    Y_k = []
    for i, M in zip(range(1, maximos+1), M_points):
        _partes = datos_x_hist // i
        _indice_exacto = _partes * i
        _matriz = historia[0:_indice_exacto].reshape(_partes, i)
        _intervalos = _matriz.sum(axis=1, dtype='uint32')
        _intervalos = np.random.choice(_intervalos, M, replace=False)
        Y_k.append(np.var(_intervalos, ddof=1) / np.mean(_intervalos) - 1)
    return Y_k


def afey_varianza_paralelo_skip(leidos, numero_de_historias, dt_maximo,
        **kwargs):
    """
    Metodo de alfa-Feynman aplicado variance to mean, en paralelo.

    Ver el DocString de "metodo_alfa_feynman" para parametros y resultados.

    """
    # Fracción de puntos que se van a tomar para el promedio
    corr_time = kwargs.get('corr_time')

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

        # Construyo de ante-mano cuántos puntos se elijirán para cada
        # agrupamiento, basado en la fracción especificada
        skip_points = [] # Cantidad de intervalos que salteo
        M_points = []    # Puntos promediados por cada T_i
        for i in range(1, max_int + 1):
            _skipped  = int(np.ceil(corr_time / dt_base / i))
            skip_points.append(_skipped)
            M_points.append(int((datos_x_hist // i) /( _skipped + 1)))

        # Argumento de 'agrupamiento_historia_choice' como tupla
        arg_tupla = agrupa_argumentos(historias, max_int, datos_x_hist,
                                      skip_points)
        Y_historias.append(pool.map(agrupamiento_historia_skip, arg_tupla))
    return Y_historias, dt_base, M_points


def agrupamiento_historia_skip(arg_tupla):
    """
    Técnica de agrupamiento modificada para una historia

    Se saltean intervalos al calcular el promedio para cada T_i
    """

    historia, maximos, datos_x_hist, skipped = arg_tupla
    Y_k = []
    for i, S in zip(range(1, maximos+1), skipped):
        _partes = datos_x_hist // i
        _indice_exacto = _partes * i
        _matriz = historia[0:_indice_exacto].reshape(_partes, i)
        _intervalos = _matriz.sum(axis=1, dtype='uint32')
        _intervalos = [_intervalos[k] for k in range(0, len(_intervalos), S + 1)]
        Y_k.append(np.var(_intervalos, ddof=1) / np.mean(_intervalos) - 1)
    return Y_k


def afey_varianza_paralelo_mca(leidos, numero_de_historias, dt_maximo,
                               **kwargs):
    """
    Metodo de alfa-Feynman aplicado variance to mean, en paralelo.

    Ver el DocString de "metodo_alfa_feynman" para parametros y resultados.

    """
    # Puntos que se van a saltear
    k = kwargs.get('skip_mca')
    # Método utilizado para promediar los T_i
    method_mca = kwargs.get('method_mca')

    Y_historias = []
    M_list = []
    for leido in leidos:
        a, dt_base = leido
        historias, max_int, datos_x_hist = \
            calcula_alfa_feynman_input(a, numero_de_historias, dt_base,
                                       dt_maximo)
        # Se corre con todos los procesadores disponibles
        num_proc = mp.cpu_count()
        pool = mp.Pool(processes=num_proc)
        print('Se utilizan {} procesos'.format(num_proc))

        if method_mca=='constant':
            M = datos_x_hist * 2 * (1 + k) / (max_int + 1) / (max_int + k)
            M = int(np.floor(M))
            # Se asume cantidad constante de datos por T_i
            M_points = [M for _ in range(1, max_int + 1, k+1)]
        elif method_mca=='A_over_k':
            # Se asume que la cantidad de puntos para cada T_i tiene la forma
            # funcional A/k. Se calcula el valor de A para utilizar todos los
            # intervalos temporales de cada historia
            A = datos_x_hist * (1 + k) / (max_int + k)
            M_points = [int(A/s) for s in range(1, max_int + 1, k+1)]
            # No pueden haber intervalos con un sólo dato
            if M_points[-1] == 1:
                msg = "El tiempo de cada historia es pequeño para aplicar"
                msg += " este método. Reducir la cantidad de historias"
                msg += " o reducir el dt_max (apenas) \n"
                msg += "Se sale."
                print(msg)
                quit()

        # Argumento de 'agrupamiento_historia_mca' como tupla
        arg_tupla = agrupa_argumentos(historias, max_int, datos_x_hist, k,
                M_points)
        Y_historias.append(pool.map(agrupamiento_historia_mca, arg_tupla))
    return Y_historias, dt_base, M_points


def agrupamiento_historia_mca(arg_tupla):
    """
    Método para calcular una historia sin reutilizar intervalos base, con el
    objetivo de eliminar la correlación que introduce el método de
    agrupamiento.

    Para mejorar la estdística sólo se analizan de a k intervalos dt_i

    """

    historia, maximos, datos_x_hist, k, M_points = arg_tupla

    indx = [i for i in range(1, maximos + 1, k+1)]
    start = 0
    Y_k = []
    for i, M in zip(indx, M_points):
        _matriz = historia[start:start + M*i].reshape(M, i)
        _intervalos = _matriz.sum(axis=1, dtype='uint32')
        start += i*M
        # Si quedan pocos puntos para promediar, puede que se obtenga  un valor
        # medio nulo (generalmente sólo para el primer dt)
        if np.mean(_intervalos)!=0:
            Y_k.append(np.var(_intervalos, ddof=1) / np.mean(_intervalos) - 1)
        else:
            print('Se fijó un punto con Y(tau) = 0')
            Y_k.append(0.0)
    return Y_k


def afey_covarianza_paralelo(leidos, numero_de_historias, dt_maximo, **kwargs):
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
    dt_base = leidos[0][1]  # Asumo que serán iguales, tomo arbitrariamente el det1

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

    M_points = datos_promedio_Ti_agrupamiento(datos_x_hist, max_int)

    return Y_historias, dt_base, M_points


def afey_suma_paralelo(leidos, numero_de_historias, dt_maximo, **kwargs):
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
    M_points = datos_promedio_Ti_agrupamiento(datos_x_hist, max_int)
    return [pool.map(agrupamiento_historia, arg_tupla)], dt_base, M_points


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


def ordena_tasas_encabezado(tasas, calculo):
    """
    Ordena las tasas de cuenta para ser escritas en el encabezado

    Dependiendo del método construye distintas listas ya que los encabezados
    serán distintos.

    Parametros
    ----------
        tasas : lista
            Cada elemento tiene [val_medio, std_val_medio] de cada rchivo
        calculo : string
            Tipo de cálculo para implementar alfa-Feynman

    Resultados
    ----------
        tasas_ordenadas : lista
            Dependiendo del método se ordenara el promedio y desvio
            Ejemplo: para la covarianza será
             [ [mean_D1, std_D1] ,
               [mean_D2, std_D2],
               [mean_D1, std_D1, mean_D2, std_D2]
             ]

    """
    if 'sum_' in calculo:
        # Un elemento con todos los detectores) [ [D1 D2 ....] ]
        tasas_ordenadas = [[item for sublist in tasas for item in sublist]]
    elif 'cov_' in calculo:
        # Los primeros dos detectoers (tres elementos [D1 D2 [D1 D2]])
        _tasas = tasas[0:2]
        _juntas = [item for sublist in _tasas for item in sublist]
        tasas_ordenadas = _tasas + [_juntas]
    else:
        # Tantos elementos como detectores [D1 D2 ....]
        tasas_ordenadas = tasas
    return tasas_ordenadas


def escribe_archivos_promedios(mean_Y, std_mean_Y, dt_base, calculo, num_hist,
                               tasas, nombres_archivos):
    """
    Escribe los archivos que contienen el promedio y desvio de las historias
    """

    tasas_ordenadas = ordena_tasas_encabezado(tasas, calculo)
    #header = genera_encabezados(dt_base, calculo, num_hist)
    # nombres_archivos = genera_nombre_archivos(mean_Y, calculo)
    # Para diferencia
    for j, nombre in enumerate(nombres_archivos):
        header = genera_encabezados(dt_base, calculo,
                                    num_hist, tasas_ordenadas[j])
        with open(nombre, 'w') as f:
            for line in header:
                f.write(line + '\n')
        with open(nombre, 'ab') as f:
            # Lo ordeno para que quede en dos columnas
            ordenado = [mean_Y[j], std_mean_Y[j]]
            ordenado = np.vstack(ordenado)
            np.savetxt(f, ordenado.T)
    return nombres_archivos


def escribe_archivos_completos(Y_historias, dt_base, calculo, num_hist, tasas,
                               nombres_archivos):
    """
    Escribe los archivos que contienen a todas las historias
    """

    tasas_ordenadas = ordena_tasas_encabezado(tasas, calculo)
    for j, nombre in enumerate(nombres_archivos):
        header = genera_encabezados(dt_base, calculo,
                                    num_hist, tasas_ordenadas[j])
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


def escribe_archivos_Mpoints(nombres, Mpoints):
    """
    Escribe los archivos con la cantida de daatos utilizados para el promedio
    del Ti en cada historia
    """

    for nombre in nombres:
        # Cambio la extensión para diferenciarlo del promedio
        nombre = nombre.rsplit('.', 1)[0] + '.Nk'

        header = 'Cantidad de datos utilizados para hacer estadistica ' + \
                 'con cada intervalo Ti. Se usa para corregir la ' + \
                 'funcion teorica durante el ajuste'
        np.savetxt(nombre, Mpoints, fmt='%.i', header=header)


def genera_encabezados(dt_base, calculo, num_hist, tasas):
    """ Genera el enabezado + info con el intervalo dt + cantidad de hist."""

    header_str = []
    line_1 = '# Historias completas obtenidas con el método de alfa-Feynman'
    header_str.append(line_1)
    header_str.append('#')

    diccionario_calculo = {
            'var_serie': '# Cáclulo de (var/mean - 1) en serie',
            'var_paralelo': '# Cálculo de (var_i/mean_i - 1) en paralelo',
            'var_paralelo_choice': '# Cálculo de (var_i/mean_i - 1) en ' +
                                              'paralelo usando metodo choice',
            'var_paralelo_mca': '# Cálculo de (var_i/mean_i - 1) en ' +
                                              'paralelo usando metodo mca',
            'var_paralelo_skip': '# Cálculo de (var_i/mean_i -1 en ' +
                                              'paralelo usando método skip',
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
    header_str.append('# Número de historias:')
    header_str.append('{}'.format(num_hist))
    header_str.append('# Tasa de cuentas [cps]:')
    header_str.append('# [promedio desvio_promedio ...]')
    header_str.append('{}'.format(tasas))
    header_str.append('# Cada columna es una historia')
    header_str.append('#')

    return header_str


def genera_nombre_archivos(nombres_in, lenYdt, calculo, carpeta):
    """
    Genera los nombres de los archivos donde se guardarán los datos

    Parametros
    ----------
        nombres_in : list of strings
            Nombres de los archivos que fueron leidos
        lenYdt : integer
            Cantidad de curvas Y(dt) que se calcularon
        calculo : string
            Tipo de caĺculo utilizado (var, cov o sum)
        carpeta : string
            Nombre de la carpeta donde se guardarán los resultados

   Resultados
   ----------
   _final : lista de strings
        Nombre de los archivos donde se guardaran los datos

    """

    nombres_archivos = []
    id_det = []
    for nombre in nombres_in:
        _nom = nombre.split('/')[-1]
        _nom = _nom.rsplit('.')
        id_det.append(_nom[-2])
        nombres_archivos.append(carpeta + '/' + _nom[-3])

    # Para saber si se pidió var, cov o sum
    id_calculo = calculo.split('_')[0]
    id_method = calculo.split('_')[-1]
    _final = []
    for j in range(lenYdt):
        if id_calculo == 'var':
            if id_method == 'choice':
                _final.append(nombres_archivos[j] + '.' + id_det[j]
                              + '_var_choice.fey')
            elif id_method == 'mca':
                _final.append(nombres_archivos[j] + '.' + id_det[j]
                              + '_var_mca.fey')
            elif id_method == 'skip':
                _final.append(nombres_archivos[j] + '.' + id_det[j]
                              + '_var_skip.fey')
            else:
                _final.append(nombres_archivos[j] + '.' + id_det[j]
                              + '_var.fey')
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


def metodo_alfa_feynman(leidos, numero_de_historias, dt_maximo, calculo,
                        nombres, **kwargs):
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
        'var_paralelo_mca' : similar a 'var_paralelo' pero sin reutilizar datos
            Ti para sintetizar nuevos intervalos. Reduce la correlación. Es
            necesario pasarle el dato 'skip' para dict en kwargs.
        'var_paralelo_choice' : similar a 'var_paralelo' pero tomando una
            cantidad aleatoria de intervalos Ti para calcular el promedio.
            Reduce la correlación. Es necesario pasarle el dato 'fraction' como
            dict en kwargs.
        'cov_paralelo' : Método de la covarianza en paralelo
            Sólo toma los dos primeros elementos de leidos
        'sum_paralelo' : Suma los datos de todos los detectores
            Sumo todos los datos de leidos

    nombres : list of strings
        Lista con los nombres de archivos leidos. Se utiliza para generaar los
        archivos con los resultados del procesamiento

    kwargs : dictionary
        kwargs['skip_mca'] : int
            Cantidad de intervalos que se saltean cuando se usa el método _mca.
            Se lo utiliza para tener una mejor estadística en los resultados
            cuando se quiere reducir la correlación. Valores muy chicos hacen
            que sea necesaario medir durante más tiempo.
        kwargs['method_mca'] : str ('contant', 'A_over_k')
            String para identificar la forma en que se tomarán los intervalos.
                'constant' : misma cantidad de puntos para cada T_i
                'A_over_k' : se toman más punos para los primeros T_i.
            En ambos casos se calcula el máximo valor del parámetro (M ó A)
            para aprovechar todos los intervalos T_i por historia.
        kwargs['fraction'] : float
            Fracción de los datos que se seleccionarán al calcular el promedio
            para cada Ti al utilizar el método _choice.
            Cuanto más chico menor correlación en los datos a expensas de
            empeorar la estadística.
        kwargs['corr_time'] : float
        kwargs['carpeta_resultados'] : str ("resultados_afey" default)
            Nombre de la carpeta donde se guardarán los resultados

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
            'var_paralelo_choice': afey_varianza_paralelo_choice,
            'var_paralelo_mca': afey_varianza_paralelo_mca,
            'var_paralelo_skip': afey_varianza_paralelo_skip,
            'cov_paralelo': afey_covarianza_paralelo,
            'sum_paralelo': afey_suma_paralelo,
                      }
    fun_seleccionada = diccionario_afey.get(calculo)
    if fun_seleccionada is None:
        print('El calculo "{}" solicitado no está implementado'.format(calculo))
        print('Se sale del programa')
        quit()
    else:
        if calculo == 'var_paralelo_choice':
            if kwargs.get('fraction') is None:
                _msg = "Para calcular con el método {} es necesario "
                _msg += "incluir el argumento 'fraction' como diccionario \n"
                _msg += "Se sale del programa"
                print(_msg.format(calculo))
                quit()
        elif calculo == 'var_paralelo_mca':
            if kwargs.get('skip_mca') is None:
                _msg = "Para calcular con el método {} es necesario "
                _msg += "incluir el argumento 'skip' como diccionario \n"
                _msg += "Se sale del programa"
                print(_msg.format(calculo))
                quit()
            if kwargs.get('method_mca') is None:
                _msg = "Para calcular con el método {} es necesario "
                _msg += "incluir el argumento 'method_mca' como diccionario \n"
                _msg += "Los  valores posibles son 'constant' ó 'A_over_k' \n"
                _msg += "Se sale del programa"
                print(_msg.format(calculo))
                quit()

        elif calculo == 'var_paralelo_skip':
            if kwargs.get('corr_time') is None:
                _msg = "Para calcular con el método {} es necesario "
                _msg += "incluir el argumento 'corr_time' como diccionario \n"
                _msg += "Se sale del programa"
                print(_msg.format(calculo))
                quit()

        Y_historias, dt_base, M_points = \
                fun_seleccionada(leidos, numero_de_historias, dt_maximo,
                                 **kwargs)

        # Agrego la info de tasa de cuentas para ser grabada en el encabezado
        # Servirá para hacer correcciones en los parámetros estimados (por
        # ejemplo en el tiempo muerto).
        # Es un parche que se hizo a último momento. Se tendría que hacer
        # más prolijo reescribiendo toda las funciones con esto en mente
        def _tasa_de_cuentas(leidos):
            """ Calcula la tasa de cuentas promedio de cada medición """

            _tasas = []
            for leido in leidos:
                # Tasa promedio
                _prom = np.mean(leido[0]) / leido[1]
                # Desvío del promedio
                _desvio = np.std(leido[0], ddof=1) / leido[1] \
                    / np.sqrt(len(leido[0]))
                _tasas.append([_prom, _desvio])
            return _tasas

        tasas = _tasa_de_cuentas(leidos)

        carpeta = kwargs.get('carpeta_resultados', 'resultados_afey')
        if not os.path.exists(carpeta): os.makedirs(carpeta)
        # Se generan los nombres de los archivos para guardar los datos
        nom_archivos = genera_nombre_archivos(nombres, len(Y_historias),
                                              calculo, carpeta)

        # Escribe todas las historias
        escribe_archivos_completos(Y_historias, dt_base, calculo,
                                   numero_de_historias, tasas, nom_archivos)
        # Calcula estadistica sobre historias
        promedio, desvio = promedia_historias(Y_historias)
        # Escribe promedios y desvios
        escribe_archivos_promedios(promedio, desvio, dt_base, calculo,
                                   numero_de_historias, tasas, nom_archivos)
        # Escribe la cantidad de puntos utilizados para el promedio de cada Ti
        escribe_archivos_Mpoints(nom_archivos, M_points)

        return Y_historias


if __name__ == '__main__':

    """
    Ejemplo para recordar cómo usar estos módulos

    No está penasdo para que funcione, los inputs no están disponibles
    """

    import time

    # -------------------------------------------------------------------------
    # Parámetros de entrada
    # -------------------------------------------------------------------------
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
    # -------------------------------------------------------------------------
    # Lectura y agrupamiento
    leidos = wrapper_lectura(nombres, int_agrupar)
    # -------------------------------------------------------------------------

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
