#!/bin/bash

#SBATCH --mail-user=fcw@duke.edu
#SBATCH --mail-type=BEGIN,END,FAIL
#SBATCH --output=./weighted_hamming_600.out
#SBATCH --error=./weighted_hamming_600.err
#SBATCH --mem=64G
#SBATCH --account=carlsonlab

source ~/.bashrc
conda activate uhi

python ./calc_ate.py --results_path ./weighted_hamming/results_600.csv \
    --neighborhood_min_dist 600 \
    --distance_metric weighted_hamming