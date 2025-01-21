#!/bin/bash

#SBATCH --nodes=1

#SBATCH --tasks-per-node=20

#SBATCH --partition=express

#SBATCH --mem=64GB

#SBATCH --time=0-02:00:00

#SBATCH --job-name=rescale_img

#SBATCH --mail-type=ALL

#SBATCH --output /scratch/tmp/%u/output/bc_th/video/rescale_%j.log

#load modules 
#load modules
module purge
module load palma/2021a GCCcore/10.3.0 Miniconda3/4.9.2 FFmpeg/4.3.2


CONDA_BASE=$(conda info --base)
source $CONDA_BASE/etc/profile.d/conda.sh
conda deactivate
conda activate $HOME/envs/bc_th

script=/home/k/kwundram/bcth/Bachelor_Thesis/video_utils/rescale_img.py

width=1280
height=1024
pngs_folder=/scratch/tmp/kwundram/bcth/data/whole_data/converted/labels
output_folder=/scratch/tmp/kwundram/bcth/data/whole_data/converted/labels_rescaled
python $script --input_folder "$pngs_folder" --output_folder "$output_folder" --width $width --height $height

# sbatch /home/k/kwundram/bcth/Bachelor_Thesis/Bashfiles/video_utils/rescale_img.sh