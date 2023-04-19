#!/bin/bash

#SBATCH --mail-user=zachary.calhoun@duke.edu
#SBATCH --mail-type=BEGIN,END,FAIL
#SBATCH --output=./jaccard.out
#SBATCH --error=./jaccard.err
#SBATCH --mem=64G
#SBATCH --account=carlsonlab

source ~/.bashrc
conda activate uhi

python ./calc_ate.py --results_path ./jaccard/results.csv