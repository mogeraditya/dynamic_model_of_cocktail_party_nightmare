#!/bin/bash 
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1   # only start 1 task via srun because Python multiprocessing starts more tasks internally
#SBATCH --cpus-per-task=128  
#SBATCH --time 24:00:00

#SBATCH -o limchannels_%j.out
#SBATCH -e limchannels_%j.err
#SBATCH --job-name=dynamic_model
#SBATCH --mail-type=ALL
#SBATCH --mail-user=aditya.moger@uni-konstanz.de


# Recommended: prevent nested threading inside each worker process
# export OMP_NUM_THREADS=1
# export MKL_NUM_THREADS=1
# export OPENBLAS_NUM_THREADS=1
# export NUMEXPR_NUM_THREADS=1


module load anaconda/3/2023.03

conda init bash
source ~/.bashrc
conda activate /u/amoger/conda-envs/cocktail_3_dynamic_model

# Use srun inside allocations (good Slurm hygiene)
srun python3 ./JammingExperiment/Scripts/ProcessingScripts/simulation_multiple_parameters.py $SLURM_CPUS_PER_TASK

