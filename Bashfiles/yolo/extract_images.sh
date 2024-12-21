#!/bin/bash

#SBATCH --nodes=1

#SBATCH --tasks-per-node=10

#SBATCH --partition=express

#SBATCH --mem=24GB

#SBATCH --time=0-02:00:00

#SBATCH --job-name=bcth_extract_images

#SBATCH --mail-type=ALL

#SBATCH --output /scratch/tmp/%u/output/bc_th/extract_images_%j.log

#load modules 
module purge
module load palma/2022a  GCCcore/11.3.0 FFmpeg/4.4.2


# mp4 folder
video_path=$WORK/bcth/data/whole_data/split_data/B1D1/B1D1_C1/B1D1_C1_ST_converted_chunk_0_1200.mp4
#output folder
output=$WORK/bcth/data/whole_data/split_data/B1D1/B1D1_C1/extracted_images/B1D1_C1_ST_converted_chunk_0_1200/

yolo_utils=/home/k/kwundram/bcth/Bachelor_Thesis/yolo_utils/
# creates output path if it doesnt exist
python $yolo_utils/create_path.py --path $output

# sbatch $HOME/bcth/Bachelor_Thesis/Bashfiles/yolo/extract_images.sh
ffmpeg -i "$video_path" "$output"/frame%05d.png
