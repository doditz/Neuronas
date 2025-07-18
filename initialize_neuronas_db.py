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
