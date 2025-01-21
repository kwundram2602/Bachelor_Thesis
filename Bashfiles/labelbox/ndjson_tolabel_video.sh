#!/bin/bash

#SBATCH --nodes=1

#SBATCH --tasks-per-node=30

#SBATCH --partition=express
# normal ,long, express,gpua100
#SBATCH --mem=48GB

#SBATCH --time=0-02:00:00

#SBATCH --job-name=ndjson_label

#SBATCH --mail-type=ALL

#SBATCH --output /scratch/tmp/%u/output/bc_th/labelbox/ndjson_label/%j.log

module purge
module load palma/2021a Miniconda3/4.9.2

CONDA_BASE=$(conda info --base)
source $CONDA_BASE/etc/profile.d/conda.sh
conda deactivate
conda activate $HOME/envs/bc_th

script=/home/k/kwundram/bcth/Bachelor_Thesis/labelbox_utils/ndjson_to_label.py

# change ndjson and output
ndjson=/scratch/tmp/kwundram/bcth/data/whole_data/studyproject/exported_labels/2024_11_22/study_pr_export.ndjson
# has subfolders for each video( contains frames)
video_batches=/scratch/tmp/kwundram/bcth/data/whole_data/studyproject/exported_labels/2024_11_22/video_frames_png
# video batches: /scratch/tmp/kwundram/bcth/data/whole_data/studyproject/exported_labels/2024_11_22/video_frames_png

python $script --ndjson $ndjson --output_folder $video_batches --video

# sbatch /home/k/kwundram/bcth/Bachelor_Thesis/Bashfiles/labelbox/ndjson_tolabel_video.sh