#!/bin/bash

#SBATCH --mail-user=fcw@duke.edu
#SBATCH --mail-type=BEGIN,END,FAIL
#SBATCH --output=./weighted_hamming_800.out
#SBATCH --error=./weighted_hamming_800.err
#SBATCH --mem=64G
#SBATCH --account=carlsonlab

source ~/.bashrc
conda activate uhi

python ./calc_ate.py --results_path ./weighted_hamming/results_800.csv \
    --neighborhood_min_dist 800 \
    --distance_metric weighted_hamming
