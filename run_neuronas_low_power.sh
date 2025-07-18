#!/bin/bash

# Neuronas Low-Power Runtime Script
# Author: GitHub Copilot
# Date: June 24, 2025
# Description: Optimized runtime script for Neuronas system on low-power HP laptops

# Color codes for better readability
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}====================================================================${NC}"
echo -e "${BLUE}        NEURONAS LOW-POWER MODE - OPTIMIZED FOR HP LAPTOP          ${NC}"
echo -e "${BLUE}====================================================================${NC}"

# Activate conda environment
source $HOME/miniconda3/bin/activate neuronas_env

# Set environment variables for performance optimization
export PYTHONOPTIMIZE=1               # Disable debug features
export PYTHONUNBUFFERED=1             # Disable output buffering
export NUMBA_CACHE_DIR=/tmp/numba     # Set Numba cache to /tmp (if used)
export OMP_NUM_THREADS=2              # Limit OpenMP threads
export MKL_NUM_THREADS=2              # Limit MKL threads (if NumPy uses MKL)
export OPENBLAS_NUM_THREADS=2         # Limit OpenBLAS threads
export VECLIB_MAXIMUM_THREADS=2       # Limit VecLib threads
export NUMEXPR_NUM_THREADS=2          # Limit numexpr threads

# System optimization
echo -e "${YELLOW}Applying system optimizations for low-power mode...${NC}"
# Reduce swappiness temporarily if user has sudo access
if command -v sudo &> /dev/null; then
    echo -e "${YELLOW}Would you like to apply system optimizations? (requires sudo) (y/n)${NC}"
    read -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        sudo sysctl -w vm.swappiness=10
        # Clean memory cache
        sudo sync && sudo echo 3 > /proc/sys/vm/drop_caches
        echo -e "${GREEN}System optimizations applied.${NC}"
    fi
fi

# Start Neuronas with optimized Python flags
echo -e "${YELLOW}Starting Neuronas in low-power mode...${NC}"
echo -e "${BLUE}====================================================================${NC}"

# Run with optimized flags
python -O -X pycache_prefix=/tmp app.py --low-power-mode

# Reset system settings when done
if command -v sudo &> /dev/null && [[ $REPLY =~ ^[Yy]$ ]]; then
    sudo sysctl -w vm.swappiness=60
fi
