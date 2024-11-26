#!/bin/bash

#SBATCH --nodes=1

#SBATCH --tasks-per-node=10

#SBATCH --partition=express
# try normal , express

#SBATCH --mem=24GB

#SBATCH --time=0-02:00:00

#SBATCH --job-name=MAL_extract_images

#SBATCH --mail-type=ALL

#SBATCH --output /scratch/tmp/%u/output/bc_th/MAL_extract/extract_images_%j.log

#load modules 
module purge
module load palma/2022a  GCCcore/11.3.0 FFmpeg/4.4.2

output="$WORK"/bcth/data/whole_data/extracted_images/
yolo_utils=/home/k/kwundram/bcth/Bachelor_Thesis/yolo_utils/

data="$WORK"/bcth/data/whole_data/split_data/B1D1/B1D1_C1/
for FILE in "$data"*; do

filename="$(basename "$FILE" .${FILE##*.})"
video_path="$data/$filename.mp4"
output_dir="$output/$filename/"
# creates output path if it doesnt exist
python $yolo_utils/create_path.py --path $output_dir
ffmpeg -i "$video_path" "$output_dir"/ex_frame_%05d.png
done

# sbatch /home/k/kwundram/bcth/Bachelor_Thesis/Bashfiles/extract_images_for_MAL.sh

