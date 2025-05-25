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
Component Testing for NeuronasX

This script tests each NeuronasX component independently to help debug any issues.
"""

import os
import sys
import logging
import time
import json
import uuid
from datetime import datetime
import traceback
import pprint

# Configure detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

def test_database_connection():
    """Test database connection and tables"""
    logger.info("Testing database connection...")
    
    try:
        from flask import Flask
        from flask_sqlalchemy import SQLAlchemy
        
        # Create a minimal Flask application
        app = Flask(__name__)
        app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
        app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
        
        # Initialize SQLAlchemy
        db = SQLAlchemy(app)
        
        # Test basic connection
        with app.app_context():
            engine = db.engine
            connection = engine.connect()
            
            # Check tables
            from sqlalchemy import inspect
            inspector = inspect(engine)
            tables = inspector.get_table_names()
            logger.info(f"Database tables: {tables}")
            
            # Check specific tables we're interested in
            if 'reinforced_hypotheses' in tables:
                columns = inspector.get_columns('reinforced_hypotheses')
                column_names = [col['name'] for col in columns]
                logger.info(f"ReinforcedHypotheses columns: {column_names}")
                
                # Check if category and user_id columns exist
                if 'category' in column_names and 'user_id' in column_names:
                    logger.info("ReinforcedHypotheses table has the required columns")
                else:
                    logger.warning("ReinforcedHypotheses table is missing required columns")
            else:
                logger.warning("ReinforcedHypotheses table not found")
                
            connection.close()
            logger.info("Database connection test completed successfully")
            return True
            
    except Exception as e:
        logger.error(f"Database connection error: {e}")
        traceback.print_exc()
        return False

def test_bronas_ethics():
    """Test BRONAS ethics repository functionality"""
    logger.info("Testing BRONAS ethics repository...")
    
    try:
        # Import necessary modules
        from flask import Flask
        from flask_sqlalchemy import SQLAlchemy
        import sys
        
        # Add the directory to sys.path if needed
        if os.getcwd() not in sys.path:
            sys.path.append(os.getcwd())
            
        # Create a minimal Flask application
        app = Flask(__name__)
        app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
        app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
        
        # Initialize SQLAlchemy
        db = SQLAlchemy(app)
        
        # Initialize database tables
        with app.app_context():
            # Create necessary table
            db.engine.execute('''
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
            ''')
            
            # Add a test principle if the table is empty
            result = db.engine.execute("SELECT COUNT(*) FROM reinforced_hypotheses")
            count = result.scalar()
            
            if count == 0:
                logger.info("Adding test principle to BRONAS repository")
                db.engine.execute('''
                    INSERT INTO reinforced_hypotheses 
                    (hypothesis, confidence, feedback_count, category)
                    VALUES 
                    ('Respect user privacy', 0.9, 1, 'privacy')
                ''')
            
            # Query principles
            result = db.engine.execute("SELECT * FROM reinforced_hypotheses LIMIT 5")
            principles = [dict(row) for row in result]
            
            logger.info(f"BRONAS principles: {principles}")
            logger.info("BRONAS ethics test completed successfully")
            return True
            
    except Exception as e:
        logger.error(f"BRONAS ethics test error: {e}")
        traceback.print_exc()
        return False

def test_geolocation():
    """Test geolocation adaptation service"""
    logger.info("Testing geolocation service...")
    
    try:
        # Test cultural context mapping
        from geolocation_service import GeolocationService
        
        geo_service = GeolocationService()
        
        # Test cultural contexts
        countries = ["JP", "US", "DE", "IN", "BR"]
        
        for country in countries:
            context = geo_service.get_cultural_context(country)
            logger.info(f"Cultural context for {country}: {context['context']['name']}")
            logger.info(f"  Language: {context['context']['language_preference']}")
            logger.info(f"  Formality level: {context['context']['formality_level']}")
            logger.info(f"  Communication style: {context['context']['communication_style']}")
            
        # Test response adaptation
        adapted = geo_service.adapt_response(
            "This is a test response that should be adapted based on cultural context.",
            country_code="JP"
        )
        
        logger.info(f"Adapted response for JP: {adapted['cultural_context']['name']}")
        logger.info("Geolocation service test completed successfully")
        return True
        
    except Exception as e:
        logger.error(f"Geolocation service test error: {e}")
        traceback.print_exc()
        return False

def test_session_transparency():
    """Test session transparency functionality"""
    logger.info("Testing session transparency...")
    
    try:
        from session_transparency import SessionTransparency
        
        # Create a session tracker without database dependency
        session_system = SessionTransparency(None)
        
        # Create a session
        session_info = session_system.create_session(
            source_info={"ip": "127.0.0.1", "user_agent": "Debug Test"}
        )
        
        session_id = session_info['session_id']
        logger.info(f"Created session: {session_id}")
        
        # Record interactions
        for i in range(3):
            interaction = session_system.record_interaction(
                session_id,
                "test_interaction",
                data={"test_key": f"test_value_{i}"}
            )
            logger.info(f"Recorded interaction {i+1}: {interaction['interaction_id']}")
            
        # Validate session
        is_valid = session_system.validate_session(session_id)
        logger.info(f"Session validation: {is_valid}")
        
        # Get session info
        session_data = session_system.get_session_info(session_id)
        logger.info(f"Session info: {session_data}")
        
        logger.info("Session transparency test completed successfully")
        return True
        
    except Exception as e:
        logger.error(f"Session transparency test error: {e}")
        traceback.print_exc()
        return False

def test_agent_positioning():
    """Test agent positioning system"""
    logger.info("Testing agent positioning system...")
    
    try:
        from smas_dispatcher import SMASDispatcher, PositionType
        from agent_positioning_system import AgentPositioningSystem
        
        # Initialize components
        smas = SMASDispatcher()
        agent_system = AgentPositioningSystem(smas_dispatcher=smas)
        
        # Test different positions
        positions = ["left", "central", "right", "hybrid"]
        
        for position in positions:
            agent_system.set_position(position)
            state = agent_system.get_positioning_state()
            logger.info(f"Set position to {position}")
            logger.info(f"  Current position: {state['current_position']}")
            logger.info(f"  Position locked: {state['position_locked']}")
            logger.info(f"  Analytical weight: {state['analytical_weight']}")
            logger.info(f"  Creative weight: {state['creative_weight']}")
            
        # Test processing a query
        query = "This is a test query for agent positioning"
        result = agent_system.process_with_positioning(query)
        
        logger.info(f"Processing result:")
        logger.info(f"  Response length: {len(result.get('response', ''))}")
        logger.info(f"  Position: {result.get('agent_position')}")
        logger.info(f"  Hemisphere used: {result.get('hemisphere_used')}")
        
        logger.info("Agent positioning test completed successfully")
        return True
        
    except Exception as e:
        logger.error(f"Agent positioning test error: {e}")
        traceback.print_exc()
        return False

def test_progress_tracker():
    """Test progress tracking system"""
    logger.info("Testing progress tracking system...")
    
    try:
        from progress_tracker import ProgressTracker, ChangeType, SystemComponent, MilestoneStatus
        
        # Initialize progress tracker
        tracker = ProgressTracker()
        
        # Log some test changes
        tracker.log_change(
            "Test database implementation",
            ChangeType.FEATURE_ADDED,
            SystemComponent.DATABASE,
            user="test_user",
            details="Added initial database schema"
        )
        
        tracker.log_change(
            "Fix memory maintenance issue",
            ChangeType.BUG_FIXED,
            SystemComponent.MEMORY,
            user="test_user",
            details="Fixed bug in memory tier maintenance"
        )
        
        # Add a test phase
        phase = tracker.add_phase(
            "Test Phase",
            start_date="2025-05-25",
            end_date="2025-05-30",
            description="Phase for testing"
        )
        
        # Add some milestones
        tracker.add_milestone(
            "Test milestone 1",
            phase['id'],
            SystemComponent.CORE,
            "First test milestone",
            MilestoneStatus.COMPLETED
        )
        
        tracker.add_milestone(
            "Test milestone 2",
            phase['id'],
            SystemComponent.DATABASE,
            "Second test milestone",
            MilestoneStatus.IN_PROGRESS
        )
        
        # Get progress summary
        summary = tracker.get_progress_summary()
        logger.info(f"Progress summary:")
        logger.info(f"  Overall progress: {summary['overall_progress']:.1f}%")
        logger.info(f"  Completed milestones: {summary['milestone_stats']['completed']}")
        logger.info(f"  In-progress milestones: {summary['milestone_stats']['in_progress']}")
        
        # Generate report
        report_path = tracker.generate_html_report("test_progress.html")
        logger.info(f"Generated progress report at: {report_path}")
        
        logger.info("Progress tracking test completed successfully")
        return True
        
    except Exception as e:
        logger.error(f"Progress tracking test error: {e}")
        traceback.print_exc()
        return False
        
def run_all_tests():
    """Run all component tests"""
    logger.info("Starting comprehensive component testing...")
    
    test_results = {
        "database": test_database_connection(),
        "bronas_ethics": test_bronas_ethics(),
        "geolocation": test_geolocation(),
        "session_transparency": test_session_transparency(),
        "agent_positioning": test_agent_positioning(),
        "progress_tracker": test_progress_tracker()
    }
    
    # Print summary
    logger.info("\n===== TEST RESULTS SUMMARY =====")
    for component, result in test_results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        logger.info(f"{component}: {status}")
        
    # Overall status
    success_count = sum(1 for result in test_results.values() if result)
    total_count = len(test_results)
    logger.info(f"\nOverall: {success_count}/{total_count} tests passed")
    
    return all(test_results.values())
    
if __name__ == "__main__":
    run_all_tests()