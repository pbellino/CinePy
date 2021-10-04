#!/usr/bin/env python3

import numpy as np
from uncertainties import ufloat
import os
import matplotlib.pyplot as plt
import seaborn as sns
sns.set()
import sys
sys.path.append("/home/pablo/CinePy")
from constantes.lectura import lee_constantes_retardados
from constantes.constantes_reactores import RA3 as REACTOR
from modules.point_kinetics.reactimeter import reactimetro
from modules.point_kinetics.direct_kinetic_solver import cinetica_directa
from modules.point_kinetics.ajuste_CEM import lee_archivo_CIN, \
                                            deteccion_borde, \
                                            deteccion_tiempo_caida, \
                                            estima_reactividad_reactimetro, \
                                            salto_instantaneo_espacial, \
                                            ajuste_simulacion_espacial



if __name__ == "__main__":

    # -----
    # Se lee el archivo .CIN
    folder = "data"

    archivo = "S-B23A-1.CIN"
    #archivo = "S-B23A-2.CIN"
    #archivo = "SCT-13-1.CIN"
    #archivo = "SCT-13-2.CIN"

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

    # Normalizo con el promedio 
    t_i_ref = 0.1
    t_f_ref = 3
    ind_ref = (t_cin >= t_i_ref) & (t_cin <= t_f_ref)
    n_cin_nor = n_cin / np.mean(n_cin[ind_ref])
    # Calcula tiempo cuando empieza a caer la barra
    t_cero = deteccion_borde(t_cin, n_cin_nor, (t_i_ref, t_f_ref))
    print(f"t_cero = {t_cero}")

    # -------------------------------------------------------------------------
    # 3. Ajuste para obtener A_3^(1)
    t_fit_i = t_cero + 6
    t_fit_f = t_cero + 80
    parametros = {
                  't_ajuste': (t_fit_i, t_fit_f),
                  'constantes_cineticas': constantes_cineticas,
                  't1_vary': True,
                  'A1_vary': False,
                  'A3_vary': True,
                  }

    result = ajuste_simulacion_espacial(t_cin, n_cin_nor, **parametros)

    A3 = ufloat(result.params['A3'].value, result.params['A3'].stderr)
    print(f"A3 = {A3:.3e}")

    # -------------------------------------------------------------------------
    # 4.  Cinética inversa para obtener $op
    ########
    # A3 = ufloat(-0.7972e-4, 0)
    ########
    dt = t_cin[1]
    rho_r, t_r, _ = reactimetro(n_cin_nor - A3.n, dt, lam, b, Lambda_red)

    # Se estima el tiempo que tarda en caer la barra
    t_caida, indx_t_caida = deteccion_tiempo_caida(t_r, rho_r, t_cero)
    print("t_caida = {:.2f} s".format(t_caida))

    # Estimar la reactividad promedio en una zona constante
    rho_op, t_in_ajuste = estima_reactividad_reactimetro(t_r, rho_r, t_caida)
    print(f"rho_op = {rho_op} obtenido a partir de t={t_in_ajuste:.2f} s")
    print(80*'-')
    # TODO: ver promedios por bloque para evitar bias por correlación el datos

    # Se obtiene R(t)
    rho_en_t_caida = rho_r[t_r == t_caida][-1]
    R_t = rho_r / rho_en_t_caida
    #TODO: comparar con la R_t obtenida con el fercin4


    rho_old = rho_op.n
    _corta = False
    while not _corta:

        # 6. Simulación cinética directa

        rho_pk = rho_old * R_t

        n_sim, t_sim = cinetica_directa(rho_pk, 1, dt, lam, b, Lambda_red, 0)

        # -----
        # 7.Ajuste para obtener t_b^1 y $om^(0)
        parametros = {
                      't_ajuste': (t_fit_i, t_fit_f),
                      'constantes_cineticas': constantes_cineticas,
                      't1_vary': True,
                      'A3_vary': False,
                      }

        result = ajuste_simulacion_espacial(t_sim, n_sim, **parametros)

        t1 = ufloat(result.params['t1'].value, result.params['t1'].stderr)
        tb = t1 - t_cero
        rho_om = ufloat(result.params['rho'].value,
                        result.params['rho'].stderr)
        print(f"t_b = {tb:.3e} s")
        print(f"$_{{om_new}} = {rho_om:.3e}")

        # ---------------------------------------------------------------------
        # 8. Ajuste para obtener $om^i y A_3^i
        parametros = {
                      't_ajuste': (t_fit_i, t_fit_f),
                      'constantes_cineticas': constantes_cineticas,
                      't1_vary': False,
                      't1_value': t1.n,
                      # con el valor dado por fercin4
                      #'t1_value': t_cero + 0.278,
                      'A3_vary': True,
                      }

        result = ajuste_simulacion_espacial(t_cin, n_cin_nor, **parametros)

        rho_new = ufloat(result.params['rho'].value ,
                                    result.params['rho'].stderr)
        A3 = ufloat(result.params['A3'].value, result.params['A3'].stderr)
        print(f"A3_new = {A3:.3e}")
        print(f"$_{{om_new}} = {rho_new:.3e}")
        print(80*'-')
        if np.absolute(rho_old - rho_new.n) < 0.01 * rho_new.s:
            _corta = True
        # TODO: Comparar los A3's
        rho_old = rho_new.n

    # -------------------------------------------------------------------------
    print(80*'-')
    # Con el nuevo A3 se calcula nuevamente la $op
    rho_r, t_r, _ = reactimetro(n_cin_nor - A3.n, dt, lam, b, Lambda_red)
    # Se estima el tiempo que tarda en caer la barra
    t_caida, indx_t_caida = deteccion_tiempo_caida(t_r, rho_r, t_cero)
    print("t_caida = {:.2f} s".format(t_caida))
    # Estimar la reactividad promedio en una zona constante
    rho_op, t_in_ajuste = estima_reactividad_reactimetro(t_r, rho_r, t_caida)
    print(f"$_op (final) = {rho_op}")

    print(archivo)
