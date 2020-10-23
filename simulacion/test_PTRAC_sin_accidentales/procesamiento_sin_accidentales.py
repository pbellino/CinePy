#!/usr/bin/env python3

"""
Script de prueba para generar la distrubución de alfa-Rossi a partir de la
simulación con PTRAC en modo lista sin tener en cuenta las coincidencias
accidentales.
"""

import numpy as np
import sys

sys.path.append('/home/pablo/CinePy/')
from modules.alfa_rossi_procesamiento import alfa_rossi_procesamiento
from modules.io_modules import read_PTRAC_CAP_bin
from modules.alfa_rossi_escritura import escribe_datos_promedio
from modules.simulacion_modules import lee_nps_entrada, \
                                       separa_en_historias_sin_accidentales


if __name__ == '__main__':

    archivo_entrada = 'in_sdef'
    archivo_n = 'in_sdef_n.p'

    # -------------------------------------------------------------------------
    # Pre-procesamiento
    # -------------------------------------------------------------------------
    # Se lee la cantidad de eventos de fuente del archivo de entrada de MCNP
    nps = lee_nps_entrada(archivo_entrada)
    # Se leen los datos en binario
    print('Leyendo arhvo de neutrones....')
    datos_n, header_n = read_PTRAC_CAP_bin(archivo_n)
    # Se separan por historias
    print('Separando datos por hisotrias....')
    times_out = separa_en_historias_sin_accidentales(datos_n)

    # -------------------------------------------------------------------------
    # Procesamiento
    # -------------------------------------------------------------------------
    # Duración de cada bin (discretización del tau) [s]
    dt_s = 2e-4
    # Máximo bin analizado (mayor tau) [s]
    dtmax_s = 2e-2
    # Nombre de la carpeta donde se guardarán los resultados
    nombre_carpeta = 'resultados_arossi'
    tb = 1
    # Procesamiento de los datos
    dat_pro = alfa_rossi_procesamiento(times_out, dt_s, dtmax_s, tb, 'all')

    # En este caso la cantidad de historias lo determina la simulación
    Nhist = np.shape(dat_pro[0])[0]
    # Se escribe sólo el promedio
    # Si se usan más detectores, se debe crear un nombre para cada detector
    archivo_out = [archivo_n]
    escribe_datos_promedio(dat_pro, archivo_out, Nhist, dt_s, dtmax_s, tb,
                           nombre_carpeta)
