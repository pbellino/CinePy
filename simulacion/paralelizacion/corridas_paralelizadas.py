#!/usr/bin/env python3

"""
Script para lanzar trabajos de mcnp6 de forma paralela

Está puesto como script independiente para poder ser
copiado fácilmente al cluster.

Recordar que si se modifica este script habrá que copiarlo
a la carpeta CinePy/simulacion/paralelizacion. Esta carpeta
es la que se copiará al cluster ya que tiene los scripts de
slurm necesarios para correr en Neurus.
"""

import os
import subprocess


def _modifica_slurm_serie(slurm_script, slurm_base, input_corrida):
    # Genera script de slurm para cada corrida en serie
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
                f.write('#SBATCH -n ' + str(n_tasks) +
                        '\t # Number of cpu cores\n')
            elif line.startswith('param='):
                # Nombre del input
                f.write('param=\"ixr tasks ' + str(n_tasks) + ' i=' +
                        input_corrida + ' n=' + input_corrida + '.\"\n')
            elif line.startswith('GOMP_DEBUG='):
                # Corrida
                f.write('GOMP_DEBUG=1 OMP_DISPLAY_ENV=VERBOSE OMP_NUM_THREADS='
                        + str(n_tasks) + ' $bin $param\n')
            else:
                f.write(line)
    return None


