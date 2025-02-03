#!/bin/bash

#SBATCH --nodes=1

#SBATCH --tasks-per-node=8

#SBATCH --partition=gpua100,gpu2080,gpuhgx,gpu3090
# try gpua100( max 240 GB),gpu2080( max 240 GB),gpuhgx,gpu3090,

#SBATCH --mem=200GB

#SBATCH --gres=gpu:1

#SBATCH --time=0-24:00:00

#SBATCH --job-name=bc_th_train

#SBATCH --output=/scratch/tmp/kwundram/output/bc_th/training/train%j.log

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
data="$yh"/data/zebrafish_data.yaml
# hyp : hyperparameters for training
# cfg : nc , backbone ,head, anchor etc.

# learning weights
pt=yolov7_training
#pt=yolov7-e6_training
if [ "$pt" == "yolov7_training" ]; then
    cfg="$yh"cfg/training/yolov7_zebrafish.yaml
    hyp="$yh"/data/hyp.scratch.p5_zebra.yaml
    train_Script=$yh/train.py
elif [ "$pt" == "yolov7-e6_training" ]; then
    cfg=$yh/cfg/training/zebrafish_yolov7-e6.yaml
    hyp="$yh"/data/hyp.scratch.p6_zebra.yaml
    train_Script=$yh/train_aux.py
fi
weights=/scratch/tmp/kwundram/bcth/pt_weights/transfer-learning/$pt.pt
day=`date +%d.%m.%Y`
time=`date +%H:%M:%S`
echo " $day, $time"
epochs=180
project=/scratch/tmp/kwundram/bcth/runs/train/"$day"/
# [1024, 896, 768, 640, 512, 384, 256]
img=640
name="$pt"$epochs"_img"$img"_t"$time""

# sbatch /home/k/kwundram/bcth/Bachelor_Thesis/Bashfiles/yolo/train.sh
# --evolve ?
python $train_Script --workers 4 --adam --device 0 --batch-size 8 --img $img $img --data "$data" --cfg "$cfg"  --weights "$weights" --hyp "$hyp" --single-cls --epochs $epochs  --name "$name"  --project "$project"

results=$HOME/bcth/Bachelor_Thesis/yolo_utils/results_graph.py
results_txt=$project/$name/results.txt
python $results --file_path $results_txt
conda deactivate
module purge