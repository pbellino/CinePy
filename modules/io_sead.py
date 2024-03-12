#! /usr/bin/env python3

import numpy as np
import pandas as pd
import os
from datetime import datetime
import xlrd

"""
Las funciones que leen los archivos en ASCII usan pandas.

La función que lee el archivo binario usa panda sólo si se lo especifica.
"""


def _merge_fecha_hora(dataframe_original):
    """
    Junta las columnas de Fecha y Hora

    Las convierte a formato 'datetime'
    """
    dataframe = dataframe_original.copy()
    # Junta (como strings) las columnas de Fecha y Hora
    dataframe.insert(0, column='Fecha_hora', value=dataframe['Fecha'] +
                     ' ' + dataframe['Hora'])
    # Convierte la nueva columna en formato 'datetime'
    dataframe['Fecha_hora'] = pd.to_datetime(dataframe['Fecha_hora'])
    # Elimina las columnas originales
    dataframe.drop(columns=['Fecha', 'Hora'], inplace=True)
    return dataframe


def lee_sead_I(file_name, separador):
    """ Cuando está separado por espacios """
    dataframe = pd.read_csv(file_name, sep=separador)
    return _merge_fecha_hora(dataframe)


def lee_sead_II(file_name):
    """ Cuando está separado por ',' """

    data_original = pd.read_csv(file_name, sep=',')
    data = data_original.copy()

    # Agrego la fecha a partir del nombre del archivo
    # Asumo que no se cambia de dia para un dado archivo
    _dia, _mes, _ano = os.path.split(file_name)[-1].split('-')[0].split('_')
    _date = str(int(_ano) + 2000) + '-' + _mes + '-' + _dia
    data['Hora'] = pd.to_datetime(_date + ' ' + data['Hora'].apply(str))
    data.rename({'Hora': 'Fecha_hora'}, axis=1, inplace=True)
    # Renombre la columna de Hora
    data['Fecha_hora'] = pd.to_datetime(data['Fecha_hora'])

    # Renombro las columnas para unificar notación
    for column in data.columns:
        if " " in column:
            data.rename({column: column.replace(" ", "_")}, axis=1,
                        inplace=True)
        elif "BC1" in column:
            data.rename({"BC1": "BC_1"}, axis=1, inplace=True)
        elif "BC2" in column:
            data.rename({"BC2": "BC_2"}, axis=1, inplace=True)
        elif "BC3" in column:
            data.rename({"BC3": "BC_3"}, axis=1, inplace=True)
        elif "BC4" in column:
            data.rename({"BC4": "BC_4"}, axis=1, inplace=True)
    return data


