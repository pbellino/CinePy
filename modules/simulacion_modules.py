#!/usr/bin/env python

import glob
import os
import numpy as np
from uncertainties import ufloat
from mcnptools import Ptrac
from modules.alfa_rossi_procesamiento import arossi_una_historia_I
from modules.io_modules import read_PTRAC_CAP_bin


def separa_en_historias_sin_accidentales(data):
    """
    Función para separar las capturas registradas en PTRAC por historias

    Cada historia corresponde a los neutriones capturados durante un mismo
    evento de fuente (notar que difiera de la definición de historia utilizada
    al procesar datos de una medicion). Es decir, cada historia es una cadena
    de fisión generada por un evento de fuente.

    De esta manera no se tienen en cuenta la parte no-correlacionada de los
    métodos de ruido, pues siempre se analiza siempre la misma cadena de
    fisión.

    Es de utilidad para comparar los resultados respecto a la simulación
    completa de una medición, donde se mezclan las cadenas de fisión mediante
    el agregado del tiempo de emisión de la fuente.

    Parámetros
    ----------
        data : list of lists
            Lista que devuelve la función 'read_PTRAC_CAP_bin()'
    Resultados
    ----------
       times_all : list of lists
            Cada elemento de la lista corresponde a un detector distinto. Cada
            elemento es una lista de listas, con cada elemento indica los
            tiempos de captura para cada nps del archivo (cadena de fisión).
    """

    data_out = np.asarray(data)
    # Sólo me quedo con los datos de: nps, tiempos y celda
    data_out = data_out[:, 0:3]
    # Ordeno datos de acuerdo a número de historia creciente
    data_out = data_out[data_out[:, 0].argsort()]
    #
    # TODO: separar por celda en este punto cuando se necesite
    #
    times_all = []  # Lista de tiempos para todos los detectores
    # Dejo planteado el loop sobre los detectores para un futuro
    for _ in ['det1']:    # Este loop recorre todos los detectores
        # Encuentra los valores e índices de historia
        _, _indxs, _counts = np.unique(data_out[:, 0],
                                       return_index=True, return_counts=True)
        # _new = []  # Datos completas con más de una captura (debugg)
        _times = []  # Tiempos con más de una captura
        for _inx, _count in zip(_indxs, _counts):
            if _count > 1:
                # _new.append(data_out[_inx:_inx + _count, :])
                _times.append(np.sort(data_out[_inx:_inx + _count, 1])*1e-8)
        times_all.append(_times)
    return times_all


def genera_tallies(archivo_tallies, def_tallies, *args, **kargs):
    """
    Genera los tallies F8 con los GATES sucesivos para obtener la RAD

    Parámetros
    ----------
        archivo_tallies : string
            Nombre del archivo donde se guardaran las tallies

        def_tallies : dict
            Diccionario con los parámetros que se utilizarán para construir
            las tallies. Las claves deben ser:
                'id_det' : string
                    ZAID del elemento donde se quiere analizar las capturas
                    (helio-3, boro-10, etc).
                'celdas_detector' : string
                    Celda en donde se analizarán las capturas (detector)
                'gate_width' : float (en segundos)
                    Ancho de la ventana temporal (es el bin en el histogama de
                    la distribución de alfa-Rossi).
                'gate_maxim' : float (en segundos)
                    Es el máximo tiempo que se analizará para cada trigger.
                    Haciendo `gate_maxim` / `gate_width` se obtiene el número
                    de bines de la distribución.
    """
    try:
        id_det = def_tallies['id_det']
        celdas_detector = def_tallies['celdas_detector']
        gate_width_s = def_tallies['gate_width']
        gate_maxim_s = def_tallies['gate_maxim']
    except KeyError:
        print('No se especificaron todos los datos para las tallies')
        quit()

    # Convierto gates de segundos a shakes
    gate_width = gate_width_s * 1e8
    gate_maxim = gate_maxim_s * 1e8
    # Construyo vector de gates
    pd_gates = np.arange(0, gate_maxim, gate_width)
    N_bins = np.int(gate_maxim / gate_width)
    print('Distribución de a-Rossi con {} bins'.format(N_bins))

    with open(archivo_tallies, 'w') as f:
        f.write('c ' + '-'*40 + '\n')
        f.write('c Definición de las tallies con GATE\n')
        f.write('c ' + '-'*40 + '\n')
        # Tally sin GATE
        f.write('FC0008 Capturas en He3 - Sin GATE\n')
        f.write('F0008:n {}\n'.format(celdas_detector))
        f.write('FT0008 CAP {} \n'.format(id_det))
        f.write('c\n')
        # Tallies con GATE
        for i, pd_gate in enumerate(pd_gates, 1):
            f.write('FC{:03d}8 Capturas en He3 - PD={:.2e}s GW={:.1e}s\n'.format(i, pd_gate/1e8, gate_width/1e8))
            f.write('F{:03d}8:n {}\n'.format(i, celdas_detector))
            f.write('FT{:03d}8 CAP {} GATE {} {}\n'.format(i, id_det, pd_gate,
                                                           gate_width))
            f.write('c\n')
        f.write('c Fin de las tallies con gate\n')
        f.write('c ' + '-'*40 + '\n')
    print('Se generó el archivo de tallies: ' + archivo_tallies)
    return None


