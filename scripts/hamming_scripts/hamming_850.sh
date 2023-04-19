#!/bin/bash

#SBATCH --mail-user=fcw@duke.edu
#SBATCH --mail-type=BEGIN,END,FAIL
#SBATCH --output=./hamming_850.out
#SBATCH --error=./hamming_850.err
#SBATCH --mem=64G
#SBATCH --account=carlsonlab

source ~/.bashrc
conda activate uhi

python ./calc_ate.py --results_path ./hamming/results_850.csv \
    --neighborhood_min_dist 850 \
    --distance_metric hamming