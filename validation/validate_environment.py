#!/usr/bin/env python3
"""
Environment validation script for Neuronas AI benchmarking repository.
Validates dependencies, resources, and dataset integrity.
"""

import sys
import platform
import importlib
import subprocess
from typing import List, Dict, Tuple, Optional
import os
import warnings

# Suppress warnings for cleaner output
warnings.filterwarnings("ignore")


def check_python_version() -> bool:
    """Check if Python version meets requirements."""
    version = sys.version_info
    min_version = (3, 9)
    
    print(f"Python version: {version.major}.{version.minor}.{version.micro}")
    
    if version[:2] >= min_version:
        print("✓ Python version is compatible")
        return True
    else:
        print(f"✗ Python version {version.major}.{version.minor} is below minimum {min_version[0]}.{min_version[1]}")
        return False


def check_dependencies() -> Dict[str, bool]:
    """Check if required dependencies are installed and importable."""
    required_packages = {
        'numpy': 'numpy',
        'pandas': 'pandas',
        'sklearn': 'scikit-learn',
        'matplotlib': 'matplotlib',
        'torch': 'torch',
        'tensorflow': 'tensorflow',
        'transformers': 'transformers',
        'datasets': 'datasets',
        'qiskit': 'qiskit',
        'pytest': 'pytest',
        'jupyter': 'jupyter'
    }
    
    results = {}
    print("\nChecking dependencies:")
    
    for import_name, package_name in required_packages.items():
        try:
            module = importlib.import_module(import_name)
            version = getattr(module, '__version__', 'unknown')
            print(f"✓ {package_name}: {version}")
            results[package_name] = True
        except ImportError:
            print(f"✗ {package_name}: Not installed")
            results[package_name] = False
    
    return results


def check_gpu_availability() -> Dict[str, bool]:
    """Check GPU availability for CUDA and other frameworks."""
    gpu_info = {}
    
    print("\nChecking GPU availability:")
    
    # Check CUDA availability
    try:
        import torch
        cuda_available = torch.cuda.is_available()
        gpu_info['CUDA'] = cuda_available
        if cuda_available:
            gpu_count = torch.cuda.device_count()
            gpu_name = torch.cuda.get_device_name(0)
            print(f"✓ CUDA available: {gpu_count} GPU(s) - {gpu_name}")
        else:
            print("○ CUDA not available (CPU-only mode)")
    except ImportError:
        gpu_info['CUDA'] = False
        print("✗ PyTorch not available for CUDA check")
    
    # Check TensorFlow GPU
    try:
        import tensorflow as tf
        tf_gpu = len(tf.config.list_physical_devices('GPU')) > 0
        gpu_info['TensorFlow-GPU'] = tf_gpu
        if tf_gpu:
            print("✓ TensorFlow GPU support available")
        else:
            print("○ TensorFlow GPU not available (CPU-only mode)")
    except ImportError:
        gpu_info['TensorFlow-GPU'] = False
        print("✗ TensorFlow not available for GPU check")
    
    return gpu_info


def check_memory_resources() -> Dict[str, float]:
    """Check system memory resources."""
    import psutil
    
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    
    memory_gb = memory.total / (1024**3)
    available_memory_gb = memory.available / (1024**3)
    disk_gb = disk.total / (1024**3)
    available_disk_gb = disk.free / (1024**3)
    
    print(f"\nSystem Resources:")
    print(f"Total Memory: {memory_gb:.1f} GB")
    print(f"Available Memory: {available_memory_gb:.1f} GB")
    print(f"Total Disk: {disk_gb:.1f} GB")
    print(f"Available Disk: {available_disk_gb:.1f} GB")
    
    return {
        'total_memory_gb': memory_gb,
        'available_memory_gb': available_memory_gb,
        'total_disk_gb': disk_gb,
        'available_disk_gb': available_disk_gb
    }


def check_jupyter_compatibility() -> bool:
    """Check if Jupyter/Colab compatibility requirements are met."""
    print("\nChecking Jupyter/Colab compatibility:")
    
    try:
        import jupyter
        print("✓ Jupyter installed")
        jupyter_available = True
    except ImportError:
        print("✗ Jupyter not installed")
        jupyter_available = False
    
    # Check for Google Colab detection capability
    try:
        # This is how you typically detect Colab environment
        import sys
        in_colab = 'google.colab' in sys.modules
        print(f"○ Colab detection: {'Running in Colab' if in_colab else 'Not in Colab'}")
    except Exception as e:
        print(f"○ Colab detection: Error - {e}")
    
    return jupyter_available


def validate_dataset_directory() -> bool:
    """Validate dataset directory structure."""
    print("\nValidating dataset directory:")
    
    datasets_dir = os.path.join(os.path.dirname(__file__), '..', 'datasets')
    
    if os.path.exists(datasets_dir):
        print("✓ Datasets directory exists")
        
        # Check for DATA_SOURCES.md
        data_sources_file = os.path.join(datasets_dir, 'DATA_SOURCES.md')
        if os.path.exists(data_sources_file):
            print("✓ DATA_SOURCES.md found")
            return True
        else:
            print("✗ DATA_SOURCES.md not found")
            return False
    else:
        print("✗ Datasets directory not found")
        return False


def run_validation() -> Dict[str, bool]:
    """Run complete environment validation."""
    print("=" * 60)
    print("Neuronas Environment Validation")
    print("=" * 60)
    
    validation_results = {}
    
    # Check Python version
    validation_results['python_version'] = check_python_version()
    
    # Check dependencies
    dep_results = check_dependencies()
    validation_results['dependencies'] = all(dep_results.values())
    
    # Check GPU availability (optional)
    gpu_results = check_gpu_availability()
    validation_results['gpu_available'] = any(gpu_results.values())
    
    # Check system resources
    try:
        import psutil
        memory_results = check_memory_resources()
        validation_results['sufficient_memory'] = memory_results['available_memory_gb'] >= 2.0
    except ImportError:
        print("\n○ psutil not available for memory check")
        validation_results['sufficient_memory'] = True  # Assume sufficient
    
    # Check Jupyter compatibility
    validation_results['jupyter_compatible'] = check_jupyter_compatibility()
    
    # Validate dataset structure
    validation_results['dataset_structure'] = validate_dataset_directory()
    
    # Summary
    print("\n" + "=" * 60)
    print("VALIDATION SUMMARY")
    print("=" * 60)
    
    total_checks = len(validation_results)
    passed_checks = sum(validation_results.values())
    
    for check, result in validation_results.items():
        status = "✓" if result else "✗"
        print(f"{status} {check.replace('_', ' ').title()}")
    
    print(f"\nOverall: {passed_checks}/{total_checks} checks passed")
    
    if passed_checks == total_checks:
        print("🎉 Environment validation successful!")
        return True
    else:
        print("⚠️  Some validation checks failed. See details above.")
        return False


if __name__ == "__main__":
    success = run_validation()
    sys.exit(0 if success else 1)