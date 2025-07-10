# Dataset Sources

This document outlines the data sources used in the Neuronas AI benchmarking repository.

## Open Source Datasets

### Natural Language Processing
- **Hugging Face Datasets**: https://huggingface.co/datasets
  - License: Various open source licenses (Apache 2.0, MIT, CC BY-SA, etc.)
  - Description: Large collection of NLP datasets for various tasks
  - Usage: Text classification, question answering, language modeling

### Computer Vision
- **CIFAR-10/CIFAR-100**: https://www.cs.toronto.edu/~kriz/cifar.html
  - License: Public domain
  - Description: Image classification datasets
  - Usage: Computer vision benchmarking

- **ImageNet subset**: https://www.image-net.org/
  - License: Various (research/educational use)
  - Description: Large-scale image database
  - Usage: Image classification and object detection

### Scientific Computing
- **UCI Machine Learning Repository**: https://archive.ics.uci.edu/ml/
  - License: Various open source licenses
  - Description: Collection of databases for machine learning research
  - Usage: General ML benchmarking

### Quantum Computing
- **Qiskit Datasets**: https://qiskit.org/ecosystem/
  - License: Apache 2.0
  - Description: Quantum computing datasets and examples
  - Usage: Quantum algorithm benchmarking

## Download Instructions

1. Use the provided scripts in `/validation/` to download datasets
2. All datasets will be cached in the `/datasets/` directory
3. Verify dataset integrity using the validation scripts
4. Check licensing requirements before use

## Licensing Guidelines

- All datasets used must be freely available for research and educational purposes
- Commercial datasets requiring payment are not permitted
- Always verify and respect dataset licensing terms
- Provide proper attribution when required

## Adding New Datasets

When adding new datasets:
1. Verify the dataset has an open source or research-friendly license
2. Document the source, license, and usage in this file
3. Create validation scripts to ensure data integrity
4. Update the environment validation to include the new dataset

## Contact

For questions about dataset usage or licensing, contact the repository maintainers.