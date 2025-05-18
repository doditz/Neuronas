import os
import logging
import json
from flask import Flask, render_template, request, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Initialize SQLAlchemy base
class Base(DeclarativeBase):
    pass

# Initialize app and database
db = SQLAlchemy(model_class=Base)
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "neuronas_default_secret_key")
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///neuronas.db")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}
db.init_app(app)

# Import routes after app initialization to avoid circular imports
from routes import register_routes

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
    
    logger.info("Neuronas system initialized successfully")

# Use with app.app_context for initialization
with app.app_context():
    import models
    db.create_all()
    initialize_application()

# Register routes
register_routes(app)

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return render_template('layout.html', content="Page not found"), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('layout.html', content="Server error occurred"), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
