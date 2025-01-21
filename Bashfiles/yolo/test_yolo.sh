#!/bin/bash

#SBATCH --nodes=1

#SBATCH --tasks-per-node=8

#SBATCH --partition=gpu2080 
# try gpua100( max 240 GB),gpu2080( max 240 GB),gpuhgx,gpu3090,

#SBATCH --mem=120GB

#SBATCH --gres=gpu:1

#SBATCH --time=0-02:00:00

#SBATCH --job-name=bc_th_test

#SBATCH --output=/scratch/tmp/kwundram/output/bc_th/test/test_%j.log

#SBATCH --mail-type=ALL

#SBATCH --mail-user=kwundram@uni-muenster.de

#load modules with available GPU support (this is an example, modify to your needs!)
module purge
#module load palma/2023a CUDA/12.1.1 Miniconda3/4.12.0
module load palma/2021a Miniconda3/4.9.2

CONDA_BASE=$(conda info --base)
source $CONDA_BASE/etc/profile.d/conda.sh
conda deactivate
conda activate $HOME/envs/bc_th

# code location
yh=$HOME/bcth/Bachelor_Thesis/yolov7/
# data yaml contains absolute paths for training  and/or testing
data="$yh"/data/zebrafish_test.yaml
# weights for testing
# /scratch/tmp/kwundram/bcth/runs/train/20.01.2025/bc_th_train_ep180_img1024_t23:20:51/weights/best.pt
model=bc_th_train_ep180_img1024_t23:20:51
weights=/scratch/tmp/kwundram/bcth/runs/train/20.01.2025/$model/weights/best.pt

day=`date +%d.%m.%Y`
time=`date +%H:%M:%S`
echo " $day, $time"

project=/scratch/tmp/kwundram/bcth/runs/test/$day
# [1024, 896, 768, 640, 512, 384, 256]
img=1024
conf=0.5
iou=0.5
name="$model"_test_iou_$iou"_conf"$conf"_img"$img""

# sbatch /home/k/kwundram/bcth/Bachelor_Thesis/Bashfiles/yolo/test_yolo.sh
python $yh/test.py --data $data --verbose --save-txt --single-cls  --task test --img $img --batch 32 --conf $conf --iou $iou --device 0 --weights $weights --project $project --name $name
conda deactivate
module purge