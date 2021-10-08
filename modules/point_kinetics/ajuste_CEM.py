#!/usr/bin/env python3

import numpy as np
import os
from lmfit import Minimizer, Parameters, report_fit
from uncertainties import ufloat

import sys
sys.path.append("/home/pablo/CinePy")
from modules.point_kinetics.soluciones_analiticas import solucion_in_hour_equation


def lee_archivo_CIN(name):
    """
    Función para leer los archivos .CIN
    """

    header_length = 8
    with open(name, 'r') as f:
        header = []
        for i in range(header_length):
            header.append(f.readline().rstrip('\n'))
        data = []
        for line in f:
            if line != "0,0\n":
                data.append(line.rstrip('\n'))
            else:
                break
    data = np.asarray(data, dtype=float)
    dt = float(header[-2])
    time = dt * np.arange(len(data))
    return time, data


def salto_instantaneo_espacial(t, rho, t1, n0, A1, A3, constantes):
    """
    Función analítica para un salto en escalón considerando cinética espacial

    Parámetros
    ----------
          t : np array of floats
            Tiempos donde se evalúa la solución
        rho : float
            Reactividad insertada
        t1 : float
            Tiempo donde se produce el saalto (t1 = t0 + tb)
        n0 : float
            Valor inicial de la densidad neutrónica
        A1 : float
            Parámetro de la amplitud (A1=1 si vale cinética puntual)
        A3 : float
            Offset
        constantes: tuple
            Deben estar en el orden: b_i, lam_i, Lambda_reducido

    Resultados
    ----------
        n : numpy array
            Solución de la densidad neutrónica n(t)

    """

    b, lam, Lambda_red = constantes
    # Coeficientes de las exponenciales
    roots = solucion_in_hour_equation(rho, constantes)
    B = []
    for root in roots:
        _numerador = Lambda_red + np.sum(b / (root + lam))
        B.append(rho / root / (Lambda_red + np.sum(b * lam / (root + lam)**2)))
    # Suma de exponenciales para t>=t1
    n_pos = 0.
    for root, amp in zip(roots, B):
        n_pos += amp * np.exp(root*(t[t >= t1] - t1))
    # Multiplico por el valor inicial y la constante debido al efecto espacial
    n_pos *= n0 * A1
    # Sumo el offset
    n_pos += A3
    # Constante para t<t1
    n_pre = n0 * np.ones(np.shape(t[t < t1]))

    return np.concatenate((n_pre, n_pos))


def deteccion_borde(t, x, t_ref, borde='bajada',  n_sigmas=3.5):
    """
    Función para detectar el cambio abrupto en una señal

    Se basa en analizar las fluctuaciones previo al cabmio, y ver cuándo la
    señal cambia en más de "x_sigmas" su valor.

    Parameters
    ----------
        t : numpy array
            Vector temporal
        x : numpy array
            Señal a la cual se le quiere detectar el borde
        t_ref : tupla
            (t_inicial, t_final) del intervalo que se usará de referencia
        borde : string ('subida', 'bajada')
            Identifica si se quiere un flanco de subida o de bajada
        n_sigma: float
            Cantidad de sigmas que se tomarán como nivel para decidir si hubo
            un borde en la señal x

    Returns
    -------
        t_borde : float
            Tiempo en donde se produce el cambio en la señal

    """

    t_i, t_f = t_ref
    # Región de la señal que se tomará como referencia para analizar su
    # desvío estándar
    x_ref = x[(t >= t_i) & (t <= t_f)]
    # Nivel que usaré para decidir si hay un borde
    if borde == 'bajada':
        nivel = np.mean(x_ref) - n_sigmas * np.std(x_ref)
        # Si i es el primer dato por debajo del nivel, tomo el i-1
        _cond = (t > t_f) & (x <= nivel)
    elif borde == 'subida':
        nivel = np.mean(x_ref) + n_sigmas * np.std(x_ref)
        _cond = (t > t_f) & (x >= nivel)
    # Si i es el primer dato por encima del nivel, tomo el i-1
    return t[np.where(_cond)[0][0]-1]


