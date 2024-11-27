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

video=B1D1_C1_ST_c
# mp4 folder
video_path=/scratch/tmp/kwundram/bcth/data/whole_data/converted/Batch1/B1D1/$video.mp4
#output folder
output=/scratch/tmp/kwundram/bcth/data/whole_data/converted/extr_images/Batch1/B1D1/$video/

yolo_utils=/home/k/kwundram/bcth/Bachelor_Thesis/yolo_utils/
# creates output path if it doesnt exist
python $yolo_utils/create_path.py --path $output

# sbatch $HOME/bcth/Bachelor_Thesis/Bashfiles/yolo/extract_images.sh
ffmpeg -i "$video_path" "$output"/$video%05d.png
