#!/bin/bash

# Créer l'environnement Conda avec Python 3.10
conda create -n neuronas_env python=3.10 -y

# Activer l'environnement
conda activate neuronas_env

# Installer les dépendances principales (versions compatibles 3.10)
conda install -c conda-forge numpy=1.23 scipy=1.9 pyyaml sqlalchemy=1.4 -y

# Installer les dépendances légères
pip install fastapi==0.85.0 uvicorn[standard]==0.18.0 psycopg2-binary==2.9.3

# Installer autres dépendances (basé sur les imports observés dans le projet)
pip install jinja2 python-multipart requests

# Installer les outils de développement avec des versions légères
pip install autopep8==1.6.0 pylint==2.14.0

echo "Installation complète. Pour activer l'environnement, utilisez:"
echo "conda activate neuronas_env"
echo ""
echo "Pour démarrer VSCode en mode performance optimisée:"
echo "code . --disable-extensions except ms-python.python,ms-python.vscode-pylance"
