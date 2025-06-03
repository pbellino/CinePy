#! /usr/bin/env python3

import numpy as np

def read_acritico(filename):
    '''
    Función para leer los archivoss grabados por el programa "contador_pulsos"

    Cada dato es la cantidad de pulsos registrado en un dado dt.

    El formato en que está grabado es entero sin signo de 32 bits con
    codificación big-endian

    Se descarta al primer dato por no ser considerado confiable.

    Parameters
    ----------

    filename : string
        Nombre del archivo que se quiere leer

    Returns
    -------

    data: numpy array
        Datos leidos
    t: numpy array
        Vector temporal asociado a 'data'
    dt: float
        dt utilizado en la adquisición
    header: list of strings
        Encabezado el archivo

    '''

    # Tipo de dato: sin signo (por eso el 'u')
    #               32 bits (por eso el '4')
    #               'big-endian'(por eso el >)
    # https://docs.scipy.org/doc/numpy/reference/arrays.dtypes.html
    dt = np.dtype('>u4')

    header = []
    try:
        with open(filename, 'rb') as f:
            # Sigue leyendo el resto
            for i in range(10):
                header.append(f.readline().rstrip().decode("latin1"))
            # Continua leyendo los datos
            data = np.fromfile(f, dtype=dt, count=-1)
            # El primer dato se descarta
            data = data[1:]
            # Lee el dt del encabezado
        dt = float(header[5].rsplit(':')[-1])
        # Vector temporal
        t = dt * np.arange(0, len(data))
        return data, t, dt, header
    except IOError as err:
        print('No se pudo leer el archivo: ' + filename)
        raise err
    except:
        print('Se produjo un error inseperado al abrir/leer el archivo'
              + filename)
        sys.exit()
