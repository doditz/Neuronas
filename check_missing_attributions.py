
#!/usr/bin/env python3
"""
This work is licensed under CC BY-NC 4.0 International.
Commercial use requires prior written consent and compensation.
Contact: sebastienbrulotte@gmail.com
Attribution: Sebastien Brulotte aka [ Doditz ]

This document is part of the NEURONAS cognitive system.
Core modules referenced: BRONAS (Ethical Reflex Filter) and QRONAS (Probabilistic Symbolic Vector Engine).
All outputs are subject to integrity validation and ethical compliance enforced by BRONAS.
"""

import os
import sys
import re

# Define patterns to look for in different file types
LICENSE_PATTERNS = {
    '.py': [
        r'This work is licensed under CC BY-NC 4\.0 International',
        r'Attribution: Sebastien Brulotte aka \[ Doditz \]'
    ],
    '.js': [
        r'This work is licensed under CC BY-NC 4\.0 International',
        r'Attribution: Sebastien Brulotte aka \[ Doditz \]'
    ],
    '.css': [
        r'This work is licensed under CC BY-NC 4\.0 International',
        r'Attribution: Sebastien Brulotte aka \[ Doditz \]'
    ],
    '.html': [
        r'This work is licensed under CC BY-NC 4\.0 International',
        r'Attribution: Sebastien Brulotte aka \[ Doditz \]'
    ]
}

# Files to exclude from checking
EXCLUDE_FILES = [
    '.git', 
    '__pycache__', 
    'node_modules',
    '.replit',
    'pyproject.toml',
    'requirements.txt',
    'package.json',
    'README.md',
    'LICENSE',
    'CONTRIBUTORS.md',
    'ATTRIBUTIONS.md'
]

def check_file(file_path):
    """
    Check if a file has the required license text
    Returns True if the file has appropriate attribution, False otherwise
    """
    ext = os.path.splitext(file_path)[1].lower()
    
    # Skip if we don't have patterns for this file type
    if ext not in LICENSE_PATTERNS:
        return True
        
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Check for required patterns
        for pattern in LICENSE_PATTERNS[ext]:
            if not re.search(pattern, content):
                return False
                
        return True
    except UnicodeDecodeError:
        # Skip binary files
        return True
    except Exception as e:
        print(f"Error checking {file_path}: {e}")
        return True

def should_exclude(path):
    """Check if the path should be excluded from checking"""
    filename = os.path.basename(path)
    for exclude in EXCLUDE_FILES:
        if exclude in path:
            return True
    return False

def scan_directory(directory='.'):
    """
    Scan a directory recursively for files missing attribution
    """
    missing_attribution = []
    
    for root, dirs, files in os.walk(directory):
        # Skip excluded directories
        dirs[:] = [d for d in dirs if not should_exclude(os.path.join(root, d))]
        
        for file in files:
            file_path = os.path.join(root, file)
            
            # Skip excluded files
            if should_exclude(file_path):
                continue
                
            if not check_file(file_path):
                missing_attribution.append(file_path)
    
    return missing_attribution

if __name__ == "__main__":
    print("Checking for files missing proper attribution...")
    
    missing_files = scan_directory()
    
    if missing_files:
        print("\n⚠️ The following files need proper attribution:")
        for file in missing_files:
            print(f"  - {file}")
        print(f"\nTotal files needing attribution: {len(missing_files)}")
        sys.exit(1)
    else:
        print("✅ All applicable files have proper attribution.")
        sys.exit(0)
