#!/bin/bash

#SBATCH --nodes=1

#SBATCH --tasks-per-node=10

#SBATCH --partition=express

#SBATCH --mem=24GB

#SBATCH --time=0-02:00:00

#SBATCH --job-name=bcth_extract_images

#SBATCH --mail-type=ALL

#SBATCH --output /scratch/tmp/%u/output/bc_th/extract_images/extract_%j.log

#load modules 
module purge
module load palma/2022a  GCCcore/11.3.0 FFmpeg/4.4.2


# mp4 folder
file=B1D1_C3_OE_c
video_path=/scratch/tmp/kwundram/bcth/data/whole_data/converted/Batch1/B1D1/$file.mp4
#output folder
output=/scratch/tmp/kwundram/bcth/data/whole_data/converted/extr_images/Batch1/B1D1/$file

yolo_utils=/home/k/kwundram/bcth/Bachelor_Thesis/yolo_utils/
# creates output path if it doesnt exist
python $yolo_utils/create_path.py --path $output

# sbatch $HOME/bcth/Bachelor_Thesis/Bashfiles/yolo/extract_images.sh
ffmpeg -i "$video_path" "$output"/$file%05d.png
