#!/bin/bash

#SBATCH --nodes=1

#SBATCH --tasks-per-node=10

#SBATCH --partition=normal

#SBATCH --mem=24GB

#SBATCH --time=0-02:00:00

#SBATCH --job-name=lbx_label_upload

#SBATCH --mail-type=ALL

#SBATCH --output /scratch/tmp/%u/output/bc_th/labelbox/upload%j.log

#load modules 


#