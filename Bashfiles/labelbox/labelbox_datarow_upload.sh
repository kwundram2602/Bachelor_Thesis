#!/bin/bash

#SBATCH --nodes=1

#SBATCH --tasks-per-node=30

#SBATCH --partition=express
# normal ,long, express,gpua100
#SBATCH --mem=48GB

#SBATCH --time=0-02:00:00

#SBATCH --job-name=lbx_label_upload

#SBATCH --mail-type=ALL

#SBATCH --output /scratch/tmp/%u/output/bc_th/labelbox/datarow_upload/%j.log

#load modules 

module purge
module load palma/2021a Miniconda3/4.9.2

# conda
CONDA_BASE=$(conda info --base)
source $CONDA_BASE/etc/profile.d/conda.sh
conda deactivate
conda activate $HOME/envs/bc_th
# upload script
script=/home/k/kwundram/bcth/Bachelor_Thesis/labelbox_utils/lb_data_row_upload2.py
# folder with images for  uploading
images_folder=/scratch/tmp/kwundram/bcth/data/whole_data/converted/extr_images/Batch1/B1D1/B1D1_C1_ST_c/
slice_size=10
# ndjson from labelbox to check for already existing external ids
#ndjson="/home/k/kwundram/bcth/Bachelor_Thesis/labelbox_utils/29.11_2.ndjson"
# sbatch /home/k/kwundram/bcth/Bachelor_Thesis/Bashfiles/labelbox/labelbox_datarow_upload.sh
python $script --images_folder $images_folder  --slice_size $slice_size

# 1.12 : 18.219