def agrega_tiempo_de_fuente(tasa, nps, datos):
    """
    Agrega los tiempos de fuente al tiempo registrado en el PTRAC

    Se asume una distribución exponencial de tiempos entre eventos y se lo
    suma a todas las capturas que provienen de una misma historia

    Parámetros
    ----------

        tasa : double [1/s]
            Tasa de eventos de fuente (fisiones espontáneas) por segundo. Se
            debe calcular en base a la actividad de la fuente.

        nps : int
            Cantidad de eventos de fuente (fisiones espontáneas) generadas en
            MCNP

        datos : list of list
            Los datos leídos del archivo PTRAC. El formato debe ser:
                1er columna -> El número de historia (nps)
                2da columna -> Los tiempos registrados
                3ra columna -> La celda donde se registró
            Si hay más columnas son ignoradas.

    Resultados
    ----------
        data_sorted : numpy array
            Formado por tres vectores [nps_hist tiempos cells]
            nps_hist :
                Lista que identifica a cuál historia pertenece cada captura. En
                principio  no tiene mucha utilidad
            times :
                Lista ordenada de los tiempos de captura.
            cells :
                Celda en donde se produjo la captura. Sirve para diferenciar
                distintos detectores.

    Cada elemento de estos tres vectores hace referencia a una captura.

    Ejemplo: data_sorted[3, :] hacen referencia al tiempo de captura
    data_sorted[3, 1] del cuarto pulso que se produjo en la celda
    data_sorted[3, 2] y que pertenece a la historia data_sorted[3, 0]
    """

    # Convierto a array de numpy
    datos = np.asarray(datos)
    # Ordeno por historia para después buscar más fácil
    datos = datos[datos[:, 0].argsort()]
    # Número de historia de cada evento
    nps_hist = np.asarray(datos[:, 0], dtype='int64')
    # Cantidad de historias totales detectadas
    # num_hist_tot = np.unique(nps_hist).shape[0]
    # Tiempos del PTRAC en segundos
    times = np.asarray(datos[:, 1], dtype='float64') * 1e-8
    # Celda donde se produjo la captura
    cells = np.asarray(datos[:, 2], dtype='int64')

    # Se generan número con distribución exponencial
    beta = 1.0 / tasa
    # Genero los tiempos para cada evento de fuente
    np.random.seed(313131)
    # Tiempo para todos los eventos de fuente
    src_time_tot = np.cumsum(np.random.exponential(beta, nps))
    # Tiempo sólo para los eventos que contribuyeron en el PTRAC
    # - Esto lo comento para conservar la relación entre el tiempo generado
    # - y la histroria cuando quiero procesar neutrones y fotones
    # src_time = np.random.choice(src_time_tot, size=num_hist_tot,
    #                        replace=False)
    src_time = src_time_tot[np.unique(nps_hist)-1]
    for n, t in zip(np.unique(nps_hist), src_time):
        indx_min = np.searchsorted(nps_hist, n, side='left')
        indx_max = np.searchsorted(nps_hist, n, side='right')
        times[indx_min:indx_max] += t

    # Ordeno los tiempos y mantengo asociado el numero de historia y la celda
    _temp = np.stack((nps_hist, times, cells), axis=-1)
    # Ordeno para tiempos crecientes
    data_sorted = _temp[_temp[:, 1].argsort()]

    return data_sorted


