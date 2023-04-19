#!/bin/bash

#SBATCH --mail-user=fcw@duke.edu
#SBATCH --mail-type=BEGIN,END,FAIL
#SBATCH --output=./jensenshannon_650.out
#SBATCH --error=./jensenshannon_650.err
#SBATCH --mem=64G
#SBATCH --account=carlsonlab

source ~/.bashrc
conda activate uhi

python ./calc_ate.py --results_path ./jensenshannon/results_650.csv \
    --neighborhood_min_dist 650 \
    --distance_metric jensenshannon