#!/usr/bin/env python3

import numpy as np
import os
from lmfit import Minimizer, Parameters, report_fit
from uncertainties import ufloat
import matplotlib.pyplot as plt
import seaborn as sns
sns.set()

import sys
sys.path.append("/home/pablo/CinePy")
from modules.point_kinetics.soluciones_analiticas import solucion_in_hour_equation
from modules.point_kinetics.reactimeter import reactimetro
from modules.point_kinetics.direct_kinetic_solver import cinetica_directa


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


def archivo_referencia(fname):
    """
    Función auxiliar para leer archivo con resultados del FERCIN4
    """
    with open(fname, 'r') as f:
        datas = []
        for line in f:
            if not line.startswith('archivo'):
                if line.strip():
                    datas.append(line.split())
    datas.pop(-1)
    _dic = {}
    for data in datas:
        _dic[data[0]] = data[1:]
    return _dic


def algoritmo_angel_CEM(t, x, constantes, *args, **kargs):
    """
    Algoritmo para obtener la reactividad basado en la cinética espacial
    durante un experimento de rod-drop

    Parameters
    ----------
        t : numpy array
            Vector temporal
        x : numpy array
            Valores proporcionales a la densidad neutrónica
        constantes : touple or list (b, lambda, L*)
            b (list), lambda (list), reduced Lambda (float)
            b_i = beta_i / beta_eff
            L* = L/beta_eff
        kargs :
            Parámetros para definir el algoritmo
            "t_ref" : tupla (t_ref_i, t_ref_f) (0.1, 3)
                Define el rango que se utilizará para la normalización. Tiempos
                previos a la caída de la barra
            "t_fit" : tupla (t_fit_i, t_fit_f) (6, 80)
                Define el rango que se utilizará para el ajuste modal. Tiempos
                a partir del comienzo de la caída de la barra (t_cero)
            "epsilon": float (1e-4)
                Define el criterio de convergencia
            "n_iter_max" : int (20)
                Máximo número de iteraciones permitidas
            "verbose": boolean (False)
                Indica si se quieren imprimir en pantalla los resultados
                parciales de cada iteración
            "plot": boolean (False)
                Indica si se quieren graficar los resultados

    Returns
    -------
        results :
            Objeto de lmfit con los datos del ajuste

    TODO: ver por qué el error en tb es tan chicho
    TODO: ver promedios por bloque para evitar bias por correlación el datos
    """

    t_i_ref, t_f_ref = kargs.get("t_ref", (0.1, 3.0))
    t_i_fit, t_f_fit = kargs.get("t_fit", (6.0, 80.0))
    epsilon = kargs.get("epsilon", 1e-4)
    n_iter_max = kargs.get("n_iter_max", 20)
    verbose = kargs.get("verbose", False)
    plot = kargs.get("plot", False)

    b, lam, Lambda_red = constantes

    # Intervalo que se toma de referencia para normalizar y para obtener el t0
    ind_ref = (t >= t_i_ref) & (t <= t_f_ref)
    x_ref = np.mean(x[ind_ref])
    # Normalización de la señal medida
    x_nor = x / x_ref
    # Calcula tiempo cuando empieza a caer la barra
    t_cero = deteccion_borde(t, x_nor, (t_i_ref, t_f_ref))

    # -------------------------------------------------------------------------
    # 3. Ajuste para obtener A_3^(1)
    t_fit_i = t_cero + t_i_fit
    t_fit_f = t_cero + t_f_fit
    parametros = {
                  't_ajuste': (t_fit_i, t_fit_f),
                  'constantes_cineticas': constantes,
                  't1_vary': True,
                  'A1_vary': True,
                  'A3_vary': True,
                  }

    result = ajuste_cinetica_espacial(t, x_nor, **parametros)

    t1 = ufloat(result.params['t1'].value, result.params['t1'].stderr)
    tb = t1 - t_cero
    A3 = ufloat(result.params['A3'].value, result.params['A3'].stderr)
    if verbose:
        print(f"t_cero = {t_cero}")
        print(f"t_b = {tb:.3e} s (Primer ajuste)")
        print(f"A3 = {A3:.3e} (Primer ajuste")

        print(80*'-')
    # -------------------------------------------------------------------------
    # 4.  Cinética inversa para obtener $op
    dt = t[1] - t[0]
    rho_r, t_r, _ = reactimetro(x_nor - A3.n, dt, lam, b, Lambda_red)

    # Se estima el tiempo que tarda en caer la barra
    t_caida, indx_t_caida = deteccion_tiempo_caida(t_r, rho_r, t_cero)

    # Estimar la reactividad promedio en una zona constante
    rho_op, t_in_ajuste = estima_reactividad_reactimetro(t_r, rho_r, t_caida)

    if verbose:
        print("t_caida = {:.2f} s".format(t_caida))
        print(f"rho_op = {rho_op} obtenido a partir de t={t_in_ajuste:.2f} s")
        print(80*'-')

    # Se obtiene R(t)
    rho_en_t_caida = rho_r[t_r == t_caida][-1]
    # Se inicia en zero
    R_t = np.zeros_like(rho_r)
    # índices donde R(t) es distinto de cero y de uno
    ind_rt = (t_r >= t_cero) & (t_r <= t_caida)
    R_t[ind_rt] = rho_r[ind_rt] / rho_en_t_caida
    R_t[t_r > t_caida] = 1.0

    print(20*' ' + "Comienzo de la iteración")
    rho_old = rho_op
    _corta = False
    n_iter = 1
    while not _corta:
        print(f"Iteración {n_iter}")
        # ---------------------------------------------------------------------
        # 6. Simulación cinética directa
        rho_pk = rho_old.n * R_t
        n_sim, t_sim = cinetica_directa(rho_pk, 1, dt, lam, b, Lambda_red, 0)

        # ---------------------------------------------------------------------
        # 7.Ajuste para obtener t_b^1 y $om^(0)
        parametros = {
                      't_ajuste': (t_fit_i, t_fit_f),
                      'constantes_cineticas': constantes,
                      't1_vary': True,
                      'A3_vary': False,
                      }

        result = ajuste_cinetica_espacial(t_sim, n_sim, **parametros)

        t1 = ufloat(result.params['t1'].value, result.params['t1'].stderr)
        tb = t1 - t_cero
        rho_om0 = ufloat(result.params['rho'].value,
                        result.params['rho'].stderr)
        if verbose:
            print(f"t_b = {tb:.4e} s")
            print(f"$_{{om^0}} = {rho_om0:.3e}")

        # ---------------------------------------------------------------------
        # 8. Ajuste para obtener $om^i y A_3^i
        parametros = {
                      't_ajuste': (t_fit_i, t_fit_f),
                      'constantes_cineticas': constantes,
                      't1_vary': False,
                      't1_value': t1.n,
                      'A3_vary': True,
                      }

        result = ajuste_cinetica_espacial(t, x_nor, **parametros)

        rho_new = ufloat(result.params['rho'].value ,
                                    result.params['rho'].stderr)
        A3 = ufloat(result.params['A3'].value, result.params['A3'].stderr)
        if verbose:
            print(f"$_{{om^i}} = {rho_new:.3e}")
            print(f"A3_new = {A3:.3e}")
            print(80*'-')

        n_iter += 1

        # Condiciones para detener la iteración
        if np.absolute(rho_old.n - rho_new.n) < epsilon * rho_new.s:
            _corta = True
        if n_iter > n_iter_max:
            _corte = True
            print(f"No se obtuvo convergencia con {n_iter_max} iteraciones")
            print(f"Aumentar n_iter_max")
            return None
        rho_old = rho_new

    print(20*' ' + "Fin de la iteración")
    print(80*'-')

    # -------------------------------------------------------------------------
    print(20*' ' + "Estimación por cinética inversa")
    rho_op, t_i_fit, t_c = estima_reactimetro_CEM(t, x_nor, result, constantes,
                                                  t_cero)
    print(f"$_op = {rho_op}")
    print(f"t_ajuste_rho >= {t_i_fit:.4f} s")
    print(f"t_caida = {t_c:.4f} s")
    print(80*'-')

    print(20*' ' + "Estimación por método integral")
    _kargs = {'t_med': t , 'n_med_nor': x_nor}
    rho_oi = estima_integral_CEM(result, constantes, **_kargs)
    print(f"$_oi = {rho_oi}")
    print(80*'-')

    print(20*' ' + "Estimación por salto instantáneo")
    print(80*'-')
    rho_od = estima_salto_instantaneo_CEM(result, constantes, **_kargs)
    print(f"$_od = {rho_od}")
    print(80*'-')

    if plot:
        from mpl_toolkits.axes_grid1.inset_locator import (inset_axes,
                            InsetPosition, mark_inset)

        ind_fit = (t >= t_fit_i) & (t <= t_fit_f)
        best_fit = x_nor[ind_fit] + result.residual

        fig1, (ax1, ax2) = plt.subplots(2, 1, sharex=True,
                                       gridspec_kw={'height_ratios': [3, 1]},
                                       figsize=(9,7)
                                       )
        # Grafico de ajuste
        ax1.errorbar(t, x_nor, fmt='.', elinewidth=2, label='Mediciones',
                     capsize=4)
        ax1.plot(t[ind_fit], best_fit, 'r', zorder=3, label='Ajuste', lw=2)
        ax1.set_ylabel(r'$n(t)/n(0)$')
        # Gráfico de los límites el ajuste
        # ax1.vlines((t_fit_i, t_fit_f), ymin=-0.02, ymax=0.1, colors='g')
        # Create a set of inset Axes
        ax9 = plt.axes([0,0,1,1])
        # Manually set the position and relative size of the inset axes 
        ip = InsetPosition(ax1, [0.3,0.3,0.6,0.6])
        ax9.set_axes_locator(ip)
        # Mark the region corresponding to the inset axes on ax1 and draw lines
        mark_inset(ax1, ax9, loc1=2, loc2=4, fc="none", ec='0.5')
        ax9.errorbar(t, x_nor, fmt='.-')
        ax9.set_xlim(t_cero - 0.5, t_caida + 0.4)
        ax9.set_ylim(0, 1.02)
        # Grafico los tiempos característicos
        lin_ts = [t_cero, t1.n, t_caida]
        lin_strs = [r"$t_o$", r"$t_o + t_b$", r"$t_{caida}$"]
        for lin_t, lin_str in zip(lin_ts, lin_strs):
            ax9.axvline(lin_t, lw=1, label=lin_str, c='k')
            ax9.text(lin_t+0.02, 0.5, lin_str, {'color':'k'})
        ax9.set_xlabel("t [s]")
        ax9.set_ylabel(r'$n(t)/n(0)$')

        handles,labels = ax1.get_legend_handles_labels()
        handles = handles[::-1]
        labels = labels[::-1]
        ax1.legend(handles, labels, loc="upper center", ncol=2)

        # Gráfico de residuos
        ax2.plot(t[ind_fit], result.residual )
        ax2.set_xlabel(r'$t$ [s]')
        ax2.set_ylabel(r'Residuos')
        fig1.subplots_adjust(hspace=0.1)
        fig1.tight_layout()
    plt.show()

    return result


