#!/bin/bash

# Démarrer Neuronas en mode basse consommation
python -O -X pycache_prefix=/tmp -m app --low-power-mode
