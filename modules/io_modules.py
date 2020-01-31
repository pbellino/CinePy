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
                print('-' * 50)
                # Sigue leyendo el resto
                for i in range(6):
                    header.append(f.readline().rstrip())
            else:
                print('El archivo no tiene encabezado')
                print('-' * 50)
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


def read_timestamp_list(filenames):
    lista_datos = []
    lista_header = []
    for filename in filenames:
        _a, _header = read_timestamp(filename)
        lista_datos.append(_a)
        lista_header.append(_header)
        print('Encabezado del archivo {}:'.format(filename))
        for _line in _header:
            print(_line)
        print('-' * 50)
    return lista_datos, lista_header


def read_timestamp_list_ascii(filenames):
    """
    Función para leer un archivo de timestamping en formato ascii.

    Se asume que no tiene encabezado.
    """

    data = []
    for filename in filenames:
        data.append(np.loadtxt(filename))
    return data


# ------------- Funciones para leer datos en binario --------------------------


def uint16_at(f, pos):
    f.seek(pos)
    return np.fromfile(f, dtype=np.dtype('<u2'), count=1)[0]


def int32_at(f, pos):
    f.seek(pos)
    return np.fromfile(f, dtype=np.dtype('<i4'), count=1)[0]


def uint32_at(f, pos):
    f.seek(pos)
    _data = np.fromfile(f, dtype=np.dtype('<u4'), count=1)
    if len(_data) == 0:
        return _data
    else:
        return _data[0]


def uint64_at(f, pos):
    f.seek(pos)
    return np.fromfile(f, dtype=np.dtype('<u8'), count=1)[0]


def float64_at(f, pos):
    f.seek(pos)
    return np.fromfile(f, dtype=np.dtype('<f8'), count=1)[0]


def string_at(f, pos, length):
    f.seek(pos)
    # In order to avoid characters with not utf8 encoding
    return f.read(length).decode('utf8').rstrip('\00').rstrip()

# ---------- Fin de funciones para leer datos en binario ---------------------


def read_PTRAC_CAP_bin(filename):
    """
    Función para leer el archivo binario de PTRAC para event=CAP

    Se leen los datos en el archivo binario de PTRAC cuando se especifica
    la opción event=CAP. Se escribió porque MCNPTools no admite leer los
    archivos de PTRAC para capturas.

    Fue hecho buscando los datos en el archivo, no fue probado para cualquier
    tipo de especificaciones de entrada del PTRAC. Mientras se conserven la
    cantidad de datos, tendría que funcionar igual.

    Los datos son leidos hasta que se termina el archivo.

    Parametros
    ----------

       filename : string

    Resultados
    ----------

        datos : list of list
            Cada línea se guarda como una lista de datos. La segunda columna
            corresponde a los tiempos de captura en shakes (10e-8s).

        header : list
            Encabezados y demás parámetros que se encuentran antes de los
            datos en el archivo PTRAC. Muchos de ellos no son relevantes cuando
            se utiliza PTRAC con la opción `event=CAP'.

    TODO: Aprender a hacer esto bien.

    """

    def _lee_datos_CAP(f, pos):
        """ Función para leer los datos de capturas luego del encabezado """

        data = []
        while True:
            line = []
            line.append(uint32_at(f, pos))
            # Se lee hasta llegar al final del archivo
            if not line[-1]:
                break
            else:
                pass
            line.append(float64_at(f, pos+8))
            for i in range(7):
                line.append(int32_at(f, pos+16+4*i))
            pos = f.tell() + 8
            data.append(line)
        return data

    with open(filename, 'rb') as f:
        # Lectura de las primeras tres líneas del archivo
        line1 = int32_at(f, 4)
        line2 = string_at(f, 16, 40)
        line3 = string_at(f, 64, 128)

        # Lectura de los 30 números con especificaciones de PTRAC
        ptrac_input_data = []
        f.seek(f.tell() + 8)
        for i in range(32):
            if i in [10, 21]:
                continue
            ptrac_input_data.append(float64_at(f, 200 + 8*i))
        num_variables = []

        # Lectura de los 20 números de variables
        f.seek(f.tell()+8)
        num_variables = np.fromfile(f, '<i4', count=2)
        f.seek(f.tell()+4)
        _temp1 = np.fromfile(f, '<i8', count=9)
        _temp2 = np.fromfile(f, '<i4', count=9)
        num_variables = np.append(num_variables, _temp1)
        num_variables = np.append(num_variables, _temp2)

        # Lectura de los tipos de variables
        f.seek(f.tell()+8)
        tipos_var = np.fromfile(f, '<i8', count=4)
        _temp1 = np.fromfile(f, '<i4', count=79)
        tipos_var = np.append(tipos_var, _temp1)

        header = [line1, line2, line3, ptrac_input_data,
                  num_variables, tipos_var]

        # Se leen los datos de las capturas
        pos = f.tell() + 8
        datos = _lee_datos_CAP(f, pos)

    return datos, header


def lee_tally_F8_RAD(archivo):
    """
    Lee los datos de tallies en la salida del MCNP para obtener la RAD

    Se leen las 'tally fluctuation charts' asumiendo que siempre la primera
    será de captura total sin GATE, y el resto serán con GATES y PREDELAY
    sucesivos.

    También se leen los neutrones creados en la fuente para la normalización.
    Recordar que en SDEF par=SF normalizar por neutrones y par=-SF por fisiones

    Parámetros
    ----------

        archivo : string
            Nombre del archivo de salida de MCNP

    Resultados
    ----------

       RAD_data : numpy ndarray
            Array de la tally fluctuation charts (mean, error, vov, slope, fom)
            para la distribución de alfa-Rossi.

       no_gate_data : numpy array
            Array de la tally fluctuation chart cuando no se utiliza GATE

       source_neutrons : int
            Cantidad de neutrones emitidos por fisión espontánea. Este es el
            número por el cual están normalizadas las tallies si es que se
            utilizó par=SF en la SDEF.
    """

    data = []
    with open(archivo, 'r') as f:
        for line in f:
            if line.startswith(' '*10 + 'nps'):
                tally_line = next(f).split('   ')[5:]
                for tally in tally_line:
                    data.append(tally.split())
            # Se lee los neutrones creados por fuente
            if line.startswith(' neutron creation'):
                next(f)
                next(f)
                source_neutrons = int(next(f).split()[1])

    no_gate_data = np.asarray(data[0], dtype='float64')
    RAD_data = np.asarray(data[1:], dtype='float64')
    return RAD_data, no_gate_data, source_neutrons


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
