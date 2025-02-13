#!/bin/bash

#SBATCH --nodes=1

#SBATCH --tasks-per-node=8

#SBATCH --partition=express
# try normal, express,long

#SBATCH --mem=92GB

#SBATCH --time=0-0:30:00

#SBATCH --job-name=interpolate_det

#SBATCH --output=/scratch/tmp/kwundram/output/bc_th/interpolate/inerpolate_%j.log

#SBATCH --mail-type=ALL

#SBATCH --mail-user=kwundram@uni-muenster.de

#load modules
module purge
module load palma/2021a Miniconda3/4.9.2

CONDA_BASE=$(conda info --base)
source $CONDA_BASE/etc/profile.d/conda.sh
conda deactivate
conda activate $HOME/envs/bc_th

script=/home/k/kwundram/bcth/Bachelor_Thesis/yolo_utils/interpolate_detections.py

detections=/scratch/tmp/kwundram/bcth/runs/detect_heatmap/B1D1_C3_OE_c_10_min_0.5/
label_folder=$detections/labels
output_folder=$detections/interpolated_labels
cd $detections
if [ ! -d ./interpolated_labels ]; then
    mkdir ./interpolated_labels
fi

python $script --label_folder $label_folder --output_folder $output_folder
# sbatch /home/k/kwundram/bcth/Bachelor_Thesis/Bashfiles/yolo/interpolate_detections.py.sh