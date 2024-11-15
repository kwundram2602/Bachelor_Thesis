#!/bin/bash

#SBATCH --nodes=1

#SBATCH --tasks-per-node=10

#SBATCH --partition=normal

#SBATCH --mem=24GB

#SBATCH --time=0-02:00:00

#SBATCH --job-name=bcth_extract_images

#SBATCH --mail-type=ALL

#SBATCH --output /scratch/tmp/%u/output/bc_th/extract_images_%j.log

#load modules 
module purge
module load palma/2022a  GCCcore/11.3.0 FFmpeg/4.4.2

data="$WORK"/bcth/data/warmup_data
batch=batch1_day2_1753_1805
#batch=batch3_day7_1829_1847.mp4
video_path="$data"/$batch.mp4
output="$data"/extracted_images/$batch
yolo_utils=/home/k/kwundram/bcth/Bachelor_Thesis/yolo_utils/
# creates output path if it doesnt exist
python $yolo_utils/create_path.py --path $output

#sbatch $HOME/bcth/Bachelor_Thesis/Bashfiles/extract_images.sh
ffmpeg -i "$video_path" "$output"/ex_frame_%05d.png
