#!/bin/bash

#SBATCH --nodes=1

#SBATCH --tasks-per-node=30

#SBATCH --partition=express
# normal ,long, express,gpua100
#SBATCH --mem=48GB

#SBATCH --time=0-02:00:00

#SBATCH --job-name=ndjson_label

#SBATCH --mail-type=ALL

#SBATCH --output /scratch/tmp/%u/output/bc_th/labelbox/ndjson_label/%j.log

module purge
module load palma/2021a Miniconda3/4.9.2

CONDA_BASE=$(conda info --base)
source $CONDA_BASE/etc/profile.d/conda.sh
conda deactivate
conda activate $HOME/envs/bc_th

ndjson=/scratch/tmp/kwundram/bcth/data/whole_data/label_ndjsons/zebrafish_ba_kjell12_12_2024_151.ndjson
output_folder=/scratch/tmp/kwundram/bcth/data/whole_data/converted/labels/B1D1_C1_ST
script=/home/k/kwundram/bcth/Bachelor_Thesis/labelbox_utils/ndjson_to_label.py
pngs=/scratch/tmp/kwundram/bcth/data/whole_data/converted/extr_images/Batch1/B1D1/B1D1_C1_ST_c/

python $script --ndjson $ndjson --output_folder $output_folder --pngs $pngs

# sbatch /home/k/kwundram/bcth/Bachelor_Thesis/Bashfiles/labelbox/ndjson_tolabel.sh