def estima_reactimetro_CEM(t, n_nor, result, constantes, t_o, *args, **kargs):
    """
    Estima la reactividad usando cinética invera junto con la cinética modal.

    Se corrige el offset en los datos medidos utilizando el valor A3 obtenido
    del algoritmo para la CEM

    TODO: Falta calcular mejor la incerteza en $_op (ver promedios por bloque)

    Parameters
    ----------
        t : numpy array
            Vector temporal
        n : numpy array
            Valores medidos y normalizados
        result : lmfit object
            Resultados del último ajuste (t1 está fijo)
        constantes : touple or list (b, lambda, L*)
            b (list), lambda (list), reduced Lambda (float)
            b_i = beta_i / beta_eff
            L* = L/beta_eff
        t_o : float
            Tiempo estimado en donde comienza a insertarse la barra

    Returns
    -------
        rho_op : ufloat
            Reactividad estimada
        t_in_rho : float
            Tiempo a partir del cual se promedia la reactividad
        t_caida : float
            Tiempo estimado donde finaliza la inserción de barra

    """
    b, lam, Lambda_red = constantes
    A3 = ufloat(result.params['A3'].value, result.params['A3'].stderr)
    t1 = result.params['t1'].value
    dt = t[1] - t[0]
    # Con el nuevo A3 se calcula nuevamente la $op
    rho_r, t_r, _ = reactimetro(n_nor - A3.n, dt, lam, b, Lambda_red)
    # Se estima el tiempo que tarda en caer la barra
    t_caida, indx_t_caida = deteccion_tiempo_caida(t_r, rho_r, t_o)
    # Estimar la reactividad promedio en una zona constante
    rho_op, t_in_rho = estima_reactividad_reactimetro(t_r, rho_r, t_caida)
    rho_op *= -1

    fig, (ax1, ax2) = plt.subplots(2, 1)
    # Gráfico de la reactividad
    ax1.plot(t_r, rho_r, '.')
    in_rho_op = t >= t_in_rho
    _lab = f"$\$_{{op}}$ = {rho_op:.3f}"
    ax1.plot(t_r[in_rho_op], -rho_op.n * np.ones(sum(in_rho_op)), 'r',
             label=_lab, lw=2)
    ax1.set_xlabel(r"Tiempo [s]")
    ax1.set_ylabel(r"$(t)")
    ax1.legend()
    ax1.set_title("TODO: falta estimar correctamente la incerteza")

    # Gráfico de la R(t)

    # Se obtiene R(t)
    rho_en_t_caida = rho_r[t_r == t_caida][-1]
    # índices donde R(t) es distinto de cero y de uno
    ind_rt = (t_r >= t_o) & (t_r <= t_caida)
    R_t = rho_r[ind_rt] / rho_en_t_caida
    ax2.plot(t_r[ind_rt], R_t, '.')
    # Gráfico te tiempos característicos
    lin_ts = [t_o, t1, t_caida]
    lin_strs = [r"$t_o$", r"$t_o + t_b$", r"$t_{caida}$"]
    _of = [0.02, 0.02, -0.15]
    for lin_t, lin_str, of in zip(lin_ts, lin_strs, _of):
        ax2.axvline(lin_t, lw=1, label=lin_str, c='r')
        ax2.text(lin_t + of, 0.5, lin_str, {'color':'r'})

    ax2.set_xlabel(r"Tiempo [s]")
    ax2.set_ylabel(r"R(t)")

    fig.tight_layout()

    return rho_op, t_in_rho, t_caida


