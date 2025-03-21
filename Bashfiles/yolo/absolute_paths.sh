#!/bin/bash

#SBATCH --nodes=1

#SBATCH --tasks-per-node=10

#SBATCH --partition=express

#SBATCH --mem=16GB

#SBATCH --time=0-00:30:00

#SBATCH --job-name=absolute_paths

#SBATCH --mail-type=ALL

#SBATCH --output /scratch/tmp/%u/output/bc_th/absolutepaths/apaths_%j.log

#load modules 
module purge
module load palma/2022a  GCCcore/11.3.0


# main folder must be one level higer than folder with frames and label files

main_folder_path=/scratch/tmp/kwundram/bcth/data/whole_data/converted/labels_rescaled
#main_folder_path=/scratch/tmp/kwundram/bcth/data/whole_data/studyproject/exported_labels/2024_11_22/video_frames_png_rescaled
#only test:
#python /home/k/kwundram/bcth/Bachelor_Thesis/yolo_utils/create_test_path_txt.py --main_folder_path "$main_folder_path"
# train, val, test:
python "$HOME"/bcth/Bachelor_Thesis/yolo_utils/create_absolutepath.py --main_folder_path "$main_folder_path"

# sbatch /home/k/kwundram/bcth/Bachelor_Thesis/Bashfiles/yolo/absolute_paths.sh
