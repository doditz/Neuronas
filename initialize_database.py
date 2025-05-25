"""
Database Initialization for NeuronasX

This script initializes and updates the database models for the NeuronasX system,
ensuring all components work together properly.
"""

import os
import logging
import uuid
from datetime import datetime, timedelta
from sqlalchemy.exc import IntegrityError
from flask import Flask
from models import db, User, ReinforcedHypotheses, QueryLog, CognitiveMemory

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_app():
    """Create a Flask app for database initialization"""
    app = Flask(__name__)
    
    # Configure database
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_recycle": 300,
        "pool_pre_ping": True,
    }
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    
    # Initialize SQLAlchemy
    db.init_app(app)
    
    return app

def update_reinforced_hypotheses_model():
    """Update the ReinforcedHypotheses model to include the category field"""
    # Check if table exists first
    if not db.engine.has_table(ReinforcedHypotheses.__tablename__):
        logger.info("Creating ReinforcedHypotheses table")
        db.create_all()
        return
        
    # Check if category column exists
    inspector = db.inspect(db.engine)
    columns = [col['name'] for col in inspector.get_columns(ReinforcedHypotheses.__tablename__)]
    
    if 'category' not in columns:
        logger.info("Adding category column to ReinforcedHypotheses table")
        db.engine.execute(
            f"ALTER TABLE {ReinforcedHypotheses.__tablename__} ADD COLUMN category VARCHAR(50)"
        )
        
    # Check if user_id column exists
    if 'user_id' not in columns:
        logger.info("Adding user_id column to ReinforcedHypotheses table")
        db.engine.execute(
            f"ALTER TABLE {ReinforcedHypotheses.__tablename__} ADD COLUMN user_id INTEGER"
        )

def initialize_database():
    """Initialize the database tables and relationships"""
    # Create all tables if they don't exist
    db.create_all()
    
    # Add additional fields or make schema updates
    try:
        update_reinforced_hypotheses_model()
        
        # Add any other model updates here
        logger.info("Database schema updated successfully")
    except Exception as e:
        logger.error(f"Error updating database schema: {e}")

def create_initial_user():
    """Create an initial admin user if none exists"""
    if User.query.count() == 0:
        logger.info("Creating initial admin user")
        
        try:
            # Create admin user
            admin = User(
                username="admin",
                email="admin@neuronasx.ai",
                is_admin=True,
                d2_temperature=0.5,
                hemisphere_balance=0.5,
                creativity_weight=0.5,
                analytical_weight=0.5
            )
            
            # Set a secure random password
            admin.set_password(str(uuid.uuid4()))
            
            db.session.add(admin)
            db.session.commit()
            
            logger.info("Initial admin user created successfully")
        except IntegrityError:
            db.session.rollback()
            logger.warning("Admin user already exists")
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error creating admin user: {e}")

def seed_initial_memory():
    """Seed initial memory data if none exists"""
    # Check if we already have memory data
    if CognitiveMemory.query.count() > 0:
        return
        
    logger.info("Seeding initial memory data")
    
    try:
        # Create some initial memory items for both hemispheres
        current_time = datetime.utcnow()
        
        # Left hemisphere memories (analytical)
        left_memories = [
            {
                "hemisphere": "L",
                "tier": 1,
                "key": "system_architecture",
                "value": "The NeuronasX system uses a dual-hemisphere architecture with analytical and creative processing.",
                "importance": 0.9,
                "expiration": current_time + timedelta(hours=24)
            },
            {
                "hemisphere": "L",
                "tier": 1,
                "key": "memory_structure",
                "value": "Memory is organized in three tiers (L1/L2/L3 and R1/R2/R3) with different retention periods.",
                "importance": 0.85,
                "expiration": current_time + timedelta(hours=20)
            },
            {
                "hemisphere": "L",
                "tier": 2,
                "key": "d2_mechanism",
                "value": "The D2 mechanism controls hemisphere balance, with D2Pin reducing and D2Stim increasing creativity.",
                "importance": 0.8,
                "expiration": current_time + timedelta(days=7)
            },
            {
                "hemisphere": "L",
                "tier": 3,
                "key": "bronas_ethics",
                "value": "BRONAS provides ethical guidance based on reinforced hypotheses and core principles.",
                "importance": 0.75,
                "expiration": current_time + timedelta(days=30)
            }
        ]
        
        # Right hemisphere memories (creative)
        right_memories = [
            {
                "hemisphere": "R",
                "tier": 1,
                "key": "creativity_patterns",
                "value": "Creative thinking involves pattern recognition across seemingly unrelated domains.",
                "importance": 0.85,
                "expiration": current_time + timedelta(hours=24)
            },
            {
                "hemisphere": "R",
                "tier": 1,
                "key": "metaphorical_thinking",
                "value": "Using metaphors allows for deeper understanding through creative mapping of concepts.",
                "importance": 0.8,
                "expiration": current_time + timedelta(hours=20)
            },
            {
                "hemisphere": "R",
                "tier": 2,
                "key": "divergent_ideation",
                "value": "Divergent thinking generates multiple solutions rather than converging on a single answer.",
                "importance": 0.75,
                "expiration": current_time + timedelta(days=7)
            },
            {
                "hemisphere": "R",
                "tier": 3,
                "key": "creative_intuition",
                "value": "Intuitive leaps connect disparate concepts in ways logical analysis might miss.",
                "importance": 0.7,
                "expiration": current_time + timedelta(days=30)
            }
        ]
        
        # Add memories to database
        for memory_data in left_memories + right_memories:
            memory = CognitiveMemory(**memory_data)
            db.session.add(memory)
            
        db.session.commit()
        logger.info(f"Added {len(left_memories)} left hemisphere and {len(right_memories)} right hemisphere memories")
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error seeding initial memory data: {e}")

def initialize_all():
    """Initialize all database components"""
    app = create_app()
    
    with app.app_context():
        logger.info("Starting database initialization")
        
        # Initialize database schema
        initialize_database()
        
        # Create initial admin user
        create_initial_user()
        
        # Seed initial memory data
        seed_initial_memory()
        
        logger.info("Database initialization complete")

if __name__ == "__main__":
    initialize_all()