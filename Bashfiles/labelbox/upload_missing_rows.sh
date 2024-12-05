#!/bin/bash

#SBATCH --nodes=1

#SBATCH --tasks-per-node=30

#SBATCH --partition=express
# normal ,long, express,gpua100
#SBATCH --mem=48GB

#SBATCH --time=0-02:00:00

#SBATCH --job-name=lbx_upload_missing

#SBATCH --mail-type=ALL

#SBATCH --output /scratch/tmp/%u/output/bc_th/labelbox/upload_missing/%j.log

#load modules 

module purge
module load palma/2021a Miniconda3/4.9.2

# conda
CONDA_BASE=$(conda info --base)
source $CONDA_BASE/etc/profile.d/conda.sh
conda deactivate
conda activate $HOME/envs/bc_th

# script location
script=/home/k/kwundram/bcth/Bachelor_Thesis/labelbox_utils/lb_upload_missing_rows.py

ndjson_path=/scratch/tmp/kwundram/bcth/data/whole_data/export_5_12_24.ndjson
local_files=/scratch/tmp/kwundram/bcth/data/whole_data/converted/extr_images/Batch1/B1D1/B1D1_C1_ST_c

python $script --ndjson_path $ndjson_path --local_files $local_files
# sbatch /home/k/kwundram/bcth/Bachelor_Thesis/Bashfiles/labelbox/upload_missing_rows.sh