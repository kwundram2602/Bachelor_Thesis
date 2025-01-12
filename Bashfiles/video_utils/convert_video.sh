#!/bin/bash

#SBATCH --nodes=1

#SBATCH --tasks-per-node=20

#SBATCH --partition=express

#SBATCH --mem=64GB

#SBATCH --time=0-00:30:00

#SBATCH --job-name=bcth_split_video

#SBATCH --mail-type=ALL

#SBATCH --output /scratch/tmp/%u/output/bc_th/convert_video/convert%j.log

#load modules 
#load modules
module purge
module load palma/2021a GCCcore/10.3.0 Miniconda3/4.9.2 FFmpeg/4.3.2


CONDA_BASE=$(conda info --base)
source $CONDA_BASE/etc/profile.d/conda.sh
conda deactivate
conda activate $HOME/envs/bc_th

convert_output=/scratch/tmp/kwundram/bcth/data/whole_data/converted/Batch1/B1D1/B1D1_C3_OE_c.mp4
video_path=/scratch/tmp/kwundram/bcth/data/whole_data/Batch1/B1D1/B1D1_C3_OE.mp4
script=/home/k/kwundram/bcth/Bachelor_Thesis/video_utils/video_split.py
python $script --video_path "$video_path" --convert_output "$convert_output"
# sbatch /home/k/kwundram/bcth/Bachelor_Thesis/Bashfiles/video_utils/convert_video.sh