#!/bin/bash

#SBATCH --nodes=1

#SBATCH --tasks-per-node=8

#SBATCH --partition=long
# try normal, express,long

#SBATCH --mem=92GB

#SBATCH --time=1-01:00:00

#SBATCH --job-name=bc_th_detect_mal

#SBATCH --output=/scratch/tmp/kwundram/output/bc_th/detect_mal/detect_mal%j.log

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

yh=$HOME/bcth/Bachelor_Thesis/yolov7/
weights=/scratch/tmp/kwundram/bcth/runs/train/09.11.2024/bc_th_train_ep150_img1024_t19:40:37/weights/best.pt

data="$WORK"/bcth/data/whole_data/split_data/B1D1/B1D1_C1/
extracted_images=/scratch/tmp/kwundram/bcth/data/whole_data/extracted_images/B1D1/
day=`date +%d.%m.%Y`
time=`date +%H:%M:%S`
conf=0.2
for folder in "$extracted_images"*; do
    echo "$folder"
    chunk="$(basename "$folder")"
    project=/scratch/tmp/kwundram/bcth/runs/detect_mal/$day/$time/
    name=$chunk
    python "$yh"detect.py --weights "$weights" --conf $conf --img-size 1024 --source "$folder" --save-txt --project "$project" --name "$name"

done
conda deactivate
module purge

# pre trained weights (own or yolo weights)
#weights="$WORK"/bcth/pt_weights/yolov7x.pt  yolov7-e6e.pt
#weights="$WORK"/bcth/pt_weights/yolov7-e6e.pt

# parent folder for detection tests on trained models ( not only pretrained yolov7)
# parent folder for detection (only when using yolo weights)
#project=/scratch/tmp/kwundram/bcth/runs/detect


# sbatch /home/k/kwundram/bcth/Bachelor_Thesis/Bashfiles/detect_for_MAL.sh
#python "$yh"detect.py --weights "$weights" --conf $conf --img-size 1024 --source "$source" --save-txt --project "$project" --name "$name"
