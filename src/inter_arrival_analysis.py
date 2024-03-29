#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" Script para graficar histograma de tiempo entre pulsos """

import numpy as np
import matplotlib.pyplot as plt
import uncertainties as unc
import seaborn as sns
sns.set()

import sys
sys.path.append('../')

from modules.io_modules import read_timestamp
from modules.estadistica import rate_from_timestamp

plt.style.use('paper')


def genera_tiempos_entre_pulsos(nombres, unidad='pulsos', t_base=12.5e-9):
    """
    Calcula el tiempo entre pulsos para los datos especificados.

    Lo calcula directamente cno numpy.diff(). Recordar que lo hace sobre los
    datos sin corrección del roll-over y en uint32. Se aprovecha que la resta
    en python hace un nuevo roll-over para mantenerse dentro de uint32.

    Parámetros
    ----------
    nombres : lista de strings
        Nombre de los archivos que se quieren leer

    unidad : string, opcional
        Se especifica las unidades para el tiempo
        'pulsos' : (default) Unidades de pulsos de reloj utilizado
        'tiempo' : segundos (utiliza el valor de `t_base`)

    t_base: float, opcional
        Periodo del reloj utilizado para contar. Para el sistema NI se
        utiliza un reloj de 80MHz, por lo cual t_base=12.5e-9s.

    Resultados
    ----------
    tiempo_entre_pulsos : list of numpy.ndarray
        Cada elemento es la lista con tiempos entre pulsos.
        De acuerdo a la unidad de tiempo seleccionada `unidad` el tipo de
        dato será:
            `unidad`='pulsos': uint32
            `unidad'='tiempo': float64

    unidad : string
        Unidad utilizada para el tiempo. La misma para todos los archivos.
        Se pone como salida para utilizarla en los gráficos.

    Se graba el gráfico en un archivo llamado `nombre'_hist.png

    """

    if isinstance(nombres, list):
        _es_lista = True
    else:
        _es_lista = False
        nombres = [nombres]
    tiempo_entre_pulsos = []
    for nombre in nombres:
        _data, _header = read_timestamp(nombre)
        _dts = np.diff(_data)
        if unidad == 'tiempo':
            print('Tiempo expresado en [s] con numpy.ndarray de float64')
            _dts = np.float64(_dts*t_base)
        elif unidad == 'pulsos':
            pass
        else:
            print('Se especificó mal la unidades de tiempo')
            print('Se toma `pulsos`')
            unidad = 'pulsos'
        tiempo_entre_pulsos.append(_dts)
    if not _es_lista:
        tiempo_entre_pulsos = tiempo_entre_pulsos[0]
    return tiempo_entre_pulsos, unidad


def grafica_histograma_interarrivals(tiempo_entre_pulsos, *args, **kargs):
    """
    Grafica el histograma de tiempo entre pulsos

    Parámetros
    ----------
        tiempo_entre_pulsos : numpy array
            Vector con los tiempo entre pulsos

        unidad : string ('pulsos')
            Unidad utilizada para `tiempo_entre_pulsos` ('tiempo' o 'pulsos')

        nbins : int (1000)
            Cantidad de bines para el histograma. También puede ser un array
            con las posiciones de los bines

        yscale : string ('linear')
            Escala para el eje y ('linear', 'log')

        nombre : string ('Datos')
            Nombre para la leyenda que identifica la curva

        anota : boolean ('True')
            Escribe o no la tasa de cuetnas en el gráfico
        tb : float [segundos]
            Tiempo del reloj que se utilizó para contar los pulsos

    Resultados
    ----------
        fig : figure handler

    """
    if kargs is not None:
        unidad = kargs.get('unidad', 'pulsos')
        nbins = kargs.get('nbins', 1000)
        yscale = kargs.get('yscale', 'linear')
        nombre = kargs.get('nombre', 'Datos')
        anota = kargs.get('anota', True)
        tb = kargs.get('tb', None)
        fig = kargs.get('fig', None)

    h_coun, h_bin = np.histogram(tiempo_entre_pulsos, bins=nbins, density=True)
    if fig is not None:
        ax1 = fig.axes[0]
    else:
        fig, ax1 = plt.subplots(1, 1)

    # Genero vector de bins centrados
    center_bin = h_bin[:-1] + np.diff(h_bin)
    ax1.plot(center_bin, h_coun, '.', label=nombre)
    ax1.set_yscale(yscale)
    # Asigno unidades a los bines
    if unidad == 'tiempo':
        xscale = r'Tiempo [s]'
    elif unidad == 'pulsos':
        xscale = r'Pulsos'
    else:
        print('No se reconoce la unidad temporal')
        xscale = 'Desconocido'
    ax1.set_xlabel(xscale)
    ax1.set_ylabel(u'Densidad de probabilidad')
    ax1.set_title('Histograma de tiempo entre pulsos')
    ax1.legend(loc='best')
    ax1.grid('True')
    ax1.ticklabel_format(style='sci', axis='x', scilimits=(0, 0),
                         useMathText=True)

    if yscale is not 'log':
        ax1.ticklabel_format(style='sci', axis='y', scilimits=(0, 0),
                             useMathText=True)
    fig.tight_layout()

    # Tasa de cuentas
    if unidad == 'pulsos':
        if tb is None:
            print('Falta indicar el tiempo del reloj para calcular la tasa')
            print('Se toma tb=1')
            tb = 1
        _tiempo_segundos = tiempo_entre_pulsos * tb
    else:
        _tiempo_segundos = tiempo_entre_pulsos
    _R, _R_std = rate_from_timestamp(_tiempo_segundos)
    R = unc.ufloat(_R, _R_std)
    str_R = r'R = (${:1.2uL}$) cps'.format(R)
    if anota:
        bbox_props = dict(boxstyle='Round', fc='w')
        ax1.annotate(str_R, xy=(0.3, 0.8), bbox=bbox_props, size=15,
                     xycoords='axes fraction')
    # Graba el archivo
    # fig.savefig(nombre + '_hist.png')
    # Imprime en pantalla
    print('-' * 50)
    print('Nombre: ' + nombre)
    print('R = ' + str(R))
    print('-' * 50)
    return fig


if __name__ == '__main__':

    # -------------------------------------------------------------------------
    # Parámetros de entrada
    # -------------------------------------------------------------------------
    # Archivos a leer
    nombres = [
              '../datos/medicion04.a.inter.D1.bin',
              '../datos/medicion04.a.inter.D2.bin',
              ]
    unidad = 'pulsos'
    nbins = 10000
    yscale = 'log'
    # -------------------------------------------------------------------------
    # Para la leyenda del gráfico
    archivos = []
    for nombre in nombres:
        archivos.append(nombre.rsplit('/')[-1])

    # Se generan los tiempos entre pulsos
    tiempos, unidad = genera_tiempos_entre_pulsos(nombres, unidad)
    # Se grafican los histogramas
    for tiempo, archivo in zip(tiempos, archivos):
        # Opciones para graficar
        parametros_histo = {'unidad': unidad,
                            'nbins': nbins,
                            'yscale': yscale,
                            'nombre': archivo,
                            'tb': 12.5e-9,
                            }
        # Graficación
        grafica_histograma_interarrivals(tiempo, **parametros_histo)

    plt.show()
