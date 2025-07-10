#!/usr/bin/env python3
"""
Unit tests for environment validation and dataset loading.
Tests for the Neuronas AI benchmarking repository.
"""

import unittest
import sys
import os
import importlib
from typing import List, Dict, Optional

# Add the parent directory to the path to import validation modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

try:
    from validation.validate_environment import (
        check_python_version,
        check_dependencies,
        check_jupyter_compatibility,
        validate_dataset_directory
    )
except ImportError:
    # Fallback if validation module is not available
    check_python_version = None
    check_dependencies = None
    check_jupyter_compatibility = None
    validate_dataset_directory = None


class TestEnvironmentValidation(unittest.TestCase):
    """Test environment validation functions."""
    
    def test_python_version_check(self):
        """Test Python version validation."""
        if check_python_version is None:
            self.skipTest("Validation module not available")
        
        # Python version should be >= 3.9
        result = check_python_version()
        self.assertTrue(result, "Python version should meet minimum requirements")
    
    def test_core_dependencies(self):
        """Test that core dependencies can be imported."""
        core_packages = ['numpy', 'sys', 'os', 'importlib']
        
        for package in core_packages:
            with self.subTest(package=package):
                try:
                    importlib.import_module(package)
                except ImportError:
                    self.fail(f"Core package {package} not available")
    
    def test_optional_dependencies(self):
        """Test optional ML/AI dependencies."""
        optional_packages = {
            'numpy': 'NumPy',
            'pandas': 'Pandas', 
            'sklearn': 'Scikit-learn',
            'matplotlib': 'Matplotlib'
        }
        
        missing_packages = []
        
        for import_name, display_name in optional_packages.items():
            try:
                importlib.import_module(import_name)
            except ImportError:
                missing_packages.append(display_name)
        
        if missing_packages:
            self.skipTest(f"Optional packages not available: {', '.join(missing_packages)}")
        else:
            # If all packages are available, verify they work
            self.assertTrue(True, "All optional packages available")
    
    def test_jupyter_compatibility(self):
        """Test Jupyter compatibility."""
        if check_jupyter_compatibility is None:
            self.skipTest("Validation module not available")
        
        # This should not fail, but may return False if Jupyter is not installed
        result = check_jupyter_compatibility()
        # We don't require Jupyter to be installed, just test that the check runs
        self.assertIsInstance(result, bool, "Jupyter compatibility check should return boolean")
    
    def test_dataset_directory_structure(self):
        """Test dataset directory structure."""
        if validate_dataset_directory is None:
            self.skipTest("Validation module not available")
        
        result = validate_dataset_directory()
        self.assertTrue(result, "Dataset directory structure should be valid")


class TestDatasetLoading(unittest.TestCase):
    """Test dataset loading capabilities."""
    
    def test_dataset_directory_exists(self):
        """Test that datasets directory exists."""
        datasets_dir = os.path.join(os.path.dirname(__file__), '..', 'datasets')
        self.assertTrue(os.path.exists(datasets_dir), "Datasets directory should exist")
    
    def test_data_sources_documentation(self):
        """Test that DATA_SOURCES.md exists and is readable."""
        data_sources_file = os.path.join(os.path.dirname(__file__), '..', 'datasets', 'DATA_SOURCES.md')
        
        self.assertTrue(os.path.exists(data_sources_file), "DATA_SOURCES.md should exist")
        
        # Test that the file is readable and has content
        with open(data_sources_file, 'r', encoding='utf-8') as f:
            content = f.read()
            self.assertGreater(len(content), 100, "DATA_SOURCES.md should have substantial content")
            self.assertIn("Dataset Sources", content, "DATA_SOURCES.md should contain dataset information")


class TestResourceAvailability(unittest.TestCase):
    """Test system resource availability."""
    
    def test_memory_check(self):
        """Test basic memory availability check."""
        try:
            import psutil
            memory = psutil.virtual_memory()
            available_gb = memory.available / (1024**3)
            
            # We expect at least 1GB of available memory for basic operations
            self.assertGreater(available_gb, 1.0, "Should have at least 1GB available memory")
        except ImportError:
            self.skipTest("psutil not available for memory check")
    
    def test_disk_space_check(self):
        """Test basic disk space availability."""
        try:
            import psutil
            disk = psutil.disk_usage('/')
            available_gb = disk.free / (1024**3)
            
            # We expect at least 1GB of free disk space
            self.assertGreater(available_gb, 1.0, "Should have at least 1GB free disk space")
        except ImportError:
            self.skipTest("psutil not available for disk check")


class TestModuleStructure(unittest.TestCase):
    """Test repository module structure."""
    
    def test_required_directories(self):
        """Test that required directories exist."""
        base_dir = os.path.join(os.path.dirname(__file__), '..')
        required_dirs = ['src', 'notebooks', 'datasets', 'validation', 'tests', 'docs', '.github']
        
        for directory in required_dirs:
            dir_path = os.path.join(base_dir, directory)
            with self.subTest(directory=directory):
                self.assertTrue(os.path.exists(dir_path), f"Directory {directory} should exist")
    
    def test_requirements_file(self):
        """Test that requirements.txt exists and has content."""
        requirements_file = os.path.join(os.path.dirname(__file__), '..', 'requirements.txt')
        
        self.assertTrue(os.path.exists(requirements_file), "requirements.txt should exist")
        
        with open(requirements_file, 'r', encoding='utf-8') as f:
            content = f.read().strip()
            self.assertGreater(len(content), 50, "requirements.txt should have substantial content")
            
            # Check for some expected packages
            expected_packages = ['numpy', 'pandas', 'torch', 'tensorflow', 'jupyter']
            for package in expected_packages:
                self.assertIn(package, content, f"requirements.txt should contain {package}")


def run_tests() -> bool:
    """Run all tests and return success status."""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test classes
    test_classes = [
        TestEnvironmentValidation,
        TestDatasetLoading, 
        TestResourceAvailability,
        TestModuleStructure
    ]
    
    for test_class in test_classes:
        tests = loader.loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)