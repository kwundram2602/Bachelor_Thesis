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
camera=C3

videoname="$batch_day"_"$camera"_OE #  C1_ST, C2_BE, C3_OE

# detected labels
#folder_path=/scratch/tmp/kwundram/bcth/runs/detect_heatmap/"$videoname"_c_10_min_0.5/interpolated_labels
#folder_path=/scratch/tmp/kwundram/bcth/data/whole_data/converted/extr_images/for_over_time_gt/interpolated_labels
folder_path=/scratch/tmp/kwundram/bcth/data/whole_data/converted/extr_images/for_over_time_gt/detected_labels2/labels
# output folder for plot
output_folder=/scratch/tmp/kwundram/bcth/data/whole_data/converted/extr_images/for_over_time_gt
#output_folder=/scratch/tmp/kwundram/bcth/data/whole_data/count_objs/over_time/$videoname
# ground truth labels
ground_truth=/scratch/tmp/kwundram/bcth/data/whole_data/converted/extr_images/for_over_time_gt/real_labels

# 120 frames =5 sec
# 180 frames =7.5 sec
# 240 frames =10 sec
# if object count is smaller than 5 for x sec ...
highlight_frames=48
plot_type=count   # count or percentage
output_path=$output_folder/plot_"$plot_type"_segment_"$highlight_frames".png

if [ "$batch_day" == "B1D1" ]; then
    if [ "$camera" == "C2" ]; then
        gt_pipe_events=("0:10" "0:13" "0:16" "0:22" "0:50" "0:50" "1:05" "1:15" "1:18" "1:19" "1:22" "1:26" "1:49" "1:50" "2:07" "2:16" "2:19" "2:36" "2:47" "2:48" "2:53" "2:55" "2:56" "2:59" "3:01" "3:21" "3:30" "3:34" "3:38" "3:40" "3:41" "3:46" "3:50" "3:50" "3:59" "4:00" "4:07" "4:08" "4:10" "4:14" "4:15" "4:21" "4:26" "4:35" "4:36" "4:42" "4:44" "4:45" "4:48" "4:52" "4:53" "5:02" "5:04" "5:08" "5:16" "5:20" "5:24" "5:30" "5:32" "5:40" "5:45" "5:51" "5:54" "6:09" "6:22" "6:28" "6:35" "6:39" "6:40" "6:44" "6:48" "6:59" "7:19" "7:30" "7:34" "7:45" "7:48" "7:51" "8:18" "8:23" "8:25" "8:35" "8:39" "8:52" "8:53" "9:06" "9:15" "9:18" "9:23" "9:28" "9:53")

    elif [ "$camera" == "C3" ]; then
        
        gt_pipe_events=("0:05" "2:05" "2:33" "2:47" "3:48" "3:56" "6:23" "6:29" "6:32" "6:33" "9:17" "9:42" "9:45" "9:46" "9:51" "9:57")
    fi

elif [ "$batch_day" == "B1D3" ]; then
    if [ "$camera" == "C2" ]; then
        echo "no gt yet"
    elif [ "$camera" == "C3" ]; then
        gt_pipe_events=(2:29 2:41 4:12 4:42 4:51 5:12 5:24 5:45 6:50 7:47 8:01 8:10 8:17 8:26 8:49 9:31 9:42)
   
    fi
fi
for pipe in "${gt_pipe_events[@]}"; do
    pipe_args+=("--gt_pipe_events $pipe")
done
gt_pipe_events_string=$(IFS=" "; echo "${pipe_args[*]}")
# sbatch /home/k/kwundram/bcth/Bachelor_Thesis/Bashfiles/yolo/count_objs_over_time.sh
python /home/k/kwundram/bcth/Bachelor_Thesis/video_utils/create_path.py --path $output_folder

python $script --folder_path "$folder_path" --ground_truth $ground_truth  --highlight_frames $highlight_frames --output_path "$output_path" --plot_type "$plot_type"