def RAD_sin_accidentales(nombre, dt_s, dtmax_s):
    """
    Función para obtener la distribución RAD a partir del PTRAC

    El objetivo es comparar con la RAD obtenida con tallies F8 + GATES. Por
    este motivo se deben eliminar las coincidencias accidentales.

    Notar que pueden haber algunas diferencias porque la forma de obtener la
    RAD con las tallies y con los algoritmos míos (arossi_una_historia_I) son
    distintos. Yo obligo a que todos los triggers alcancen el 'dtmax_s'. Las
    tallies F8 en cambio, abren un GATE para cualquier trigger.

    Parámetros
    ----------
        nombre : string
            Nombre del archivo binario PTRAC obtenido con event=CAP

        dt_s : float (segundos)
            Intervalo temporal para cada bin de la distribución

        dtmax : float (segundos)
            Máximo intervalo de la distribución de alfa-Rossi

    Importante
    ----------
        Los valores dt_s y dtmax deben coincidir con los utilizados para
        construir las tallies F8 con GATES sucesivas
    """
    # Leo el archivo binario de PTRAC con event=CAP
    datos, header = read_PTRAC_CAP_bin(nombre)

    # Convierto a array numpy
    datos = np.asarray(datos)
    # Números de historia
    nps = np.asarray(datos[:, 0], dtype='int64')
    # Tiempos
    timestamp = np.asarray(datos[:, 1], dtype='float64') * 1e-8
    # Obtiene los timestamp para una misma historia
    times_historia = []
    for n in set(nps):
        indx = np.where(nps == n)
        # Timestamp por historia y ordenado
        list_by_hist = np.sort(timestamp[indx])
        # Se fija t=0 en el primer pulso
        list_by_hist -= list_by_hist[0]
        times_historia.append(list_by_hist)

    # Datos de la RAD
    historias = []
    for time in times_historia:
        P_historia, _, N_trig, P_trig =  \
            arossi_una_historia_I(time, dt_s, dtmax_s, 1)
        # print(P_trig)
        # Analizo los triggers para no tener que operar sobre P_historia
        # (molesta la normalización en este caso)
        if P_trig.size:
            # Sumo todos trigger
            historias.append(np.sum(P_trig, axis=0))
    # Sumo entre todos los eventos para obtener la distribución de alfa-Rossi
    RAD = np.sum(historias, axis=0)
    return RAD


def lee_nps_entrada(nombre):
    """
    Lee la cantidad de historias simuladas desde el archivo de entrada de MCNP
    """
    with open(nombre, 'r') as f:
        for line in f:
            if line.startswith('NPS'):
                return int(float(line.split()[-1]))
        print('No se pudo leer la cantidad nps del archivo: ' + nombre)


def read_PTRAC_estandar(archivo, tipo, eventos):
    """
    Función para leer archivo PTRAC estandar de MCNP

    Parametros
    ----------
        archivo : string
            Nombre del archivo que se quiere leer
        tipo : string ('asc', 'bin')
            Tipo del archivo PTRAC. ASCII o binario ('asc' o 'bin')
        eventos : list of strings ('src', 'ter', 'bnk', 'col', 'src')
            Lista con los eventos que se desean leer

    Resultados
    ----------
        data : list of lists
           Cada elemento de data contiene una lista con:
                [numero_historia, tiempo, celda, tipo_de_evento]

    """

    Nbatch = 1000
    if tipo == 'bin':
        p = Ptrac(archivo, Ptrac.BIN_PTRAC)
    elif tipo == 'asc':
        p = Ptrac(archivo, Ptrac.ASC_PTRAC)
    else:
        raise NameError('Tipo de archivo no reconocido.' +
                        'Debe ser "bin" o "asc"')

    event_types = {'sur': Ptrac.SUR, 'ter': Ptrac.TER, 'bnk': Ptrac.BNK,
                   'col': Ptrac.COL, 'src': Ptrac.SRC}

    try:
        eventos_selec = [event_types[s] for s in eventos]
    except KeyError:
        print('Tipo de evento no válido ("sur", "ter", "bnk", "col", "src")')

    # Se obtienen las historias
    hists = p.ReadHistories(Nbatch)

    data = []
    while hists:
        # Loop en las historias
        for h in hists:
            # Número de historia
            numero_nps = h.GetNPS().NPS()
            # Loop en los eventos
            for e in range(h.GetNumEvents()):
                event = h.GetEvent(e)
                # Se guardan los eventos seleccionados
                if event.Type() in eventos_selec:
                    data.append([
                                  numero_nps,
                                  event.Get(Ptrac.TIME),
                                  int(event.Get(Ptrac.CELL)),
                                  event.Type(),
                                  ]
                                )

                # if event.Type() == Ptrac.SUR:
                #    print(event.Get(Ptrac.X))

        hists = p.ReadHistories(Nbatch)
    return data, None


