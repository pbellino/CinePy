#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script de prueba para leer un archivo PTRAC generado por MCNP
"""

from mcnptools import Ptrac


if __name__ == '__main__':

    # Se abren los archivos (binarios y ascii)
    p_bin = Ptrac("ptrac_TER_bin", Ptrac.BIN_PTRAC)
    # No se puede leer CAP en binario
    # p_bin = Ptrac("ptrac_CAP_bin", Ptrac.BIN_PTRAC)

    # Se obtienen las historias
    histories_bin = p_bin.ReadHistories(10000)
    # Cantidad de eventos de cada historia
    num_events = []
    for historie in histories_bin:
        num_events.append(historie.GetNumEvents())

    # Obtener todos los tiempos para cada evento de cada historia
    times = []
    nps = []
    event_type = []
    print('Termination event (1:escape 12:capture)')
    for historie in histories_bin:
        for i in range(historie.GetNumEvents()):
            nps.append(historie.GetNPS().NPS())
            event = historie.GetEvent(i)
            event_type.append(event.Type())
            if event.Type() == Ptrac.TER:
                print(i+1, event.Get(Ptrac.TERMINATION_TYPE))
            times.append(event.Get(Ptrac.TIME)/1e8)

    # Ordeno los tiempos
    # times.sort()
    print('Se leyeron {} tiempos'.format(len(times)))
    print('-'*50)
    print('Tiempos leídos: \n')
    print('nps   event_type    times')
    for time in zip(nps, event_type, times):
        print(*time)
