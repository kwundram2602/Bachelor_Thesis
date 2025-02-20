#!/bin/bash

#SBATCH --nodes=1

#SBATCH --tasks-per-node=8

#SBATCH --partition=express,normal,long
# try normal, express,long

#SBATCH --mem=92GB

#SBATCH --time=0-2:00:00

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

#detections=/scratch/tmp/kwundram/bcth/runs/detect_heatmap/B1D1_C3_OE_c_10_min_0.5/
detections=/scratch/tmp/kwundram/bcth/runs/detect_heatmap/B1D3_C3_OE_c_10_min_0.5

label_folder=$detections/labels # real labels
#label_folder=/scratch/tmp/kwundram/bcth/data/whole_data/converted/extr_images/for_over_time_gt/detected_labels2/labels
output_folder=$detections/interpolated_labels # interpolated labels
#output_folder=/scratch/tmp/kwundram/bcth/data/whole_data/converted/extr_images/for_over_time_gt/interpolated_labels
cd $detections
if [ ! -d ./interpolated_labels ]; then
    mkdir ./interpolated_labels
fi
if [ ! -d ./deleted_bbox ]; then
    mkdir ./deleted_bbox
fi
#aoi_filtered
if [ ! -d ./aoi_filtered ]; then
    mkdir ./aoi_filtered
fi
# x_min, y_min, x_max, y_max  : 
# rectangle spans horizontally from x_min to x_max and vertically from y_min to y_max
# B1D3_C3_OE
aois=("80 480 1180 850")   
# parse aois to string
aoi_args=()
for aoi in "${aois[@]}"; do
    aoi_args+=("--aoi $aoi")
done
aoi_args_string=$(IFS=" "; echo "${aoi_args[*]}")

python $script --label_folder $label_folder --output_folder $output_folder --pngs_dir $detections $aoi_args_string
# sbatch /home/k/kwundram/bcth/Bachelor_Thesis/Bashfiles/yolo/interpolate_detections.py.sh