def lee_tally_E_mcnptools(filename, tally):
    """ Read energy tally from mctal file using MCNPTools """

    from mcnptools import Mctal, MctalTally

    m = Mctal(filename)
    if tally not in m.GetTallyList():
        raise ValueError('El número de tally no existe en el archivo')

    tal = m.GetTally(tally)
    bins = tal.GetEBins()
    tfc = MctalTally.TFC
    val = []
    err = []
    for e in range(len(bins)):
        val.append(tal.GetValue(tfc, tfc, tfc, tfc, tfc, tfc, e, tfc))
        err.append(tal.GetError(tfc, tfc, tfc, tfc, tfc, tfc, e, tfc))
    return map(np.asarray, (bins, val, err))


def lee_tally_E_facet_mcnptools(filename, tally):
    """ Read energy tally with facets from mctal file using MCNPTools """

    from mcnptools import Mctal, MctalTally

    m = Mctal(filename)
    if tally not in m.GetTallyList():
        raise ValueError('El número de tally no existe en el archivo')

    tal = m.GetTally(tally)
    bins = tal.GetEBins()
    facets = tal.GetFBins()
    tfc = MctalTally.TFC
    vals = []
    errs = []
    for f in range(len(facets)):
        val = []
        err = []
        for e in range(len(bins)):
            val.append(tal.GetValue(f, tfc, tfc, tfc, tfc, tfc, e, tfc))
            err.append(tal.GetError(f, tfc, tfc, tfc, tfc, tfc, e, tfc))
        vals.append(val)
        errs.append(err)
    return map(np.asarray, (bins, vals, errs))


def corrige_t_largos(datos, tasa, nps_tot, metodo='elimina'):
    """
    Corrección de los tiempos muy largos en medios multiplicativos

    Si el medio multiplicativo está cercano a crítico, se pueden generar
    cadenas de fisión muy largas, mucho más allá del tiempo del último
    evento de fuente.

    Parámetros
    ----------
        datos : numpy ndarray
            Datos de la simulación que salen de `agrega_tiempo_de_fuente()`.
            Son tres columnas con: [nps_hist tiempos cells]
        tasa : double
            Tasa de la fuente (eventos de fuente por unidad de tiempo)
        npts_tot : int
            Cantidad total de eventos de fuente
        metodo : str ('elimina', 'pliega')
            'elimina' : Elimina todos los eventos con un t > nps_tot/tasa
            (que es el tiempo total de medición). Tiene la desventaja de que
            los primeros puntos también deben ser corregidos hasta alcanar un
            régimen estacionario
            'plegado' :  a los tiempos t > t_med = nps_tot/tasa les calcula el
            módulo(t_med) y los agrega a los eventos dentro de t < t_med.
            Permite corregir tanto el final como el comienzo de la simulación.

    Resultados
    ----------
        datos_corregidos : numpy ndarray
            Datos en el mismo formato que `datos` [nps_hist tiempos cells]
    """
    # Tiempo total de la medición
    t_med = nps_tot / tasa
    if metodo == "elimina":
        # Elimina todo t > t_med
        datos_corregidos = datos[datos[:, 1] < t_med]
    elif metodo == "pliega":
        # Pliegatodo t > t_med
        datos[:, 1] = datos[:, 1] % t_med
        # Ordena los tiempos
        datos_corregidos = datos[datos[:, 1].argsort()]

    return datos_corregidos


