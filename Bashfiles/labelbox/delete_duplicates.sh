#!/bin/bash

#SBATCH --nodes=1

#SBATCH --tasks-per-node=10

#SBATCH --partition=express
# normal , express
#SBATCH --mem=24GB

#SBATCH --time=0-02:00:00

#SBATCH --job-name=delete_duplicates

#SBATCH --mail-type=ALL

#SBATCH --output /scratch/tmp/%u/output/bc_th/labelbox/delete_duplicates/%j.log

#load modules 

module purge
module load palma/2021a Miniconda3/4.9.2

# conda
CONDA_BASE=$(conda info --base)
source $CONDA_BASE/etc/profile.d/conda.sh
conda deactivate
conda activate $HOME/envs/bc_th


script=/home/k/kwundram/bcth/Bachelor_Thesis/labelbox_utils/delete_duplicates.py

python $script
# sbatch /home/k/kwundram/bcth/Bachelor_Thesis/Bashfiles/labelbox/delete_duplicates.sh