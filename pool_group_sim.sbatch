#!/bin/bash 
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1   # only start 1 task via srun because Python multiprocessing starts more tasks internally
#SBATCH --cpus-per-task=128  
#SBATCH --time 24:00:00

#SBATCH -o group_experiment_%j.out
#SBATCH -e group_experiment_%j.err
#SBATCH --job-name=dynamic_model
#SBATCH --mail-type=ALL
#SBATCH --mail-user=aditya.moger@uni-konstanz.de


# Recommended: prevent nested threading inside each worker process
export OMP_NUM_THREADS=1
export MKL_NUM_THREADS=1
export OPENBLAS_NUM_THREADS=1
export NUMEXPR_NUM_THREADS=1
# export OMP_NUM_THREADS=1

module load anaconda/3/2023.03

conda init bash
source ~/.bashrc
conda activate /u/amoger/conda-envs/cocktail_3_dynamic_model

# Use srun inside allocations (good Slurm hygiene)
srun python3 ./dynamic_model/simulation/simulation_multiple_parameters.py $SLURM_CPUS_PER_TASK

# rsync -av -e 'ssh -J amoger@gate1.mpcdf.mpg.de' amoger@viper.mpcdf.mpg.de:/u/amoger/dynamic_model_of_cocktail_party_nightmare/sensitivity_analysis /home/adityamoger/Documents/csv_storage --include="*/" --include="*.csv" --exclude="*"
# rsync -av -e 'ssh -J amoger@gate1.mpcdf.mpg.de' amoger@viper.mpcdf.mpg.de:/u/amoger/dynamic_model_of_cocktail_party_nightmare/ /home/adityamoger/Documents/out_err_file_storage --include="*/" --include="*.out" --include="*.err" --exclude="*"
