#!/bin/bash

#SBATCH --nodes=1

#SBATCH --tasks-per-node=8

#SBATCH --partition=express
# try normal, express,long

#SBATCH --mem=92GB

#SBATCH --time=0-0:30:00

#SBATCH --job-name=bc_th_count_objs_over_time

#SBATCH --output=/scratch/tmp/kwundram/output/bc_th/count_objs_over_time/count_%j.log

#SBATCH --mail-type=ALL

#SBATCH --mail-user=kwundram@uni-muenster.de

#load modules
module purge
module load palma/2021a Miniconda3/4.9.2

CONDA_BASE=$(conda info --base)
source $CONDA_BASE/etc/profile.d/conda.sh
conda deactivate
conda activate $HOME/envs/bc_th

script=/home/k/kwundram/bcth/Bachelor_Thesis/yolo_count/count_objs_over_time.py

# just change videoname and maybe conf
videoname=B1D1_C1_ST


folder_path=/scratch/tmp/kwundram/bcth/runs/detect_count_over_time/"$videoname"_c_10_min_0.4/labels
output_folder=/scratch/tmp/kwundram/bcth/data/whole_data/count_objs/$videoname
# 120 frames =5 sec
# 180 frames =7.5 sec
# 240 frames =10 sec
highlight_frames=180
plot_type=count   # count or percentage
output_path=$output_folder/plot_"$plot_type"_segment_"$highlight_frames".png
# sbatch /home/k/kwundram/bcth/Bachelor_Thesis/Bashfiles/yolo/count_objs_over_time.sh
python /home/k/kwundram/bcth/Bachelor_Thesis/video_utils/create_path.py --path $output_folder

python $script --folder_path "$folder_path" --output_path "$output_path" --plot_type "$plot_type"