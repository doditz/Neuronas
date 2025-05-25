"""
This work is licensed under CC BY-NC 4.0 International.
Commercial use requires prior written consent and compensation.
Contact: sebastienbrulotte@gmail.com
Attribution: Sebastien Brulotte aka [ Doditz ]

This document is part of the NEURONAS cognitive system.
Core modules referenced: BRONAS (Ethical Reflex Filter) and QRONAS (Probabilistic Symbolic Vector Engine).
All outputs are subject to integrity validation and ethical compliance enforced by BRONAS.
"""

"""
Schema Update for NeuronasX

This script updates the database schema with new fields for BRONAS ethics,
session transparency, and geolocation features.
"""

import os
import sys
import logging
import time
from flask import Flask
from sqlalchemy import create_engine, text

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def update_schema():
    """Update database schema with new fields"""
    logger.info("Starting schema update...")
    
    # Get database URL from environment
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        logger.error("DATABASE_URL environment variable not set")
        return False
        
    # Create engine directly
    engine = create_engine(database_url)
    
    try:
        # Check if reinforced_hypotheses table exists
        with engine.connect() as conn:
            result = conn.execute(text(
                "SELECT EXISTS (SELECT FROM information_schema.tables "
                "WHERE table_name = 'reinforced_hypotheses')"
            ))
            table_exists = result.scalar()
            
            if not table_exists:
                logger.warning("reinforced_hypotheses table doesn't exist, creating it")
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS reinforced_hypotheses (
                        id SERIAL PRIMARY KEY,
                        hypothesis VARCHAR(255) NOT NULL,
                        confidence FLOAT DEFAULT 0.5,
                        feedback_count INTEGER DEFAULT 0,
                        category VARCHAR(50) DEFAULT 'general',
                        user_id INTEGER,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """))
                logger.info("Created reinforced_hypotheses table")
            else:
                # Check if category column exists
                result = conn.execute(text(
                    "SELECT EXISTS (SELECT FROM information_schema.columns "
                    "WHERE table_name = 'reinforced_hypotheses' AND column_name = 'category')"
                ))
                category_exists = result.scalar()
                
                if not category_exists:
                    logger.info("Adding category column to reinforced_hypotheses table")
                    conn.execute(text(
                        "ALTER TABLE reinforced_hypotheses "
                        "ADD COLUMN category VARCHAR(50) DEFAULT 'general'"
                    ))
                    
                # Check if user_id column exists
                result = conn.execute(text(
                    "SELECT EXISTS (SELECT FROM information_schema.columns "
                    "WHERE table_name = 'reinforced_hypotheses' AND column_name = 'user_id')"
                ))
                user_id_exists = result.scalar()
                
                if not user_id_exists:
                    logger.info("Adding user_id column to reinforced_hypotheses table")
                    conn.execute(text(
                        "ALTER TABLE reinforced_hypotheses "
                        "ADD COLUMN user_id INTEGER"
                    ))
            
            # Add some initial principles if table is empty
            result = conn.execute(text("SELECT COUNT(*) FROM reinforced_hypotheses"))
            count = result.scalar()
            
            if count == 0:
                logger.info("Adding initial ethical principles to BRONAS repository")
                
                # Core ethical principles to add
                principles = [
                    ("Respect for human autonomy", 0.95, "foundational"),
                    ("Non-maleficence (do no harm)", 0.95, "foundational"),
                    ("Beneficence (do good)", 0.92, "foundational"),
                    ("Justice and fairness", 0.90, "foundational"),
                    ("Transparency in decision-making", 0.88, "foundational"),
                    ("Respect user privacy", 0.93, "privacy"),
                    ("Secure user data", 0.92, "privacy"),
                    ("Obtain informed consent", 0.90, "privacy"),
                    ("Allow data access and control", 0.87, "privacy"),
                    ("Limit data collection to necessary", 0.85, "privacy")
                ]
                
                # Insert principles
                for hypothesis, confidence, category in principles:
                    conn.execute(text(
                        "INSERT INTO reinforced_hypotheses "
                        "(hypothesis, confidence, feedback_count, category) "
                        "VALUES (:hypothesis, :confidence, 1, :category)"
                    ), {"hypothesis": hypothesis, "confidence": confidence, "category": category})
                    
                logger.info(f"Added {len(principles)} initial ethical principles")
                
            logger.info("Schema update completed successfully")
            return True
                
    except Exception as e:
        logger.error(f"Error updating schema: {e}")
        return False

if __name__ == "__main__":
    update_schema()