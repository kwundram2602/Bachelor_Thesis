#!/bin/bash

#SBATCH --nodes=1

#SBATCH --tasks-per-node=8


#SBATCH --partition=gpua100,gpu2080,gpuhgx,gpu3090
# try gpua100( max 240 GB),gpu2080( max 240 GB),gpuhgx,gpu3090,requeue-zen,gpuexpress
#SBATCH --mem=60GB

#SBATCH --gres=gpu:1

#SBATCH --time=0-01:00:00

#SBATCH --job-name=bc_th_detect_aoi

#SBATCH --output=/scratch/tmp/kwundram/output/bc_th/detect_aoi/detect_%j.log

#SBATCH --mail-type=ALL

#SBATCH --mail-user=kwundram@uni-muenster.de

#load modules
module purge
module load palma/2021a Miniconda3/4.9.2

CONDA_BASE=$(conda info --base)
source $CONDA_BASE/etc/profile.d/conda.sh
conda deactivate
conda activate $HOME/envs/bc_th

yh=$HOME/bcth/Bachelor_Thesis/yolov7/
# video batch and folder with extracted images as source for detection

batch=Batch2
batch_day=B2D3 # B1D1, B1D3, B2D2, B2D3
camera=C3
suffix=OE  # BE (C2) or OE (C3)
videoname="$batch_day"_"$camera"_"$suffix"_c
#videoname=test_"$batch_day"_"$camera"
source=/scratch/tmp/kwundram/bcth/data/whole_data/converted/extr_images/first_x_min/$batch/$batch_day/"$batch_day"_"$camera"_"$suffix"_c_10_min
#source=/scratch/tmp/kwundram/bcth/data/whole_data/test_extr_images/
# pre trained weights (own or yolo weights)
weights=/scratch/tmp/kwundram/bcth/runs/train/20.01.2025/bc_th_train_ep180_img1024_t23:20:51/weights/best.pt

day=`date +%d.%m.%Y`
time=`date +%H:%M:%S`
# parent folder for detection tests on trained models ( not only pretrained yolov7)
project=/scratch/tmp/kwundram/bcth/runs/detect_aoi/$batch_day/$day/
# parent folder for detection (only when using yolo weights)
#project=/scratch/tmp/kwundram/bcth/runs/detect
conf=0.4

# x_min, y_min, x_max, y_max  :Y is width and X is height
# B1D1
if [ "$batch_day" == "B1D1" ]; then
    if [ "$camera" == "C2" ]; then
        aois=("365 720 465 920" "840 720 940 920") # works
    elif [ "$camera" == "C3" ]; then
        aois=("155 670 255 870" "670 670 770 870") # works
    else
        aois=("0 0 1280 1024")
    fi
# B1D3
elif [ "$batch_day" == "B1D3" ]; then
    if [ "$camera" == "C2" ]; then
        aois=("360 650 460 900" "855 650 955 900") # works
    elif [ "$camera" == "C3" ]; then
        aois=("150 570 250 785" "690 570 790 785") # works
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

aoi_args_string=$(IFS=" "; echo "${aoi_args[*]}")
name="${videoname}_conf${conf}_$time"

# sbatch $HOME/bcth/Bachelor_Thesis/Bashfiles/yolo/detect_aoi.sh
image_size=1024
#python "$yh"detect_aoi.py --weights "$weights" $aoi_args_string --conf $conf --img-size $image_size --source "$source" --save-txt --project "$project" --name "$name"

#label_folder=$project/$name/labels
label_folder=/scratch/tmp/kwundram/bcth/runs/detect_aoi/B2D3/23.01.2025/B2D3_C3_OE_c_conf0.4_11:00:42/labels
count=/home/k/kwundram/bcth/Bachelor_Thesis/yolo_count/count_objs_over_time.py

output_path=/scratch/tmp/kwundram/bcth/data/whole_data/count_objs/aoi/$day/$name/"$videoname"_aoi.png
python $count --folder_path $label_folder  --output_path $output_path --dw 1280 --dh $image_size --plot_type aoi $aoi_args_string

conda deactivate
module purge