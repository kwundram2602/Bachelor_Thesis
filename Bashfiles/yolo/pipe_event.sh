#!/bin/bash

#SBATCH --nodes=1

#SBATCH --tasks-per-node=8

#SBATCH --partition=express,normal,long
# try normal, express,long

#SBATCH --mem=92GB

#SBATCH --time=0-0:30:00

#SBATCH --job-name=pipe_event

#SBATCH --output=/scratch/tmp/kwundram/output/bc_th/pipe_event/pipe_event_%j.log

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
camera=C3  # C1_ST, C2_BE, C3_OE
videoname="$batch_day"_"$camera"_OE #  
# detected labels
conf=0.5
#folder_path=/scratch/tmp/kwundram/bcth/runs/detect_heatmap/"$videoname"_c_10_min_"$conf"/labels
folder_path=/scratch/tmp/kwundram/bcth/runs/detect_heatmap/"$videoname"_c_10_min_"$conf"/interpolated_labels
# output folder for plot
output_folder=/scratch/tmp/kwundram/bcth/data/whole_data/count_objs/pipe_event/$videoname

# B1D1
if [ "$batch_day" == "B1D1" ]; then
    if [ "$camera" == "C2" ]; then
        aois=("365 720 465 920" "840 720 940 920") # works
        gt_pipe_events=("0:10" "0:13" "0:16" "0:22" "0:50" "0:50" "1:05" "1:15" "1:18" "1:19" "1:22" "1:26" "1:49" "1:50" "2:07" "2:16" "2:19" "2:36" "2:47" "2:48" "2:53" "2:55" "2:56" "2:59" "3:01" "3:21" "3:30" "3:34" "3:38" "3:40" "3:41" "3:46" "3:50" "3:50" "3:59" "4:00" "4:07" "4:08" "4:10" "4:14" "4:15" "4:21" "4:26" "4:35" "4:36" "4:42" "4:44" "4:45" "4:48" "4:52" "4:53" "5:02" "5:04" "5:08" "5:16" "5:20" "5:24" "5:30" "5:32" "5:40" "5:45" "5:51" "5:54" "6:09" "6:22" "6:28" "6:35" "6:39" "6:40" "6:44" "6:48" "6:59" "7:19" "7:30" "7:34" "7:45" "7:48" "7:51" "8:18" "8:23" "8:25" "8:35" "8:39" "8:52" "8:53" "9:06" "9:15" "9:18" "9:23" "9:28" "9:53")

    elif [ "$camera" == "C3" ]; then
        aois=("155 670 255 870" "670 670 770 870") # works
        gt_pipe_events=("0:05" "2:05" "2:33" "2:47" "3:48" "3:56" "6:23" "6:29" "6:32" "6:33" "9:17" "9:42" "9:45" "9:46" "9:51" "9:57")
    else
        aois=("0 0 1280 1024")
    fi
# B1D3
elif [ "$batch_day" == "B1D3" ]; then
    if [ "$camera" == "C2" ]; then
        aois=("360 650 460 900" "855 650 955 900") # works
    elif [ "$camera" == "C3" ]; then
        aois=("150 570 250 785" "690 570 790 785") # works
        gt_pipe_events=(2:29 2:41 4:12 4:42 4:51 5:12 5:24 5:45 6:50 7:47 8:01 8:10 8:17 8:26 8:49 9:31 9:42)
    else
        aois=("0 0 1280 1024")
    fi
elif [ "$batch_day" == "B2D2" ]; then
    if [ "$camera" == "C2" ]; then
        aois=("350 650 450 900" "855 650 955 900") # works
    elif [ "$camera" == "C3" ]; then    
        aois=("200 600 300 810" "760 600 860 810") # works
    else
        aois=("0 0 1280 1024")
    fi
elif [ "$batch_day" == "B2D3" ]; then
    if [ "$camera" == "C2" ]; then
        aois=("330 620 430 860" "830 620 930 860") # works
    elif [ "$camera" == "C3" ]; then
        aois=("200 590 300 830" "765 590 865 830") # works
    else
        aois=("0 0 1280 1024")
    fi
else
    aois=("0 0 1280 1024")
fi
# parse aois to string
aoi_args=()
for aoi in "${aois[@]}"; do
    aoi_args+=("--aoi $aoi")
done
pipe_args=()
for pipe in "${gt_pipe_events[@]}"; do
    pipe_args+=("--gt_pipe_events $pipe")
done

aoi_args_string=$(IFS=" "; echo "${aoi_args[*]}")
gt_pipe_events_string=$(IFS=" "; echo "${pipe_args[*]}")
echo $gt_pipe_events_string
plot_type=aoi_cb   # count or percentage
output_path=$output_folder/"$videoname"_pipe_event.png
# sbatch /home/k/kwundram/bcth/Bachelor_Thesis/Bashfiles/yolo/pipe_event.sh
python /home/k/kwundram/bcth/Bachelor_Thesis/video_utils/create_path.py --path $output_folder

python $script --folder_path "$folder_path" $gt_pipe_events_string --dw 1280 --dh 1024 --output_path "$output_path" --plot_type "$plot_type"  $aoi_args_string