#!/usr/bin/env python3

import numpy as np
import sys
import re


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
    tasas: ndarray numpy
        Tasa de cuenta promedio y su desvío

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
                    tasas = next(f).rstrip()
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

    # Convierto a numpy array
    tasas = np.asarray(tasas[1:-1].split(','), dtype=float)

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
    tasas : array numpy
        Tasa de cuenta promedio y su desvío

    """
    vec_temp, data, num_hist, tasas = lee_historias_completas(nombre)
    mean_Y = data[:, 0]
    std_Y = data[:, 1]

    return vec_temp, mean_Y, std_Y, num_hist, tasas


def read_timestamp(filename, common_time=False):
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

    Por default, los tiempos comienzan en cero. Si esto no es lo que se quiere,
    se puede utilizar common_time=True para mostrar los tiempos comunes (en
    caso de que se mida con más de un detector y se necesite un tiempo común
    entre ambos).

    Parameters
    ----------

    filename : string
        Nombre del archivo que se quiere leer
    common_time: boolean
        Si es falso, a todos los valores temporales se le resta el tiempo de
        llegada del primer pulso. Si es verdadero, no.

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
            # Se toma t=0 con el primer pulso en caso de usar common_time=False
            if not common_time: a -= a[0]
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


def read_val_teo(name):
    """
    Función para leer archivo con vaores teóricos de la simulación realizada en
    octave.

    Son valores teóricos basados en los parámetros de entrada, no en valores
    calculados durante la simulación.

    Parametros
    ----------
        name : string
        Nombre del archivo para leer

    Resultados
    ----------
        lst : dictionary
            Diccionario con las claves que aparecen en el archivo y sus valores

    """

    lst = []
    with open(name, 'r') as f:
        for line in f:
            key, val = line.split(':')
            lst.append((key, float(val)))
    return dict(lst)


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

# ------------- Funciones para leer archivos de MCNP  -------------------------


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

    Se optimizó la función para que lea líneas completas, en lugar de número
    por número. Redujo el tiempo de lectura casi en un factor 10x. Se podría
    seguir optimizando si fuera muy necesario. Lo único optimizado fue la
    función interna '_lee_datos_CAP()'.

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
        # Formato de una línea del archivo PTRAC con F8+CAP
        dt7 = np.dtype("<u8, <f8, <i4, <u4, <u4, <u4, <u4, <u4, <u4")
        # Al final de cada línea hay un caracter ¿salto de línea? que también
        # se podría incluir. Es problemático en la última línea, porque dicho
        # caracter no está y devuelve un array vacío.
        # dt7 = np.dtype("<u8, <f8, <u4, <u4, <u4, <u4, <u4, <u4, <u4, <u8")
        pp = 'aa'  # Cualquier cosa que tenga len() distinto de cero
        f.seek(pos)
        while len(pp):
            # Leo los siete números de cada captura
            pp = np.fromfile(f, dtype=dt7, count=1)
            # Salteo el final de línea
            f.seek(f.tell() + 8)
            # Lo guardo como lista
            data.append(list(*pp))
        # Como la última línea está vacía, la quito
        data.pop()
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
        # Sumando puedo obtener la cantidad de variables que
        # se deben leer en el próximo paso
        sum_num_var = np.sum(num_variables[0:11])
        # Indica el ID de la partícula
        # (=0 si es un problema con más de una partícula, y esta info se
        # agrega dentro de las líneas de cada evento)
        tipo_particula = num_variables[11]
        # El valor #13 siempre debe valer cuatro
        assert num_variables[12] == 4, 'Falla en lectura de encabezado'

        # Lectura de los tipos de variables
        f.seek(f.tell()+8)
        tipos_var = np.fromfile(f, '<i8', count=4)
        _temp1 = np.fromfile(f, '<i4', count=sum_num_var-4)
        tipos_var = np.append(tipos_var, _temp1)

        header = [line1, line2, line3, ptrac_input_data,
                  num_variables, tipos_var, tipo_particula]

        # Se leen los datos de las capturas
        pos = f.tell() + 8
        datos = _lee_datos_CAP(f, pos)

    return datos, header


def read_PTRAC_CAP_bin_obsoleta(filename):
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
        # Sumando puedo obtener la cantidad de variables que
        # se deben leer en el próximo paso
        sum_num_var = np.sum(num_variables[0:11])
        # Indica el ID de la partícula
        # (=0 si es un problema con más de una partícula, y esta info se
        # agrega dentro de las líneas de cada evento)
        tipo_particula = num_variables[11]
        # El valor #13 siempre debe valer cuatro
        assert num_variables[12] == 4, 'Falla en lectura de encabezado'

        # Lectura de los tipos de variables
        f.seek(f.tell()+8)
        tipos_var = np.fromfile(f, '<i8', count=4)
        _temp1 = np.fromfile(f, '<i4', count=sum_num_var-4)
        tipos_var = np.append(tipos_var, _temp1)

        header = [line1, line2, line3, ptrac_input_data,
                  num_variables, tipos_var, tipo_particula]

        # Se leen los datos de las capturas
        pos = f.tell() + 8
        datos = _lee_datos_CAP(f, pos)

    return datos, header


def read_PTRAC_CAP_asc(filename):
    """
    Función para leer el archivo ascii de PTRAC para event=CAP

    Leer docstring de `read_PTRAC_CAP_bin` para más información. Tiene
    el mismo formato (salvo la resolución temporal).
    """
    data = []
    header = []
    with open(filename, 'r') as f:
        # Se lee encabezado
        for _ in range(10):
            header.append(f.readline().rstrip())
        # Se leen datos
        for line in f:
            # Eventos que aparecen como '0' en lugar de la celda
            if line.split()[2] == '0':
                pass
            else:
                _dat_str = line.split()
                _data_num = [int(_dat_str[0]), float(_dat_str[1])]
                _data_num.extend(list(map(int, _dat_str[2:])))
                data.append(_data_num)
    return data, header


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
                # _separados = next(f).split()[1:]
                _separados = next(f)
                _tmp_line = _separados
                while _tmp_line.startswith('    '):
                    _separados = _tmp_line
                    _tmp_line = next(f)
                _separados = _separados.split()[1:]
                _n_t = int(len(_separados) / 5)
                for i in range(_n_t):
                    data.append(_separados[i*5:5*(i+1)])
            # Se lee los neutrones creados por fuente
            if line.startswith(' neutron creation'):
                next(f)
                next(f)
                source_neutrons = int(next(f).split()[1])

    no_gate_data = np.asarray(data[0], dtype='float64')
    RAD_data = np.asarray(data[1:], dtype='float64')
    return RAD_data, no_gate_data, source_neutrons


def lee_tallies(archivo):
    """
    Lee los datos de las tallies del archivo de salida de MCNP

    Se leen las 'tally fluctuation charts' en el orden en que aparecen las
    tallies. También busca valor de partículas generadas por fuente.

    Parametros
    ----------

        archivo : string
            Nombre del archivo de salida de MCNP

    Resultados
    ---------

        data : numpy ndarray
            Array de la tally fluctuation chart (mean, error, vov, slope, fom)

        nps : int
            Valores de nps que se utilizí en la corrida

        source_neutrons : int
            Cantidad de partículas generadas por la fuente (puede no coincidir
            con nps (por ejemplo, en fisiones espontáneas)
    """

    data = []
    with open(archivo, 'r') as f:
        for line in f:
            # Busca el comienzo de las TFC
            if line.startswith(' '*10 + 'nps'):
                _separados = next(f)
                _tmp_line = _separados
                while _tmp_line.startswith('    '):
                    _separados = _tmp_line
                    _tmp_line = next(f)
                # Se lee el valor de nps
                nps = int(_separados.split()[0])
                # Se lee el resto del renglón
                _separados = _separados.split()[1:]
                # De cuentan la cantidad de tallies
                _n_t = int(len(_separados) / 5)
                # Se guardan los valores de cada tally
                for i in range(_n_t):
                    data.append(_separados[i*5:5*(i+1)])
            # Se lee los neutrones creados por fuente
            if line.startswith(' neutron creation'):
                next(f)
                next(f)
                source_neutrons = int(next(f).split()[1])
    return data, nps, source_neutrons


def lee_tally_E_card(archivo):
    """
    Función para leer los datos al utilizar la tarjeta e en un tally de MCNP

    Se hace una búsqueda de la palabra '1tally' seguidoa de 'nps'. De leen
    todas las tallies del archivo

    Parámetros
    ----------
    archivo : string
        Nombre del archivo de salida de MCNP

    Resultados
    ----------
    datos : dictionary
        Diccionario donde cada clave es un string con el número del tally, y el
        valor es un ndarray de numpy con [energia valor error_rel].
    bins : dictionary
        Diccionario donde cada clave es un string con el número del tally, y el
        valor es un ndarray con [valor_bin_inferior valor_bin_superior]
    nombres : list of strings
        Lista con strings correspondientes a cada tally leída. Sólo para
        debuggear. Deben coincidir con los keys del diccionario 'datos'.
    """

    nombres = []
    datos = {}
    bins = {}
    with open(archivo, 'r') as f:
        for line in f:
            if line.startswith('1tally'):
                line_sep = line.split()
                # Lee los resultados de las tallies
                if line_sep[2] == 'nps':
                    _tally_n = line_sep[1]
                    nombres.append(_tally_n)
                    _un_tally = []
                    while True:
                        _line = f.readline()
                        if _line.startswith('      energy'):
                            while True:
                                val_line = f.readline()
                                if 'total' in val_line:
                                    break
                                else:
                                    _un_tally.append(val_line.rsplit())
                            break
                        elif _line.startswith(' ======'):
                            print('No se lee valor de tally. Sin energías.')
                            break
                    datos[_tally_n] = np.asarray(_un_tally, dtype=float)
                # Lee los bins de las tallies
                elif line_sep[2] == 'print':
                    _tally_n = line_sep[1]
                    _un_bin = []
                    _cont = 0
                    while True:
                        _cont += 1
                        _line = f.readline()
                        if _line.startswith(' energy bins'):
                            while True:
                                bin_line = f.readline()
                                if '-i' in bin_line:
                                    _un_bin.append([-1, 0])
                                    # print('Se simula un bin negativo')
                                    bin_line = f.readline()
                                if 'total' in bin_line:
                                    break
                                else:
                                    _un_bin.append([bin_line.rsplit()[j] for j
                                                    in [0, 2]])
                            break
                        elif _cont >= 10:
                            print('Tally sin energías')
                            break
                        # print('No se encontraaron bines de energía')
                        # _un_bin = []
                    bins[_tally_n] = np.asarray(_un_bin, dtype=float)
    return datos, nombres, bins


def lee_tally_E_card_tagged(archivo):
    """
    Función para leer los datos al utilizar la tarjeta e en un tally de MCNP

    Se hace una búsqueda de la palabra '1tally' seguidoa de 'nps'. De leen
    todas las tallies del archivo

    Está hecha para leer tallies que poseen un FT TAG, aunque funciona igual si
    no lo tiene. Se diferencia de "lee_tally_E_card()" en que devuelve un
    diccionario de diccionarios.

    Parámetros
    ----------
    archivo : string
        Nombre del archivo de salida de MCNP

    Resultados
    ----------
    datos : dictionary of dictionaries
        Diccionario donde cada clave es un string con el número del tally, y el
        valor es un diccionario para los tags. Las claves de éstos últimos son
        los códigos con que se especifican los tags (ver manual MCNP pg 3-245)
        Si el tally no tiene tag, devuelve un diccionario con la clave 'total'.
    bins : dictionary
        Diccionario donde cada clave es un string con el número del tally, y el
        valor es un ndarray con [valor_bin_inferior valor_bin_superior]
    nombres : list of strings
        Lista con strings correspondientes a cada tally leída. Sólo para
        debuggear. Deben coincidir con los keys del diccionario 'datos'.
    """

    nombres = []
    datos = {}
    bins = {}
    with open(archivo, 'r') as f:
        for line in f:
            if line.startswith('1tally'):
                line_sep = line.split()
                # Lee los resultados de las tallies
                if line_sep[2] == 'nps':
                    _tally_n = line_sep[1]
                    nombres.append(_tally_n)
                    _tally_tag = {}
                    while True:
                        _line = f.readline()
                        if _line.startswith(' user bin'):
                            tag = _line.split()[-1]
                            _line= f.readline()
                        elif _line.startswith(' ======'):
                            # print('No se lee valor de tally. Sin energías.')
                            break
                        else:
                            tag = None
                        if _line.startswith('      energy'):
                            _un_tally = []
                            while True:
                                val_line = f.readline()
                                if 'total' in val_line:
                                    break
                                else:
                                    _un_tally.append(val_line.rsplit())
                            if tag is None:
                                _tally_tag['total'] = np.asarray(_un_tally, dtype=float)
                            else:
                                _tally_tag[tag] = np.asarray(_un_tally, dtype=float)
                    datos[_tally_n] = _tally_tag
                # Lee los bins de las tallies
                elif line_sep[2] == 'print':
                    _tally_n = line_sep[1]
                    _un_bin = []
                    _cont = 0
                    while True:
                        _cont += 1
                        _line = f.readline()
                        if _line.startswith(' energy bins'):
                            while True:
                                bin_line = f.readline()
                                if '-i' in bin_line:
                                    _un_bin.append([-1, 0])
                                    # print('Se simula un bin negativo')
                                    bin_line = f.readline()
                                if 'total' in bin_line:
                                    break
                                else:
                                    _un_bin.append([bin_line.rsplit()[j] for j
                                                    in [0, 2]])
                            break
                        elif _cont >= 10:
                            print('Tally sin energías')
                            break
                        # print('No se encontraaron bines de energía')
                        # _un_bin = []
                    bins[_tally_n] = np.asarray(_un_bin, dtype=float)
    return datos, nombres, bins


def read_kcode_out(filename):
    """
    Lee parámetros de la salida de MCNP6 cuando se corre con KCODE

    Parametros
    ----------
        filename : string
            Nombre del archivo de salida de una corrida con KCODE

    Resultados
    ----------
        output : dic
            Diccionario con los valores leídos

            output['keff'] = (keff, keff_sd)
            output['Lambda'] = (Lambda, Lambda_sd) [en segundos]
            output['Rossi'] = (rossi, rossi_sd) [en 1/segundos]
            output['betaeff'] = (betaeff, betaeff_sd) [en 1/segundos]
            output['precursores'] = np.ndarray de np.floats (similar a como
                                    aparece en el archivo de salida)

            Si no se piden parámetros cinéticos (KINETICS=no) las keys
            'Lambda', 'Rossi' y 'betaeff' poseen valores None
            Si no se piden información sobre precursores (PRECURSOR=no),
            output['precursores'] = None

    TODO: Mejorar el formato del bloque de precursores
    """
    # Flag para saber si se pidieron parámetros cinéticos
    _flag_kin = False
    # Flag para saber si se pidieron parámetros sobre precursores
    _flag_prec = False
    # Diccionario de salida
    output = {}
    with open(filename, 'r') as f:
        # Flag para saber si lee la parte del input
        _eco_input = True
        for line in f:
            if _eco_input:
                # Busca qué se pidió en la entrada
                if "* Random Number Generator" in line:
                    _eco_input = False
                if "kopts" in [it.lower() for it in line.split()]:
                    if re.search(r"kinetics *= *yes", line, re.IGNORECASE):
                        _flag_kin = True
                    if re.search(r"precursor *= *yes", line, re.IGNORECASE):
                        _flag_prec = True
            else:
                # Busca los resultados de la simulación
                if line.startswith(" | the final estimated combined"):
                    # Lee el keff y su incerteza
                    keff = re.search(r"keff = (\d+.\d*) ", line).group(1)
                    keff_sd = re.search(r"deviation of (\d+.\d*) ",
                                        line).group(1)
                    output['keff'] = (np.float(keff), np.float(keff_sd))
                if _flag_kin:
                    if 'gen. time' in line:
                        # Lee el Lambda
                        line_split = line.split()
                        # Determina la unidad del Lambda y de Rossi-alpha
                        if line_split[-1] == '(usec)':
                            conv = 1e-6
                        elif line_split[-1] == '(msec)':
                            conv = 1e-3
                        elif line_split[-1] == '(nsec)':
                            conv = 1e-9
                        else:
                            print("No se reconocen unidades para Lambda")
                        Lambda = np.float(line_split[2])*conv
                        Lambda_sd = np.float(line_split[3])*conv
                        output['Lambda'] = (Lambda, Lambda_sd)
                        # Lee Rossi-alpha
                        line_split = f.readline().split()
                        rossi = np.float(line_split[1])/conv
                        rossi_sd = np.float(line_split[2])/conv
                        output['Rossi'] = (rossi, rossi_sd)
                        # Lee el beta efectivo
                        line_split = f.readline().split()
                        beta_eff = np.float(line_split[1])
                        beta_eff_sd = np.float(line_split[2])
                        output['betaeff'] = (beta_eff, beta_eff_sd)
                if _flag_prec:
                    # Lee información sobre precursores
                    if re.search(r"^ *precursor", line) is not None:
                        next(f)
                        next(f)
                        prec = []
                        for i in range(6):
                            prec.append(f.readline().split())
                        prec = np.asarray(prec)
                        output['precursores'] = prec
    if not _flag_kin:
        for key in ['Lambda', 'Rossi', 'betaeff']:
            output[key] = None
    if not _flag_prec:
        output['precursores'] = None
    return output


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
