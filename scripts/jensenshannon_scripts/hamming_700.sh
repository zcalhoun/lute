#!/bin/bash

#SBATCH --mail-user=fcw@duke.edu
#SBATCH --mail-type=BEGIN,END,FAIL
#SBATCH --output=./jensenshannon_700.out
#SBATCH --error=./jensenshannon_700.err
#SBATCH --mem=64G
#SBATCH --account=carlsonlab

source ~/.bashrc
conda activate uhi

python ./calc_ate.py --results_path ./jensenshannon/results_700.csv \
    --neighborhood_min_dist 700 \
    --distance_metric jensenshannon