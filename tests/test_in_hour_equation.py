#!/usr/bin/env python3

import sys
sys.path.append("/home/pablo/CinePy")
from constantes.lectura import lee_constantes_retardados
from modules.point_kinetics.soluciones_analiticas import solucion_in_hour_equation
from constantes.constantes_reactores import RA3

if __name__ == "__main__":

    rho = 0.0
    b, lam, beta = lee_constantes_retardados('Tuttle')
    Lambda_red = RA3.LAMBDA_REDUCIDO
    constants = b, lam, Lambda_red

    # Raices de la ecuación in-hour
    roots = solucion_in_hour_equation(rho, constants)
    print(f"Roots [1/s]: \n {roots}")
    # Tiempos asociados a dichas raices
    print(f"Tiempos [s]: \n {1/roots}")