def deteccion_tiempo_caida(t, rho, t_cero):
    """
    Función para detectar el tiempo en donde finaliza la caída de barra/s

    Busca, a partir de t_cero, el momento donde la reactividad deja de
    disminuir.

    Parameters
    ----------
        t : numpy array
            Vector temporal
        rho : numpy array
            Vector con los valores de reactividad
        t_cero : float
            Tiempo donde comienza a caer la barra. Es para evitar las
            fluctuaciones previas a la caída de la barra

    Returns
    -------
        t_caida : float
            Tiempo en donde finaliza la caída de barra/s
        indx_caida: int
            Índice de t_caida en el array t

    """

    # Condiciones para encontrar el t_caida:
    #  - Busco entre t_cero y 20s
    #  - Busco que la reactividad aumente (agrego un cero en np.diff para
    #  mantener el tamaño del array)
    _cond = (t > t_cero) & (t < 20) & (np.diff(rho, append=0) >= 0)
    if any(t[_cond]):
        # Es el primer valor que cumple con las _cond
        return t[_cond][0], np.where(_cond==True)[0][0]
    else:
        raise ValueError("No se pudo determinar el tiempo de caída de barra")


def ajuste_cinetica_espacial(t, n, n_err=None, **kargs):
    """
    Ajusta utilizacion como modelo la cinética espacial.

    Se usa la función:
                f(t) = A1 sum_i B_i e^{-omega_i (t-t1)} + A3

    donde omega_i son las soluciones de la ecuación in-hour, t1 es el tiempo en
    donde se produce el salto instantáneo y A3 el offset de la señal. La
    función asume que los datos están normalizados.

    Admite un ajuste variando los parámetros: rho, A1, A3 y t1. También pueden
    dejarse fijos algunos de ellos.

    Las condiciones iniciales por defecto son:
         rho = -1 $
          tb = 2 s
          A1 = 1
          A3 = 0

    Se utiliza el paquete lmfit. El método es 'leastsq' iLevenberg-Marquardt,
    ver documentación de lmfit para más datos)

    Parameters
    ----------
        t : numpy array
            Vector temporal
        n : numpy array
            Datos que se quieren ajustar
        n_err : numpy array (Optativo)
            Incerteza en los datos
        kargs : dict
            Parámetros para definir el ajuste. Pueden ser:

            't_ajuste' : tupla (t_i, t_f)
                Tiempos iniciales y finales del rango de ajuste
            'constantes_cineticas' : touple or list (b, lambda, L*)
                            b (list), lambda (list), reduced Lambda (float)
                            b_i = beta_i / beta_eff
                            L* = L/beta_eff
            'param_ini' : touple or array
                Parámetros iniciales del ajuste. Si no se varía algún
                parámetro, su valor lo fija el valor inicial, salvo Si se
                especifica "t1_value" (se toma este valor).
            't1_vary' : Boolean
                Si se quiere variar t1
            't1_value' : float
                Valor inicial de t1. Si no se varía t1 es el valor que se fija
                (sobreescribe a la condición inicial)
            'A1_vary' : Boolean
                Si se quiere variar A1. Si es Falsa, se fija A1=1
            'A3_vary' : Boolean
                Si se quiere variar A3. Si es Falsa, se fija A3=0

    Result
    ------
        result : lmfit result
            Todos los datos del ajuste, característimo de lmfit

    """

    t_inicio, t_final = kargs.get('t_ajuste')
    constantes_cineticas = kargs.get('constantes_cineticas')
    param_ini = kargs.get("init_values", [-1, 2, 1, 1, 0])
    t1_vary = kargs.get("t1_vary")
    param_ini[1] = kargs.get('t1_value', 1)
    A1_vary = kargs.get("A1_vary", True)
    A3_vary = kargs.get("A3_vary", True)

    def residual_analitico(params, t, data=None, sigma=None, constantes=None):
        parvals = params.valuesdict()
        rho = parvals['rho']
        t1 = parvals['t1']
        n0 = parvals['n0']
        A1 = parvals['A1']
        A3 = parvals['A3']

        model = salto_instantaneo_espacial(t, rho, t1, n0, A1, A3, constantes)

        if data is None:
            return model
        if sigma is None:
            return model - data
        return (model - data) / sigma

    # Se definen los parámetros del ajuste
    params = Parameters()
    params.add('rho', value=param_ini[0])
    params.add('t1', value=param_ini[1], vary=t1_vary)
    params.add('n0', value=param_ini[2], vary=False)
    params.add('A1', value=param_ini[3], vary=A1_vary)
    params.add('A3', value=param_ini[4], vary=A3_vary)

    # Selección del intervalo de ajuste
    ind_fit = (t >= t_inicio) & (t <= t_final)
    t_fit = t[ind_fit]
    n_fit = n[ind_fit]
    # Se define la minimización
    minner = Minimizer(residual_analitico, params,
                       fcn_args=(t_fit,),
                       fcn_kws={'data': n_fit,
                                'sigma': n_err,
                                'constantes': constantes_cineticas,
                               }
                       )

    metodo = 'leastsq'
    result = minner.minimize(method=metodo)

    return result


