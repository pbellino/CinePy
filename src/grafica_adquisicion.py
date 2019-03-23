#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np
import matplotlib.pyplot as plt

import sys
sys.path.append('../')

from modules.estadistica import agrupa_datos
from alfa_feynman import lee_bin_datos_dt

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
    int_agrupar : entero, opcional
        Cantidad de intervalos que se quieren agrupar. Si no se especifica
        se calcula de tal manera de obetner un dt_agrupado de 1 seg
        (y el gráfico será la tasa de cuentas en cps)

    """
   
    datos, dt_base = lee_bin_datos_dt(nombres)
   
    if int_agrupar is None:
        int_agrupar = int(1.0 / dt_base)
        str_ylabel = 'Tasa de cuentas [cps]'
    else:
        str_ylabel = 'Cuentas cada {} s'.format(dt_base*int_agrupar)
 
    datos_agrupados = []
    vec_temp = []
    for dato in datos:
        _data, dt_agrupado = agrupa_datos(dato, int_agrupar, dt_base) 
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
    ax1.set_ylabel(str_ylabel)
 
    # Nombre de los archivos para la leyenda
    str_legend = []
    for nombre in nombres:
        str_legend.append(nombre.rsplit('/')[-1])
  
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
   
    #grafica_datos_agrupados(nombres)
    grafica_datos_agrupados(nombres, int_agrupar)
