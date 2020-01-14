#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Escribe los resultados del procesamiento con el método de alfa-Rossi.

Genera el archivo [nombre]_ros_dat con todas las historias.
Genera el archivo [nombre].ros con el promedio entre historias.

Toma os resultados provenientes de `alfa_rossi_procesamiento()` que está en el
script `alfa_rossi_procesamiento.py`.

Nota: Las funciones de escritura tienen entre sus argumentos a la lista de
tuplas `resultados`. El cuarto elemento de la tupla contiene la información
de las cuentas en bruto para cada trigger de cada historia. Por ahora no se
utiliza, pero si más adelante es necesario para calcular multiplicidades, se
podrá utilizar fácilmente (ver función arossi_una_historia_I() en
`alfa_rossi_procesamiento.py`.
"""

import numpy as np
import os
import datetime

import sys
sys.path.append('../')

from modules.alfa_rossi_preprocesamiento import alfa_rossi_preprocesamiento
from modules.alfa_rossi_procesamiento import alfa_rossi_procesamiento


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
    encabezado.append('# Duración del bin (dt) [s]')
    encabezado.append('{:1.4E}'.format(dt_s))
    encabezado.append('# Máximo bin analizado (dt_max) [s]')
    encabezado.append('{:.4E}'.format(dtmax_s))
    encabezado.append('# Puntos analizados por trigger')
    encabezado.append('{}'.format(int(dtmax_s / dt_s)))
    encabezado.append('# Tiempo base del contador [s]')
    encabezado.append('{:.4E}'.format(tb))
    encabezado.append('# Número de historias (N_hist)')
    encabezado.append('{}'.format(Nhist))
    encabezado.append('# ' + '-'*50)
    return encabezado


def genera_camino_archivo(nombre, tipo, nom_carpeta):
    """ Genera camino del archivo de datos dado el nombre leído """

    if not os.path.exists(nom_carpeta):
        os.makedirs(nom_carpeta)

    # Me quedo sólo con el nombre
    _solo_nombre = os.path.split(nombre)[-1]
    # Quita la extensión
    _nom_sinext = _solo_nombre.rsplit('.', 1)[0]
    # Escribe camino
    if tipo == 'completo':
        camino = os.path.join(nom_carpeta, _nom_sinext + '_ros.dat')
    elif tipo == 'promedio':
        camino = os.path.join(nom_carpeta, _nom_sinext + '.ros')
    return camino


def escribe_datos_completos(resultados, nombres, Nhist, dt_s, dtmax_s, tb,
                            nom_carpeta, *args, **kargs):
    """
    Escribe los P(tau) de cada historia e información de parámetros utilizados

    El nombre del arhivo que escribe es [nombre]_ros.dat, donde [nombre] es
    basa en el parámetro de entrada `nombres` sin la extensión. El archivo se
    crea dentro de la carpeta `./nom_carpeta/`.

    El tau está centrado en el bin.

    El desvío estándar es del promedio de la tasa de cuentas (ya está dividido
    por raiz(N)).

    """

    extras = ''  # Para agregar algo más en un futuro
    # Se escribe iterando en los archivos (detectores)
    for nombre, resultado in zip(nombres, resultados):
        header = genera_encabezado(nombre, Nhist, dt_s, dtmax_s, tb, extras)
        camino = genera_camino_archivo(nombre, 'completo', nom_carpeta)
        with open(camino, 'w') as f:
            f.write('# Archivo con P(tau) de todas las historias\n')
            f.write('#\n')
            for line in header:
                f.write(line + '\n')
        R = np.asarray(list(resultado[:, 1]))
        with open(camino, 'a') as f:
            f.write('# Tasa de cuentas promedio en cada historia [cps] \n')
            f.write('# historia_#1   ....    historia_#N_hist \n')
        with open(camino, 'ab') as f:
            np.savetxt(f, R[:, 0], fmt='%1.6e', newline=' ')
        with open(camino, 'a') as f:
            f.write('\n# Desvío estándar del promedio de la tasa de cuentas ' +
                    'de cada historia [cps] \n')
            f.write('# historia_#1   ....    historia_#N_hist \n')
        with open(camino, 'ab') as f:
            np.savetxt(f, R[:, 1], fmt='%1.6e', newline=' ')
        with open(camino, 'a') as f:
            f.write('\n# Cantidad de triggers de cada historia \n')
            f.write('# triggers_#1   ...   triggers_#N_hist \n')
        with open(camino, 'ab') as f:
            np.savetxt(f, resultado[:, 2], fmt='%u', newline=' ')
        with open(camino, 'a') as f:
            f.write('\n# Tau centrado [s] y función P(tau) normalizada para '
                    'cada historia \n')
            f.write('# tau [s] P(tau)_#1   ...   P(tau)_#N_hist \n')
        # Vector temporal
        tau = np.linspace(0, dtmax_s, int(dtmax_s / dt_s), endpoint=False)
        tau += dt_s / 2  # Centrado en el bin
        _hist = np.transpose(list(np.asarray(resultado[:, 0])))
        _tod = np.column_stack((tau, _hist))
        with open(camino, 'ab') as f:
            np.savetxt(f, _tod, fmt='%1.6e')
        print('Se grabó el archivo "' + camino + '" con todas las historias')
        print('-'*50)
    return None


def escribe_datos_promedio(resultados, nombres, Nhist, dt_s, dtmax_s, tb,
                           nom_carpeta, *args, **kargs):
    """
    Escribe el P(tau) promedio e información de parámetros utilizados

    El nombre del arhivo que escribe es [nombre].ros, donde [nombre] es
    basa en el parámetro de entrada `nombres` sin la extensión. El archivo se
    crea dentro de la carpeta `./nom_carpeta/`.

    """

    extras = ''  # Para agregar algo más en un futuro
    # Se escribe iterando en los archivos (detectores)
    for nombre, resultado in zip(nombres, resultados):
        header = genera_encabezado(nombre, Nhist, dt_s, dtmax_s, tb, extras)
        camino = genera_camino_archivo(nombre, 'promedio', nom_carpeta)
        with open(camino, 'w') as f:
            f.write('# Archivo con P(tau) promediada entre las historias\n')
            f.write('#\n')
            for line in header:
                f.write(line + '\n')
        R = np.asarray(list(resultado[:, 1]))
        # Sólo me interesan los promedios
        R = R[:, 0]
        R_mean = np.mean(R)
        R_std = np.std(R) / np.sqrt(R.size)
        N_trig = resultado[:, 2]
        N_trig_mean = np.mean(N_trig)
        N_trig_std = np.std(N_trig) / np.sqrt(N_trig.size)
        with open(camino, 'a') as f:
            f.write('# Tasa de cuentas promedio [cps] \n')
            f.write('{:1.6e}\n'.format(R_mean))
            f.write('# Desvío estándar de la tasa de cuentas [cps] \n')
            f.write('{:1.6e}\n'.format(R_std))
            f.write('# Cantidad de triggers promedio \n')
            f.write('{:1.6}\n'.format(N_trig_mean))
            f.write('# Desvío estándar de la cantidad de triggers \n')
            f.write('{:1.6}\n'.format(N_trig_std))
            f.write('# Tau centrado [s]    <P(tau)>    std(<P(tau)>) \n')
        # Vector temporal
        tau = np.linspace(0, dtmax_s, int(dtmax_s / dt_s), endpoint=False)
        tau += dt_s / 2  # Centrado en el bin
        # Todas las historias
        _historias = resultado[:, 0]
        P_mean = np.mean(_historias)
        P_std = np.std(_historias) / np.sqrt(Nhist)
        # Agrupa en columnas
        _es = np.column_stack((tau, P_mean, P_std))
        with open(camino, 'ab') as f:
            np.savetxt(f, _es, fmt='%1.6e')
        print('Se grabó el archivo "' + camino + '" con el promedio')
        print('-'*50)
    return None


def escribe_ambos(resultados, nombres, Nhist, dt_s, dtmax_s, tb, *args,
                  **kargs):
    """
    Escribe los dos archivos a la vez (historias y promedio)

    Opcionalmente se puede ingresar un keyword argument:

        'carpeta' : nombre de la carpeta donde se escribirán los datos
                    (relativa al directorio de donde sea llamada). El valor
                    por default es 'resultados_arossi'.
    """
    if kargs is not None:
        nom_carpeta = kargs.get('carpeta', 'resultados_arossi')

    escribe_datos_completos(resultados, nombres, Nhist, dt_s, dtmax_s, tb,
                            nom_carpeta)
    escribe_datos_promedio(resultados, nombres, Nhist, dt_s, dtmax_s, tb,
                           nom_carpeta)
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
    resultados = alfa_rossi_procesamiento(data_bloq, dt_s, dtmax_s, tb)
    # Escritura
    escribe_ambos(resultados, nombres, Nhist, dt_s, dtmax_s, tb,
                  carpeta='resultados_arossi')
