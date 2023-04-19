#!/bin/bash

#SBATCH --mail-user=fcw@duke.edu
#SBATCH --mail-type=BEGIN,END,FAIL
#SBATCH --output=./jaccard_550.out
#SBATCH --error=./jaccard_550.err
#SBATCH --mem=64G
#SBATCH --account=carlsonlab

source ~/.bashrc
conda activate uhi

python ./calc_ate.py --results_path ./jaccard/results_550.csv \
    --neighborhood_min_dist 550 \
    --distance_metric jaccard