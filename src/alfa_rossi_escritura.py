#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
TODO
"""

import numpy as np
import matplotlib.pyplot as plt
import os
import datetime

from alfa_rossi_preprocesamiento import alfa_rossi_preprocesamiento
from alfa_rossi_procesamiento import arossi_historias

import sys
sys.path.append('../')


def arossi_inspecciona_resultados(resultados, nombres, N_hist, dt_s, dtmax_s):
    """
    Grafica los resultados obtenidos con `arossi_historias`

    Los parámetros de entrada son los mismos que en arossi_historias.

    """

    # Nombres para identificar archivos
    nombres_lab = []
    for nombre in nombres:
        if '/' not in nombre:
            nombres_lab.append(nombre)
        else:
            nombres_lab.append(nombre.rsplit('/')[-1])

    # Gráficos de triggers y tasa de cuentas para cada historia
    fig1, axs = plt.subplots(2, 1, sharex='col')
    # Vector con los números de historias
    hist = np.linspace(1, N_hist, N_hist, dtype=int)
    # Grafico todos los archivos
    for i, resultado in enumerate(resultados):
        R = np.asarray(list(resultado[:, 1]))
        axs[0].errorbar(hist, R[:, 0], yerr=R[:, 1], fmt='.', elinewidth=0.5,
                        lw=0, label=nombres_lab[i])
        Trig = resultado[:, 2]
        axs[1].plot(hist, Trig, '.', label=nombres_lab[i])

    axs[0].set_ylabel('Tasa de cuentas [cps]')
    axs[1].set_ylabel('# triggers')
    axs[1].set_xlabel('Historias')

    for ax in axs:
        ax.grid(True)
        ax.legend(loc='best')

    # Gráfico de la curva de alfa-Rossi
    # Vector temporal
    tau = np.linspace(0, dtmax_s, int(dtmax_s / dt_s), endpoint=False)
    # Lo hago centrado en el bin
    tau += dt_s / 2
    fig2, ax1 = plt.subplots(1, 1)
    # Grafico todos los archivos leidos en el mismo gráfico
    for i, resultado in enumerate(resultados):
        historias = resultado[:, 0]
        P_mean = np.mean(historias)
        P_std = np.std(historias) / np.sqrt(N_hist)
        ax1.errorbar(tau, P_mean, yerr=P_std, fmt='.', elinewidth=0.5,
                     lw=0, label=nombres_lab[i])

    ax1.set_xlabel(r'Tiempo [s]')
    ax1.set_ylabel(r'P($\tau$)')
    ax1.grid(True)
    ax1.legend(loc='best')
    plt.show()

    return None


def genera_encabezado(nombre, Nhist, dt_s, dtmax_s, tb, *args, **kargs):
    """ Genera string con encabezado para todos los archivos por igual """

    encabezado = []
    # Fecha y hora del procesamiento (asumiendo que se escribe a continuación)
    now = datetime.datetime.now()
    now_str = now.strftime(now.strftime("%d-%m-%Y %H:%M"))

    line_1 = '# Nombre del archivo procesado: ' + nombre.rsplit('/')[-1]
    encabezado.append(line_1)
    encabezado.append('#')
    encabezado.append('# Fecha de procesamiento: {}'.format(now_str))
    encabezado.append('#')
    encabezado.append('# Tipo de procesamiento: alfa-Rossi Tipo I')
    encabezado.append('#')
    encabezado.append('# Duración del bin (dt): {:.2E} s'.format(dt_s))
    encabezado.append('# Máximo bin analizado (dt_max): '
                      + '{:.2E} s'.format(dtmax_s))
    encabezado.append('# Puntos analizados por trigger: {}'.format(
                                                          int(dtmax_s / dt_s)))
    encabezado.append('# Tiempo base del contador: {:.2E} s'.format(tb))
    encabezado.append('# Número de historias (N_hist): {}'.format(Nhist))
    encabezado.append('# ' + '-'*50)
    return encabezado


def escribe_datos_completos(resultados, nombres, Nhist, dt_s, dtmax_s, tb,
                            *args, **kargs):
    """
    TODO

    El tau está centrado en el bin.

    El desvío estándar es del promedio de la tasa de cuentas (ya está dividido
    por raiz(N)).

    """
    def _genera_camino_archivo(nombre):
        """ Genera camino del archivo de datos dado el nombre leído """
        # Directorio donde se guardarán
        directorio = 'resultados_arossi'
        if not os.path.exists(directorio):
            os.makedirs(directorio)

        # Me quedo sólo con el nombre
        _solo_nombre = os.path.split(nombre)[-1]
        # Quita la extensión
        _nom_sinext = _solo_nombre.rsplit('.', 1)[0]
        # Escribe camino
        camino = os.path.join(directorio, _nom_sinext + '_ros.dat')
        return camino

    extras = ''  # Para agregar algo más en un futuro
    # Se escribe iterando en los archivos (detectores)
    for nombre, resultado in zip(nombres, resultados):
        header = genera_encabezado(nombre, Nhist, dt_s, dtmax_s, tb, extras)
        camino = _genera_camino_archivo(nombre)
        with open(camino, 'w') as f:
            for line in header:
                f.write(line + '\n')
            R = np.asarray(list(resultado[:, 1]))
        with open(camino, 'a') as f:
            f.write('# Tasa de cuentas promedio en cada historia [cps] \n')
            f.write('# historia_#1   ....    historia_#N_hist \n')
        with open(camino, 'ab') as f:
            np.savetxt(f, R[:, 0], fmt='%1.6e', newline='\t')
        with open(camino, 'a') as f:
            f.write('\n# Desvío estándar del promedio de la tasa de cuentas ' +
                    'de cada historia [cps] \n')
            f.write('# historia_#1   ....    historia_#N_hist \n')
        with open(camino, 'ab') as f:
            np.savetxt(f, R[:, 1], fmt='%1.6e', newline='\t')
        with open(camino, 'a') as f:
            f.write('\n# Cantidad de triggers de cada historia \n')
            f.write('# triggers_#1   ...   triggers_#N_hist \n')
        with open(camino, 'ab') as f:
            np.savetxt(f, resultado[:, 2], fmt='%u', newline='\t')
        with open(camino, 'a') as f:
            f.write('\n# Tau centrado [s] y función P(tau) normalizada para '
                    'cada historia \n')
            f.write('# tau [s] P(tau)_#1   ...   P(tau)_#N_hist \n')
        with open(camino, 'ab') as f:
            # Vector temporal
            tau = np.linspace(0, dtmax_s, int(dtmax_s / dt_s), endpoint=False)
            tau += dt_s / 2  # Centrado en el bin
            _hist = np.transpose(list(np.asarray(resultado[:, 0])))
            _tod = np.column_stack((tau, _hist))
            np.savetxt(f, _tod, fmt='%1.6e')
        print('Se grabó el archivo "' + camino + '" con todas las historias')
        print('-'*50)
    return None


if __name__ == '__main__':

    # -------------------------------------------------------------------------
    # Parámetros de entrada
    # -------------------------------------------------------------------------
    # Archivos a leer
    nombres = [
               '../datos/medicion04.a.inter.D1.bin',
               '../datos/medicion04.a.inter.D2.bin',
              ]
    # Cantidad de historias
    Nhist = 5
    # Tiempo base del contador [s]
    tb = 12.5e-9
    dt_s = 0.5e-3
    dtmax_s = 50e-3

    # -------------------------------------------------------------------------
    # Preprocesamiento
    data_bloq, _, _ = alfa_rossi_preprocesamiento(nombres, Nhist, tb)
    # Procesamiento
    resultados = arossi_historias(data_bloq, dt_s, dtmax_s, tb)
    # Escritura
    escribe_datos_completos(resultados, nombres, Nhist, dt_s, dtmax_s, tb)
