#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Script para graficar histograma de tiempo entre pulsos """

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
sns.set()

import sys
sys.path.append('../')

from modules.io_modules import read_timestamp

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

    """

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
    return (tiempo_entre_pulsos, unidad)


def grafica_histograma_interarrivals(tiempo_entre_pulsos, *args, **kargs):
    """
    Grafica el histograma de tiempo entre pulsos

    Parámetros
    ----------
    tiempo_entre_pulsos : numpy array
        Vector con los tiempo entre pulsos

    unidad : string
        Unidad utilizada para `tiempo_entre_pulsos`

    nbins : int
        Cantidad de bines para el histograma

    yscale : string
        Escala para el eje y ('linear', 'log')

    nombre : string
        Nombre para la leyenda que identifica la curva

    """
    if kargs is not None:
        unidad = kargs.get('unidad', 'pulsos')
        nbins = kargs.get('nbins', 1000)
        yscale = kargs.get('yscale', 'linear')
        nombre = kargs.get('nombre', 'Datos')

    h_coun, h_bin = np.histogram(tiempo_entre_pulsos, bins=nbins, density=True)
    fig1, ax1 = plt.subplots(1, 1)
    # Genero vector de bins centrados
    center_bin = h_bin[:-1] + np.diff(h_bin)
    ax1.plot(center_bin, h_coun, '.')
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
    ax1.legend([nombre], loc='best')
    ax1.grid('True')
    ax1.ticklabel_format(style='sci', axis='x', scilimits=(0, 0),
                         useMathText=True)

    # TODO: mejorar esto
    dt_mean = np.mean(tiempo_entre_pulsos)
    dt_std = np.std(tiempo_entre_pulsos)/np.sqrt(len(tiempo_entre_pulsos))
    print('Tasa de cuentas promedios:')
    # Propagación lineal, buscar la forma correcta
    print(str(1.0/dt_mean) + ' +/- ' + str(dt_std/dt_mean**2))
    return None


if __name__ == '__main__':

    # ---------------------------------------------------------------------------------
    # Parámetros de entrada
    # ---------------------------------------------------------------------------------
    # Archivos a leer
    nombres = [
              '../datos/medicion04.a.inter.D1.bin',
              '../datos/medicion04.a.inter.D2.bin',
              ]
    # ---------------------------------------------------------------------------------
    unidad = 'tiempo'
    nbins = 10000
    archivos = []
    # Para la leyenda del gráfico
    for nombre in nombres:
        archivos.append(nombre.rsplit('/')[-1])

    # Se generan los tiempos entre pulsos
    tiempos, unidad = genera_tiempos_entre_pulsos(nombres, unidad)
    # Se grafican los histogramas
    for tiempo, archivo in zip(tiempos, archivos):
        # Opciones para graficar
        parametros_histo = {'unidad': unidad,
                            'nbins': nbins,
                            'yscale': 'log',
                            'nombre': archivo,
                            }
        # Graficación
        grafica_histograma_interarrivals(tiempo, **parametros_histo)

    plt.show()