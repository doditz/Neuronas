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
Debug Utilities for NeuronasX

This module provides comprehensive debugging tools to test and verify
all components of the NeuronasX system.
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
from flask import Flask, current_app

# Enable detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

class DebugUtilities:
    """Debug utilities for testing NeuronasX components"""
    
    def __init__(self, app=None):
        """
        Initialize debug utilities
        
        Args:
            app: Flask application instance
        """
        self.app = app
        
    def enable_debug_mode(self):
        """Enable detailed debug logging for all components"""
        # Configure root logger to DEBUG
        logging.getLogger().setLevel(logging.DEBUG)
        
        # Configure specific loggers
        for logger_name in [
            'cognitive_memory_manager',
            'dual_llm_system', 
            'tiered_memory_integration',
            'routes',
            'bronas_ethics',
            'geolocation_service',
            'session_transparency',
            'progress_tracker',
            'smas_dispatcher',
            'agent_positioning_system',
            'models',
            'sqlalchemy.engine'
        ]:
            logging.getLogger(logger_name).setLevel(logging.DEBUG)
            
        logger.info("Debug mode enabled for all components")
        
    def test_database_connection(self):
        """Test database connection and schema"""
        from models import db
        
        logger.info("Testing database connection...")
        
        try:
            # Test basic connection
            engine = db.engine
            connection = engine.connect()
            connection.close()
            logger.info("Database connection successful")
            
            # Inspect tables
            from sqlalchemy import inspect
            inspector = inspect(engine)
            tables = inspector.get_table_names()
            logger.info(f"Database tables: {tables}")
            
            # Test models
            from models import User, CognitiveMemory, ReinforcedHypotheses, QueryLog
            
            models_to_check = [
                (User, "User"),
                (CognitiveMemory, "CognitiveMemory"),
                (ReinforcedHypotheses, "ReinforcedHypotheses"),
                (QueryLog, "QueryLog")
            ]
            
            for model, name in models_to_check:
                try:
                    # Check if model can be queried
                    count = model.query.count()
                    logger.info(f"{name} model check successful, count: {count}")
                    
                    # Check columns in ReinforcedHypotheses
                    if name == "ReinforcedHypotheses":
                        columns = [column.name for column in inspect(model).columns]
                        logger.info(f"{name} columns: {columns}")
                        
                        # Verify category and user_id columns exist
                        assert 'category' in columns, "category column missing"
                        assert 'user_id' in columns, "user_id column missing"
                        logger.info(f"{name} column validation successful")
                        
                except Exception as e:
                    logger.error(f"Error checking {name} model: {e}")
                    traceback.print_exc()
                    
            return True
            
        except Exception as e:
            logger.error(f"Database connection error: {e}")
            traceback.print_exc()
            return False
            
    def test_bronas_ethics(self):
        """Test BRONAS ethics repository"""
        logger.info("Testing BRONAS ethics repository...")
        
        try:
            from bronas_ethics import BRONASEthicsRepository
            from models import db
            
            # Initialize BRONAS repository
            bronas = BRONASEthicsRepository(db)
            
            # Get statistics
            stats = bronas.get_statistics()
            logger.info(f"BRONAS statistics: {json.dumps(stats, indent=2)}")
            
            # Get principles
            principles = bronas.get_principles(limit=5)
            logger.info(f"Top 5 BRONAS principles: {json.dumps(principles, indent=2)}")
            
            # Test evaluation
            evaluation = bronas.evaluate_statement(
                "Users should have control over their personal data",
                session_id=str(uuid.uuid4())
            )
            logger.info(f"BRONAS evaluation: {json.dumps(evaluation, indent=2)}")
            
            return True
            
        except Exception as e:
            logger.error(f"BRONAS ethics test error: {e}")
            traceback.print_exc()
            return False
            
    def test_geolocation_service(self):
        """Test geolocation adaptation service"""
        logger.info("Testing geolocation service...")
        
        try:
            from geolocation_service import GeolocationService
            
            # Initialize geolocation service
            geo_service = GeolocationService()
            
            # Test cultural contexts
            countries = ["JP", "US", "DE", "IN", "BR", "DEFAULT"]
            
            for country in countries:
                context = geo_service.get_cultural_context(country)
                logger.info(f"Cultural context for {country}: {json.dumps(context, indent=2)}")
                
            # Test response adaptation
            adapted = geo_service.adapt_response(
                "This is a test response that should be adapted based on cultural context.",
                country_code="JP"
            )
            logger.info(f"Adapted response for JP: {json.dumps(adapted, indent=2)}")
            
            return True
            
        except Exception as e:
            logger.error(f"Geolocation service test error: {e}")
            traceback.print_exc()
            return False
            
    def test_session_transparency(self):
        """Test session transparency system"""
        logger.info("Testing session transparency system...")
        
        try:
            from session_transparency import SessionTransparency
            from models import db
            
            # Initialize session transparency
            session_system = SessionTransparency(db)
            
            # Create a session
            session_info = session_system.create_session(
                source_info={"ip": "127.0.0.1", "user_agent": "Debug Test"}
            )
            logger.info(f"Created session: {json.dumps(session_info, indent=2)}")
            
            # Record interactions
            session_id = session_info['session_id']
            
            for i in range(3):
                interaction = session_system.record_interaction(
                    session_id,
                    "test_interaction",
                    data={"test_key": f"test_value_{i}"},
                    system_components=["debug", "test"]
                )
                logger.info(f"Recorded interaction {i+1}: {json.dumps(interaction, indent=2)}")
                
            # Verify interaction
            verify_result = session_system.verify_interaction(interaction)
            logger.info(f"Interaction verification result: {verify_result}")
            
            # Get session info
            session_data = session_system.get_session_info(session_id)
            logger.info(f"Session info: {json.dumps(session_data, indent=2)}")
            
            return True
            
        except Exception as e:
            logger.error(f"Session transparency test error: {e}")
            traceback.print_exc()
            return False
            
    def test_progress_tracker(self):
        """Test progress tracking system"""
        logger.info("Testing progress tracking system...")
        
        try:
            from progress_tracker import ProgressTracker, ChangeType, SystemComponent
            
            # Initialize progress tracker
            tracker = ProgressTracker()
            
            # Log a test change
            change = tracker.log_change(
                "Test change for debugging",
                ChangeType.ENHANCEMENT,
                SystemComponent.CORE,
                user="debug_user",
                details="This is a test change for debugging purposes"
            )
            logger.info(f"Logged test change: {json.dumps(change, indent=2)}")
            
            # Get changes
            changes = tracker.get_changes(limit=5)
            logger.info(f"Recent changes: {json.dumps(changes, indent=2)}")
            
            # Get progress summary
            summary = tracker.get_progress_summary()
            logger.info(f"Progress summary: {json.dumps(summary, indent=2)}")
            
            return True
            
        except Exception as e:
            logger.error(f"Progress tracker test error: {e}")
            traceback.print_exc()
            return False
            
    def test_agent_positioning(self):
        """Test agent positioning system"""
        logger.info("Testing agent positioning system...")
        
        try:
            from agent_positioning_system import AgentPositioningSystem
            from smas_dispatcher import SMASDispatcher
            
            # Initialize SMAS dispatcher
            smas = SMASDispatcher()
            
            # Initialize agent positioning
            agent_system = AgentPositioningSystem(smas_dispatcher=smas)
            
            # Test different positions
            positions = ["left", "central", "right", "hybrid"]
            
            for position in positions:
                result = agent_system.set_position(position)
                state = agent_system.get_positioning_state()
                logger.info(f"Set position to {position}: {result}")
                logger.info(f"Agent state: {json.dumps(state, indent=2)}")
                
                # Test processing with this position
                process_result = agent_system.process_with_positioning(
                    f"This is a test query processed from the {position} position"
                )
                logger.info(f"Processing result from {position}: {json.dumps(process_result, indent=2)}")
                
            return True
            
        except Exception as e:
            logger.error(f"Agent positioning test error: {e}")
            traceback.print_exc()
            return False
            
    def test_development_history(self):
        """Test development history system"""
        logger.info("Testing development history system...")
        
        try:
            from development_history import DevelopmentHistory
            from progress_tracker import ProgressTracker
            
            # Initialize progress tracker
            tracker = ProgressTracker()
            
            # Initialize development history
            history = DevelopmentHistory(tracker)
            
            # Generate timeline report
            report_path = history.generate_timeline_report("debug_timeline.html")
            logger.info(f"Generated timeline report at: {report_path}")
            
            return True
            
        except Exception as e:
            logger.error(f"Development history test error: {e}")
            traceback.print_exc()
            return False
            
    def test_all_components(self):
        """Test all components together"""
        logger.info("Starting comprehensive test of all components...")
        
        # Enable debug mode
        self.enable_debug_mode()
        
        # Test database first
        db_result = self.test_database_connection()
        
        if not db_result:
            logger.error("Database test failed, stopping further tests")
            return False
            
        # Test all components
        test_results = {
            "database": db_result,
            "bronas_ethics": self.test_bronas_ethics(),
            "geolocation": self.test_geolocation_service(),
            "session_transparency": self.test_session_transparency(),
            "progress_tracker": self.test_progress_tracker(),
            "agent_positioning": self.test_agent_positioning(),
            "development_history": self.test_development_history()
        }
        
        # Print overall results
        logger.info("TEST RESULTS SUMMARY:")
        for component, result in test_results.items():
            status = "PASSED" if result else "FAILED"
            logger.info(f"{component}: {status}")
            
        # Calculate overall success
        overall_success = all(test_results.values())
        logger.info(f"OVERALL TEST STATUS: {'SUCCESS' if overall_success else 'FAILURE'}")
        
        return overall_success
        
# Run tests when executed directly
if __name__ == "__main__":
    # Create Flask app for testing
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    
    from models import db
    db.init_app(app)
    
    with app.app_context():
        debug = DebugUtilities(app)
        debug.test_all_components()