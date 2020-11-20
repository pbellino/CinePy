#!/usr/bin/env python3

"""
Script de prueba para generar la distrubución de alfa-Rossi a partir de la
simulación con PTRAC en modo lista.
"""

import numpy as np
import sys

sys.path.append('/home/pablo/CinePy/')
from modules.io_modules import read_PTRAC_CAP_bin
from modules.simulacion_modules import agrega_tiempo_de_fuente, \
                                       lee_nps_entrada, read_PTRAC_estandar, \
                                       corrige_t_largos, \
                                       split_and_save_listmode_data, \
                                       separa_capturas_por_celda


if __name__ == '__main__':

    archivo_entrada = 'in_sdef'
    archivo_n = 'in_sdef_n.p'
    archivo_p = 'in_sdef_p.p'

    # Se lee la cantidad de eventos de fuente del archivo de entrada de MCNP
    nps = lee_nps_entrada(archivo_entrada)
    # Se leen los datos en binario
    print('Leyendo arhvo de neutrones....')
    datos_n, header_n = read_PTRAC_CAP_bin(archivo_n)
    datos_n = np.asarray(datos_n)

    print('Leyendo arhvo de fotones....')
    datos_p, _ = read_PTRAC_estandar(archivo_p, 'bin', ['sur'])

    # Se agrega el tiempo del evento de fuente [1/s]
    tasa = 2000.0

    print('Se simularon {} neutrones'.format(nps))
    print('La tasa de eventos agregada es {} 1/s'.format(tasa))
    print('El tiempo total de la simulación será: {} s'.format(nps / tasa))

    # Agrega el tiempo de funte y guarda los tiempos en archivos
    print('se agrega el tiempo de fuente...')
    print(80*'-')
    datos_n = agrega_tiempo_de_fuente(tasa, nps, datos_n)
    datos_p = agrega_tiempo_de_fuente(tasa, nps, datos_p)

    # Corrección para los tiempos largos
    print('se corrigen los tiempos largos...')
    print(80*'-')
    datos_n_corr = corrige_t_largos(datos_n, tasa, nps, metodo='pliega')
    datos_p_corr = corrige_t_largos(datos_p, tasa, nps, metodo='pliega')

    # Separa y graba datos temporales en modo lista
    print('se separann y gardan los datos...')
    print(80*'-')
    datos = [datos_n_corr, datos_p_corr]
    nombres = ["times_listmode_n", "times_listmode_p"]
    split_and_save_listmode_data(datos, nombres, comprime=True)

