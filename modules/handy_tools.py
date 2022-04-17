#! /usr/bin/env python3

import numpy as np

def empalma_rangos(n, t, tiempo_saltos, t_previo=5):
    """
    Función para corregir los saltos de rango que se observan al adquirir
    señales con un amplificador lineal.

    En lugar de utilizar el valor teórico (x10 en cada salto) se hace una
    extrapolación de la señal previa al salto y se ajusta la señal posterior al
    salto para que coincida con el valor extrapolado. Se asume una evolución
    exponencial durante el cambio de rango.

    Si durante el cambio de rangos hay puntos erráticos, se los elimina y se
    los reemplaza por la evolución exponencial extrapolada.

    Parametros
    ----------
        n: numpy array
           Array con saltos discretos debido a cambios de rango
        t: numpy array
           Vector 1D temporal asociado al n
        tiempo_saltos: list of touples
           Lista con (t1, t2) donde t1 es el último tiempo antes del salto y
           t2 el primero luego del salto
        t_previo: float (5 segundos)
            Tiempo en segundos previo al salto en donde se hace el ajuste para
            extraplar la evollución.

    Resultados
    ----------
        n_empalmado: numpy array
            Array con los valores de n empalmados

    """
    n_empalmado = np.copy(n)

    for t1, t2 in tiempo_saltos:
        #- Ajuste linal previo al salto
        nlog = np.log(n_empalmado)
        # Tiempos donde se hace el ajuste lineal
        ind_fit = (t >= (t1 - t_previo)) & (t <= t1)
        x = t[ind_fit]
        y = nlog[ind_fit]
        p = np.polyfit(x, y, 1)
        omega = p[0]

        #- Empalma en t2
        # Se asume función exponencial durante el cambio de rango
        exp_fun = lambda x: n_empalmado[t <= t1][-1] * np.exp(omega * (x - t1))
        n_empalmado[t >= t2] = \
                  n_empalmado[t >= t2] * exp_fun(t2) / n_empalmado[t <= t2][-1]

        #- Reemplaza puntos erráticos durante el salto
        ind_inter = (t > t1) & (t < t2)
        n_empalmado[ind_inter] = exp_fun(t[ind_inter])
    return n_empalmado

