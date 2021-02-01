#!/usr/bin/env python3

"""
Script con funciones para leer datos y/o constantes

TODO: es temporal, después hacerlo más prolijo y copiando a constantes.py
"""

import numpy as np
import os


def lee_constantes_retardados(nom_constantes):
    """
    Función para leer las constantes de neutrones retardados.

    Lee el archivo `Constantes_nr.txt` que debe estar en el mismo directorio

    Parámetros
    ----------
        nom_constantes : string
            Nombre del juego de constantes retardados ['Tuttle', 'Keepin']

    Resultados
    ----------
        b : numpy array
            Fracciones reducida (beta_i/beta_nuclear) de neutrones retardados
        lam : numpy array
            Constantes de decaimiento de los grupos de neutones retardados
        beta_nuclear : float
            Fracción de neutrones retardsdos nuclear
    """

    if nom_constantes not in ['Tuttle', 'Keepin']:
        print('El nombre de las constantes ingresado es inválido')
        print('Sólo se admiten "Tuttle" y "Keepin"')
        quit()

    archivo = 'Constantes_nr.txt'
    # Directorio donde está este archivo
    path_this_file = os.path.dirname(__file__)
    # Ubicación absoluta del archivo con constantes
    full_path_archivo = os.path.join(path_this_file, archivo)

    b = []
    lam = []
    with open(full_path_archivo, 'r') as f:
        for line in f:
            if line.startswith(nom_constantes):
                [next(f) for _ in range(3)]
                while True:
                    _r_line = f.readline()
                    if _r_line == '\n':
                        break
                    else:
                        b.append(_r_line.rstrip())
                next(f)
                next(f)
                while True:
                    _r_line = f.readline()
                    if _r_line == '\n':
                        break
                    else:
                        lam.append(_r_line.rstrip())
                next(f)
                next(f)
                beta_nuclear = f.readline().rstrip()

    b = np.asarray(b, dtype=float)
    lam = np.asarray(lam, dtype=float)
    return b, lam, beta_nuclear


if __name__ == '__main__':

    nom_constantes = 'Tuttle'
    # nom_constantes = 'Keepin'

    b, lam, beta = lee_constantes_retardados(nom_constantes)
    print(b)
    print(lam)
    print(beta)
