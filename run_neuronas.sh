#!/bin/bash

# Activate conda environment
source $HOME/miniconda3/bin/activate neuronas_env

# Run the application with optimized settings
python -O -X pycache_prefix=/tmp app.py --low-power-mode
