#!/bin/bash


#SBATCH --nodes=1

#SBATCH --tasks-per-node=8

#SBATCH --partition=express
# try normal, express

#SBATCH --mem=20GB

#SBATCH --time=0-01:00:00

#SBATCH --job-name=bc_th_heatmap

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
yolo_utils=/home/k/kwundram/bcth/Bachelor_Thesis/yolo_utils/
yh=$HOME/bcth/Bachelor_Thesis/
video="/scratch/tmp/kwundram/bcth/data/whole_data/split_data/B1D1/B1D1_C1/B1D1_C1_ST_converted_chunk_0_1200.mp4"
labels_folder=/scratch/tmp/kwundram/bcth/runs/detect_test/12.11.2024/batch1_day2_1753_1805/detect_batch1_day2_1753_1805_conf0.2_t13:17:19/labels
frame_folder="$WORK/bcth/data/whole_data/split_data/B1D1/B1D1_C1/extracted_images/B1D1_C1_ST_converted_chunk_0_1200"
output_path=/scratch/tmp/kwundram/bcth/data/whole_data/heatmaps/B1D1_C1_ST_converted_chunk_0_1200/
# sbatch /home/k/kwundram/bcth/Bachelor_Thesis/Bashfiles/yolo/heatmap_over_time.sh
python $yolo_utils/create_path.py --path $output_path
script=heatmap_over_time.py 
python "$yh"/yolo_count/$script --labels_folder "$labels_folder"  --frame_folder "$frame_folder"  --output_path "$output_path"