def estima_integral_CEM(result, constantes, *args, **kargs):
    """
    Estima la reactividad usando método integral junto con la cinética modal.

    Para la integración se utiliza la función f(t) con los mejores parámetros
    del ajuste CEM.

    Se corrige el offset en los datos medidos utilizando el valor A3 obtenido
    del algoritmo para la CEM.

    Se toma el tiempo inicial de la integración como t1 = t0 + tb

    Se toma el tiempo final como t1 + 600s

    TODO: Falta calcular la incerteza en $_oi

    Parameters
    ----------
        result : lmfit object
            Resultados del último ajuste (t1 está fijo)
        constantes : touple or list (b, lambda, L*)
            b (list), lambda (list), reduced Lambda (float)
            b_i = beta_i / beta_eff
            L* = L/beta_eff
        kargs :
            't_med' : Vector temporal de la medición
            'n_med_nor' : Vector de datos medidos y normalizados

    Returns
    -------
        rho_oi : loat
            Reactividad estimada

    """

    t_med = kargs.get('t_med')
    n_med_nor = kargs.get('n_med_nor')

    rho = result.params['rho'].value
    t1 = result.params['t1'].value
    n0 = result.params['n0'].value
    A1 = result.params['A1'].value
    A3 = result.params['A3'].value
    _args = rho, t1, n0, A1, A3

    # Tiempos en que se va a integrar, (t1 = t_o + t_b , t1 + 10min)
    t_int = np.linspace(t1, t1 + 600, 100000)
    f_t_int = salto_instantaneo_espacial(t_int, *_args, constantes)
    n_t_int = (f_t_int - A3) / (1 - A3)

    b, lam, Lambda_red = constantes
    # calculo la integral
    int_n = np.trapz(n_t_int, t_int)
    # Calculo la reactividad
    rho_oi = (Lambda_red + np.dot(b, 1/lam)) / int_n
    # Gráficos
    fig, ax = plt.subplots(1, 1)
    # Función n(t) en todo el rango
    t = np.linspace(0, t1 + 600, 100000)
    f_t = salto_instantaneo_espacial(t, *_args, constantes)
    n_t = (f_t - A3) / (1 - A3)

    n_med = (n_med_nor - A3) / (1 - A3)
    ax.plot(t_med, n_med, '.', label="Medición")
    ax.plot(t, n_t, label="Ajuste CEM", lw=2)
    _lab = f"$\$_{{oi}}$ = {rho_oi:.3f}"
    ax.fill_between(t_int, n_t_int, color='r', label=_lab)

    ax.set_xlabel(r"Tiempo [s]")
    ax.set_ylabel(r'$n_{CEM}(t)$')
    ax.set_yscale('log')
    ax.legend()

    return rho_oi