def lectura_SEAD_RA3_bin(file_names, variables=[], panda=True, formato='datetime',
                     region=False):
    """
    Función para leer los archivo guardados por el SEAD del RA3 binarios

    Las variables que se guardan son:
    (columna) (identificación)          (descripción)
        0   Fecha y hora
        1   LOG M1                        Corriente logarítmico de marcha 1
        2   LOG M2                        Corriente logarítmico de marcha 2
        3   LOG M3                        Corriente logarítmico de marcha 3
        4   TASA M3                       Tasa de crecimiento de marcha 3
        5   LIN M3                        Corriente lineal de marcha 3
        6   CIP                           Corriente CIP
        7   DELTA P                       Delta P
        8   LIN M4                        Corriente lineal de marcha 4
        9   QP                            Caudal del primario
        10  TEN 1                         Temperatura de entrada al núcleo 1
        11  TSN 1                         Temperatura de salida al núcleo 1
        12  TEN 3                         Temperatura de entrada al núcleo 3
        13  TSN 3                         Temperatura de salida al núcleo 3
        14  MA SB                         Monitor de área sala de bombas
        15  MA PC                         Monitor de área ¿?
        16  MA TM                         Monitor de área telem-anipuladores
        17  MA BT1                        Monitor de área boca de tanque 1
        18  MA BT2                        Monitor de área boca de tanque 2
        19  MA BT3                        Monitor de área boca de tanque 3
        20  MA CO                         Monitor de área consola
        21  CI N16-1                      Corriente de cámara 1 de N16
        22  CI N16-2                      Corriente de cámara 2 de N16
        23  TEN 2                         Temperatura de entrada al núcleo 2
        24  TSN 2                         Temperatura de salida al núcleo 2
        25  LOG A1                        Cuentas logarítmico de arranque 1
        26  LOG A2                        Cuentas logarítmico de arranque 2
        27  LOG A3                        Cuentas logarítmico de arranque 3
        28  TASA A1                       Tasa de cuentas de arranque 1
        29  TASA A2                       Tasa de cuentas de arranque 2
        30  COND                          ?
        31  BC1                           Porcentaje de extracción de barra 1
        32  BC4                           Porcentaje de extracción de barra 4
        33  REACTIV                       Reactividad calculada con LIN M4

    Notas:
        MA TM era originalmente LAB52
        TEN 2 figura como DELTA T1 usando RA3Convert
        TSN 2 figura como DELTA T3 usando RA3Covnert
        REACTIV Nno se escribe usand RA3Convert

    Parámetros
    ----------
        file_names: string or list of strings
            Nombre(s) de el(los) archivo(s) .RA3 que se quiere(n) leer
            Si es una lista, concatena los archivos en el orden en que se
            ingresan. Es últil para leer archivos consecutivos en el tiempo.
        variables: list of strings
            Nombre de las variables que se quieren leer. Si no se especifica
            nada se devuelven todas las variables disponibles
        panda: boolean
            Si es True, devuelve un dataframe con todas las variables
            Si es False, devuelve un array de datetime y otro array de numpy
            con el resto de las variables.
        formato: string ('datetime', 'time')
            Indica el formato de la primer columna. 'datetima' es fecha + hora.
            'time' es sólo hora
        region: TODO
            Especifica el intervalo temporal que se quiere leer

    Resultados
    ----------
        df: pandas dataframe (sólo si panda=True)
            Dataframe con las columnas leidas
        datetime, data_nparray: datetime array, numpy array (sólo si
                                panda=False)

    """
    # Diccionario para asociar columnas con variables
    label_to_int = {
                    'LOG M1': 1,    # Corriente logarítmico de marcha 1
                    'LOG M2': 2,    # Corriente logarítmico de marcha 2
                    'LOG M3': 3,    # Corriente logarítmico de marcha 3
                    'TASA M3': 4,   # Tasa de crecimiento de marcha 3
                    'LIN M3': 5,    # Corriente lineal de marcha 3
                    'CIP': 6,       # Corriente CIP
                    'DELTA P': 7,   # Delta P
                    'LIN M4': 8,    # Corriente lineal de marcha 4
                    'QP': 9,        # Caudal del primario
                    'TEN 1': 10,    # Temperatura de entrada al núcleo 1
                    'TSN 1': 11,    # Temperatura de salida al núcleo 1
                    'TEN 3': 12,    # Temperatura de entrada al núcleo 3
                    'TSN 3': 13,    # Temperatura de salida al núcleo 3
                    'MA SB': 14,    # Monitor de área sala de bombas
                    'MA PC': 15,    # Monitor de área ¿?
                    'MA TM': 16,    # Monitor de área telem-anipuladores (originalmente LAB52")
                    'MA BT1': 17,   # Monitor de área boca de tanque 1
                    'MA BT2': 18,   # Monitor de área boca de tanque 2
                    'MA BT3': 19,   # Monitor de área boca de tanque 3
                    'MA CO': 20,    # Monitor de área consola
                    'CI N16-1': 21, # Corriente de cámara 1 de N16
                    'CI N16-2': 22, # Corriente de cámara 2 de N16
                    'TEN 2': 23,    # Temperatura de entrada al núcleo 2
                    'TSN 2': 24,    # Temperatura de salida al núcleo 2
                    'LOG A1': 25,   # Cuentas logarítmico de arranque 1
                    'LOG A2': 26,   # Cuentas logarítmico de arranque 2
                    'LOG A3': 27,   # Cuentas logarítmico de arranque 3
                    'TASA A1': 28,  # Tasa de cuentas de arranque 1
                    'TASA A2': 29,  # Tasa de cuentas de arranque 2
                    'COND': 30,     # ?
                    'BC1': 31,      # Porcentaje de extracción de barra 1
                    'BC4': 32,      # Porcentaje de extracción de barra 4 
                    'REACTIV': 33,  # Reactividad (calculada con LIN M4)
                    }

    # -- Lectura de todos los datos
    # Si hay sólo un string, lo convierto a lista de un elemento
    if isinstance(file_names, str): file_names = [file_names]
    # Variable para guardar datos de calibración del archivo
    calibracion = []
    # Itero sobre todos los archivos
    for file_name in file_names:
        with open(file_name, 'rb') as f:
            data_raw = np.fromfile(f, dtype='float', count=-1)
        # Datos en columnas para el archivo leido
        data_cols_single = np.reshape(data_raw, (-1, 34)).T
        # La primer lectura corresponde a valores de calibración
        # TODO: cuando se sepa qué es, ver cómo usarlos
        calibracion.append(data_cols_single[:, 0])
        #  print(f"Datos de calibración:\n {calibracion}")
        # Sigo trabajando sin la calibración
        data_cols_single = data_cols_single[:, 1:]
        # Concateno los datos en columnas de todos los archivos
        try:
            data_cols = np.concatenate((data_cols, data_cols_single), axis=1)
        except UnboundLocalError:
            # Si la variable data_new no existe
            data_cols = data_cols_single

    if formato == 'datetime':
        to_datetime = lambda t: xlrd.xldate_as_datetime(t, 0)
    elif formato == 'time':
        to_datetime = lambda t: xlrd.xldate_as_datetime(t, 0).time()
    else:
        ValueError("'formato' no reconocido para datetime")
    # Convierto datetime del formato excell al formato datetime de python
    datetime = np.vectorize(to_datetime)(data_cols[0, :])


    # Convierto las variables que quiero leer en el índice de su columna
    if len(variables) !=0:
        sel_indx = [label_to_int[s] for s in variables]
        col_names = variables
    else:
        sel_indx = list(range(1, 34))
        col_names = label_to_int.keys()

    if panda:
        # Se devuelve un dataframe
        import pandas as pd
        df = pd.DataFrame(data_cols[sel_indx, :].T, columns=col_names)
        # Agrago columna con fecha y hora
        df.insert(0, 'Fecha-Hora', datetime)
        # Hago que la fecha y hora sea el índice del dataframe
        # df = df.set_index('Fecha-Hora')
        return df
    else:
        # Se devuelve por separado vector de Fecha-Hora y datos
        return datetime, data_cols[sel_indx, :]


