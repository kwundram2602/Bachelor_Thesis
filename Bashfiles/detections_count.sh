#!/bin/bash


#SBATCH --nodes=1

#SBATCH --tasks-per-node=8

#SBATCH --partition=express

#SBATCH --mem=20GB

#SBATCH --time=0-01:00:00

#SBATCH --job-name=bc_th_detect

#SBATCH --output=/scratch/tmp/kwundram/output/bc_th/detect_count/detect_count%j.log

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
yh=$HOME/bcth/Bachelor_Thesis/
labels_folder=/scratch/tmp/kwundram/bcth/runs/detect_test/12.11.2024/batch1_day2_1753_1805/detect_batch1_day2_1753_1805_conf0.2_t13:17:19/labels
image_path=/scratch/tmp/kwundram/bcth/runs/detect_test/12.11.2024/batch1_day2_1753_1805/detect_batch1_day2_1753_1805_conf0.2_t13:17:19/ex_frame_00001.png
output_path=/scratch/tmp/kwundram/bcth/data/whole_data/heatmaps/
# sbatch /home/k/kwundram/bcth/Bachelor_Thesis/Bashfiles/detections_count.sh

python "$yh"/yolo_count/count_detections.py --labels_folder "$labels_folder" --image_path "$image_path" --output_path "$output_path"


