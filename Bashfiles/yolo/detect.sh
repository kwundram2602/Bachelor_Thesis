#!/bin/bash

#SBATCH --nodes=1

#SBATCH --tasks-per-node=8


#SBATCH --partition=gpua100

#SBATCH --mem=64GB

#SBATCH --time=1-00:00:00

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

batch=B1D1_C1_ST_c
source=/scratch/tmp/kwundram/bcth/data/whole_data/converted/extr_images/Batch1/B1D1/$batch
# pre trained weights (own or yolo weights)
weights=/scratch/tmp/kwundram/bcth/runs/train/09.11.2024/bc_th_train_ep150_img1024_t19:40:37/weights/best.pt
#weights="$WORK"/bcth/pt_weights/yolov7x.pt  yolov7-e6e.pt
#weights="$WORK"/bcth/pt_weights/yolov7-e6e.pt
day=`date +%d.%m.%Y`
time=`date +%H:%M:%S`
# parent folder for detection tests on trained models ( not only pretrained yolov7)
project=/scratch/tmp/kwundram/bcth/runs/detect_lbx/$day/
# parent folder for detection (only when using yolo weights)
#project=/scratch/tmp/kwundram/bcth/runs/detect
conf=0.2
name=$batch"_conf"$conf

# sbatch $HOME/bcth/Bachelor_Thesis/Bashfiles/yolo/detect.sh
python "$yh"detect.py --weights "$weights" --conf $conf --img-size 1024 --source "$source" --save-txt --project "$project" --name "$name"
conda deactivate
module purge