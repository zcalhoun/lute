#!/bin/bash

#SBATCH --mail-user=fcw@duke.edu
#SBATCH --mail-type=BEGIN,END,FAIL
#SBATCH --output=./jensenshannon_800.out
#SBATCH --error=./jensenshannon_800.err
#SBATCH --mem=64G
#SBATCH --account=carlsonlab

source ~/.bashrc
conda activate uhi

python ./calc_ate.py --results_path ./jensenshannon/results_800.csv \
    --neighborhood_min_dist 800 \
    --distance_metric jensenshannon
