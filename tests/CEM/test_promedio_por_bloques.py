#!/usr/bin/env python3

import numpy as np
import os
import matplotlib.pyplot as plt
import seaborn as sns
sns.set()
import sys
sys.path.append("/home/pablo/CinePy")
from constantes.lectura import lee_constantes_retardados
from constantes.constantes_reactores import RA3 as REACTOR
from modules.point_kinetics.reactimeter import reactimetro
from modules.point_kinetics.ajuste_CEM import lee_archivo_CIN, \
                                            deteccion_borde, \
                                            deteccion_tiempo_caida, \
                                            estima_reactividad_reactimetro, \
                                            ajuste_cinetica_espacial
from modules.estadistica import promedio_por_bloques


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

    # Intervalo que se toma de referencia para normalizar y para obtener el t0
    t_i_ref = 0.1
    t_f_ref = 3
    ind_ref = (t_cin >= t_i_ref) & (t_cin <= t_f_ref)
    # Normalización de la señal medida
    n_cin_nor = n_cin / np.mean(n_cin[ind_ref])
    # Calcula tiempo cuando empieza a caer la barra
    t_cero = deteccion_borde(t_cin, n_cin_nor, (t_i_ref, t_f_ref))

    # -------------------------------------------------------------------------
    # 3. Ajuste para obtener A_3^(1)
    t_fit_i = t_cero + 6
    t_fit_f = t_cero + 80
    parametros = {
                  't_ajuste': (t_fit_i, t_fit_f),
                  'constantes_cineticas': constantes_cineticas,
                  't1_vary': True,
                  't1_value': t_cero + 0.27,
                  'A1_vary': True,
                  'A3_vary': True,
                  }

    result = ajuste_cinetica_espacial(t_cin, n_cin_nor, **parametros)
    # A3 = ufloat(result.params['A3'].value, result.params['A3'].stderr)
    A3 = result.params['A3'].value

    # -------------------------------------------------------------------------
    # 4.  Cinética inversa para obtener $op
    dt = t_cin[1]
    rho_r, t_r, _ = reactimetro(n_cin_nor - A3.n, dt, lam, b, Lambda_red)

    # Se estima el tiempo que tarda en caer la barra
    t_caida, indx_t_caida = deteccion_tiempo_caida(t_r, rho_r, t_cero)

    # Estimar la reactividad promedio en una zona constante
    rho_op, t_in_ajuste = estima_reactividad_reactimetro(t_r, rho_r, t_caida)

    # Selecciono la parte donde es constante la reactividad
    ind_ct = (t_r >= t_in_ajuste) & (t_r <= 70)

    promedio_por_bloques(rho_r[ind_ct], metodo='ajuste_en_segmentos',
                         pts_por_ajuste=100)
