# 🧠 Neuronas v4.3 - AI Benchmarking Platform

## Collaborative, Reproducible AI Benchmarking Repository

Neuronas is a comprehensive AI benchmarking platform designed for collaborative research and reproducible experiments. Built on top of a revolutionary neuromorphic AI system, it provides tools and frameworks for benchmarking various AI/ML approaches across different domains.

This repository supports benchmarking for:
- **Quantum Computing** with Qiskit
- **Deep Learning** with PyTorch and TensorFlow  
- **Natural Language Processing** with Transformers
- **Traditional Machine Learning** with Scikit-learn
- **Neuromorphic Computing** with custom modules

![Neuronas Benchmarking Platform](https://raw.githubusercontent.com/doditz/Neuronas/main/docs/img/neuronas_architecture.png)

## 📁 Repository Structure

```
/notebooks/     # Jupyter/Colab notebooks for benchmarks and demos
/src/          # Core Python modules and neuromorphic system
/datasets/     # Downloaded open datasets and documentation
/validation/   # Scripts for code/data validation
/tests/        # Unit and integration tests  
/logs/         # Audit and execution logs
/docs/         # Documentation
/.github/      # CI/CD workflows and contribution guidelines
```

## 🔧 Core Architecture (Underlying Neuronas System)

The benchmarking platform is built on top of several innovative AI components:

### 🔍 D²STIB – Dynamic Derivative Semantic Token Information Bottleneck

Le cœur du système applique des **dérivées premières et secondes** sur les mots pour détecter les *frontières sémantiques* (changements importants dans le sens). Cela permet de **sauter** ou de **simplifier le traitement de nombreux mots**, réduisant la charge informatique de plus de 60%.

### 🧮 SED – Semantic Efficiency Director

Identifie les zones où le sens change rapidement, et décide où **allouer ou économiser du calcul**.

### 🧩 BRONAS & QRONAS – Réseaux de Décision Biologique & Quantique

- **BRONAS** applique des filtres inspirés du cerveau pour ne garder que ce qui est pertinent, en intégrant des principes éthiques fondamentaux.
- **QRONAS** émule un comportement quantique : plusieurs réponses sont évaluées *en parallèle*, puis une seule est "effondrée" (choisie) en fonction du contexte.

### 🔄 Système de Mémoire Hiérarchique

Notre système utilise une architecture de mémoire en niveaux (L1/L2/L3 pour l'hémisphère gauche et R1/R2/R3 pour l'hémisphère droit) inspirée des structures cérébrales humaines pour un traitement optimisé de l'information.

## 🚀 Caractéristiques Clés

- **Traitement Neuromorphique** - Utilise des réseaux spikants pour moduler dynamiquement la puissance de calcul
- **Superposition Décisionnelle** - Simule des états quantiques dans les réponses
- **Prise de Décision Éthique** - Le DoditzAI agit comme modérateur visionnaire et éthique
- **Équilibre Hemisphérique** - Équilibre dynamique entre les processus analytiques et créatifs

## 📊 Performances D²STIB Mesurées

| **Métrique**              | **Standard** | **Neuronas D²STIB**    | **Amélioration** |
|---------------------------|--------------|------------------------|------------------|
| Temps par token           | 26.8ms       | 10.5ms                 | ↓ 60.8%          |
| RAM par séquence          | 2.3 KB       | 1.1 KB                 | ↓ 52.2%          |
| Tokens totalement traités | 100%         | ~43% (restes prédits)  | ↓ 57.0%          |
| Fidélité sémantique       | Baseline     | 99.3%                  | ≈ 100%           |

## 🔐 Directives Asimov Neuromorphiques

NeuronasX intègre des directives Asimov avancées spécifiquement adaptées aux systèmes neuromorphiques et quantiques, incluant:

- Protocole de Sécurité Humaine Quantique
- Conformité à la Réalité Intriquée
- Équilibre Éthique Dopaminergique
- Principe de Conservation Cognitive
- Mandat de Transparence de la Fonction d'Onde
- Directive d'Efficacité du Goulot d'Étranglement

## 🧬 Principes Éthiques BRONAS

Nos principes éthiques sont intégrés dans le cœur du système:

- **Principes Globaux**: Équité, Respect culturel, Accessibilité
- **Lois Fondamentales**: Bien-être humain, Adaptabilité locale, Durabilité

## 🚀 Quick Start

### Local Setup
```bash
# Clone the repository
git clone https://github.com/doditz/Neuronas.git
cd Neuronas

# Install dependencies
pip install -r requirements.txt

# Validate environment
python validation/validate_environment.py

# Run example notebook
jupyter notebook notebooks/example.ipynb
```

### Google Colab Setup
1. Open [notebooks/example.ipynb](./notebooks/example.ipynb) in Google Colab
2. The notebook will automatically install dependencies
3. Follow the setup validation steps

### Usage for Benchmarking
```bash
# Run tests
pytest tests/ -v

# Validate data sources
python validation/validate_environment.py

# Start benchmarking (see notebooks/ for examples)
jupyter notebook notebooks/
```

## 🌐 Available Benchmarks

The platform provides benchmarking capabilities for:

- **`/notebooks/quantum_benchmarks/`** - Quantum computing with Qiskit
- **`/notebooks/nlp_benchmarks/`** - NLP tasks with Transformers
- **`/notebooks/cv_benchmarks/`** - Computer vision with PyTorch/TensorFlow
- **`/notebooks/ml_benchmarks/`** - Traditional ML with Scikit-learn
- **`/notebooks/neuromorphic_benchmarks/`** - Custom neuromorphic modules

## 🧪 Benchmarking Features

- **Reproducible Experiments** - Standardized evaluation protocols
- **Multi-Framework Support** - PyTorch, TensorFlow, Qiskit, Scikit-learn
- **Automated Validation** - Built-in environment and data validation
- **Collaborative Tools** - GitHub Actions CI/CD, standardized formats
- **Open Source Only** - No paid APIs or premium datasets required

## 📚 Documentation

Pour plus d'informations sur l'architecture et les concepts, visitez les pages:

- [Architecture D²STIB](https://github.com/doditz/Neuronas/wiki/D2STIB-Architecture)
- [Système BRONAS](https://github.com/doditz/Neuronas/wiki/BRONAS-Ethics)
- [Mémoire Hiérarchique](https://github.com/doditz/Neuronas/wiki/Hierarchical-Memory)

## 🔄 Contributing to Benchmarks

We welcome contributions! Please see:

- [Contributing Guidelines](CONTRIBUTORS.md) for general contribution info
- [GitHub Copilot Instructions](.github/copilot-instructions.md) for AI-assisted development
- [Dataset Guidelines](datasets/DATA_SOURCES.md) for adding new datasets

### Contribution Requirements:
- ✅ Use only open-source, free libraries
- ✅ Ensure Jupyter/Colab compatibility  
- ✅ Include type hints and docstrings
- ✅ Add validation tests for new modules
- ✅ Follow PEP 8 style guidelines
- ✅ Document all data sources and licenses

### Development Workflow:
1. Fork and clone the repository
2. Create a feature branch
3. Add your benchmark/improvement
4. Run validation: `python validation/validate_environment.py`
5. Run tests: `pytest tests/ -v`
6. Submit a pull request

## 📄 Licence

Ce projet est sous licence CC BY-NC 4.0 International.
Commercial use requires prior written consent and compensation.
Contact: sebastienbrulotte@gmail.com
Attribution: Sebastien Brulotte aka [ Doditz ]

## 🙏 Remerciements

- Recherches sur les limitations cognitives de Zheng & Meister
- Inspiration des réseaux SpiNNaker pour le traitement neuromorphique
- Bibliothèques Python open-source utilisées dans ce projet
- Tous les contributeurs directs et indirects (voir [CONTRIBUTORS.md](CONTRIBUTORS.md))
- Attributions détaillées des composants (voir [ATTRIBUTIONS.md](ATTRIBUTIONS.md))
