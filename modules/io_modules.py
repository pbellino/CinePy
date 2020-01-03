#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np
import sys


def read_bin_dt(filename):
    '''
    Función para leer los archivoss grabados por el programa "intervaltime_MC"

    Cada dato es la cantidad de pulsos registrado en un dado dt.
    Los archivos más viejos no tenían encabezado, mientras que los nuevos sí.
    El formato en que está grabado es entero sin signo de 32 bits con
    codificación big-endian

    Parameters
    ----------

    filename : string
        Nombre del archivo que se quiere leer

    Returns
    -------

    a : np.array
        Datos leidos
    header: list of strings
        Encabezado el archivo

    '''

    # Tipo de dato: sin signo (por eso el 'u')
    #               32 bits (por eso el '4')
    #               'big-endian'(por eso el >)
    # https://docs.scipy.org/doc/numpy/reference/arrays.dtypes.html
    dt = np.dtype('>u4')

    # Puntos que quiero leer de datos (-1 son todos)
    nread = -1

    header = []
    try:
        with open(filename, 'rb') as f:
            # Se fija si tiene encabezado
            header.append(f.readline().rstrip())
            if header[0].startswith(b'Nombre'):
                print('El archivo tiene encabezado')
                # Sigue leyendo el resto
                for i in range(6):
                    header.append(f.readline().rstrip())
            else:
                print('El archivo no tiene encabezado')
                # El encabezado aparecerá vacío
                header = []
                # Vuelvo al comienzo del archivo
                f.seek(0, 0)
            # Continua leyendo los datos
            a = np.fromfile(f, dtype=dt, count=nread)
            # El primer dato se descarta
        return a[1:], header
    except IOError as err:
        print('No se pudo leer el archivo: ' + filename)
        raise err
    except:
        print('Se produjo un error inseperado al abrir/leer el archivo'
              + filename)
        sys.exit()


def lee_dt_encabezado(encabezado):
    """
    Lee en el encabezado el intervalo dt con que se realizó la adquisición

    """

    dt = encabezado[4].decode('utf8').rsplit(':')[-1]
    dt = np.float(dt)
    print('Intervalo de adquisición leido del encabezado es: {} s'.format(dt))
    return dt


def lee_bin_datos_dt(nombres):
    """
    Lee los datos del archivo binario y obteiene el dt del encabezado

    Parametros
    ----------
        nombres : lista de strings
            Lista con el camino y nombre del archivo a leer

    Resultados
    ----------
        result: lista de tuplas
            Cada elemento es una tupla con (datos, dt_base), siendo estos
            datos : lista de numpy array
                Datos leidos de cada archivo dado en 'nombres'
            dt_base : lista de float
                Intervalo temporal con que se hizo la medición para cada
                archivo

    """

    result = []
    for nombre in nombres:
        datos_leidos, header = read_bin_dt(nombre)
        print('-'*50)
        print('    Encabezado')
        print('-'*50)
        for line in header:
            print(line)
        print('-'*50)
        result.append((datos_leidos, lee_dt_encabezado(header)))
    return result


def lee_historias_completas(nombre):
    """
    Lee el archivo que contiene todas las historias de alfa-Feynman

    Parametros
    ----------
    nombre: string
        Camino y nombre del archivo a leer (*.dat)

    Resultados
    ----------
    vec_tamp: array numpy
        Vector temporal de los dt para alfa-Feynman
    data: ndarray numpy
        Array en 2D donde cada columna es una de las historias calculadas

    """

    try:
        with open(nombre, 'r') as f:
            # Se lee el dt
            for line in f:
                if line.startswith('# Valor de dt'):
                    dt = np.double(next(f).rstrip())
                elif line.startswith('# Número de historias'):
                    num_hist = np.uint32(next(f).rstrip())
                elif line.startswith('# Tasa de cuentas'):
                    next(f)
                    tasas = np.array(next(f).rstrip())
                    break
            # Se leen todas las historias
            data = np.loadtxt(nombre, skiprows=15)
    except IOError as err:
        print('No se pudo leer el archivo: ' + nombre)
        raise err
        sys.exit()

    # Vector temporal
    vec_temp = np.arange(0, dt * data.shape[0], dt)
    vec_temp = vec_temp + dt

    return vec_temp, data, num_hist, tasas


