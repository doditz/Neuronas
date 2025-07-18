#!/bin/bash

# Neuronas Installation Script
# Author: GitHub Copilot
# Date: June 24, 2025
# Description: Comprehensive installation script for Neuronas system optimized for HP laptops

# Exit immediately if a command exits with a non-zero status.
set -e

# Color codes for better readability
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}====================================================================${NC}"
echo -e "${BLUE}        NEURONAS INSTALLATION SCRIPT - OPTIMIZED FOR HP LAPTOP      ${NC}"
echo -e "${BLUE}====================================================================${NC}"

# Check if conda is installed
echo -e "${YELLOW}Checking if conda is installed...${NC}"
if command -v conda &> /dev/null; then
    echo -e "${GREEN}Conda is already installed.${NC}"
else
    echo -e "${RED}Conda is not installed. Installing Miniconda...${NC}"
    # Download Miniconda installer
    wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O miniconda.sh
    # Install Miniconda
    bash miniconda.sh -b -p $HOME/miniconda3
    # Add conda to path
    echo 'export PATH="$HOME/miniconda3/bin:$PATH"' >> ~/.bashrc
    source ~/.bashrc
    # Initialize conda
    conda init bash
    source ~/.bashrc
    echo -e "${GREEN}Miniconda installed successfully.${NC}"
fi

# Create a new conda environment with Python 3.10
echo -e "${YELLOW}Creating conda environment 'neuronas_env' with Python 3.10...${NC}"
conda create -n neuronas_env python=3.10 -y

# Activate the environment for the script
eval "$(conda shell.bash hook)"
conda activate neuronas_env

# Install core binary dependencies from conda-forge
echo -e "${YELLOW}Installing core binary dependencies from conda-forge...${NC}"
conda install -c conda-forge \
    numpy==1.23.5 \
    scipy==1.9.3 \
    pyyaml==6.0 \
    sqlalchemy==2.0.23 \
    psycopg2==2.9.3 \
    sqlite \
    -y

# Install application and tool dependencies with pip
echo -e "${YELLOW}Installing application dependencies from requirements-core.txt...${NC}"
pip install --no-cache-dir -r requirements-core.txt

# Install additional dependencies
pip install --no-cache-dir \
    fastapi==0.85.0 \
    uvicorn[standard]==0.18.0 \
    flask-dance==7.1.0 \
    requests-oauthlib==1.3.1 \
    email-validator==1.3.1 \
    twilio==7.16.0 \
    autopep8==1.6.0 \
    pylint==2.14.0 \
    pytest==7.3.1

# Generate a comprehensive requirements file for future use
echo -e "${YELLOW}Generating pip freeze output for reproducibility...${NC}"
pip freeze > requirements-generated.txt

# Database Setup and Verification
echo -e "${YELLOW}Setting up database environment...${NC}"

# Check if SQLite is available
echo -e "${YELLOW}Checking SQLite installation...${NC}"
if command -v sqlite3 &> /dev/null; then
    echo -e "${GREEN}SQLite is available: $(sqlite3 --version)${NC}"
else
    echo -e "${YELLOW}Installing SQLite...${NC}"
    conda install -c conda-forge sqlite -y
fi

# Create database directory
mkdir -p data

# Create database initialization script
cat > initialize_neuronas_db.py << 'EOF'
#!/usr/bin/env python3
"""
Neuronas Database Initialization Script
Creates all necessary database tables and sets up the tiered memory system.
"""

import os
import sys
import sqlite3
import logging
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def create_database_file(db_path):
    """Create a SQLite database file if it doesn't exist."""
    try:
        if not os.path.exists(db_path):
            # Create the database file
            conn = sqlite3.connect(db_path)
            conn.execute("SELECT 1")  # Simple test query
            conn.close()
            logger.info(f"Created database: {db_path}")
        else:
            logger.info(f"Database already exists: {db_path}")
        return True
    except Exception as e:
        logger.error(f"Error creating database {db_path}: {e}")
        return False

