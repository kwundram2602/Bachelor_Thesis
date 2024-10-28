#!/bin/bash

#SBATCH --nodes=1

#SBATCH --tasks-per-node=10

#SBATCH --partition=normal

#SBATCH --mem=24GB

#SBATCH --time=0-02:00:00

#SBATCH --job-name=bcth_warmup

#SBATCH --mail-type=ALL

#SBATCH --output /scratch/tmp/%u/output/wheat_det/training/warmup%j.log

#load modules 
module purge
module load palma/2021a Miniconda3/4.9.2

CONDA_BASE=$(conda info --base)
source $CONDA_BASE/etc/profile.d/conda.sh
conda deactivate
conda activate $HOME/envs/bc_th


wd="$HOME"/bcth/Bachelor-Thesis/warmup
data_folder="$WORK"/bcth/data/warmup_data


python "$wd"/warmup1.py --data_folder "$data_folder"