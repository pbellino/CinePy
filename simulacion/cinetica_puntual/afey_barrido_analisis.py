#!/usr/bin/env python3

import numpy as np
import matplotlib.pyplot as plt
import os

import sys
sys.path.append('/home/pablo/CinePy')

from modules.io_modules import lee_fey
from modules.alfa_feynman_analisis import grafica_afey, ajuste_afey, lee_Nk


if __name__ == '__main__':

    script_dir = os.path.dirname(__file__)
    # Carpeta que contiene a las carpetas que se barrieron
    folder_main = "barrido"
    folder_main = os.path.join(script_dir, folder_main)
    # Lista con subcareptas
    _, dts_fold, _ = next(os.walk(folder_main))
    # Path completo
    _list_fold = [os.path.join(folder_main, dt) for dt in dts_fold]

    var_names = ['alfa', 'eficiencia', 'fis_rate']

    nom_dic = []
    for dt_fold in _list_fold:
        nombres = {
                'bounching': os.path.join(dt_fold, 'times.D1_var.fey'),
                   'choice': os.path.join(dt_fold, 'times.D1_var_choice.fey'),
                     'skip': os.path.join(dt_fold, 'times.D1_var_skip.fey'),
                      'mca': os.path.join(dt_fold, 'times.D1_var_mca.fey'),
                  }
        nom_dic.append(nombres)
    metodos = nom_dic[0].keys()

    # Inicializo diccionario para resultados
    results = {}
    for key in metodos:
        results[key] = {}
        for var in var_names:
            results[key][var] = []

    # Análisis en cada carpeta
    for nombres in nom_dic:
        for key, nombre in nombres.items():
            # Camino absoluto del archivo que se quiere leer
            abs_nombre = os.path.join(script_dir, nombre)
            tau, Y, std_Y, num_hist, tasas = lee_fey(abs_nombre)
            # Puntos para cada tau por batch
            Nk = lee_Nk(nombre.rstrip('fey') + 'Nk')

            _, val, teo = ajuste_afey(tau, Y, std_Y, [400, 10, 0],
                                      vary=[1, 1, 0], Nk=Nk, tasa=tasas,
                                      verbose=False, plot=0, conf_int=False)

            for name, _v in zip(var_names, val):
                results[key][name].append(_v)

            #[print(f"Estimados: {va:.4e} - Teóricos: {te:.4e}")  \
            #        for va, te in zip(val, teo)]

    # Tiempos máximos analizados (numéricos)
    dts_max = [float(dt) for dt in dts_fold]

    fig, axs = plt.subplots(3, 1, sharex=True, figsize=(10,9))

    for met, result in results.items():
        for key, ax in zip(result.keys(), axs):
            _res_n = [k.n for k in result[key]]
            _res_s = [k.s for k in result[key]]
            ax.errorbar(dts_max, _res_n, yerr=_res_s, fmt='s', label=met)
    axs[-1].set_xlabel(r"$\tau_{{max}}$ [s]")
    varis = [r"$\alpha$ [1/s]", r"$\epsilon$", r"$F$ [1/s]"]

    # Gráfico valores teóricos
    x_teo = np.linspace(min(dts_max), max(dts_max), 100)
    y_teo = np.ones(np.shape(x_teo))
    for ax, var, te in zip(axs, varis, teo):
        ax.set_ylabel(var)
        ax.plot(x_teo, te * y_teo, 'k', lw=2, label="Reference")

    axs[0].legend(bbox_to_anchor=(0.5, 1.40), loc="upper center",
            ncol=len(nombres)+1)
    plt.tight_layout()
    plt.show()


