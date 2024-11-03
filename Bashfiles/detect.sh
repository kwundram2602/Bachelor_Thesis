#!/bin/bash

#SBATCH --nodes=1

#SBATCH --tasks-per-node=8

#SBATCH --partition=express

#SBATCH --mem=20GB

#SBATCH --time=0-01:00:00

#SBATCH --job-name=bc_th_detect

#SBATCH --output=/scratch/tmp/kwundram/output/bc_th/detect/detect%j.log

#SBATCH --mail-type=ALL

#SBATCH --mail-user=kwundram@uni-muenster.de

#load modules
module purge
module load palma/2021a Miniconda3/4.9.2

CONDA_BASE=$(conda info --base)
source $CONDA_BASE/etc/profile.d/conda.sh
conda deactivate
conda activate $HOME/envs/bc_th

# code location
WORK=/scratch/tmp/kwundram/
yh=$HOME/bcth/Bachelor_Thesis/yolov7/
#/scratch/tmp/kwundram/bcth/data/warmup_data/extracted_images/batch3_day7_1829_1847
batch=batch3_day7_1829_1847
source="$WORK"/bcth/data/warmup_data/extracted_images/"$batch"/
#weights="$WORK"/bcth/pt_weights/yolov7x.pt  yolov7-e6e.pt
weights="$WORK"/bcth/pt_weights/yolov7-e6e.pt
project=/scratch/tmp/kwundram/bcth/runs/detect
name=detect_"$batch"


python "$yh"detect.py --weights "$weights" --conf 0.01 --img-size 1024 --source "$source" --save-txt --project "$project" --name "$name"
conda deactivate
module purge1024