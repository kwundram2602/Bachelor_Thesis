#!/bin/bash

#SBATCH --nodes=1

#SBATCH --tasks-per-node=10

#SBATCH --partition=express

#SBATCH --mem=16GB

#SBATCH --time=0-00:30:00

#SBATCH --job-name=bcth_split_video

#SBATCH --mail-type=ALL

#SBATCH --output /scratch/tmp/%u/output/bc_th/split_video_%j.log

#load modules 
module purge
module load palma/2022a  GCCcore/11.3.0

folder_path="$WORK"/bcth/data/warmup_data
output_path="$WORK"/bcth/data/warmup_data/test


python "$HOME"/bcth/Bachelor_Thesis/yolo_utils/data_split.py --folder_path "$folder_path" --output_path"$output_path"