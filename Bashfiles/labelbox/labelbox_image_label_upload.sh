#!/bin/bash

#SBATCH --nodes=1

#SBATCH --tasks-per-node=10

#SBATCH --partition=long
# normal , express, bigsmp
#SBATCH --mem=24GB

#SBATCH --time=0-60:00:00

#SBATCH --job-name=lbx_label_upload

#SBATCH --mail-type=ALL

#SBATCH --output /scratch/tmp/%u/output/bc_th/labelbox/label_upload/upload%j.log

#load modules 

module purge
module load palma/2021a Miniconda3/4.9.2

# conda
CONDA_BASE=$(conda info --base)
source $CONDA_BASE/etc/profile.d/conda.sh
conda deactivate
conda activate $HOME/envs/bc_th

# repo
repo=/home/k/kwundram/bcth/Bachelor_Thesis/
# args
ndjson_path=/scratch/tmp/kwundram/bcth/data/whole_data/90k_finalexport_chunk1.ndjson
#external_id=B1D1_C1_ST_converted_chunk_7200_8400.mp4
#external_id_woe="$(basename "$external_id" .${external_id##*.})"
#echo "$external_id_woe"
label_path=/scratch/tmp/kwundram/bcth/runs/detect_lbx/28.11.2024/B1D1_C1_ST_c_conf0.2/labels
#label_path=/scratch/tmp/kwundram/bcth/runs/detect_mal/24.11.2024/18:37:40/$external_id_woe/labels/
# run labelbox upload
# sbatch /home/k/kwundram/bcth/Bachelor_Thesis/Bashfiles/labelbox/labelbox_image_label_upload.sh
python $repo/labelbox_utils/lb_image_label_upload.py  --label_path $label_path --ndjson_path $ndjson_path