#!/usr/bin/env python3

import numpy as np
import matplotlib.pyplot as plt


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

    >>> a = np.array([3, 6, 7, 9, 1])
    >>> agrupa_datos(a, 2)
    Se agrupan 2 intervalos base
    array([ 9, 16], dtype=uint32)
    >>> agrupa_datos(a, 2, 0.3)
    Se agrupan 2 intervalos base
    Intervalo de adquisición agrupado: 0.6 s
    (array([ 9, 16], dtype=uint32), 0.6)
    '''

    data = np.array(data)
    if n_datos == 1:
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
            return datos_agrupados, dt_agrupado


def rate_from_timestamp(tiempo_entre_pulsos):
    """
    Estima la tasa de cuentas e incerteza a partir del tiempo entre pulsos

    Parámetros
    ----------
        tiempo_entre_pulsos : numpy array
            Vector con los tiempos entre pulsos. Cuidado con las unidades.

    Resultados
    ----------
        R_mean : float
            Tasa de cuentas promedio
        R_std : float
            Desviación estandar del promedio de la tasa de cuentas.
            Se calcula con la fórmula de propagación de errores a primer órden.
    """
    # Promedio
    _dt_mean = np.mean(tiempo_entre_pulsos)
    R_mean = 1.0/_dt_mean
    # Desvío
    _dt_std = np.std(tiempo_entre_pulsos, ddof=1) \
        / np.sqrt(len(tiempo_entre_pulsos))
    # Fórmula de propagación de errores a primer orden
    R_std = _dt_std / _dt_mean**2
    return R_mean, R_std


def timestamp_to_timewindow(datos, dt, units_in, units_out, tb):
    """
    Convierte los datos de time-stamp en cantidad de pulsos en dt

    Parámetros
    ----------
        datos : (list of) numpy array
            Datos expresados como tiempos de llegada de cada pulso
        dt : float or int
            Intervalo temporal en que se agruparán los pulsos
        units_in : string ('segundos', 'pulsos')
            Unidad de tiempo de `dt`
        units_out : string ('segundos', 'pulsos')
            Unidad de tiempo que se utilizará para hacer pulsos/dt
        tb : float
            Duración del pulso utilizado para contar

    Resultados
    ----------
        datos_binned : (list of) numpy array
            Pulsos agrupado en el dt
        tiempos: (list of) numpy array
            Cada elemento es un vector temporal asociado a cada bin centrado
            Los elementos están asociados a los elementos de `datos_binnes`,
            conservando el orden.
            (si `units_out` = 'segundos')
            Vector con índices dsde 0 ... Nbin-1 (si `units_out` = 'pulsos')

    >>> a = np.asarray([0, 2, 3, 6, 7, 8, 14])
    >>> y, t = timestamp_to_timewindow(a, 3, 'pulsos', 'pulsos', 1)
    >>> y
    array([2, 1, 3, 0])
    >>> t
    array([0, 1, 2, 3])

    """

    if isinstance(datos, list):
        _es_lista = True
    else:
        _es_lista = False
        datos = [datos]
    # Paso a unidades de pulsos
    if units_in == 'segundos':
        dt = np.float(dt / tb)
    elif units_in == 'pulsos':
        pass
    else:
        print('La unidad de dt_in sólo puede ser "segundos" o "pulsos"')
        quit()

    if units_out not in ['pulsos', 'segundos']:
        print('La unidad de salida sólo puede ser "segundos" o "pulsos"')
        quit()

    datos_binned = []
    tiempos = []
    for dato in datos:
        # --------------------------------------------------------------------
        # No recuerdo si esto era realmente necesario luego de esquivar el bug
        # que tiene numpy.bincount()
        #
        # if dato[-1] <= (2**64 / 2 - 1):
        #     dato = dato.astype(np.int64)
        # else:
        #     print('No se puede aplicar binncount(), buscar otra forma')
        #     quit()
        # --------------------------------------------------------------------
        # Cantidad de bines que se generan
        _Nbin = np.uint64(dato[-1] // dt)
        # Tiempo máximo exacto que voy a tomar respecto al dt_in
        t_exacto = (dato[-1] // dt) * dt
        # Índice del tiempo exacto
        i_exacto = np.searchsorted(dato, t_exacto, side='left')
        _dat = dato[0:i_exacto] // dt
        _bines = np.bincount(_dat.astype('int64'), minlength=_Nbin)
        # _bines = np.bincount(dato[0:i_exacto] // dt, minlength=_Nbin)
        if units_out == 'segundos':
            _bines = _bines / dt / tb
        datos_binned.append(_bines)

        # Construyo vectores temporales para cada vector leido
        tiempo = np.arange(_bines.size)

        if units_out == 'segundos':
            # vector centrado en los bines
            tiempo = tiempo + 0.5
            tiempo = tiempo * dt * tb
        tiempos.append(tiempo)

    # En caso de que no sea una lista
    if not _es_lista:
        datos_binned = datos_binned[0]
        tiempos = tiempos[0]

    return datos_binned, tiempos


def promedio_por_bloques(x, metodo=None, *args, **kargs):
    """
    Función para obtener la incerteza del promedio de los datos

    Es de utilidad cuando los datos están correlacionados, y deja de ser válido
    tomar el desvío del promedio como std/sqrt(N).

    Se basa en el método propuesto en http://dx.doi.org/10.1063/1.457480

    Se calculan promedios agrupando los datos en bloques. Se busca el punto
    donde cambiar el agrupamiento no modifique la incerteza obtenida.

    Además se implementan métodos para buscar la parte constante de forma
    automática (se podría hacer directamente mirando el gráfico). Es algo
    optativo.

    TODO: completar los métodos para obtener el valor constante

    Parameters
    ----------
        x : numpy arra
            Datos. Deben tener un valor medio constante.
        metodo : string ("ajuste_en_segmentos", "ajuste_lim_inf")
            Método para calcular de forma automática el punto donde el desvío
            estandar es independiente del agrupamiento.
            "ajuste_en_segmentos" : realiza ajustes lineales tomando segmentos
            de datos
            'ajuste_lim_inf" : realiza ajustes lineales cambiando el límite
            inferior del ajuste, siempre hasta el último dato
        kargs :
            "pts_por_ajuste" : float (5 por defecto)
                Cantidad de puntos que se utilizan para el ajuste lineal si se
                selecciona metodo="ajuste_en_segmentos"

    """

    # Promedio y desvío del promedio asumiendo que son independientes
    x_m, x_m_std = np.mean(x), np.std(x) / np.sqrt(len(x))

    fig1, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(10,8))
    ax1.plot(x, '.')
    ax1.set_xlabel("Índice de los dastos")
    ax1.set_ylabel("Datos")
    ax1.set_title(f"Asumiendo independencia $x$ = {x_m:.4f} +/- {x_m_std:.4f}")

    # Cantidad de datos
    n_x = len(x)
    std_estimate = []
    std_std_estimate = []
    n_points = []
    # Cantidad máxima de puntos por bloque que puedo tomar
    max_ptos_bloques = n_x // 2
    # Loop sobre la cantidad de puntos por bloque
    for pts_per_block in range(1, max_ptos_bloques + 1):
        # Cantidad de bloques
        num_blocks = n_x // pts_per_block
        # Cantida de datos máximo para hacer una división entera
        num_max = num_blocks * pts_per_block
        # Separo en bloques
        bloques = np.split(x[:num_max], num_blocks)
        # Promedio de cada bloque
        x_transformado = [np.mean(d) for d in bloques]
        # Desvío estandar de cada bloque
        _std_estimate = np.std(x_transformado) / np.sqrt(num_blocks - 1)
        std_estimate.append(_std_estimate)
        # Desvío estandar del desvío estandar de cada bloque (asumiendo indep.)
        std_std_estimate.append(_std_estimate / np.sqrt( 2 * (num_blocks - 1)))
        n_points.append(pts_per_block)

    std_estimate = np.asarray(std_estimate)
    std_std_estimate = np.asarray(std_std_estimate)
    n_points = np.asarray(n_points)

    ax2.errorbar(n_points, std_estimate, yerr=std_std_estimate, fmt='.',
                  capsize=5)
    ax2.set_xlabel("Tamaño del bloque")
    ax2.set_ylabel(r"$\sigma( \langle x \rangle)$")

    # Una vez con los valores por bloques, se busca un criterio para
    # seleccionar de forma automática el rango en donde tomar el sigma.
    # Se puede hacer a ojo, y es relativamente fácil.

    if metodo == "ajuste_en_segmentos":
        # ---------------------------------------------------------------------
        # Partiendo el gráfico en bloques y haciendo ajustes lineales
        # ---------------------------------------------------------------------
        # Cantidad de puntos que se utilizan para el ajuste lineal
        len_line = kargs.get("pts_por_ajuste", 5)
        # Cantidad de ajustes que se harán
        num_splits = len(std_estimate) // len_line
        # ültimo elemento que se utilizrá para hacer el split 
        max_data = len_line * num_splits
        # Se parten los datos en num_splits bloques
        est_splits = np.split(std_estimate[:max_data], num_splits)
        err_est_splits = np.split(std_std_estimate[:max_data], num_splits)
        points_split = np.split(n_points[:max_data], num_splits)
        # Para cada bloque se hace un ajuste lineal
        ps = []
        for pts, est, err_est in zip(points_split, est_splits, err_est_splits):
            p = np.polyfit(pts, est, deg=1,  w=1/err_est)
            ps.append(p)
        n_points = np.arange(1, num_splits + 1)

        ps = np.asarray(ps)
        # Busco los puntos cuya pendiente no sea muy grande
        ind_sel = abs(ps[:, 0]) <= 5e10
        #ax3.plot(n_points[ind_sel], ps[ind_sel, 0], '.')
        _label = f"Ajustando con {len_line} puntos"
        ax3.plot(n_points[ind_sel], ps[ind_sel, 1], '.', label=_label)
        #ax3.set_yscale('log')
        ax3.set_ylabel(r"$\sigma( \langle \$_{op} \rangle)$")
        ax3.set_xlabel(r"Segmento ajustado")
        ax3.legend()

    elif metodo == "ajuste_lim_inf":
        # ---------------------------------------------------------------------
        # Ajustes lineales variando el punto inferior del rango de ajuste
        # ---------------------------------------------------------------------
        ps = []
        lim_inf = []
        for i in range(len(std_estimate) - 5):
            p = np.polyfit(n_points[i:], std_estimate[i:], deg=1,
                           w=1/std_std_estimate[i:])
            ps.append(p)
            lim_inf.append(i)

        ps = np.asarray(ps)
        lim_inf = np.asarray(lim_inf)
        # Busco los puntos cuya pendiente no sea muy grande
        ind_sel = abs(ps[:, 0]) <= 3e20
        #ax3.plot(n_points[ind_sel], ps[ind_sel, 0], '.')
        ax3.plot(lim_inf[ind_sel], ps[ind_sel, 1], '.')
        #ax3.set_yscale('log')
        ax3.set_ylabel(r"$\sigma( \langle \$_{op} \rangle)$")
        ax3.set_xlabel(r"Inicio del ajuste")
    else:
        print("Método no reconocido")
        pass

    fig1.tight_layout()
    plt.show()

    return None


if __name__ == "__main__":
    import doctest
    doctest.testmod()
