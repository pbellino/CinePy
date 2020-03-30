#!/bin/bash
#
# Version de script: 201812131110
#
## En SBATCH los comentarios son: "## ...."
#
#SBATCH -J MCNP6_OpenMP        # Job NAME (human input)
#SBATCH -n 8                    # number of cpu cores (human input)
#SBATCH -N 1                 # number of Nodes (human)
#SBATCH --mem-per-cpu=1G         # Minimum memory required per allocated CPU (human input)
#SBATCH --wait-all-nodes=1       # Do not begin execution until all nodes are ready for use
#SBATCH -o %j.slurm.out          # STDOUT file
#SBATCH -e %j.slurm.err          # STDERR file
#SBATCH --cpu-freq high          # Set the highest available cpu frequency
#SBATCH --verbose                # Be verbose
#
#
#More options: https://slurm.schedmd.com/sbatch.html
#
## Ejemplo de comentario SBATCH 
#SBATCH  --hint=nomultithread   # TURN OFF hyperthreading
#SBATCH  --threads-per-core=1   # Number of threads per core to allocate (use "1" with --hint=nomultithread)

############################## MAIN ################################


#Limpia enviroment
module purge

#Suma la posibilidad de cargar modulos propios del usuario
module load use.own 


module load mcnp6.2
module load gcc/6.3.0

#Show user limits
echo
echo "Plantilla DCAP (OpenMP_gcc6.3) rev. 201812131110" 
echo
echo
echo "User limits:"
echo
ulimit -a
echo
#Show slurm var:
echo
echo "Slurm enviroment:"
echo
if [ -z "$SLURM_NPROCS" ] ; then
    if [ -z "$SLURM_NTASKS_PER_NODE" ] ; then
      SLURM_NTASKS_PER_NODE=1
    fi
    SLURM_NPROCS=$(( $SLURM_JOB_NUM_NODES * $SLURM_NTASKS_PER_NODE ))
fi
echo "SLURM_JOBID             = " $SLURM_JOBID
echo "SLURM_JOB_NAME          = " $SLURM_JOB_NAME
echo "SLURM_JOB_NODELIST      = " $SLURM_JOB_NODELIST
echo "SLURM_JOB_PARTITION     = " $SLURM_JOB_PARTITION
echo "SLURM_JOB_ACCOUNT       = " $SLURM_JOB_ACCOUNT
echo "SLURM_MEM_PER_CPU       = " $SLURM_MEM_PER_CPU
echo "SLURM_MEM_PER_NODE      = " $SLURM_MEM_PER_NODE
echo "SLURM_ARRAY_JOB_ID      = " $SLURM_ARRAY_JOB_ID
echo "SLURM_ARRAY_TASK_ID     = " $SLURM_ARRAY_TASK_ID
echo "SLURMTMPDIR             = " $SLURMTMPDIR
echo "SLURM_RESTART_COUNT     = " $SLURM_RESTART_COUNT
echo "SLURM_TASKS_PER_NODE    = " $SLURM_TASKS_PER_NODE
echo "SLURM_NTASKS            = " $SLURM_NTASKS
echo "SLURM_NTASKS_PER_CORE   = " $SLURM_NTASKS_PER_CORE
echo "SLURM_NTASKS_PER_NODE   = " $SLURM_NTASKS_PER_NODE
echo "SLURM_NTASKS_PER_SOCKET = " $SLURM_NTASKS_PER_SOCKET
echo "SLURM_JOB_NUM_NODES     = " $SLURM_JOB_NUM_NODES 
echo "SLURM_NNODES            = " $SLURM_NNODES 
echo "SLURM_CPUS_PER_TASK     = " $SLURM_CPUS_PER_TASK
echo "SLURM_NPROCS            = " $SLURM_NPROCS
echo "SLURM_SUBMIT_DIR        = " $SLURM_SUBMIT_DIR
echo "SLURM_SUBMIT_HOST       = " $SLURM_SUBMIT_HOST
echo "SLURM_CPU_FREQ_REQ      = " $SLURM_CPU_FREQ_REQ

####Backward compatibility""""""
cd $SLURM_SUBMIT_DIR
srun --nodes=${SLURM_NNODES} bash -c 'hostname'> $SLURM_JOBID.machines
srun --nodes=${SLURM_NNODES} bash -c 'hostname' | sort -r | uniq > $SLURM_JOBID.mpd.hosts
NUM_PROCS=`cat $SLURM_JOBID.machines|wc -l`
NUM_NODES=`cat $SLURM_JOBID.mpd.hosts|wc -l`
echo NUM_PROCS = $NUM_PROCS
echo NUM_NODES = $NUM_NODES

#Launch

echo
echo
echo -n "pwd: "
pwd
echo -n "LD_LIBRARY_PATH: "
echo $LD_LIBRARY_PATH
echo
echo -n "BEGIN  RUN started date-time: "
date --iso-8601=seconds
echo

#OpenMP BEGIN

bin="/share/grcn/pbellino/MCNP_v6.2/MCNP_CODE/bin/mcnp6"
param="ixr tasks 8  n=C29i"
echo $bin $param
GOMP_DEBUG=1 OMP_DISPLAY_ENV=VERBOSE OMP_NUM_THREADS=8 $bin $param
#OpenMP END

echo
echo -n "END RUN ended date-time: "
date --iso-8601=seconds

