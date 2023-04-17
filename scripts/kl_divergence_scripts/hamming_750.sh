#!/bin/bash

#SBATCH --mail-user=fcw@duke.edu
#SBATCH --mail-type=BEGIN,END,FAIL
#SBATCH --output=./kl_divergence_750.out
#SBATCH --error=./kl_divergence_750.err
#SBATCH --mem=64G
#SBATCH --account=carlsonlab

source ~/.bashrc
conda activate uhi

python ./calc_ate.py --results_path ./kl_divergence/results_750.csv \
    --neighborhood_min_dist 750 \
    --distance_metric kl_divergence