def lee_fey(nombre):
    """
    Lee el archivo que contiene la curva promedio y desvio de a-Feynman

    Usa la función lee_historias_completas() ya que el encabezado es similar.
    Se leen las dos columnas y se definen las variables de interés.

    Parametros
    ----------
    nombre : string
        Camino y nombre del archivo a leer (*.fey)

    Resultados
    ----------
    vec_tamp : array numpy
        Vector temporal de los dt para alfa-Feynman
    mean_Y : array numpy
        Array con el valor medio de Y(Dt)
    std_Y : array numpy
        Array con la desviación estandar del valor medio de Y(Dt)

    """
    vec_temp, data, num_hist, tasas = lee_historias_completas(nombre)
    mean_Y = data[:, 0]
    std_Y = data[:, 1]

    return vec_temp, mean_Y, std_Y, num_hist, tasas


def read_timestamp(filename):
    '''
    Función para leer los archivoss grabados por el programa "Timestamping_3C"
    (o alguna de sus versiones previas).

    Cada dato es el tiempo en que llegó un pulso respecto al comienzo de la
    adquisición.
    El tiempo está medido en unidades de pulsos de 80Mhz (periodo de 12.5ns).
    Esto es, si se registra t=2 significa que transcurrieron 12.5ns x 2 = 25ns.
    Los archivos más viejos no tenían encabezado, mientras que los nuevos sí.
    El formato en que está grabado es entero sin signo de 32 bits con
    codificación big-endian.

    Parameters
    ----------

    filename : string
        Nombre del archivo que se quiere leer

    Returns
    -------

    a : np.array con uint32
        Datos leidos
    header: list of strings
        Encabezado el archivo

    '''

    # Tipo de dato: sin signo (por eso el 'u')
    #               32 bits (por eso el '4')
    #               'big-endian'(por eso el >)
    # https://docs.scipy.org/doc/numpy/reference/arrays.dtypes.html
    dt = np.dtype('>u4')

    # Puntos que quiero leer de datos (-1 son todos)
    nread = -1

    header = []
    try:
        with open(filename, 'rb') as f:
            # Se fija si tiene encabezado
            header.append(f.readline().rstrip())
            if header[0].startswith(b'Nombre'):
                print('El archivo tiene encabezado')
                # Sigue leyendo el resto
                for i in range(6):
                    header.append(f.readline().rstrip())
            else:
                print('El archivo no tiene encabezado')
                # El encabezado aparecerá vacío
                header = []
                # Vuelvo al comienzo del archivo
                f.seek(0, 0)
            # Continua leyendo los datos
            a = np.fromfile(f, dtype=dt, count=nread)
            # Se toma t=0 con el primer pulso
            a -= a[0]
        return a, header
    except IOError as err:
        print('No se pudo leer el archivo: ' + filename)
        raise err
    except:
        print('Se produjo un error inseperado al abrir/leer el archivo'
              + filename)
        sys.exit()


if __name__ == '__main__':

    # Prueba read_bin_dt
    a, header = read_bin_dt('../datos/nucleo_01.D1.bin')
    for line in header:
        print(line)
    print('Cantidad de datos: {}'.format(len(a)))
    # 10 datos intermedios
    print(a[45000-1:45010-1])
    # Los últimos 10 datos
    print(a[-10:])

    print('-'*50)
    # Prueba lee_historia

    nombre = '../src/resultados/nucleo_01.D1.dat'
    nombre = '../src/resultados/nucleo_01.D1D2_sum.dat'
    vec_t, data, num_hist, tasas = lee_historias_completas(nombre)

    print('Tasas de cuenta: {}'.format(tasas))
    print('Número de historias: {}'.format(num_hist))
    print(vec_t)
    print(data.shape)
    print(data[:, 19])
