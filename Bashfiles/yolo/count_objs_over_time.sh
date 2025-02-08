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
batch_day=B1D1

videoname="$batch_day"_C1_ST #  C1_ST, C2_BE, C3_OE

# detected labels
#folder_path=/scratch/tmp/kwundram/bcth/runs/detect_count_over_time/"$videoname"_c_10_min_0.4/labels
folder_path=/scratch/tmp/kwundram/bcth/data/whole_data/converted/overtime_labeled/detected_labels/labels
# output folder for plot
output_folder=/scratch/tmp/kwundram/bcth/data/whole_data/converted/overtime_labeled
#output_folder=/scratch/tmp/kwundram/bcth/data/whole_data/count_objs/over_time/$videoname
# ground truth labels
ground_truth=/scratch/tmp/kwundram/bcth/data/whole_data/converted/overtime_labeled/real_labels

# 120 frames =5 sec
# 180 frames =7.5 sec
# 240 frames =10 sec
# if object count is smaller than 5 for x sec ...
highlight_frames=180
plot_type=count   # count or percentage
output_path=$output_folder/plot_"$plot_type"_segment_"$highlight_frames".png
# sbatch /home/k/kwundram/bcth/Bachelor_Thesis/Bashfiles/yolo/count_objs_over_time.sh
python /home/k/kwundram/bcth/Bachelor_Thesis/video_utils/create_path.py --path $output_folder

python $script --ground_truth $ground_truth --folder_path "$folder_path" --highlight_frames $highlight_frames --output_path "$output_path" --plot_type "$plot_type"