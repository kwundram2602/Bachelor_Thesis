#!/bin/bash

#SBATCH --nodes=1

#SBATCH --tasks-per-node=20

#SBATCH --partition=express,normal,long,requeue

#SBATCH --mem=64GB

#SBATCH --time=0-00:30:00

#SBATCH --job-name=take_x_min

#SBATCH --mail-type=ALL

#SBATCH --output /scratch/tmp/%u/output/bc_th/video/take_x_min_%j.log

#load modules 
#load modules
module purge
module load palma/2021a GCCcore/10.3.0 Miniconda3/4.9.2 FFmpeg/4.3.2


CONDA_BASE=$(conda info --base)
source $CONDA_BASE/etc/profile.d/conda.sh
conda deactivate
conda activate $HOME/envs/bc_th

script=/home/k/kwundram/bcth/Bachelor_Thesis/video_utils/take_x_min.py
# input video
# B1D1, B1D3, B2D2, B2D3
batch=Batch1
batch_day=B1D3
video_name="$batch_day"_C3_OE_c.mp4
input=/scratch/tmp/kwundram/bcth/data/whole_data/converted/$batch/$batch_day/$video_name

# duration in minutes
duration=1
# starting point in min
start_point=35
# output video
video_name_no_ext="${video_name%.*}"
new_name=${video_name_no_ext}_$duration"_min_st$start_point.mp4"
output=/scratch/tmp/kwundram/bcth/data/whole_data/converted/first_x_min/$batch/$batch_day/$new_name

# sbatch /home/k/kwundram/bcth/Bachelor_Thesis/Bashfiles/video_utils/take_x_min.sh
python $script --input "$input" --output_path "$output" --duration $duration --start_point $start_point