def calcula_param_cin(dic, verbose=False):
    """
    Calcula parámetros cinéticos a partir de las estimaciones de MCNP

    Escribe los resultados en un archivo llamado <parametros.cin>
    Utiliza el modulo uncertainties para propagación de incertezas.

    Si <dic> no contiene la información de parámetros necesarias, se sale.
    Dicha información es el "Lambda", "beta_eff", etc (todo lo que estima MCNP6
    cuando se le da la opción "KOPTS KINETICS=yes"

    Parámetros
    ----------
        dic : dict
            Diccionario que devuelve la función read_kcode_out()
        verbose : Bool (False)
            Cuando es True imprime en pantalla las estimaciones realizadas

    Resultados
    ---------
        dic_out: dic
            Diccionaario con keys
                dic_out['keff']
                dic_out['Lambda']
                dic_out['rho']
                dic_out['rho_dol']
                dic_out['alfa']
            Todos los valores son dtype=ufloat (del paquete uncertainties9

        'parametros.cin'
            Archivo que se escribe con los resultados estimados. Sobreescribe
            el archivo en caso de que existiera

    """

    if dic['Lambda'] is None:
        print("El diccionario de entrada no tiene los datos necesarios")
        print("calcula_param_cin() se aborta")
        quit()

    # Magnitudes estimadas por MCNP
    keff = ufloat(*dic['keff'])
    Lambda = ufloat(*dic['Lambda'])
    beta = ufloat(*dic['betaeff'])

    # Magnitudes derivadas
    rho = (keff-1) / keff
    rho_dol = rho / beta
    alfa = (beta - rho) / Lambda

    data_str = "#" + 79*"-" + "\n"
    data_str += "# Magnituds simuladas por MCNP\n"
    data_str += "#" + 79*"-" + "\n"
    data_str += "k_effectivo =  {:.2u}\n".format(keff)
    data_str += "Lambda = {:.2e}\n".format(Lambda)
    data_str += "beta efectivo = {:.2e}\n".format(beta)
    data_str += "#" + 79*"-" + "\n"
    data_str += "# Magnituds derivadas\n"
    data_str += "#" + 79*"-" + "\n"
    data_str += "rho = {:.2u}\n".format(rho)
    data_str += "$ = {:.2u} dólares\n".format(rho_dol)
    data_str += "alfa = {:.2u} 1/s\n".format(alfa)

    out_name = 'parametros.cin'
    with open(out_name, 'w') as f:
        f.write(data_str)

    dic_out = {}
    dic_out['keff'] = keff
    dic_out['Lambda'] = Lambda
    dic_out['rho'] = rho
    dic_out['rho_dol'] = rho_dol
    dic_out['alfa'] = alfa

    if verbose:
        print(data_str)

    return dic_out


def separa_capturas_por_celda(datos_n):
    """
    Separa los datos dependiendo de las celdas donde se efectuaron las capturas

    Parámetros
    ----------
        datos_n : numpy_array o list of list
            Datos leidos del archivo ptrac

    Resultados
    ----------
        separados : dict
            Diccionario cuyas claves son los números de celda (positivos) y los
            valores los numpy array con mismo formato que 'datos_n'
        origen : dict
            Diccionario cuyas claves son los números de celda (negativos y
            positivos) y los valores la cantidad de captura en cada celda y con
            cada signo. Sirve para analizar cuántas detecciones provienen
            directas de fuente y cuántas de fisiones

    """
    # Por las dudas fuerzo numpy arrray
    datos = np.asarray(datos_n)
    _celdas_all = datos_n[:, 2]
    _celdas = np.unique(_celdas_all)
    origen = {}
    for celda in _celdas:
        origen[str(int(celda))] = np.shape(datos[datos[:, 2] == celda])[0]
    separados = {}
    for celda in np.unique(np.abs(_celdas)):
        separados[str(int(celda))] = datos[(datos[:, 2] == celda) |
                                           (datos[:, 2] == -celda)
                                           ]
    return separados, origen


