#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np
import matplotlib.pyplot as plt

import sys
sys.path.append('../')

from modules.estadistica import agrupa_datos
from modules.io_modules import lee_bin_datos_dt

plt.style.use('paper')

def grafica_datos_agrupados(nombres, int_agrupar=None):
    """
    Grafica los datos de los archivos adquiridos

    Como en general serán con un dt muy pequeño, se permite agrupar
    intervalos.

    Parametros
    ----------
    nombres : lista de strings
        Camino y nombre de los archivos .bin que se quieren graficar
    int_agrupar : entero ó lista de enteros, opcional
        Cantidad de intervalos que se quieren agrupar. Si no se especifica
        se calcula de tal manera de obetner un dt_agrupado de 1 seg
        (y el gráfico será la tasa de cuentas en cps)
        Si se da una lista, se usan distintos intervalos para cada archivo
        

    """
    _results = lee_bin_datos_dt(nombres)
   
    def _define_int_agrupar():
        """ Define los intervalos a agrupar en base al dado en el input """

        if int_agrupar is not None:
            if type(int_agrupar) is not list:
                # Si sólo es un número, se hace que sea una lista con el mismo valor
                # para todos los archivos leidos
                int_agrupar_it = [int_agrupar for _ in nombres]
            elif len(int_agrupar) != len(nombres):
                # Si es una lista y no coinciden los tamaños, se sale
                print('No coinciden los tamaños')
                quit()
            else: int_agrupar_it = int_agrupar
        else:
            int_agrupar_it = []
            for _, dt_base in _results:
                int_agrupar_it.append(int(1.0 / dt_base))
        return int_agrupar_it

    int_agrupar_it = _define_int_agrupar()
    print(int_agrupar_it)

    datos_agrupados = []
    vec_temp = []
    for j, result in enumerate(_results):
        dato = result[0]
        dt_base = result[1]
        _data, dt_agrupado = agrupa_datos(dato, int_agrupar_it[j], dt_base) 
        datos_agrupados.append(_data)
        # Construyo vector temporal
        dt_max = dt_agrupado * len(_data)
        vec_temp.append(np.arange(dt_agrupado, dt_max + dt_agrupado, dt_agrupado))

    # Grafico
    fig1 = plt.figure(1)
    ax1 = fig1.add_subplot(1,1,1)
    
    for x, y in zip(vec_temp, datos_agrupados):
        ax1.plot(x,y)

    ax1.set_xlabel('Tiempo [s]')

    dt_agrupado = [vec[0] for vec in vec_temp]
    # Nombre de los archivos para la leyenda
    # Se cambia dependiendo si se grafican tasa de cuentas (dt=1s)
    # Si no, se agrega info del dt en la leyenda
    str_legend = []
    if int_agrupar is None:
        ax1.set_ylabel('Tasa de cuentas [cps]')
        for nombre in nombres:
            str_legend.append(nombre.rsplit('/')[-1])
    else:
        ax1.set_ylabel('Cuentas por dt')
        for nombre, dt in zip(nombres, dt_agrupado):
            str_legend.append(nombre.rsplit('/')[-1] + ' (dt={} s)'.format(dt))
  
    ax1.legend(str_legend, loc='best')

    plt.show()
    

if __name__ == '__main__':


    # ---------------------------------------------------------------------------------
    # Parámetros de entrada
    # ---------------------------------------------------------------------------------
    # Archivos a leer
    nombres = [
              '../datos/nucleo_01.D1.bin',
              '../datos/nucleo_01.D2.bin',
              ]
    # Intervalos para agrupar los datos adquiridos
    int_agrupar = 5000
    # ---------------------------------------------------------------------------------
   
    grafica_datos_agrupados(nombres)
    #grafica_datos_agrupados(nombres, [1000, 2000])
    #grafica_datos_agrupados(nombres, int_agrupar)
