#!/bin/bash

#SBATCH --nodes=1

#SBATCH --tasks-per-node=8

#SBATCH --partition=express,normal,long
# try normal, express,long

#SBATCH --mem=92GB

#SBATCH --time=0-2:00:00

#SBATCH --job-name=track

#SBATCH --output=/scratch/tmp/kwundram/output/bc_th/track/track%j.log

#SBATCH --mail-type=ALL

#SBATCH --mail-user=kwundram@uni-muenster.de

#load modules
module purge
module load palma/2021a Miniconda3/4.9.2

CONDA_BASE=$(conda info --base)
source $CONDA_BASE/etc/profile.d/conda.sh
conda deactivate
conda activate $HOME/envs/bc_th

script=/home/k/kwundram/bcth/Bachelor_Thesis/yolo_utils/track.py

#detections=/scratch/tmp/kwundram/bcth/runs/detect_heatmap/B1D1_C3_OE_c_10_min_0.5/
#detections=/scratch/tmp/kwundram/bcth/runs/detect_heatmap/B1D3_C3_OE_c_10_min_0.5

#label_folder=$detections/labels # real labels
detections=/scratch/tmp/kwundram/bcth/runs/detect_heatmap/B1D3_C3_OE_c_10_min_0.5
label_folder=$detections/interpolated_labels
output_folder=$detections/labels_del_short 
#label_folder=/scratch/tmp/kwundram/bcth/runs/test_track/labels
#pngs=/scratch/tmp/kwundram/bcth/runs/test_track/pngs
pngs=$detections

cd $pngs
if [ ! -d ./tracked ]; then
    mkdir ./tracked
fi
if [ ! -d ./labels_del_short ]; then
    mkdir ./labels_del_short
fi
#cp -a "$label_folder/*" "$output_folder/"
python $script --label_folder $label_folder --pngs $pngs --output_folder $output_folder
# sbatch /home/k/kwundram/bcth/Bachelor_Thesis/Bashfiles/yolo/track.sh