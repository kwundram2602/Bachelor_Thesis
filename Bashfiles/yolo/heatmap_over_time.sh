#!/bin/bash


#SBATCH --nodes=1

#SBATCH --tasks-per-node=8

#SBATCH --partition=gpua100
# try normal, express ,gpua100

#SBATCH --mem=64GB

#SBATCH --time=0-01:00:00

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
video_path="/scratch/tmp/kwundram/bcth/data/whole_data/split_data/B1D1/B1D1_C1/B1D1_C1_ST_converted_chunk_0_1200.mp4"
# place were extarcted frames are / or output for them 
frames_output_path="$WORK/bcth/data/whole_data/split_data/B1D1/B1D1_C1/extracted_images/B1D1_C1_ST_converted_chunk_0_1200"
#output for color map masks ( for single frames )
output_path=/scratch/tmp/kwundram/bcth/data/whole_data/heatmaps/B1D1_C1_ST_converted_chunk_0_1200/
# confidence for detection
confidence=0.45
# model weights
weights=/scratch/tmp/kwundram/bcth/runs/train/15.12.2024/bc_th_train_ep150_img1024_t12:35:26/weights/best.pt

day=`date +%d.%m.%Y`
time=`date +%H:%M:%S`
#  labels_folder=os.path.join(project,name,"labels")
project=/scratch/tmp/kwundram/bcth/runs/detect_heatmap/$day/
name=HM_4_conf"$confidence"

# sbatch /home/k/kwundram/bcth/Bachelor_Thesis/Bashfiles/yolo/heatmap_over_time.sh
python $yolo_utils/create_path.py --path $output_path
script=heatmap_over_time.py 
#--already_detected
python "$yh"/yolo_count/$script  --already_extracted  --confidence $confidence --project $project --name $name --weights $weights --video_path $video_path  --frames_output_path $frames_output_path  --output_path "$output_path"


