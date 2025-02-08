#!/bin/bash

#SBATCH --nodes=1

#SBATCH --tasks-per-node=8


#SBATCH --partition=gpua100,gpu2080,gpuhgx,gpu3090

#SBATCH --mem=64GB

#SBATCH --gres=gpu:1

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


# video batch and folder with extracted images as source for detection

#batch=B1D1_C2_BE_c
#source=/scratch/tmp/kwundram/bcth/data/whole_data/converted/extr_images/Batch1/B1D1/$batch
source=/scratch/tmp/kwundram/bcth/data/whole_data/converted/overtime_labeled/pngs
# pre trained weights (own or yolo weights)
weights=/scratch/tmp/kwundram/bcth/runs/train/20.01.2025/bc_th_train_ep180_img1024_t23:20:51/weights/best.pt

# parent folder for detection 
project=/scratch/tmp/kwundram/bcth/data/whole_data/converted/overtime_labeled
conf=0.5
name=detected_labels

# sbatch $HOME/bcth/Bachelor_Thesis/Bashfiles/yolo/detect.sh
python "$yh"detect.py --weights "$weights" --conf $conf --img-size 1024 --source "$source" --save-txt --project "$project" --name "$name"
conda deactivate
module purge