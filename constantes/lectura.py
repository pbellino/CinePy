#!/usr/bin/env python3

"""
Script con funciones para leer datos y/o constantes

TODO: es temporal, después hacerlo más prolijo y copiando a constantes.py
"""

import numpy as np
import os


def lee_constantes_retardados(nom_constantes, *args, **kargs):
    """
    Función para leer las constantes de neutrones retardados.

    Lee el archivo `Constantes_nr.txt` que debe estar en el mismo directorio

    Observación: la efectividad de los fotoneutrones no se lee de los archivos
    donde están las constantes de los foteneutrones. Se lee del archivo
    "constantes_reactores.py". Se deja el valor por compatibilidad con los
    programas en LabVIEW

    Parámetros
    ----------
        nom_constantes : string
            Nombre del juego de constantes retardados ['Tuttle', 'Keepin']
        kargs :
            "Fotoneutrones" : Boolean (False)
            Indica si se incluyen los fotoneutrones
            "Constantes fotoneutrones": String ("Deuterio")
            Nombre de las constantes de fotonesutrones a utilizar
            "Grupos fotoneutrones" : float
            Cantidad de grupos de fotoneutrones que se utilizarán. Si no se
            especifica, se toma la cantidad máxima de grupos leidas. Se
            seleccionan los de menor vida media.
            "Efecctividad fotoneutrones" : float
            Efectividad de los fotoneutrones.
            "Beta efectivo" : float
            Beta efectivo, se necesita para recalcular el nuevo beta efectivo
            que incluye a los fotoneutrones


    Resultados
    ----------
        b_tot : numpy array
            Fracciones reducida (beta_i/beta_nuclear) de neutrones retardados.
            Incluyen a los fotoneutrones si se pidieron
        lam_tot : numpy array
            Constantes de decaimiento de los grupos de neutones retardados.
            Incluyen a los fotoneutrones si se pidieron
        dic_ctes : dictionary
            Diccionario con información auxiliar sobre las constantes leídas
            y/o procesadas.
                "b_i retardados": b_i de los retardados
                "lambda_i retardados": lambda_i de los retardados
                "beta nuclear retardados": beta nucleaar de los retardado
            Si no se pidieorn fotoneutrones, los primeros dos son redundantes
            (es lo mismo que b_tot y lam_tot).
            Si además se pidieron fotoneutrones, se incluyen:
                "beta efectivo total" : beta efectivo total (ret + foton)
                "beta_i nuclear fotoneutrones": beta_i nuclear de fotoneutrones
                "lambda_i fotoneutrones" : lambda_i de fotoneutrones
                "beta nuclear fotoneutrones" : beta nuclear de fotoneutrones


    """

    fotoneutrones = kargs.get("Fotoneutrones", False)
    const_fotoneut = kargs.get("Constantes fotoneutrones", None)
    grupos_fotoneut = kargs.get("Grupos fotoneutrones", None)
    efect_fotoneut = kargs.get("Efectividad fotoneutrones", None)
    beta_efectivo_ret = kargs.get("Beta efectivo retardados", None)

    if fotoneutrones:
        if None in [const_fotoneut, efect_fotoneut, beta_efectivo_ret]:
            print("Faltan especifcar datos sobre fotoneutrones")
            quit()
        name2file ={
                    "Deuterio": "JC_deuterio.dat",
                    }

    if nom_constantes not in ['Tuttle', 'Keepin']:
        print('El nombre de las constantes ingresado es inválido')
        print('Sólo se admiten "Tuttle" y "Keepin"')
        quit()

    archivo = 'Constantes_nr.txt'
    # Directorio donde está este archivo
    path_this_file = os.path.dirname(__file__)
    # Ubicación absoluta del archivo con constantes
    full_path_archivo = os.path.join(path_this_file, archivo)

    b_ret = []
    lam_ret = []
    with open(full_path_archivo, 'r') as f:
        for line in f:
            if line.startswith(nom_constantes):
                [next(f) for _ in range(3)]
                while True:
                    _r_line = f.readline()
                    if _r_line == '\n':
                        break
                    else:
                        b_ret.append(_r_line.rstrip())
                next(f)
                next(f)
                while True:
                    _r_line = f.readline()
                    if _r_line == '\n':
                        break
                    else:
                        lam_ret.append(_r_line.rstrip())
                next(f)
                next(f)
                beta_ret_nuclear = f.readline().rstrip()

    b_ret = np.asarray(b_ret, dtype=float)
    lam_ret = np.asarray(lam_ret, dtype=float)
    dic_ctes = {
                "b_i retardados": b_ret,
                "lambda_i retardados": lam_ret,
                "beta nuclear retardados": beta_ret_nuclear,
                }
    b_tot = b_ret
    lam_tot = lam_ret

    # Lectura de los fotoneutrones
    if fotoneutrones:
        full_path_archivo_fot = os.path.join(path_this_file,
                                              name2file[const_fotoneut])
        # Leo todos los datos en una sola columna
        _dat_fn = np.loadtxt(full_path_archivo_fot, comments='%')
        # Quito el valor de la efectividad de los fotoneutrones
        _dat_fn = _dat_fn[:-1]
        _n_dat_fn = len(_dat_fn)
        # beta_i de los fotoneutrones
        beta_i_fn = _dat_fn[:int(_n_dat_fn/2)]
        # lambda_i de los fotoneutrones
        lam_fn = _dat_fn[int(_n_dat_fn/2):]

        # Selecciono la cantidad de grupos de fotoneutrones
        if grupos_fotoneut is None: grupos_fotoneut = len(lam_fn)
        if grupos_fotoneut <= len(lam_fn):
            # Se seleccionan los de menor vida media (lambda más grandes)
            beta_i_fn = beta_i_fn[-grupos_fotoneut:]
            lam_fn = lam_fn[-grupos_fotoneut:]
        else:
            _msg = "La cantidad de grupos de fotoneutrones solicitada es mayor"
            _msg += " a la cantidad de grupos leidos. Se toma la máxima."
            print(_msg)

        # beta_i efectivos para los retardados
        beta_i_eff_ret = b_ret * beta_efectivo_ret
        # beta_i efectivos para los fotoneutrones
        beta_i_eff_fn = beta_i_fn * efect_fotoneut
        # Se juntan constantes de retardados y fotoneutrones
        beta_i_tot = np.concatenate([beta_i_eff_ret, beta_i_eff_fn])
        lam_tot = np.concatenate([lam_ret, lam_fn])
        # Se ordenan constantes de acuerdo a su lambda
        _inx_sort = lam_tot.argsort()
        lam_tot = lam_tot[_inx_sort]
        beta_i_tot = beta_i_tot[_inx_sort]
        # beta efectivo total
        beta_eff_tot = np.sum(beta_i_tot)
        # beta_i total (retardados + fotoneutrones)
        b_tot = beta_i_tot / beta_eff_tot
        dic_ctes["beta efectivo total"] = beta_eff_tot
        dic_ctes["beta_i nuclear fotoneutrones"] = beta_i_fn
        dic_ctes["lambda_i fotoneutrones"] = lam_fn
        dic_ctes["beta nuclear fotoneutrones"] = sum(beta_i_fn)

    return b_tot, lam_tot, dic_ctes


if __name__ == '__main__':

    nom_constantes = 'Tuttle'
    # nom_constantes = 'Keepin'

    b, lam, beta = lee_constantes_retardados(nom_constantes)
    print(b)
    print(lam)
    print(beta)
