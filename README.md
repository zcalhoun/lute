# lute
Land Use Temperature Effect


# To trigger matching script
Request a CPU in interactive mode (no GPU needed). Make sure you request a high amount of memory.
```bash
srun --mem=64G --pty bash -i
```

Then activate your conda environment
```bash
conda activate uhi
```

Then run the script in interactive mode.
```bash
python calc_ate.py
```

Alternatively, you could create as an sbatch script, but that isn't necessary at the moment.
