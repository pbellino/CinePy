#!/usr/bin/env python3

import numpy as np
import os
import sys
sys.path.append("/home/pablo/CinePy")
from constantes.lectura import lee_constantes_retardados
from constantes.constantes_reactores import RA3 as REACTOR
from modules.point_kinetics.ajuste_CEM import lee_archivo_CIN, \
                                              algoritmo_angel_CEM, \
                                              archivo_referencia


if __name__ == "__main__":

    # -----
    # Se lee el archivo .CIN
    folder = "data"

    archivo = "S-B23A-1.CIN"
    archivo = "S-B23A-2.CIN"
    #archivo = "SCT-13-1.CIN"
    archivo = "SCT-13-2.CIN"

    file_path = os.path.join(folder, archivo)

    t_cin, n_cin = lee_archivo_CIN(file_path)

    # Se leen juego de cosntantes nucleares de neutrones retardados
    b, lam , beta = lee_constantes_retardados('Tuttle')

    if "B23A" in archivo:
        from constantes.constantes_reactores import RA1 as REACTOR
    elif "SCT" in archivo:
        from constantes.constantes_reactores import RA3 as REACTOR

    # Se leen constantes características de cada reactor
    Lambda_red = REACTOR.LAMBDA_REDUCIDO
    constantes_cineticas = b, lam, Lambda_red

    _parametros = {
                   "t_ref": (0.1, 3),
                   "t_fit": (6.0, 80),
                   "epsilon": 1e-3,
                   "n_iter_max": 20,
                   "verbose": True,
                   "plot": True,
                  }

    result = algoritmo_angel_CEM(t_cin, n_cin, constantes_cineticas,
                                 **_parametros)

    # Archivo para comparar resultados
    name = os.path.join("./data/", "resultados_fercin4.txt")
    dic_ref = archivo_referencia(name)
    ref_vals = dic_ref[archivo.rstrip('.CIN')]

    print(80*'-')
    print(20*' ' + "Valores de referencia (FERCIN-4)")
    print(80*'-')
    print(f"t_cero = {ref_vals[0]} ")
    print(f"t_b = 0.124 s (Primer ajuste)")
    print(f"t_b (final) = {ref_vals[1]}")
    print(f"$_om (final) = {ref_vals[3]}")
    print(f"A3 (final) = {ref_vals[2]}")
    print("")
    print(f"$_op (final) = {ref_vals[6]}")
    print(f"$_oi  = {ref_vals[4]}")
    print(f"$_od  = {ref_vals[5]}")
    print(80*'-')
