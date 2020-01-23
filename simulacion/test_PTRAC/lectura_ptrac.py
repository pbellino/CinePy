#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script de prueba para leer un archivo PTRAC generado por MCNP
"""

from mcnptools import Ptrac


if __name__ == '__main__':

    # Se abren los archivos (binarios y ascii)
    p_bin = Ptrac("ptrac_bin", Ptrac.BIN_PTRAC)
    # p_asc = Ptrac("ptrac_asc", Ptrac.ASC_PTRAC)

    # Se obtienen las historias
    histories_bin = p_bin.ReadHistories(10000)

    # Cantidad de eventos de cada historia
    num_events = []
    for historie in histories_bin:
        num_events.append(historie.GetNumEvents())

    # De la historia #1 toma el evento #2
    event = histories_bin[0].GetEvent(3)
    print('Para el segundo evento de la primer historia')
    print('Tipo de evento:', event.Type())
    print(event.BankType())
    print(event.Get(Ptrac.TIME))
    print('-'*50)

    # Obtener todos los tiempos para cada evento de cada historia
    times = []
    for historie in histories_bin:
        for i in range(historie.GetNumEvents()):
            event = historie.GetEvent(i)
            times.append(event.Get(Ptrac.TIME))

    # Ordeno los tiempos
    # times.sort()
    print('Se leyeron {} tiempos'.format(len(times)))
    print('-'*50)
    print('Tiempos leídos: \n')
    for time in times:
        # Convierte a segundos
        print(time*1e-8)