def run_paralelo(n_corridas, input_mcnp, machine='PC', n_tasks=1,
                 queue_script=None, parallelization=None, nombre='case',
                 run_script=None):
    """
    Función para realizar distintas corridas en paralelo de MCNP

    Se debe indicar el input que se quiere correr.

    Si se corre en un cluster, se deberá indicar también el archivo del
    gestor de colas. La modificación de este archivo se hizo basado en
    los scripts de slurm dados por la GTIC para MCNP6. Sólo se puede
    correr con OpenMP o en serie (pues no está compilado con MPI en
    Neurus).

    Debe aparecer la tarjeta "RAND" para que reemplace correctamente
    Si se llama a otro archivo, debe aparecer "READ" y luego "FILE="

    Es posible también correr en la misma copia-carpeta dos corridas
    para PTRAC con neutrones y otra para fotones. Parte del manejo de
    los inputs lo hace el script en bash. En 'PC' el script ejecuta MCNP,
    mientras que en 'cluster' el script debe generar dos inputs agregando
    "_n" y "_p" (esto es importante).

    Parámetros
    ----------
        n_corridas : int
            Número de corridas que se van a ejecutar
        input_mcnp : str
            Entrada de MCNP que se quiere paralelizar
        machine : str ('PC', 'cluster')
            'PC' : paraleliza  en una PC
            'cluster' : paraleliza en un cluster
        n_tasks : int
            Cantidad de procesos a correr por cada corrida
            Sólo se utiliza con 'PC' y con 'cluster'+'OpenMP'
        queue_script : str
            Nombre del script para lanzar la corrida en el cluster
        parallelization : str ('OpenMP', 'serie')
            Tipo de paralelización que se va a utilizar. Se asume que cada
            una posee un 'queue_script' diferente (como sucede en Neurus).
            Si se toma 'serie' se ignora la variable 'n_tasks'
        nombre : str
            Nombre de las carpetas que se generan para cada copia.
            Se crean carpetas con nombre "nombre_xxx".
        run_script : str
            Nombre del script que se va a ejecutar en cada copia.
            Cuando se corre 'PC' el script separa en corridas para fotones
            y neutrones y luego ejecuta MCNP para ambos inputs.
            Cuando se corre en 'cluster' el script sólo debe separ el input
            en otros dos con terminaciones "_n" y "_p"

    TODO: Reescribir en python lo que hacen los scripts en bash
    """

    if machine == 'cluster':
        if queue_script is None:
            print("No se especificó el script para correr en cluster")
            print("Se aborta script...")
            quit()
        if parallelization is None:
            print("No se especifica el tipo de paralelización para " +
                  "correr en un cluster")
            print("Se aborta script...")
            quit()

    # Directorio raiz
    parent = os.getcwd()

    # Se lee el input base de MCNP para ser modificado
    with open(input_mcnp, 'r') as f:
        mcnp_input_base = f.readlines()

    if machine == 'cluster':
        # Se lee el script se slurm para ser modificado
        with open(queue_script, 'r') as f:
            slurm_base = f.readlines()

    # Se generan las corridas
    for i in range(1, n_corridas + 1):
        # Identificación de cada corrida
        id_corrida = str(i).zfill(3)
        dir_corrida = nombre + '_' + id_corrida
        # Crea las carpetas si no existen
        # si existen se saltean (se deja como estaba)
        try:
            os.mkdir(dir_corrida)
        except FileExistsError:
            print("El directorio " + dir_corrida + " ya existe, se saltea")
            continue
        # Entra a la carpeta
        os.chdir(dir_corrida)
        # Genera input para cada corrida
        input_corrida = dir_corrida
        with open(input_corrida, 'w') as f:
            for line in mcnp_input_base:
                if 'RAND ' in line:
                    # Nueva semilla
                    rand_num = 2*i - 1
                    f.write('RAND GEN=4 STRIDE=500000 SEED='
                            + str(rand_num) + '\n')
                elif line.startswith("READ"):
                    # Si el input lee otro archivo, subo un nivel
                    f.write(line.replace('FILE=', 'FILE=../'))
                else:
                    f.write(line)

        # Genera script de slurm
        # Si se corre en el cluster
        if machine == 'cluster':
            if run_script:
                subprocess.call(['../' + run_script, input_corrida])
                posfix = ['_n', '_p']
            else:
                posfix = ['']

            for pos in posfix:
                new_que = queue_script + pos
                new_inp = input_corrida + pos
                # Si se utiliza OpenMP
                if parallelization == "OpenMP":
                    _modifica_slurm_openmp(new_que, slurm_base,
                                           new_inp, n_tasks)
                # Si se utiliza en serie
                elif parallelization == 'serie':
                    _modifica_slurm_serie(new_que, slurm_base,
                                          new_inp)
                # Se envia el job
                command = "sbatch " + new_que
                process = subprocess.Popen(command.split(),
                                           stdout=subprocess.PIPE)
                output, error = process.communicate()
        # Si se corre en una PC
        elif machine == 'PC':
            if run_script:
                command = '../' + run_script + ' ' + input_corrida
            else:
                command = "mcnp6 tasks {0} i={1} n={1}.".format(n_tasks,
                                                                input_corrida)
            subprocess.Popen(command.split(), stdout=subprocess.DEVNULL)

        print(' Se sale de la carpeta ' + dir_corrida)
        # Se vuelve al directorio original
        os.chdir(parent)
    return None


if __name__ == '__main__':

    # Para correr en una PC un solo archivo
    # run_paralelo(4, 'input', machine='PC')

    # Para correr en una PC con n + p por separado
    # (leer 'run_sdef.sh' para ver cómo tiene que ser el input
    run_paralelo(n_corridas=4,
                 input_mcnp='in_sdef',
                 machine='PC',
                 run_script='run_sdef.sh')

    # Para correr en Neurus en serie
    # n_corridas = 4
    # input_mcnp = 'input'
    # run_paralelo(n_corridas,
    #              input_mcnp,
    #              machine='cluster',
    #              queue_script='mcnp6.slurm',
    #              parallelization='serie',
    #              run_script='run_sdef_cluster.sh')

    # Para correr en Neurus con OpenMP
    # n_corridas = 4
    # input_mcnp = 'input'
    # run_paralelo(n_corridas,
    #              input_mcnp,
    #              machine='cluster',
    #              n_tasks=8,
    #              queue_script='mcnp6_gcc6.3_openmp.slurm',
    #              parallelization='OpenMP',
    #              run_script='run_sdef_cluster.sh')
