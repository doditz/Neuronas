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
Model Management Routes for NeuronasX

This module provides API routes for model management operations
including listing, downloading, and deleting models from various repositories.
"""

from flask import Blueprint, request, jsonify, current_app
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Create blueprint
models_bp = Blueprint('models', __name__, url_prefix='/api/models')

@models_bp.route('/list', methods=['GET'])
def list_models():
    """List available models from the specified repository"""
    try:
        # Get repository parameter
        repository = request.args.get('repository', 'ollama')
        
        # Initialize model manager if needed
        if not hasattr(current_app, 'model_manager'):
            from model_management import ModelManager
            current_app.model_manager = ModelManager()
        
        # Get models
        models = current_app.model_manager.list_models(repository)
        
        return jsonify({
            'success': True,
            'repository': repository,
            'models': models
        })
    
    except Exception as e:
        logger.error(f"Error listing models: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@models_bp.route('/download', methods=['POST'])
def download_model():
    """Download a model from the specified repository"""
    try:
        # Get request data
        data = request.json
        
        if not data or 'model_name' not in data:
            return jsonify({
                'success': False,
                'error': 'Model name is required'
            }), 400
        
        # Get parameters
        model_name = data.get('model_name')
        repository = data.get('repository', 'ollama')
        
        # Initialize model manager if needed
        if not hasattr(current_app, 'model_manager'):
            from model_management import ModelManager
            current_app.model_manager = ModelManager()
        
        # Download model
        task_info = current_app.model_manager.download_model(model_name, repository)
        
        return jsonify({
            'success': True,
            'task_id': task_info['task_id'],
            'model_name': model_name,
            'repository': repository,
            'status': task_info['status']
        })
    
    except Exception as e:
        logger.error(f"Error downloading model: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@models_bp.route('/status/<task_id>', methods=['GET'])
def get_download_status(task_id):
    """Get the status of a model download task"""
    try:
        # Initialize model manager if needed
        if not hasattr(current_app, 'model_manager'):
            from model_management import ModelManager
            current_app.model_manager = ModelManager()
        
        # Get task status
        task_info = current_app.model_manager.get_download_status(task_id)
        
        if not task_info:
            return jsonify({
                'success': False,
                'error': 'Task not found'
            }), 404
        
        return jsonify({
            'success': True,
            'task_id': task_id,
            'model_name': task_info['model_name'],
            'repository': task_info['repository'],
            'status': task_info['status'],
            'progress': task_info['progress'],
            'start_time': task_info['start_time'],
            'end_time': task_info['end_time'],
            'error': task_info['error']
        })
    
    except Exception as e:
        logger.error(f"Error getting download status: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@models_bp.route('/delete', methods=['POST'])
def delete_model():
    """Delete a model"""
    try:
        # Get request data
        data = request.json
        
        if not data or 'model_name' not in data:
            return jsonify({
                'success': False,
                'error': 'Model name is required'
            }), 400
        
        # Get parameters
        model_name = data.get('model_name')
        repository = data.get('repository', 'ollama')
        
        # Initialize model manager if needed
        if not hasattr(current_app, 'model_manager'):
            from model_management import ModelManager
            current_app.model_manager = ModelManager()
        
        # Delete model
        success = current_app.model_manager.delete_model(model_name, repository)
        
        if not success:
            return jsonify({
                'success': False,
                'error': 'Failed to delete model'
            }), 500
        
        return jsonify({
            'success': True,
            'model_name': model_name,
            'repository': repository
        })
    
    except Exception as e:
        logger.error(f"Error deleting model: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

def register_model_routes(app):
    """Register model routes with the application"""
    app.register_blueprint(models_bp)
    
    # Add route for advanced mobile interface
    @app.route('/mobile')
    def advanced_mobile():
        """View the advanced mobile interface"""
        from flask import render_template
        return render_template('advanced_mobile.html')
    
    @app.route('/architecture')
    def architecture_view():
        """View the Neuronas architecture details"""
        from flask import render_template
        return render_template('architecture.html')
    
    @app.route('/asimov')
    def asimov_view():
        """View the Neuronas Asimov directives"""
        from flask import render_template
        return render_template('asimov_directives.html')
    
    return app