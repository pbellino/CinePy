#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np

def agrupa_datos(data, n_datos=1, dt=None):
    ''' 
    Agrupa los datos de data en n_datos 
    
    Parametros
    ----------
        data : numpy array
            datos que se quieren agrupar
        n_datos : entero
            número de intervalos que se agruparán
        dt : flotante, opcional
            intervalo de tiempo original de 'data'

    Salida
    ------
        datos_agrupados : numpy array
            datos agrupados cada n_datos
        dt_agrupado : flotante, opcional
            Si se especificó dt se devuelve el dt agrupado
            (dt_agrupado = dt*n_datos)
    '''
    
    data = np.array(data)
    if n_datos==1:
        if dt is None:
            return data
        else:
            return data, dt
    elif n_datos >= 2:
        print('Se agrupan {} intervalos base'.format(n_datos))
        # Al hacer reshape, el array debe tener el tamaño exacto
        # Se deben obviar los datos sobrantes
        _partes = len(data) // n_datos
        _indice_exacto = _partes * n_datos
        _matriz = data[0:_indice_exacto].reshape(_partes, n_datos)
        datos_agrupados = _matriz.sum(axis=1, dtype='uint32')
        if dt is None:
            return datos_agrupados
        else:
            dt_agrupado = dt * n_datos
            print('Intervalo de adquisición agrupado: {} s'.format(dt_agrupado))
            return datos_agrupados , dt_agrupado


if __name__ == "__main__":
    # Prueba de agrupa_datos
    # TODO: pasarla a la carpeta tests
    a = np.array([3, 6, 7, 9, 1])
    b = agrupa_datos(a, 2)
    print(b)
    c, c_dt = agrupa_datos(a, 2, 0.3)
    print(c, c_dt)


