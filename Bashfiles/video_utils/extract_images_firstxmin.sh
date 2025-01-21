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

yolo_utils=/home/k/kwundram/bcth/Bachelor_Thesis/yolo_utils/
batch=Batch1
batch_day=B1D3
video_dir="/scratch/tmp/kwundram/bcth/data/whole_data/converted/first_x_min/$batch/$batch_day/"

# Iterate over each video file in the directory
for video in "$video_dir"*.mp4; do
    echo "Processing $video"
    # video name
    video_name=$(basename "$video")
    video_name_no_ext="${video_name%.*}"
    echo "... $video_name"
    output=/scratch/tmp/kwundram/bcth/data/whole_data/converted/extr_images/first_x_min/$batch/$batch_day/$video_name_no_ext/
    echo "output $output"
    # creates output path if it doesnt exist
    python $yolo_utils/create_path.py --path $output
    #
    ffmpeg -i "$video" "$output"/$video_name_no_ext%05d.png
done

# sbatch $HOME/bcth/Bachelor_Thesis/Bashfiles/video_utils/extract_images_firstxmin.sh