def estima_salto_instantaneo_CEM(result, constantes, *args, **kargs):
    """
    Estima la reactividad usando método del salto instantáneo junto con la
    cinética modal.

    Para obtener el salto instantáneo se utiliza la función f(t) con los
    mejores parámetros del ajuste CEM.

    Se corrige el offset en los datos medidos utilizando el valor A3 obtenido
    del algoritmo para la CEM.

    Se toma al tiempo del salto instantáneo como t1 =  t0 + tb

    TODO: Falta calcular la incerteza en $_oi
    TODO: El méotdo para estiar el salto instantáneo no parece ser muy robusto


    Parameters
    ----------
        result : lmfit object
            Resultados del último ajuste (t1 está fijo)
        constantes : touple or list (b, lambda, L*)
            b (list), lambda (list), reduced Lambda (float)
            b_i = beta_i / beta_eff
            L* = L/beta_eff
        kargs :
            't_med' : Vector temporal de la medición
            'n_med_nor' : Vector de datos medidos y normalizados

    Returns
    -------
        rho_od : loat
            Reactividad estimada

    """

    t_med = kargs.get('t_med')
    n_med_nor = kargs.get('n_med_nor')

    rho = result.params['rho'].value
    t1 = result.params['t1'].value
    n0 = result.params['n0'].value
    A1 = result.params['A1'].value
    A3 = result.params['A3'].value
    _args = rho, t1, n0, A1, A3

    b, lam, Lambda_red = constantes
    # Tiempo del salto instantáneo pasado a numpy array para ser evaluado en
    # la función f(t)
    t1_np = np.linspace(t1, t1+1, 50)
    # Evaluación
    f_t_salto = salto_instantaneo_espacial(t1_np, *_args, constantes)
    # Puede haber problemas en t1
    f_t_salto = f_t_salto[t1_np > t1][0]
    n_t_salto = (f_t_salto - A3) / (1 - A3)
    # Calculo la reactividad
    rho_od = 1 / n_t_salto - 1

    # Gráficos
    fig, ax = plt.subplots(1, 1)
    # Evaluación de la f(t) en los rangos de la medición
    t = np.linspace(t_med[0], t_med[-1], 2000)
    f_t = salto_instantaneo_espacial(t, *_args, constantes)
    n_t = (f_t - A3) / (1 - A3)
    # Curva medida
    n_med = (n_med_nor - A3) / (1 - A3)
    ax.plot(t_med, n_med, '.', label="Medición")
    ax.plot(t, n_t, label="Ajuste CEM", lw=1)
    _lab = f"$\$_{{od}}$ = {rho_od:.3f}"
    # Salto instantáneo
    ax.plot(t1, n_t_salto, 'ro', label=_lab)
    ax.set_xlabel(r"Tiempo [s]")
    ax.set_ylabel(r'$n_{CEM}(t)$')
    ax.set_xlim(t1-4, t1 + 5)
    # ax.set_yscale('log')
    ax.legend()

    return rho_od


if __name__ == "__main__":

    pass