def test_database_connection(db_path):
    """Test database connection and basic operations."""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Test basic operation
        cursor.execute("CREATE TABLE IF NOT EXISTS test_table (id INTEGER PRIMARY KEY, name TEXT)")
        cursor.execute("INSERT OR IGNORE INTO test_table (name) VALUES ('test')")
        cursor.execute("SELECT * FROM test_table")
        result = cursor.fetchone()
        
        # Clean up test table
        cursor.execute("DROP TABLE IF EXISTS test_table")
        conn.commit()
        conn.close()
        
        logger.info(f"Database connection test passed: {db_path}")
        return True
    except Exception as e:
        logger.error(f"Database connection test failed for {db_path}: {e}")
        return False

def initialize_flask_tables():
    """Initialize Flask app and create all tables."""
    try:
        # Add current directory to path
        sys.path.insert(0, os.getcwd())
        
        # Import Flask app and models
        from app import app, db
        from models import (User, UserSetting, OAuth, QueryLog, CognitiveMemory, 
                          ExternalKnowledge, StateOptimization, CognitiveMetrics, 
                          ReinforcedHypotheses, SMSNotification)
        
        with app.app_context():
            # Create all tables
            db.create_all()
            logger.info("All Flask database tables created successfully")
            
            # Create test admin user if none exists
            admin_user = User.query.filter_by(username='admin').first()
            if not admin_user:
                admin_user = User(
                    username='admin',
                    email='admin@neuronas.ai',
                    is_admin=True,
                    d2_temperature=0.7,
                    hemisphere_balance=0.5,
                    creativity_weight=0.6,
                    analytical_weight=0.4
                )
                admin_user.set_password('neuronas2025')  # Default password
                db.session.add(admin_user)
                db.session.commit()
                logger.info("Created default admin user (username: admin, password: neuronas2025)")
            
            # Initialize some sample cognitive memory entries
            sample_memories = [
                {'hemisphere': 'L', 'tier': 1, 'key': 'system_status', 'value': 'initialized', 'importance': 0.9},
                {'hemisphere': 'R', 'tier': 1, 'key': 'creativity_mode', 'value': 'active', 'importance': 0.8},
                {'hemisphere': 'L', 'tier': 2, 'key': 'logical_framework', 'value': 'quantum_enhanced', 'importance': 0.7},
                {'hemisphere': 'R', 'tier': 2, 'key': 'pattern_recognition', 'value': 'neural_symbolic', 'importance': 0.7},
            ]
            
            for memory_data in sample_memories:
                existing = CognitiveMemory.query.filter_by(
                    hemisphere=memory_data['hemisphere'],
                    tier=memory_data['tier'],
                    key=memory_data['key']
                ).first()
                
                if not existing:
                    memory = CognitiveMemory(**memory_data)
                    db.session.add(memory)
            
            db.session.commit()
            logger.info("Sample cognitive memory entries created")
            
        return True
    except Exception as e:
        logger.error(f"Error initializing Flask tables: {e}")
        return False

def main():
    """Main database initialization function."""
    print("=" * 60)
    print("NEURONAS DATABASE INITIALIZATION")
    print("=" * 60)
    
    # Database files to create (tiered memory system)
    database_files = [
        'neuronas.db',  # Main application database
        'l1.db',        # Level 1 memory (short-term, high-speed)
        'l2.db',        # Level 2 memory (medium-term, balanced)
        'l3.db',        # Level 3 memory (long-term, compressed)
    ]
    
    success_count = 0
    
    # Create and test each database
    for db_file in database_files:
        if db_file == 'neuronas.db':
            db_path = db_file  # Main database in root directory
        else:
            db_path = os.path.join('data', db_file)  # Tiered memory databases in data directory
        
        logger.info(f"Setting up database: {db_path}")
        
        # Create database directory if needed
        if os.path.dirname(db_path):  # Only create directory if path has a directory component
            os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        # Create database file
        if create_database_file(db_path):
            # Test connection
            if test_database_connection(db_path):
                success_count += 1
                logger.info(f"✓ Database {db_path} is ready")
            else:
                logger.error(f"✗ Database {db_path} failed connection test")
        else:
            logger.error(f"✗ Failed to create database {db_path}")
    
    # Initialize Flask application tables
    if 'neuronas.db' in [os.path.basename(f) for f in database_files]:
        logger.info("Initializing Flask application tables...")
        if initialize_flask_tables():
            logger.info("✓ Flask application tables initialized")
        else:
            logger.error("✗ Failed to initialize Flask application tables")
    
    # Summary
    print("=" * 60)
    print(f"Database initialization complete: {success_count}/{len(database_files)} databases ready")
    
    if success_count == len(database_files):
        print("✓ All databases are ready for Neuronas!")
        print("✓ Default admin user created (username: admin, password: neuronas2025)")
        print("✓ Sample cognitive memory entries initialized")
        return True
    else:
        print("✗ Some databases failed to initialize. Check the logs above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
EOF

# Run database initialization
echo -e "${YELLOW}Initializing Neuronas databases...${NC}"
python initialize_neuronas_db.py

if [ $? -eq 0 ]; then
    echo -e "${GREEN}Database initialization completed successfully!${NC}"
else
    echo -e "${RED}Database initialization failed. Please check the logs.${NC}"
    exit 1
fi

# Optional: Install low-resource ML tools if needed
echo -e "${YELLOW}Do you want to install optimized ML libraries? (y/n)${NC}"
read -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}Installing optimized ML libraries...${NC}"
    conda install -c conda-forge scikit-learn=1.1 -y
    pip install --no-cache-dir torch==1.13.1 --index-url https://download.pytorch.org/whl/cpu
    echo -e "${GREEN}ML libraries installed successfully.${NC}"
