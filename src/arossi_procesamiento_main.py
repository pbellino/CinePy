#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script principal que lee los archivo de timestamping binarios, procesa los
datos y escribe los resultados a los archivos.

Los archivos son escritos en la carpeta indicada y llevarán se llamarán:
    [nombre del archivo leido sin extensión]_ros.dat : todas las historias
    [nombre del archivo leido sin extensión].ros : Curva P(tau) promedio

Si no se indica nombre de carpeta, por default se toma `resultados_arossi`.

"""

import sys
sys.path.append('../')

from modules.alfa_rossi_preprocesamiento import alfa_rossi_preprocesamiento, \
                                                grafica_mediciones_cuentas, \
                                                grafica_timestamping
from modules.alfa_rossi_procesamiento import alfa_rossi_procesamiento, \
                                             arossi_inspecciona_resultados
from modules.alfa_rossi_escritura import escribe_ambos


if __name__ == '__main__':

    # -------------------------------------------------------------------------
    # Parámetros de entrada
    # -------------------------------------------------------------------------
    # Archivos a leer
    nombres = [
               '../datos/medicion04.a.inter.D1.bin',
               '../datos/medicion04.a.inter.D2.bin',
               # '../datos/medicion04.a.inter.D1.txt',
              ]
    tipo = 'binario'
    # Cantidad de historias
    Nhist = 200
    # Tiempo base del contador, o factor para convertir a segundos [s]
    if tipo == 'binario':
        tb = 12.5e-9
    elif tipo == 'ascii':
        tb = 1
    # Duración de cada bin (discretización del tau) [s]
    dt_s = 0.5e-3
    # Máximo bin analizado (mayor tau) [s]
    dtmax_s = 50e-3
    # Nombre de la carpeta donde se guardarán los resultados
    nombre_carpeta = 'resultados_arossi'

    # -------------------------------------------------------------------------
    # Preprocesamiento
    # -------------------------------------------------------------------------
    #
    # ---- Graficación la tasa de cuentas de los arhivos .bin (OPCIONAL)
    grafica_mediciones_cuentas(nombres, 1.0, tb, tipo)
    # ---- Corrección de roll-over y separación en historias (OBLIGATORIO)
    data_bloq, data_sin_rol, data_con_rol = \
        alfa_rossi_preprocesamiento(nombres, Nhist, tb, formato_datos=tipo)
    # ---- Grafica los datos de timestamping (OPCIONAL)
    grafica_timestamping(nombres, data_con_rol, data_sin_rol, data_bloq, tipo)
    #
    # -------------------------------------------------------------------------
    # Procesamiento
    # -------------------------------------------------------------------------
    #
    # ---- Procesamiento de los datos por historia (OBLIGATORIO)
    resultados = alfa_rossi_procesamiento(data_bloq, dt_s, dtmax_s, tb)
    # ---- Se grafican resultados (opcional)
    arossi_inspecciona_resultados(resultados, nombres, Nhist, dt_s, dtmax_s)
    #
    # -------------------------------------------------------------------------
    # Escritura
    # -------------------------------------------------------------------------
    #
    # ---- Escribe los resultado del procesamienti (OBLIGATORIO)
    escribe_ambos(resultados, nombres, Nhist, dt_s, dtmax_s, tb,
                  carpeta=nombre_carpeta)
    #
