#!/usr/bin/env python3

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
sns.set()

import sys
sys.path.append('/home/pablo/CinePy')

from constantes.lectura import lee_constantes_retardados
from constantes.constantes_reactores import RA3
from modules.point_kinetics.direct_kinetic_solver import cinetica_directa
from modules.point_kinetics.reactimeter import reactimetro
from modules.point_kinetics.soluciones_analiticas import solucion_analitica_Ia


if __name__ == "__main__":
    """
    Se prueba la performance de los algoritmos de cinética inversa y de
    cinética directa.

    Se los aplican de forma sucesiva y se analiza en qué situaciones se
    recupera el valor original de reactividad.

    Sólo hay un esquema para la cinética inversa, y se lo aplica tanto a
    soluciones numéricas (con varios esquemas) como a soluciones analíticas.

    Los métodos basados en la integración del flujo tienen problemas cuando las
    funciones no son derivables. Pero si se los aplican en conjunto, dichos
    errores se cancelan. Es de esperar porque uno se despeja del otro.

    Sin embargo, cuando se aplica el reactímetro a una solución analítica, el
    problema se hace evidente. Todo se soluciona reduciendo el dt.

    Ver en los otros scripts que al utilizar la cinética directa basada en
    integrate.ode, no son tan evidentes los problemas cuando la función no es
    derivable. TODO: modificar el reactímetro con alguno de los métodos
    deducidos en el informe.
    """

    # Delayed neutron constants 
    b, lam , beta = lee_constantes_retardados('Tuttle')
    # Reduced generation time
    Lambda_red = RA3.LAMBDA_REDUCIDO

    constants = b, lam, Lambda_red

    # Cantidad de puntos
    Npunt = 10000
    # Paso de integración
    dt = 0.001
    # Vector temporal
    t = dt * np.arange(0, Npunt)
    #t = np.linspace(0.0, tmax, Npunt)
    # Paso de integración 
    # dt = t[1]-t[0]

    # Cambio en reactividad (en dólares)
    rho = -0.1
    # Tiempo del salto instantáneo
    t0 = 2
    # Valor inicial
    n0 = 10
    # Reactividad en función del tiempo
    reactividad = rho * np.ones_like(t)
    reactividad[t<=t0] = 0.0

    n_analitica = solucion_analitica_Ia(t, rho, t0, n0, constants)
    n_num, t_num = cinetica_directa(reactividad, n0, dt, lam, b, Lambda_red, 0)

    # Reconstruyo la reactividad utilizando al reactímetro
    rho_ana, t_ana, _ = reactimetro(n_analitica, dt, lam, b, Lambda_red)
    rho_num, t_num, _ = reactimetro(n_num, dt, lam, b, Lambda_red)

    # Graficación
    fig, ax = plt.subplots(2, 1, figsize=(7,6), sharex=True)
    ax[0].plot(t, reactividad, '.-', label="Original")
    ax[0].plot(t_ana, rho_ana, '.-', label="Con analítica")
    ax[0].plot(t_num, rho_num, '.-', label="Con numérica")
    ax[0].set_ylabel(r'$\$$(t)')
    ax[0].set_yscale('linear')
    ax[0].legend()

    ax[1].plot(t, n_analitica, '.-', label='Analítica')
    ax[1].plot(t_num, n_num, '.-', label='Numérica')
    ax[1].set_ylabel('n(t)')
    ax[1].set_xlabel('Tiempo [s]')
    ax[1].legend()

    fig.tight_layout()

    plt.show()