def merge_outputs(carpetas=None, nombre='case', dos_corridas=False):
    """
    Función para leer los archivos ptrac de cada carpeta y juntarlos. No los
    ordena, sólo hace un append cambiando el nps para que no se repitan.

    Se asume que el input tiene el mismo nombre que la carpeta en donde se
    encuentra.

    Se escriben aarchivos binarios .npy con los datos ya juntados. Esto se hace
    para evitar tener que leer los archivos PTRAC cada vez que se quiera
    reprocesar.

    NOTA: si los archivos existen, la función devuelve los datos leidos de
    archivos .npy existentes. NO VUELVE A LEER LOS ARCHIVOS PTRAC.

    Parámetros
    ----------
        carpetas : list of strings
            Lista con los nombres de las carpetas que se quieren leer
            Si no se especifica se toma 'case_001, case_002, ...'
        nombre : str
            Nombre con que se identifican las carpetas, se lee "nombre_xxx"
        dos_corridas : boolean
            Si se hicieron una corrida para neutrones y otra para fotones,
            con esta opción se indica que lea ambos archivos en la misma
            carpeta. Serán "nombre_carpeta"_n.p (para neutrones
            "nombre_carpeta"_p.p (para fotones).

    Resultados
    ----------
        out : numpy array
            Datos agrupados entre todas las carpetas. No están ordenados. Tiene
            el mismo formato que la salida de las funciones de lectura de los
            archivos PTRAC.
        nps_tot : float
            Cantidad de eventos totales. Es la suma de los nps de cada carpeta.

        Archivos 'nombre_n_merged.npy'  'nombre_n_merged.npy' y
        'nombre_np_nps_merged.npy' (si dos_corridas=True)

        Archivos 'nombre_merged.npy' y 'nombre_nps_merged.npy (si
        dos_corridas=False)
    """

    # Se fija si existen archivos binarios con los datos ya agrupado
    # Si es así, se leen dichos valores y se sale de la función,
    # No se leen los archivos PTRAC
    if dos_corridas:
        _nom_n = nombre + "_n_merged.npy"
        _nom_p = nombre + "_p_merged.npy"
        # Asumo que también existe el archivo con info del nps
        _nom_nps = nombre + "_np_nps_merged.npy"
        if os.path.exists(_nom_n) or os.path.exists(_nom_p):
            print("Ya existen archivos con resultados combinados")
            print("No se procesa ni se escriben nuevos archivos.")
            print("Se leen archivos existentes.")
            return np.load(_nom_n), np.load(_nom_p), np.load(_nom_nps)
    else:
        _nom = nombre + "_merged.npy"
        # Asumo que también existe el archivo con info del nps
        _nom_nps = nombre + "_nps_merged.npy"
        if os.path.exists(_nom):
            print("Ya existen archivos con resultados combinados")
            print("No se procesa ni se escriben nuevos archivos.")
            print("Se leen archivos existentes.")
            return np.load(_nom), np.load(_nom_nps)

    # Se leen los archivos PTRAC
    parent = os.getcwd()
    if not carpetas:
        carpetas = glob.glob(nombre + '_*')
    nps_tot = 0
    out_n = np.empty((0, 9), float)
    out_p = np.empty((0, 4), float)
    out = np.empty((0, 9), float)
    for carpeta in carpetas:
        os.chdir(carpeta)
        if dos_corridas:
            datos_n, _ = read_PTRAC_CAP_bin(carpeta + '_n.p')
            datos_p, _ = read_PTRAC_estandar(carpeta + '_p.p', 'bin', ['sur'])
            if datos_n:
                datos_n = np.asarray(datos_n)
                datos_n[:, 0] = datos_n[:, 0] + nps_tot
                out_n = np.append(out_n, datos_n, axis=0)
            if datos_p:
                datos_p = np.asarray(datos_p)
                datos_p[:, 0] = datos_p[:, 0] + nps_tot
                out_p = np.append(out_p, datos_p, axis=0)
        else:
            datos, _ = read_PTRAC_CAP_bin(carpeta + '.p')
            if datos:
                datos = np.asarray(datos)
                datos[:, 0] = datos[:, 0] + nps_tot
                out = np.append(out, datos, axis=0)
        nps_tot += lee_nps_entrada(carpeta)
        os.chdir(parent)
    if dos_corridas:
        out_n = np.asarray(out_n)
        out_p = np.asarray(out_p)
        np.save(nombre + '_n_merged', out_n)
        np.save(nombre + '_p_merged', out_p)
        np.save(nombre + '_np_nps_merged', nps_tot)
        return out_n, out_p, nps_tot
    else:
        out = np.asarray(out)
        np.save(nombre + '_merged', out)
        np.save(nombre + '_nps_merged', nps_tot)
        return out, nps_tot