fi

# Setup directory structure if needed
echo -e "${YELLOW}Setting up project directory structure...${NC}"
mkdir -p static templates logs data

# Create a VS Code settings file
echo -e "${YELLOW}Creating optimized VS Code settings...${NC}"
mkdir -p .vscode
cat > .vscode/settings.json << 'EOF'
{
  "extensions": {
    "recommendations": [
      "ms-python.python",
      "ms-python.vscode-pylance",
      "GitHub.copilot",
      "ms-toolsai.jupyter",
      "esbenp.prettier-vscode",
      "eamodio.gitlens",
      "anaconda-conda.conda-package-manager",
      "wholroyd.jinja"
    ]
  },
  "settings": {
    "python.defaultInterpreterPath": "${env:CONDA_PREFIX}/bin/python",
    "python.languageServer": "Pylance",
    "python.analysis.diagnosticSeverityOverrides": {
      "reportMissingImports": "none",
      "reportUndefinedVariable": "none"
    },
    "python.analysis.extraPaths": ["./src"],
    "python.formatting.provider": "autopep8",
    "python.linting.pylintEnabled": true,
    "python.linting.enabled": true,
    "files.autoSave": "afterDelay",
    "editor.fontSize": 12,
    "editor.renderWhitespace": "boundary",
    "terminal.integrated.rendererType": "dom",
    "workbench.colorTheme": "Default Light+",
    "conda.path": "$HOME/miniconda3/bin/conda"
  }
}
EOF

# Create a run script
echo -e "${YELLOW}Creating startup script...${NC}"
cat > run_neuronas.sh << 'EOF'
#!/bin/bash

# Activate conda environment
source $HOME/miniconda3/bin/activate neuronas_env

# Run the application with optimized settings
python -O -X pycache_prefix=/tmp app.py --low-power-mode
EOF
chmod +x run_neuronas.sh

# Create a VS Code argv.json for performance optimization
echo -e "${YELLOW}Creating VS Code performance optimizations...${NC}"
VSCODE_CONFIG_DIR="$HOME/.config/Code"
mkdir -p "$VSCODE_CONFIG_DIR"
cat > "$VSCODE_CONFIG_DIR/argv.json" << 'EOF'
{
  "disable-hardware-acceleration": true,
  "enable-crash-reporter": false,
  "disable-renderer-backgrounding": true
}
EOF
echo -e "${GREEN}VS Code performance settings applied to '$VSCODE_CONFIG_DIR/argv.json'.${NC}"

echo -e "${GREEN}Neuronas installation completed successfully!${NC}"
echo -e "${YELLOW}To activate the environment, run:${NC}"
echo -e "${BLUE}conda activate neuronas_env${NC}"
echo -e "${YELLOW}To start Neuronas, run:${NC}"
echo -e "${BLUE}./run_neuronas.sh${NC}"
echo -e "${YELLOW}To open VS Code with optimized settings:${NC}"
echo -e "${BLUE}code . --disable-extensions except ms-python.python,ms-python.vscode-pylance${NC}"
echo -e "${BLUE}====================================================================${NC}"
