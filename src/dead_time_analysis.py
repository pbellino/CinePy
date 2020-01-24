#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" Simulación de tiempos muertos a partir de datos de timestamping """

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
sns.set()

import sys
sys.path.append('../')

from modules.io_modules import read_timestamp
from inter_arrival_analysis import grafica_histograma_interarrivals
from modules.alfa_rossi_preprocesamiento import corrige_roll_over
from modules.flag_np_deadtime import flag_np_deadtime

plt.style.use('paper')


def _control_unidades_tau(tau, unidades):
    """ Función auxiliar para manejar las unidades de tiempo (MEJORAR) """
    if unidades == 'pulsos':
        tau = np.uint64(tau)
        print('Tiempo muerto simulado: {} pulsos'.format(tau))
    elif unidades == 'tiempo':
        print('Tiempo muerto simulado: {} s'.format(tau))
        tau = np.uint64(tau / tb)
        print('Tiempo muerto simulado: {} pulsos'.format(tau))
    else:
        print('Se trabaja en unidades de pulsos')
        print('Tiempo muerto simulado: {} pulsos'.format(tau))
        unidades = 'pulsos'
    return tau, unidades


def genera_np_deadtime(datos, tau, unidades=None, tb=12.5e-9):
    """
    Función para simular un tiempo muerto no-paralizable en los datos

    Llama a la función `flag_np_deadtime()` compilada con cython donde se
    definieron los tipos de datos de sus argumentos. Por esa razón se debe
    ser extricto y verificar bien que coincidan con los que se le pasan desde
    python.

    Recordar que hay que compilar la función `flag_np_deadtime()` (está en
    `./modules`) con cython para generar el .so. Ver el Readme en `./doc`.

    Parámetros
    ----------
        datos : array
            Pulsos con timestaming
        tau :
            Tiempo muerto no-paralizable que se simulará
        unidades : string ('pulsos', 'tiempo')
            Unidades en las que se especifica el `tau`. También define las
            unidades de los tiempos simulados
        tb : float
            Tiempo de los pulsos del contador

    Resultados
    ----------
        datos_np_simulados : array
            Pulsos con timestaming con el tiempo muerto np ya simulado. Las
            unidades las define `unidades`.

    TODO: Pensar mejor cómo especificar las unidades. Está raro.
    """
    if datos.dtype != 'uint64':
        print('Los datos están en: {}'.format(datos.dtype))
        print('Hay que pasar los datos a uint64')
        print('O recompliar el script de cython con el dtype de datos')
        quit()

    tau, unidades = _control_unidades_tau(tau, unidades)
    # Es cómo se identificar los pulsos que se eliminarán
    # (no existe nan para numpy array de enteros)
    flag = np.uint64(2**64 - 1)
    # Es muy improbable que algún dato valga el flag, pero se comprueba
    if any(datos == flag):
        print('No se pude simular tiempo muerto no paralizable')
        print('No es posible utilizar un flag en esos datos')
        quit()

    # Se generan los datos con los flags para ser eliminados
    new_data = flag_np_deadtime(datos, tau, flag)
    new_data = np.asarray(new_data)
    # Se buscan los flags
    indx_to_remove = np.where(new_data == flag)[0]
    # Se eliminan los pulsos
    datos_np_simulados = np.delete(new_data, indx_to_remove)

    print('Pulsos originales: {}'.format(datos.size))
    print('Pulsos eliminados: {}'.format(indx_to_remove.size))
    print('Pulsos restantes: {}'.format(datos_np_simulados.size))

    # Control de unidades de la salida
    if unidades == 'tiempo':
        datos_np_simulados = datos_np_simulados*tb
    return datos_np_simulados


def genera_p_deadtime(datos, tau, unidades=None, tb=12.5e-9):
    """
    Función para generar un tiempo muerto paralizable en los datos

    Parámetros
    ----------
        datos : array
            Pulsos con timestaming
        tau :
            Tiempo muerto no-paralizable que se simulará
        unidades : string ('pulsos', 'tiempo')
            Unidades en las que se especifica el `tau`. También define las
            unidades de los tiempos simulados
        tb : float
            Tiempo de los pulsos del contador

    Resultados
    ----------
        datos_np_simulados : array
            Pulsos con timestaming con el tiempo muerto np ya simulado. Las
            unidades las define `unidades`.

    """
    # Ponge las unidades especificadas
    tau, unidades = _control_unidades_tau(tau, unidades)
    # Calcula tiempo entre pulsos
    dts = np.diff(datos)
    # Busca los índices cuyo dt sea menor al tiempo muerto
    # (se le suma uno porque con numpy.diff() se quita un punto)
    indx_to_remove = np.where(dts <= tau)[0] + 1
    # Se quitan todos los pulsos
    datos_p_simulados = np.delete(datos, indx_to_remove)

    print('Pulsos originales: {}'.format(datos.size))
    print('Pulsos eliminados: {}'.format(indx_to_remove.size))
    print('Pulsos restantes: {}'.format(datos_p_simulados.size))

    # Control de unidades de la salida
    if unidades == 'tiempo':
        datos_p_simulados = datos_p_simulados * tb
    return datos_p_simulados


if __name__ == '__main__':

    # -------------------------------------------------------------------------
    # Parámetros de entrada
    # -------------------------------------------------------------------------
    # Archivos a leer
    nombres = [
              '../datos/medicion04.a.inter.D1.bin',
              '../datos/medicion04.a.inter.D2.bin',
              ]
    unidad = 'tiempo'
    tb = 12.5e-9
    # -------------------------------------------------------------------------
    # Para la leyenda del gráfico
    archivos = []
    for nombre in nombres:
        archivos.append(nombre.rsplit('/')[-1])

    tiempos, header = read_timestamp(nombres[1])
    datos = corrige_roll_over(tiempos)

    # ------------------------------------------------------------------------
    # Tiempo muerto no-paralizable
    tau_np = 1e-3
    new_data = genera_np_deadtime(datos, tau_np, unidad, tb)
    new_dt = np.diff(new_data)

    nbins = np.linspace(0.0, tau_np*10, 301, endpoint=False)

    # Opciones para graficar
    parametros_histo = {'unidad': unidad,
                        'nbins': nbins,
                        'yscale': 'linear',
                        'nombre': 'No paralizable',
                        'tb': tb,
                        'anota': False,
                        }
    # Graficación
    fig1 = grafica_histograma_interarrivals(new_dt, **parametros_histo)

    # ------------------------------------------------------------------------
    # Tiempo muerto paralizable
    tau_p = 1e-3

    new_data = genera_p_deadtime(datos, tau_p, unidad, tb)
    new_dt = np.diff(new_data)

    # Opciones para graficar
    parametros_histo = {'unidad': unidad,
                        'nbins': nbins,
                        'yscale': 'linear',
                        'nombre': 'Paralizable',
                        'tb': tb,
                        'anota': False,
                        'fig': fig1,
                        }
    # Graficación
    grafica_histograma_interarrivals(new_dt, **parametros_histo)
    title_str = r'Simulados $\tau_{{np}}$ = {:1.2E} s y $\tau_p$ = {:1.2E} s'.format(tau_np, tau_p)
    # En la figura anterior (ver karg 'fig')
    fig1.axes[0].set_title(title_str)

    plt.show()
