#!/usr/bin/env python3

import numpy as np
import sys
sys.path.append("/home/pablo/CinePy")
from constantes.lectura import lee_constantes_retardados
from modules.point_kinetics.soluciones_analiticas import solucion_in_hour_equation
from constantes.constantes_reactores import RA3 as REACTOR


if __name__ == "__main__":


    from constantes.constantes_reactores import RA3 as REACTOR

    # Se leen constantes características de cada reactor
    Lambda_red = REACTOR.LAMBDA_REDUCIDO
    beta_efectivo_ret = REACTOR.BETA_EFECTIVO
    efect_fotoneut = REACTOR.EFECTIVIDAD_FOTONEUTRONES

    rho = -2
    # Caso que quiero comparar
    ef_foto = '2'
    # Relación entre el caso y la efectividad de los fotoneutrones
    ef_foto_comp = {
                   '1': 0.62,
                   '2': 1e-6,
                   '3': 1e-8,
                   '4': 1e-10,
                   }

    # Se leen juego de cosntantes nucleares de neutrones retardados
    _kargs = {
              "Fotoneutrones": True,
              "Constantes fotoneutrones": "Deuterio",
              "Beta efectivo retardados" : 0.00769,
              "Grupos fotoneutrones" : 9,
              "Efectividad fotoneutrones" : ef_foto_comp[ef_foto],
              }

    b, lam , dic_ctes = lee_constantes_retardados('Tuttle', **_kargs)

    print("lambda-i \t b_i")
    [print(f"{x:.8e}\t {y:.8e}") for x, y in zip(lam, b)]

    constantes = b, lam, Lambda_red

    roots = solucion_in_hour_equation(rho, constantes)

    _ref = np.loadtxt("datos_raices_inhour.dat")
    val_ref = _ref[:, int(ef_foto)-1]
    diff = 100 * (val_ref - roots) / val_ref

    print("Raices \t\t\t Diferencia [%]")
    [print(f"{x:.8e} \t {y:4e}") for x, y in zip(roots, diff)]