def lectura_SEAD_RA1_bin(file_names, variables=[], panda=True, formato='datetime',
                     region=False):
    """
    Función para leer los archivo guardados por el SEAD del RA1 binarios

    Las variables que se guardan son:
    (columna) (identificación)          (descripción)
         1    'LinM4'               # Corriente lineal de marcha 4
         2    'TasaM1'              # Tasa de crecimiento de marcha 1
         3    'LogM1'               # Corriente logarítmica de marcha 1
         4    'LinA1'               # Tasa de cuenta lineales de arranque 1
         5    'LinM5'               # Corriente lineal de marcha 5
         6    'MA1'                 # Monitor de área 1 ¿?
         7    'QP'                  # Caudal del rimario
         8    'DeltaT'              # Delta T del núcleo
         9    'N16'                 # Corriente de nitrógeno-16
         10   'BC3'                 # Porcentaje de extracción de BC3 (señal
                                      incorrecta, aparece como si fuera algo
                                      parecido a una temperatura de núcleo)
                                      (sacar advertencia cuando se arregle)
         11   'BC4'                 # Porcentaje de extracción de BC4
         12   'BC1'                 # Porcentaje de extracción de BC1
         13   'BC2'                 # Porcentaje de extracción de BC2
         14   'LogA2'               # Tasa de cuentas logarítmica de arranque 2
         15   'TasaA1'              # Tasa de cuentas lineales de arranque 1
         16   'LogA1'               # Tasa de cuentas logarítmica de arranque 1
         17   'TEN'                 # Temperatura de entrada al núcleo
         17   'TSN'                 # Temperatura de salida al núcleo


    Parámetros
    ----------
        file_names: string or list of strings
            Nombre(s) de el(los) archivo(s) .RA1 que se quiere(n) leer
            Si es una lista, concatena los archivos en el orden en que se
            ingresan. Es últil para leer archivos consecutivos en el tiempo.
        variables: list of strings (no usar por ahora)
            Nombre de las variables que se quieren leer. Si no se especifica
            nada se devuelven todas las variables disponibles
        panda: boolean
            Si es True, devuelve un dataframe con todas las variables
            Si es False, devuelve un array de datetime y otro array de numpy
            con el resto de las variables.
        formato: string ('datetime', 'time')
            Indica el formato de la primer columna. 'datetima' es fecha + hora.
            'time' es sólo hora
        region: TODO
            Especifica el intervalo temporal que se quiere leer

    Resultados
    ----------
        df: pandas dataframe (sólo si panda=True)
            Dataframe con las columnas leidas
        datetime, data_nparray: datetime array, numpy array (sólo si
                                panda=False)

    """
    # Diccionario para asociar columnas con variables
    label_to_int = {
                    'LinM4': 1,    # Corriente lineal de marcha 4
                    'TasaM1': 2,   # Tasa de crecimiento de marcha 1
                    'LogM1': 3,    # Corriente logarítmica de marcha 1
                    'LinA1': 4,    # Tasa de cuenta lineales de arranque 1
                    'LinM5': 5,    # Corriente lineal de marcha 5
                    'MA1': 6,      # Monitor de área 1 ¿?
                    'QP': 7,       # Caudal del rimario
                    'DeltaT': 8,   # Delta T del núcleo
                    'N16': 13,     # Corriente de nitrógeno-16
                    'BC3': 17,     # Porcentaje de extracción de BC3 (mala)
                    'BC4': 18,     # Porcentaje de extracción de BC4
                    'BC1': 19,     # Porcentaje de extracción de BC1
                    'BC2': 20,     # Porcentaje de extracción de BC2
                    'LogA2': 21,   # Tasa de cuentas logarítmica de arranque 2
                    'TasaA1': 22,  # Tasa de cuentas lineales de arranque 1
                    'LogA1': 24,   # Tasa de cuentas logarítmica de arranque 1
                    'TEN': 30,     # Temperatura de entrada al núcleo
                    'TSN': 32,     # Temperatura de salida al núcleo
                    }

    # -- Lectura de todos los datos
    # Si hay sólo un string, lo convierto a lista de un elemento
    if isinstance(file_names, str): file_names = [file_names]
    # Variable para guardar datos de calibración del archivo
    calibracion = []
    # Itero sobre todos los archivos
    for file_name in file_names:
        with open(file_name, 'rb') as f:
            data_raw = np.fromfile(f, dtype='float', count=-1)
        # Datos en columnas para el archivo leido
        # TODO: ¿por qué tiene la misma cantidad de columnas que para el RA3?
        # TODO: Conseguir RA1convert en la versión actual, la del 2010 no sirve
        data_cols_single = np.reshape(data_raw, (-1, 34)).T
        # La primer lectura corresponde a valores de calibración
        # TODO: cuando se sepa qué es, ver cómo usarlos
        calibracion.append(data_cols_single[:, 0])
        #  print(f"Datos de calibración:\n {calibracion}")
        # Sigo trabajando sin la calibración
        data_cols_single = data_cols_single[:, 1:]
        # Concateno los datos en columnas de todos los archivos
        try:
            data_cols = np.concatenate((data_cols, data_cols_single), axis=1)
        except UnboundLocalError:
            # Si la variable data_new no existe
            data_cols = data_cols_single

    if formato == 'datetime':
        to_datetime = lambda t: xlrd.xldate_as_datetime(t, 0)
    elif formato == 'time':
        to_datetime = lambda t: xlrd.xldate_as_datetime(t, 0).time()
    else:
        ValueError("'formato' no reconocido para datetime")
    # Convierto datetime del formato excell al formato datetime de python
    datetime = np.vectorize(to_datetime)(data_cols[0, :])


    # Convierto las variables que quiero leer en el índice de su columna
    if len(variables) !=0:
        sel_indx = [label_to_int[s] for s in variables]
        col_names = variables
        #TODO: Sacar advertencia cuando se arregle BC3
        if 'BC3' in variables: print('\n\n\nLos datos de BC3 están mal\n\n\n')
    else:
        sel_indx = list(range(1, 19))
        col_names = label_to_int.keys()
        #TODO: Sacar advertencia cuando se arregle BC3
        print('\n\n\nLos datos de BC3 están mal\n\n\n')

    if panda:
        # Se devuelve un dataframe
        import pandas as pd
        df = pd.DataFrame(data_cols[sel_indx, :].T, columns=col_names)
        # Agrago columna con fecha y hora
        df.insert(0, 'Fecha-Hora', datetime)
        # Hago que la fecha y hora sea el índice del dataframe
        # df = df.set_index('Fecha-Hora')
        return df
    else:
        # Se devuelve por separado vector de Fecha-Hora y datos
        return datetime, data_cols[sel_indx, :]


