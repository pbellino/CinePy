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

def archivo_referencia(fname):
    """
    Función auxiliar para leer archivo con resultados del FERCIN4
    """
    #data = np.loadtxt(fname, skiprows=2, usecols=(1,2,3))
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

    # Archivo para comparar resultados
    name = os.path.join("./data/", "resultados_fercin4.txt")
    dic_ref = archivo_referencia(name)
    ref_vals = dic_ref[archivo.rstrip('.CIN')]

    # Se leen juego de cosntantes nucleares de neutrones retardados
    b, lam , beta = lee_constantes_retardados('Tuttle')

    if "B23A" in archivo:
        from constantes.constantes_reactores import RA1 as REACTOR
    elif "SCT" in archivo:
        from constantes.constantes_reactores import RA3 as REACTOR

    # Se leen constantes características de cada reactor
    Lambda_red = REACTOR.LAMBDA_REDUCIDO
    print(Lambda_red)
    constantes_cineticas = b, lam, Lambda_red

    # Intervalo que se toma de referencia para normalizar y para obtener el t0
    t_i_ref = 0.1
    t_f_ref = 3
    ind_ref = (t_cin >= t_i_ref) & (t_cin <= t_f_ref)
    # Normalización de la señal medida
    n_cin_nor = n_cin / np.mean(n_cin[ind_ref])
    # Calcula tiempo cuando empieza a caer la barra
    t_cero = deteccion_borde(t_cin, n_cin_nor, (t_i_ref, t_f_ref))
    print(f"t_cero = {t_cero}")
    print(f"t_cero = {ref_vals[0]} (FERCIN4)")

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

    result = ajuste_simulacion_espacial(t_cin, n_cin_nor, **parametros)

    t1 = ufloat(result.params['t1'].value, result.params['t1'].stderr)
    tb = t1 - t_cero
    print(f"t_b = {tb:.3e} s (Primer ajuste)")
    print(f"t_b = 0.124 s (FERCIN-4 Primer ajuste)")
    print("")
    A3 = ufloat(result.params['A3'].value, result.params['A3'].stderr)
    print(f"A3 = {A3:.3e} (Primer ajuste")
    print(f"A3 = -1.027E-5 (FERCIN-4 Primer ajuste)")
    print(f"A3 (final) = {ref_vals[2]} (FERCIN4)")

    print(80*'-')
    # -------------------------------------------------------------------------
    # 4.  Cinética inversa para obtener $op
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
    # Se inicia en zero
    R_t = np.zeros_like(rho_r)
    # índices donde R(t) es distinto de cero y de uno
    ind_rt = (t_r >= t_cero) & (t_r <= t_caida)
    R_t[ind_rt] = rho_r[ind_rt] / rho_en_t_caida
    R_t[t_r > t_caida] = 1.0


    print(20*' ' + "Comienzo de la iteración")
    rho_old = rho_op
    _corta = False
    while not _corta:
        # ---------------------------------------------------------------------
        # 6. Simulación cinética directa
        rho_pk = rho_old.n * R_t
        n_sim, t_sim = cinetica_directa(rho_pk, 1, dt, lam, b, Lambda_red, 0)

        # ---------------------------------------------------------------------
        # 7.Ajuste para obtener t_b^1 y $om^(0)
        parametros = {
                      't_ajuste': (t_fit_i, t_fit_f),
                      'constantes_cineticas': constantes_cineticas,
                      't1_vary': True,
                      'A3_vary': True,
                      }

        result = ajuste_simulacion_espacial(t_sim, n_sim, **parametros)

        t1 = ufloat(result.params['t1'].value, result.params['t1'].stderr)
        tb = t1 - t_cero
        rho_om0 = ufloat(result.params['rho'].value,
                        result.params['rho'].stderr)
        print(f"t_b = {tb:.3e} s")
        print(f"$_{{om^0}} = {rho_om0:.3e}")

        # ---------------------------------------------------------------------
        # 8. Ajuste para obtener $om^i y A_3^i
        parametros = {
                      't_ajuste': (t_fit_i, t_fit_f),
                      'constantes_cineticas': constantes_cineticas,
                      't1_vary': False,
                      't1_value': t1.n,
                      'A3_vary': True,
                      }

        result = ajuste_simulacion_espacial(t_cin, n_cin_nor, **parametros)

        rho_new = ufloat(result.params['rho'].value ,
                                    result.params['rho'].stderr)
        A3 = ufloat(result.params['A3'].value, result.params['A3'].stderr)
        print(f"$_{{om^i}} = {rho_new:.3e}")
        print(f"A3_new = {A3:.3e}")
        print(80*'-')
        if np.absolute(rho_old - rho_new.n) < 0.001 * rho_new.s:
            _corta = True
        # TODO: Comparar los A3's
        rho_old = rho_new

    # -------------------------------------------------------------------------
    print(20*' ' + "Fin de la iteración")
    print(80*'-')
    print(f"t_b (final) = {ref_vals[1]} (FERCIN4)")
    print(f"$_om (final) = {ref_vals[3]} (FERCIN4)")
    print(f"A3 (final) = {ref_vals[2]} (FERCIN4)")
    print(80*'-')
    print("Se usa el último A3 para volver a aplicar el reactímetro")
    # Con el nuevo A3 se calcula nuevamente la $op
    rho_r, t_r, _ = reactimetro(n_cin_nor - A3.n, dt, lam, b, Lambda_red)
    # Se estima el tiempo que tarda en caer la barra
    t_caida, indx_t_caida = deteccion_tiempo_caida(t_r, rho_r, t_cero)
    print("t_caida = {:.2f} s".format(t_caida))
    # Estimar la reactividad promedio en una zona constante
    rho_op, t_in_ajuste = estima_reactividad_reactimetro(t_r, rho_r, t_caida)
    print(f"$_op (final) = {rho_op}")
    print(f"$_op (final) = {ref_vals[6]} (FERCIN4)")

    print(archivo)
