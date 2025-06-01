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
import logging
import json
from flask import Flask, render_template, request, jsonify, session, g
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Import core components
from tiered_memory_integration import tiered_memory
from dual_llm_system import dual_llm_system

# Import innovative 100% free open-source components
from local_llm_hybridizer import LocalDualSystem
from smas_dispatcher import SMASDispatcher
from agent_positioning_system import AgentPositioningSystem

# Initialize SQLAlchemy base
class Base(DeclarativeBase):
    pass

# Initialize app and database
db = SQLAlchemy(model_class=Base)
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "neuronas_default_secret_key")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)  # Nécessaire pour url_for avec HTTPS
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///neuronas.db")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}
db.init_app(app)

# Import routes after app initialization to avoid circular imports
from routes import register_routes
from memory_routes import memory_bp
from llm_routes import llm_bp

# Load configuration
def load_config():
    try:
        with open('config.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        logger.warning("Config file not found, using default settings")
        return {
            "core": {
                "activation_threshold": 0.5,
                "entropy_baseline": 0.2,
                "d2_baseline": 0.5
            },
            "memory": {
                "l1_retention": 20,
                "l2_retention": 50,
                "l3_retention": 100,
                "compression_ratio": 0.7
            },
            "neural": {
                "pathway_count": 5,
                "d2stim_intensity": 0.3,
                "d2pin_intensity": 0.2
            },
            "quantum": {
                "entanglement_depth": 3,
                "collapse_threshold": 0.7
            },
            "ethical": {
                "bronas_threshold": 0.8,
                "perspective_count": 3
            }
        }

# Core application initialization
# Initialize application function
def initialize_application():
    from core_modules.core_engine import CognitiveEngine
    from core_modules.gateway_interface import GatewayInterface
    from core_modules.storage_manager import StorageManager
    
    # Load configuration
    config = load_config()
    
    # Initialize core modules
    app.cognitive_engine = CognitiveEngine()
    app.gateway = GatewayInterface()
    app.storage = StorageManager()
    
    # Initialize and attach the tiered memory system
    app.tiered_memory = tiered_memory
    app.tiered_memory.start_maintenance_thread()
    
    # Initialize and attach the dual LLM system
    app.dual_llm = dual_llm_system
    
    # Initialize 100% free open-source innovative hybridization components
    # Local dual system for hemispheric processing without external APIs
    app.local_dual_system = LocalDualSystem()
    
    # Initialize SMAS dispatcher for agent positioning
    app.smas_dispatcher = SMASDispatcher()
    
    # Initialize storage manager with proper configuration
    try:
        from core_modules.storage_manager import StorageManager
        app.storage = StorageManager()
        logger.info("Storage manager initialized successfully")
    except Exception as e:
        from core_modules.core_engine import CoreStorageManager
        app.storage = CoreStorageManager()
        logger.warning(f"Using fallback storage manager due to error: {e}")
    
    # Initialize agent positioning system
    app.agent_positioning = AgentPositioningSystem(
        dual_llm_system=app.local_dual_system,  # Use our 100% free local system
        smas_dispatcher=app.smas_dispatcher
    )
    
    # Set default agent position to central
    app.agent_positioning.set_position("central", lock_position=False)
    
    logger.info("Neuronas system initialized successfully")
    logger.info("Open-source innovative hybridization initialized")

# Use with app.app_context for initialization
with app.app_context():
    import models
    db.create_all()
    initialize_application()

# Initialize Replit authentication
with app.app_context():
    from replit_auth import make_replit_blueprint, login_manager
    
    # Register Replit Auth blueprint
    replit_bp = make_replit_blueprint()
    if replit_bp:
        app.register_blueprint(replit_bp, url_prefix="/auth")
        logger.info("Replit Auth initialized successfully")
    else:
        logger.warning("Replit Auth not available - REPL_ID environment variable missing")
    
    # Register Google Auth blueprint
    from google_auth import create_google_blueprint
    google_bp = create_google_blueprint()
    app.register_blueprint(google_bp, url_prefix="/auth")
    logger.info("Google Auth blueprint registered")
        
# Make session permanent for user sessions
@app.before_request  
def make_session_permanent():
    session.permanent = True

# Register routes
register_routes(app)

# Temporarily disable old auth to avoid conflicts
# from auth import init_auth
# login_manager = init_auth(app)

# Register memory routes blueprint
app.register_blueprint(memory_bp, url_prefix='/api/memory')

# Register dual LLM routes blueprint
app.register_blueprint(llm_bp, url_prefix='/api/llm')

# Register agent positioning routes blueprint
from agent_routes import agent_bp
app.register_blueprint(agent_bp, url_prefix='/api/agent')

# Register new feature routes (BRONAS, geolocation, session, progress)
from feature_routes import register_routes as register_feature_routes
register_feature_routes(app)

# Register model management routes
from model_routes import register_model_routes
register_model_routes(app)

# Register music generation routes
from music_routes import register_music_routes
register_music_routes(app)

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return render_template('layout.html', content="<div class='text-center mt-5'><h2>Page Not Found</h2><p>The requested page could not be found.</p><a href='/' class='btn btn-info'>Return Home</a></div>"), 404

@app.errorhandler(500)
def server_error(error):
    logger.error(f"Server error: {error}")
    return render_template('layout.html', content="<div class='text-center mt-5'><h2>Server Error</h2><p>An internal server error occurred.</p><a href='/' class='btn btn-info'>Return Home</a></div>"), 500

@app.errorhandler(Exception)
def handle_exception(e):
    logger.error(f"Unhandled exception: {e}")
    return render_template('layout.html', content="<div class='text-center mt-5'><h2>An Error Occurred</h2><p>Please try again later.</p><a href='/' class='btn btn-info'>Return Home</a></div>"), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