if __name__ == "__main__":
    """
    Prueba de la función "lectura_SEAD_bin()"
    """
    import pandas as pd
    import matplotlib.pyplot as plt
    from matplotlib.dates import DateFormatter
    import seaborn as sns
    sns.set()
    # Conversión de datetime entre panda y matplotlib
    from pandas.plotting import register_matplotlib_converters
    register_matplotlib_converters()

    file_name = "14_02_20-12_00.RA3"
    magnitudes = [
                  'TEN 1', 'TEN 2', 'TEN 3',
                  'TSN 1', 'TSN 2', 'TSN 3',
                 ]

    data = lectura_SEAD_RA3_bin(file_name, magnitudes, formato='datetime')
    print(data)

    # Gráficos
    fig1, ax1 = plt.subplots()
    data.plot(ax=ax1, x='Fecha-Hora', y=magnitudes)
    date_form = DateFormatter("%H:%M")
    ax1.xaxis.set_major_formatter(date_form)
    ax1.set_xlabel("Hora")

    # Si se quiere el vector temporal en segundos
    fig2, ax2 = plt.subplots()
    diff = data['Fecha-Hora'] - data['Fecha-Hora'][0]
    t_seconds = diff.dt.total_seconds()
    ax2.plot(t_seconds, data.to_numpy()[:, 1:])
    ax2.set_xlabel("Segundos desde inicio de archivo")

    ###########################################################################
    # Para graficar un eje x superior en segundos
    # TODO: Noanda Nara
    print(80*'#')
    print("Lo que sigue es una prueba")
    t0 = data['Fecha-Hora'][0]
    def datetime_to_sec(x):
        s = x - t0
        return s.total_seconds()

    ejemplo = data['Fecha-Hora'][20]
    sec = datetime_to_sec(ejemplo)
    print(f"Dato original: {ejemplo}")
    print(f"Dato convertido a segundos desde inicio medición: {sec}")

    def sec_to_datetime(x):
        y = pd.Timestamp(x, unit='s')
        tsum = y.asm8.astype(np.int64) + t0.asm8.astype(np.int64)
        tsum = pd.Timestamp(tsum.astype('<M8[ns]'))
        return tsum.to_pydatetime()

    recon = sec_to_datetime(sec)
    print(f"Dato reconvertido a datetime: {recon}")

    d_to_s_vec = np.vectorize(datetime_to_sec)
    s_to_d_vec = np.vectorize(sec_to_datetime)

    # Esto es lo que se debería hacer, pero tira errores por las funciones
    # Nunca más trabajar con datetime
    # top_axis = ax1.secondary_xaxis('top', functions=(d_to_s_vec, s_to_d_vec))

    plt.show()
