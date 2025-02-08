#!/bin/bash


#SBATCH --nodes=1

#SBATCH --tasks-per-node=8

#SBATCH --partition=gpua100,gpu2080,gpuhgx,gpu3090
# try normal, express ,gpua100

#SBATCH --mem=240GB

#SBATCH --gres=gpu:1

#SBATCH --time=0-02:00:00

#SBATCH --job-name=bc_th_heatmap

#SBATCH --output=/scratch/tmp/kwundram/output/bc_th/detect_heatmap/detect_heatmap%j.log

#SBATCH --mail-type=ALL

#SBATCH --mail-user=kwundram@uni-muenster.de

#load modules
module purge
module load palma/2022a  Miniconda3/4.12.0 GCCcore/11.3.0 FFmpeg/4.4.2

CONDA_BASE=$(conda info --base)
source $CONDA_BASE/etc/profile.d/conda.sh
conda deactivate
conda activate $HOME/envs/bc_th

# code location
yolo_utils=/home/k/kwundram/bcth/Bachelor_Thesis/yolo_utils/
yh=$HOME/bcth/Bachelor_Thesis/

# video
batch=Batch1
batch_day=B1D3
video=B1D3_C1_ST

# place were extarcted frames are / or output for them 
frames_output_path=$WORK/bcth/data/whole_data/converted/extr_images/first_x_min/$batch/$batch_day/"$video"_c_10_min
#frames_output_path=/scratch/tmp/kwundram/bcth/data/whole_data/test_extr_images/B1D1_C2
#output for color map masks ( for single frames )
output_path=/scratch/tmp/kwundram/bcth/data/whole_data/heatmaps/$batch/$batch_day/$video
#output_path=$WORK/bcth/data/whole_data/test_extr_images/labels
mp4_output=/scratch/tmp/kwundram/bcth/data/whole_data/heatmaps/videos/$batch/$batch_day/"$video"_c_10_min_HM.mp4

# model weights
weights=$WORK/bcth/runs/train/20.01.2025/bc_th_train_ep180_img1024_t23:20:51/weights/best.pt

#  labels_folder=os.path.join(project,name,"labels")
# confidence for detection
confidence=0.5
project=/scratch/tmp/kwundram/bcth/runs/detect_heatmap
name="$video"_c_10_min_"$confidence"
#ymin xmin ymax xmax
#b1d1_c1 
#aois=("50 400 1200 950")
#b1d1_c2
#aois=("50 600 1200 950")
#b1d1_c3
aois=("50 480 1200 950")
# parse aois to string
aoi_args=()
for aoi in "${aois[@]}"; do
    aoi_args+=("--aoi $aoi")
done

aoi_args_string=$(IFS=" "; echo "${aoi_args[*]}")
echo $aoi_args_string
#name=B1D1_test
# sbatch /home/k/kwundram/bcth/Bachelor_Thesis/Bashfiles/yolo/heatmap_over_time.sh
python $yolo_utils/create_path.py --path $output_path
script=heatmap_over_time.py 
#--already_detected
#--already_extracted : done for all videos
python "$yh"/yolo_count/$script $aoi_args_string --mp4_output $mp4_output --already_extracted  --confidence $confidence --project $project --name $name --weights $weights --frames_output_path $frames_output_path  --output_path "$output_path"


