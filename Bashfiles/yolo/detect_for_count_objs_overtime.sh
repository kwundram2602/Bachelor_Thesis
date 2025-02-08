#!/bin/bash

#SBATCH --nodes=1

#SBATCH --tasks-per-node=8


#SBATCH --partition=gpua100

#SBATCH --mem=64GB

#SBATCH --gres=gpu:1

#SBATCH --time=1-00:00:00

#SBATCH --job-name=bc_th_detect_objs_over_time

#SBATCH --output=/scratch/tmp/kwundram/output/bc_th/detect/detect_%j.log

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


# video batch and folder with extracted images as source for detection
batch=Batch1
batch_day=B1D1
# 3 videos with 10 min each
video_folder="$batch_day"_C3_OE_c_10_min

source=/scratch/tmp/kwundram/bcth/data/whole_data/converted/extr_images/first_x_min/$batch/$batch_day/$video_folder
# model weights
weights=/scratch/tmp/kwundram/bcth/runs/train/16.01.2025/bc_th_train_ep180_img1024_t14:34:05/weights/best.pt

# parent folder for detection tests on trained models ( not only pretrained yolov7)
project=/scratch/tmp/kwundram/bcth/runs/detect_count_over_time/
# parent folder for detection (only when using yolo weights)
#project=/scratch/tmp/kwundram/bcth/runs/detect
conf=0.5
name="$video_folder"_$conf

# sbatch $HOME/bcth/Bachelor_Thesis/Bashfiles/yolo/detect_for_count_objs_overtime.sh
python "$yh"detect.py --weights "$weights" --conf $conf --img-size 1024 --source "$source" --save-txt --project "$project" --name "$name"
rm -r "$project/$name/*.png"
conda deactivate
module purge