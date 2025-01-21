#!/bin/bash

#SBATCH --nodes=1

#SBATCH --tasks-per-node=8


#SBATCH --partition=requeue-zen,gpua100,gpu2080,gpuhgx,gpu3090
# try gpua100( max 240 GB),gpu2080( max 240 GB),gpuhgx,gpu3090,requeue-zen,gpuexpress
#SBATCH --mem=60GB

#SBATCH --gres=gpu:1

#SBATCH --time=0-00:20:00

#SBATCH --job-name=bc_th_detect_aoi

#SBATCH --output=/scratch/tmp/kwundram/output/bc_th/detect_aoi/detect_%j.log

#SBATCH --mail-type=ALL

#SBATCH --mail-user=kwundram@uni-muenster.de

#load modules
module purge
module load palma/2021a Miniconda3/4.9.2

CONDA_BASE=$(conda info --base)
source $CONDA_BASE/etc/profile.d/conda.sh
conda deactivate
conda activate $HOME/envs/bc_th

yh=$HOME/bcth/Bachelor_Thesis/yolov7/
# video batch and folder with extracted images as source for detection
camera=C3
batch=Batch1
batch_day=B1D1
#videoname="$batch_day"_"$camera"_OE_c
videoname=test
#source=/scratch/tmp/kwundram/bcth/data/whole_data/converted/extr_images/$batch/$batchday/$videoname
source=/scratch/tmp/kwundram/bcth/data/whole_data/test_extr_images/
# pre trained weights (own or yolo weights)
weights=/scratch/tmp/kwundram/bcth/runs/train/16.01.2025/bc_th_train_ep180_img1024_t14:34:05/weights/best.pt

day=`date +%d.%m.%Y`
time=`date +%H:%M:%S`
# parent folder for detection tests on trained models ( not only pretrained yolov7)
project=/scratch/tmp/kwundram/bcth/runs/detect_aoi/$day/
# parent folder for detection (only when using yolo weights)
#project=/scratch/tmp/kwundram/bcth/runs/detect
conf=0.4
# ymin xmin ymax xmax :Y is width and X is height
# Set AOI based on camera
# Set AOIs based on camera
if [ "$camera" == "C2" ]; then
    aois=("520 350 1024 900" "100 100 200 200")
elif [ "$camera" == "C3" ]; then
    aois=("150 150 500 1000" "450 450 800 1000")
else
    aois=("0 0 1280 1024")
fi

name="${videoname}_conf${conf}_aoi"

# sbatch $HOME/bcth/Bachelor_Thesis/Bashfiles/yolo/detect_aoi.sh
python "$yh"detect_aoi.py --weights "$weights" --aoi $aois --conf $conf --img-size 1024 --source "$source" --save-txt --project "$project" --name "$name"
conda deactivate
module purge