#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np
import sys

def read_bin_dt(filename):
    '''
    Función para leer los archivos binarios grabados por el programa "intervaltime_MC"

    Cada dato es la cantidad de pulsos registrado en un dado dt.
    Los archivos más viejos no tenían encabezado, mientras que los nuevos sí. 
    El formato en que está grabado es entero sin signo de 32 bits con codificación big-endian

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
        with open(filename,'rb') as f:
            # Se fija si tiene encabezado
            header.append(f.readline().rstrip())
            if header[0].startswith(b'Nombre'):
                print('El archivo tiene encabezado')
                # Sigue leyendo el resto
                for i in range(6):
                    header.append(f.readline().rstrip())
            else:
                print('El archivo no tiene encabezado')
                # Vuelvo al comienzo del archivo
                f.seek(0,0)
            # Continua leyendo los datos
            a = np.fromfile(f, dtype=dt, count=nread)
            # El primer dato se descarta
        return a[1:], header
    except IOError as err:
        print('No se pudo leer el archivo: ' + filename)
        raise err
    except:
        print('Se produjo un error inseperado al abrir/leer el archivo' + filename)        
        sys.exit()


def lee_dt_encabezado(encabezado):
    """ Lee en el encabezado el intervalo dt con que se realizó la adquisición """

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
                Intervalo temporal con que se hizo la medición para cada archivo
    
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


if __name__ == '__main__':
    
    a, header = read_bin_dt('../datos/nucleo_01.D1.bin')
    for line in header:
        print(line)
    print('Cantidad de datos: {}'.format(len(a)))
    # 10 datos intermedios
    print(a[45000-1:45010-1])
    # Los últimos 10 datos
    print(a[-10:])
