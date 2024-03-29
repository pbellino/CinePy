#!/usr/bin/env python3

"""
Script de prueba para generar la distrubución de alfa-Rossi a partir de la
simulación con PTRAC en modo lista.
"""

import numpy as np
import sys

sys.path.append('/home/pablo/CinePy/')
from modules.alfa_rossi_procesamiento import arossi_una_historia_I
from modules.io_modules import read_PTRAC_CAP_bin, read_PTRAC_CAP_asc
from modules.simulacion_modules import agrega_tiempo_de_fuente, \
                                       lee_nps_entrada, read_PTRAC_estandar, \
                                       corrige_t_largos


if __name__ == '__main__':

    archivo_entrada = 'in_sdef'
    archivo_n = 'in_sdef_n.p'

    # Se lee la cantidad de eventos de fuente del archivo de entrada de MCNP
    nps = lee_nps_entrada(archivo_entrada)
    # Se leen los datos en binario
    print('Leyendo arhvo de neutrones....')
    datos_n, header_n = read_PTRAC_CAP_bin(archivo_n)

    # Se agrega el tiempo del evento de fuente [1/s]
    tasa = 1000.0

    print('Se simularon {} fisiones espontáneas'.format(nps))
    print('El Cf252 generó (promedio) {} neutrones de fuente'.format(3.75*nps))
    print('La tasa de eventos agregada es {} 1/s'.format(tasa))
    print('El tiempo total de la simulación será: {} s'.format(nps / tasa))

    # Agrega el tiempo de funte y guarda los tiempos en archivos
    print('se agrega el tiempo de fuente...')
    datos_n = agrega_tiempo_de_fuente(tasa, nps, datos_n)

    t_n = datos_n[:, 1]
    t_0 = t_n[0]
    np.savetxt('times_listmode_n.dat', t_n, fmt='%.12E')
    print('Tiempo total simulado de neutrones: {} s'.format(t_n[-1] - t_0))

    # Corrección para los tiempos largos
    print('se corrigen los tiempos largos...')
    datos_n_corr = corrige_t_largos(datos_n, tasa, nps, metodo='pliega')
    # datos_n_corr = corrige_t_largos(datos_n, tasa, nps, metodo='elimina')

    t_n_corr = datos_n_corr[:, 1]
    t_n_corr -= t_n_corr[0]
    np.savetxt('times_listmode_n_corr.dat', t_n_corr, fmt='%.12E')

    # Para debuggear
    # nps_hist_n = datos_n_corr[:, 0]
    # np.savetxt('historia_n.dat', nps_hist_n, fmt='%i')
