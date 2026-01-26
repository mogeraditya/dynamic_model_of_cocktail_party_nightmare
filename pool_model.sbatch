#!/bin/bash
#SBATCH --job-name=dynamic-model-test
#SBATCH --partition=dev_cpu
#SBATCH --time=00:10:00
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --output=pool-test-%j.out
#SBATCH --error=pool-test-%j.err

# Recommended: prevent nested threading inside each worker process
export OMP_NUM_THREADS=1
export MKL_NUM_THREADS=1
export OPENBLAS_NUM_THREADS=1
export NUMEXPR_NUM_THREADS=1

module load anaconda/3/2023.03
conda activate cocktail_3_dynamic_model

# Use srun inside allocations (good Slurm hygiene)
srun python test_starmap.py --tasks 256 --n 2000000
