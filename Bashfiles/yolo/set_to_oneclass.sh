#!/bin/bash

#SBATCH --nodes=1

#SBATCH --tasks-per-node=8

#SBATCH --partition=normal

#SBATCH --mem=20GB

#SBATCH --time=0-01:00:00

#SBATCH --job-name=bc_th

#SBATCH --output=/scratch/tmp/kwundram/output/bc_th/set_class/setclass%j.log

#SBATCH --mail-type=ALL

#SBATCH --mail-user=kwundram@uni-muenster.de

#load modules with available GPU support (this is an example, modify to your needs!)
module purge
module load palma/2021a 

# code location
yh=$HOME/bcth/Bachelor_Thesis/
#labels=/scratch/tmp/kwundram/bcth/runs/detect/detect_batch3_day7_1829_1847/labels
labels=/scratch/tmp/kwundram/bcth/runs/detect/detect_batch3_day7_1829_1847/labels
python "$yh"yolo_utils/yolo_labels.py --labels_folder "$labels" 
module purge