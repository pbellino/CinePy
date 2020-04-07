#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script para lanzar trabajos de mcnp6 en paralelo dentro de Neurus o en una PC

Se modifica el archivo "input" que es la entrada de MCNP donde está señalizadas
las magnitudes que se van a reemplazar (@nombre_de_la_variable@).

Si se corre en  Neurus, deben estar los scripts de slurm  en el directorioi.

Se lanzan varias corridas modificando parámetros del modelo. Cada corrida se
realiza en la carpeta "case_XXX". En dicha carpeta se escribe un archivo
llamado "info_valores.txt" con los valores del modelo utilizado para esa
simulación.
"""

import os
import random as rnd
import subprocess


def _modifica_slurm_serie(slurm_script, slurm_base, input_corrida):
    # Genera script de slurm para cada corrida
    with open(slurm_script, 'w') as f:
        for line in slurm_base:
            if line.startswith('#SBATCH -J'):
                # Nombre del job
                f.write('#SBATCH -J ' + input_corrida + '\t # Job Name \n')
            elif line.startswith('param='):
                # Nombre del input
                f.write('param=\"ixr i=' + input_corrida + ' n=' +
                        input_corrida + '.\"\n')
            else:
                f.write(line)
    return None


def _modifica_slurm_openmp(slurm_script, slurm_base, input_corrida,
                           n_tasks):
    # Genera script de slurm para cada corrida con OpenMP
    with open(slurm_script, 'w') as f:
        for line in slurm_base:
            if line.startswith('#SBATCH -J'):
                # Nombre del job
                f.write('#SBATCH -J ' + input_corrida + '\t # Job Name \n')
            elif line.startswith('#SBATCH -n'):
                # Cantidad de cores
                f.write('#SBATCH -n ' + n_tasks + '\t # Number of cpu cores\n')
            elif line.startswith('param='):
                # Nombre del input
                f.write('param=\"ixr tasks ' + n_tasks + ' i=' +
                        input_corrida + ' n=' + input_corrida + '.\"\n')
            elif line.startswith('GOMP_DEBUG='):
                # Corrida
                f.write('GOMP_DEBUG=1 OMP_DISPLAY_ENV=VERBOSE OMP_NUM_THREADS='
                        + n_tasks + ' $bin $param\n')
            else:
                f.write(line)
    return None


def reemplaza_valores(archivo, dic_valores):
    """Reemplaza los valores de dic_valores en archivo"""

    # Abre el archivo con valores a reemplazar
    with open(archivo, 'r') as f:
            _file = f.read()
    # Reemplaza los valores
    info_valores = []
    for k, v in dic_valores.items():
        _file = _file.replace(k, str(v))
        info_valores.append(k + ' = ' + str(v) + '\n')
    # Escribe en archivo los valores reemplazados
    with open('info_valores.txt', 'w') as f:
        for line in info_valores:
            f.write(line)
    # Escribe el archivo de entrada ya reemplazado
    with open(archivo, 'w') as f:
        f.write(_file)
    return None


if __name__ == '__main__':
    """
    Se modelan dos detetores de He3 ubicados verticalmente a los costados de un
    balde con agua. Se modifica el radio del agua y se simulan la cantidad de
    reacciones de cada detector.

    Los datos de los detectores correponden a los Canberra 6NH12.5 (detector 1)
    y al 48NH30 (detector 2).

    Prestar atención a que las variables definidas en el diccionario deben
    coincidir con los nombres que están en el archivo "input". Es lo que se
    utiliza para reemplazar los valores en cada corrida.
    """

    ###########################################################################
    # Input parameters
    ###########################################################################
    input_mcnp = 'input'
    slurm_script = 'mcnp6.slurm'  # Un solo proceso en serie
    slurm_script = 'mcnp6_gcc6.3_openmp.slurm'  # Usando OpenMP
    n_tasks = 8   # Sólo se utiliza para OpenMP
    corrida_en = 'pc'  # (pc | cluster)

    # Valores para reemplazar
    # Radio del balde
    # r_balde_list = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]
    r_balde_list = [0.5, 1.5, 2.5, 3.5, 4, 4.5, 5, 5.5, 6, 6.5, 7,
                    7.5, 8, 8.5, 9, 10, 11, 12, 13, 14, 15]
    # Radio de detectores
    r_det_1 = 0.5
    r_det_2 = 1.25
    # Longitud de detectores
    L_det_1 = 12.5
    L_det_2 = 30

    ###########################################################################

    try:
        n_tasks = str(n_tasks)
    except NameError:
        if 'openmp' in slurm_script:
            print('No se definió la variable n_task')
            print('Se sale')
            quit()

    # Directorio raiz
    parent = os.getcwd()

    # Se lee el input base de MCNP para ser modificado
    with open(input_mcnp, 'r') as f:
        mcnp_input_base = f.readlines()

    if corrida_en == 'cluster':
        # Se lee el script se slurm para ser modificado
        with open(slurm_script, 'r') as f:
            slurm_base = f.readlines()

    # Se generan las corridas
    for i, r_balde in enumerate(r_balde_list, 1):
        # Identificación de cada corrida
        id_corrida = str(i).zfill(3)
        dir_corrida = 'case_' + id_corrida

        os.mkdir(dir_corrida)
        os.chdir(dir_corrida)

        # Genera input para cada corrida
        input_corrida = dir_corrida
        with open(input_corrida, 'w') as f:
            for line in mcnp_input_base:
                if 'RAND ' in line:
                    # Nueva semilla
                    rand_num = 2*rnd.randrange(10000000000) + 1
                    f.write('RAND GEN=2 SEED=' + str(rand_num) + '\n')
                else:
                    f.write(line)

        # Reemplaza los valores
        val_reemplazo = {
                         '@r_balde@': r_balde,
                         '@r_det_1@': r_det_1,
                         '@r_det_2@': r_det_2,
                         '@L_det_1@': L_det_1,
                         '@L_det_2@': L_det_2,
                         '@pos_y_det_1@': r_balde + r_det_1,
                         '@pos_z_det_1@': - L_det_1 / 2.,
                         '@pos_y_det_2@': - (r_balde + r_det_2),
                         '@pos_z_det_2@': - L_det_2 / 2.,
                         }
        reemplaza_valores(input_corrida, val_reemplazo)

        # Se corre MCNP
        if corrida_en == 'cluster':
            # Genera script se slurm
            if 'openmp' in slurm_script:
                _modifica_slurm_openmp(slurm_script, slurm_base, input_corrida,
                                       n_tasks)
            else:
                _modifica_slurm_serie(slurm_script, slurm_base, input_corrida)

            # Se envia el job
            command = "sbatch " + slurm_script
        elif corrida_en == 'pc':
            # Línea de comando para la pc
            command = "mcnp6 tasks 4 i=" + input_corrida + " n=" \
                       + input_corrida + "."

        print(' Corriendo en la carpeta ' + dir_corrida + '...')
        process = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
        output, error = process.communicate()

        print(' Se sale de la carpeta ' + dir_corrida)

        os.chdir(parent)
