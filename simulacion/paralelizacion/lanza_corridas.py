#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script para lanzar trabajos de mcnp6 en serie dentro de Neurus
"""

import os
import random as rnd
import subprocess

if __name__ == '__main__':

    ###########################################################################
    # Input parameters
    ###########################################################################
    n_corridas = 8
    input_mcnp = 'input'
    slurm_script = 'mcnp6.slurm'  # Para un solo proceso en serie
    ###########################################################################

    # Directorio raiz
    parent = os.getcwd()

    # Se lee el input base de MCNP para ser modificado
    with open(input_mcnp, 'r') as f:
        mcnp_input_base = f.readlines()

    # Se lee el script se slurm para ser modificado
    with open(slurm_script, 'r') as f:
        slurm_base = f.readlines()

    # Se generan las corridas
    for i in range(1, n_corridas + 1):
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

        # Se envia el job
        command = "sbatch " + slurm_script
        process = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
        output, error = process.communicate()

        os.chdir(parent)
