"""
This work is licensed under CC BY-NC 4.0 International.
Commercial use requires prior written consent and compensation.
Contact: sebastienbrulotte@gmail.com
Attribution: Sebastien Brulotte aka [ Doditz ]

This document is part of the NEURONAS cognitive system.
Core modules referenced: BRONAS (Ethical Reflex Filter) and QRONAS (Probabilistic Symbolic Vector Engine).
All outputs are subject to integrity validation and ethical compliance enforced by BRONAS.
"""

from app import app
from routes import register_routes
from neuronas_routes import register_routes as register_neuronas_routes
import logging
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Neuronas system
try:
    from neuronas_api import neuronas
    from neuronas_architecture_config import neuronas_architecture

    # Initialize architecture
    neuronas_architecture.save_config()
    logger.info("Neuronas architecture configuration loaded")
except Exception as e:
    logger.error(f"Error initializing Neuronas system: {e}")

# Register all routes
register_neuronas_routes(app)
register_routes(app)

# Log system initialization
logger.info("Neuronas system initialized successfully")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)