def split_and_save_listmode_data(datos, nombres, comprime=False):
    """
    Graba los archivos en modo lista simulados.

    Previamente los separa por detector.

    Los nombres de los archivos con que se guardan tendrá como base lo indicado
    en 'nombres' y luego se agrega la info de la celda (".D#celda") y la
    extensión será '.dat' o '.gz' dependiendo del valor de 'comprime'.


    Parámetros
    ----------
        datos : list of numpy array
            Array los datos de la simulación (nx3)
        nombres : list of strings
            Nombres de base para cada elemento
        comprime : bolean
            Opción para guardar los archivos comprimidos (.gz)

    Se debe cumplir len(datos)=len(nombres)
    """

    if len(datos) != len(nombres):
        print('No coinciden los tamaños de las listas. Corregir')
        quit()

    if comprime:
        _ext = ".gz"
    else:
        _ext = ".dat"

    # Tomo t=0 para el primer pulso entre todos los detectores
    # Busco cuál es el tiempo mínimo entre todos
    t_iniciales = [x[:, 1][0] for x in datos]
    t_0 = min(t_iniciales)

    datos_por_detector = []
    for dato, nom in zip(datos, nombres):
        # Separo cada archivo
        _sep, _origen = separa_capturas_por_celda(dato)
        for key in _sep:
            nombre = nom + ".D" + key + _ext
            np.savetxt(nombre, _sep[key][:, 1] - t_0, fmt="%.12E")
            print("Tiempo máximo en {} = {:2e} s".format(nombre,
                  _sep[key][:, 1][-1] - t_0))
        # Info para saber cuántas reacciones (n,xn) hubieron
        for item in _origen.items():
            print("{} detecciones en {}".format(*item[::-1]))
    return None

# Funciones para PHITS


def lee_espectro_phits_eng(archivo, zona):
    """
    Lee el archivo de un tally t-track de PHITS en función de la energía,
    que fue especificado por zonas

    Parámetros
    ----------
    archivo : string
        Nombre del archivo que se quiere leer ('track_eng.out')
    zona : string
        Zona (cell) en donde se pidió medir el tally

    Resultados
    ----------
    data : diccionario
        Un diccionario cuyas claves son los nombres que pone PHITS
        para cada columna.
        data['e-lower'] : numpy array con límites inferiores del bin
        data['e-upper'] : numpy array con límites superiores del bin
        data['particula'] : 2D numpy array con los valores del tally
        y su incerteza para 'partícula'

    """
    with open(archivo, 'r') as f:
        i = 0
        lines_block = []
        regions = []
        column_names = []
        for line in f:
            i += 1
            if line.startswith('       ne ='):
                # Cantidad de puntos de energía
                ne = np.int(line.split()[2])
            elif line[1:].startswith('newpage'):
                _newp = i
                regions.append(f.readline().split('=')[2].strip())
                i += 1
            elif line.startswith('#  e-lower'):
                _elower = i
                lines_block.append([_newp, _elower])
                column_names.append(line[1:].split())

    if zona not in regions:
        print('La zona especificada no pudo ser leida')
        quit()

    info_data = {}
    for reg, lin, col in zip(regions, lines_block, column_names):
        info_data[reg] = [lin, col]

    # Selecciona la zona especificada
    _a = np.genfromtxt(archivo, skip_header=info_data[zona][0][1],
                       max_rows=ne)

    # Diccionario donde se guardan los datos
    data = {}
    # Columnas para la región de interés
    cols = info_data[zona][1]
    # Se guardan límites de los binnes
    data[cols[0]] = _a[:, 0]
    data[cols[1]] = _a[:, 1]

    # Selecciona sólo los nombres de las partículas en el tally
    cols_part = [cols[i] for i in range(2, len(cols)) if i % 2 == 0]

    # Guarda los datos de las partículas
    for j, name in enumerate(cols_part):
        data[name] = _a[:, 2*j+2:2*j+4]

    return data


if __name__ == "__main__":
    pass
