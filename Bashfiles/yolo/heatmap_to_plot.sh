#!/bin/bash


#SBATCH --nodes=1

#SBATCH --tasks-per-node=8

#SBATCH --partition=express
# try normal, express

#SBATCH --mem=20GB

#SBATCH --time=0-01:00:00

#SBATCH --job-name=bc_th_heatmap

#SBATCH --output=/scratch/tmp/kwundram/output/bc_th/heatmap_to_plot/heat_map_to_plot_%j.log

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
image_path=/scratch/tmp/kwundram/bcth/data/whole_data/converted/extr_images/Batch1/B1D1/B1D1_C1_ST_c/B1D1_C1_ST_c00002.png
output_path=/scratch/tmp/kwundram/bcth/data/whole_data/heatmaps/
# sbatch /home/k/kwundram/bcth/Bachelor_Thesis/Bashfiles/yolo/detections_count.sh

script=heatmap_to_plot.py 
python "$yh"/yolo_count/$script --labels_folder "$labels_folder" --image_path "$image_path" --output_path "$output_path"


