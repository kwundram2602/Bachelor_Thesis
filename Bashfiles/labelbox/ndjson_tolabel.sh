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

script=/home/k/kwundram/bcth/Bachelor_Thesis/labelbox_utils/ndjson_to_label.py

# change ndjson and output and pngs
# B1D1_C1_ST_c
ndjson=/scratch/tmp/kwundram/bcth/data/whole_data/studyproject/exported_labels/2024_11_22/study_pr_export.ndjson
output_folder=/scratch/tmp/kwundram/bcth/data/whole_data/studyproject/exported_labels/2024_11_22/
pngs=/scratch/tmp/kwundram/bcth/data/whole_data/converted/extr_images/Batch1/B1D1/B1D1_C1_ST_c
# B1D1_C2_BE
#ndjson=/scratch/tmp/kwundram/bcth/data/whole_data/label_C2_BE.ndjson
#output_folder=/scratch/tmp/kwundram/bcth/data/whole_data/converted/labels/B1D1_C2_BE
#pngs=/scratch/tmp/kwundram/bcth/data/whole_data/converted/extr_images/Batch1/B1D1/B1D1_C2_BE_c

python $script --ndjson $ndjson --output_folder $output_folder --pngs $pngs

# sbatch /home/k/kwundram/bcth/Bachelor_Thesis/Bashfiles/labelbox/ndjson_tolabel.sh