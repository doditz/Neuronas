
"""
Neuronas API Routes - Flask routes for interacting with Neuronas AI
"""

from flask import Blueprint, request, jsonify
import time
import random
import logging
from neuronas_api import neuronas

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create blueprint
neuronas_bp = Blueprint('neuronas', __name__, url_prefix='/api/neuronas')

@neuronas_bp.route('/status', methods=['GET'])
def get_status():
    """Get current Neuronas system status"""
    try:
        metrics = neuronas.get_system_metrics()
        
        return jsonify({
            "success": True,
            "session_id": neuronas.session_id,
            "d2_activation": neuronas.core_engine.d2_activation,
            "d2stim_level": neuronas.core_engine.d2stim_level,
            "d2pin_level": neuronas.core_engine.d2pin_level,
            "attention": neuronas.core_engine.attention,
            "metrics": metrics
        })
    except Exception as e:
        logger.error(f"Error getting status: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        })

@neuronas_bp.route('/process', methods=['POST'])
def process_query():
    """Process a query through Neuronas"""
    try:
        data = request.json
        
        if not data or 'query' not in data:
            return jsonify({
                "success": False,
                "error": "Missing required parameter: 'query'"
            })
            
        query_text = data['query']
        d2_params = data.get('d2_params')
        context = data.get('context')
        
        response = neuronas.process_query(query_text, d2_params, context)
        
        return jsonify({
            "success": True,
            "response": response
        })
    except Exception as e:
        logger.error(f"Error processing query: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        })

@neuronas_bp.route('/d2_modulation', methods=['POST'])
def set_d2_modulation():
    """Set D2 receptor modulation levels"""
    try:
        data = request.json
        
        if not data:
            return jsonify({
                "success": False,
                "error": "Missing required parameters"
            })
            
        stim_level = data.get('stim_level')
        pin_level = data.get('pin_level')
        
        if stim_level is None or pin_level is None:
            return jsonify({
                "success": False,
                "error": "Missing required parameters: 'stim_level' and/or 'pin_level'"
            })
            
        result = neuronas.set_d2_modulation(stim_level, pin_level)
        
        return jsonify({
            "success": True,
            **result
        })
    except Exception as e:
        logger.error(f"Error setting D2 modulation: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        })

@neuronas_bp.route('/attention', methods=['POST'])
def adjust_attention():
    """Adjust system attention level"""
    try:
        data = request.json
        
        if not data or 'level' not in data:
            return jsonify({
                "success": False,
                "error": "Missing required parameter: 'level'"
            })
            
        level = data['level']
        
        result = neuronas.adjust_attention(level)
        
        return jsonify({
            "success": True,
            **result
        })
    except Exception as e:
        logger.error(f"Error adjusting attention: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        })

@neuronas_bp.route('/metrics', methods=['GET'])
def get_metrics():
    """Get system metrics"""
    try:
        metrics = neuronas.get_system_metrics()
        
        return jsonify({
            "success": True,
            "metrics": metrics
        })
    except Exception as e:
        logger.error(f"Error getting metrics: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        })

@neuronas_bp.route('/memory', methods=['GET'])
def get_memory_stats():
    """Get memory system statistics"""
    try:
        stats = neuronas.get_memory_stats()
        
        return jsonify({
            "success": True,
            "stats": stats
        })
    except Exception as e:
        logger.error(f"Error getting memory stats: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        })

@neuronas_bp.route('/architecture', methods=['GET'])
def get_architecture():
    """Get architecture configuration"""
    try:
        config = neuronas.get_architecture_config()
        
        return jsonify({
            "success": True,
            "config": config
        })
    except Exception as e:
        logger.error(f"Error getting architecture: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        })

@neuronas_bp.route('/reset', methods=['POST'])
def reset_system():
    """Reset the system to default state"""
    try:
        result = neuronas.reset_system()
        
        return jsonify({
            "success": True,
            **result
        })
    except Exception as e:
        logger.error(f"Error resetting system: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        })

def register_routes(app):
    """Register Neuronas routes with the Flask app"""
    app.register_blueprint(neuronas_bp)
    logger.info("Neuronas API routes registered")