def estima_reactividad_reactimetro(t, rho, t_caida, metodo='Angel'):
    """
    Estima la reactividad promedio por cinética inversa en un rod-drop ($op)

    Dada una reactividad rho(t) en un experimento de rod-drop, busca obtener el
    promedio en una zona donde la rho(t) sea constante. Es particularmente
    importante en presencia de efectos espaciales.

    Parameters
    ----------
        t : numpy array
            Vector temporal
        rho : numpy_array
            Reactividad en función del tiempo
        t_caida : float
            Tiempo donde la barra deja de caer. Se comienza a buscar la ona de
            rho(t) = cte a partir de este tiempo
        metodo : string ('Angel')
            Método que se utiliza para buscar la zona constante
            'Angel' : Divide a rho(t) en segmentos y va calculando el desvio
            estándar desde el comienzo de cada segmento hasta el final de los
            datos. Cuanndo el desvío estándar nuevo es mayor que el anterior,
            se finaliza la búsqueda. Se obtiene el promedio y desvío.

    Returns
    -------
        rho_op : ufloat
            Reactividad estimada ($_op, en dólares)
        t_in_ajuste : float
            Tiempo inicial a parti de donde se realiza el promedio

    """
    # Valores en donde se buscará la zona constante en reactividad
    rho_const = rho[(t >= t_caida) & (t <= t_caida + 70) ]
    # Cantidad de datos que tendrá cada segmento
    datos_por_segmento = 50
    # Valor inicial exageradamente grande para pasar la primer iteración
    std_old = 1e10
    # Loop sobre los comienzos de cada segmento
    se_obtiene_resultado = False
    for start in range(0, rho_const.shape[0], datos_por_segmento):
        std_new = np.std(rho_const[start:])
        if std_new >= 1.0 * std_old:
            se_obtiene_resultado = True
            rho_op = ufloat(np.mean(rho_const[start:]),
                            np.std(rho_const[start:]))
            dt = t[1] - t[0]
            t_in_ajuste = t_caida + start * dt
            break
        else:
            std_old = std_new
    if not se_obtiene_resultado:
        _msg = "La función 'estima_reactividad_reactimetro' no pudo encontrar"
        _msg += "una zona de reactividad constante para estimar $_op"
        raise ValueError(_msg)

    return rho_op, t_in_ajuste


if __name__ == "__main__":


    folder = "data"
    archivo = "S-B23A-1.CIN"
    file_path = os.path.join(folder, archivo)

    t, n = lee_archivo_CIN(file_path)
