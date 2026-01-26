#!/bin/bash -l
#
# Python multiprocessing job script for MPCDF Viper. Running the dynamic model for all parameter combinations for sensitivity analysis. 
#
#SBATCH -o ./out.%j
#SBATCH -e ./err.%j
#SBATCH -D ./
#SBATCH -J PYTHON_MP_model
#SBATCH --nodes=1             # request a full node
#SBATCH --ntasks-per-node=1   # only start 1 task via srun because Python multiprocessing starts more tasks internally
#SBATCH --cpus-per-task=128    # assign all the cores to that first task to make room for Python's multiprocessing tasks
#SBATCH --time=00:10:00

# Recommended: prevent nested threading inside each worker process
# export OMP_NUM_THREADS=1
# export MKL_NUM_THREADS=1
# export OPENBLAS_NUM_THREADS=1
# export NUMEXPR_NUM_THREADS=1

module load anaconda/3/2023.03
conda activate cocktail_3_dynamic_model

# Use srun inside allocations (good Slurm hygiene)
srun python3 ./JammingExperiment/Scripts/ProcessingScripts/simulation_multiple_parameters.py $SLURM_CPUS_PER_TASK
