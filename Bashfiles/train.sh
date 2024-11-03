#!/bin/bash

#SBATCH --nodes=1

#SBATCH --tasks-per-node=8

#SBATCH --partition=gpua100

#SBATCH --mem=20GB

#SBATCH --gres=gpu:1

#SBATCH --time=7-00:00:00

#SBATCH --job-name=bc_th

#SBATCH --output=/scratch/tmp/kwundram/output/bc_th/training/train%j.log

#SBATCH --mail-type=ALL

#SBATCH --mail-user=kwundram@uni-muenster.de

#load modules with available GPU support (this is an example, modify to your needs!)
module purge
module load palma/2021a Miniconda3/4.9.2

CONDA_BASE=$(conda info --base)
source $CONDA_BASE/etc/profile.d/conda.sh
conda deactivate
conda activate $HOME/envs/bc_th

# code location
yh=$HOME/bcth/Bachelor_Thesis/yolov7/
# data
#tb="$WORK"/bcth/data/whole_data/
tb="$WORK"/bcth/data/
# yolov7x yaml stays same (anchor, nc, backbone )
cfg="$yh"/cfg/training/yolov7x_zebrafish.yaml
# data yaml contains absolute paths for training  and/or testing
data="$yh"/data/zebrafish_data.yaml
# hyp stays same (parameter)
hyp="$yh"/data/hyp.scratch.p5_bcth.yaml
#yolov7x weights
weights="$WORK"/bcth/pt_weights/yolov7x.pt

name="bc_th_train"
epochs=80
project="$tb"/runs

python "$yh"/yolov7/train.py --workers 4 --device 0 --batch-size 6 --img 1280 1280 --data "$data" --cfg "$cfg"  --weights "$weights" --hyp "$hyp" --single-cls --epochs $epochs  --name "$name"  --project "$project"

conda deactivate
module purge