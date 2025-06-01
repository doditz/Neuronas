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
"""
This work is licensed under CC BY-NC 4.0 International.
Commercial use requires prior written consent and compensation.
Contact: sebastienbrulotte@gmail.com
Attribution: Sebastien Brulotte aka [ Doditz ]

This document is part of the NEURONAS cognitive system.
Core modules referenced: BRONAS (Ethical Reflex Filter) and QRONAS (Probabilistic Symbolic Vector Engine).
All outputs are subject to integrity validation and ethical compliance enforced by BRONAS.
"""

from flask import Blueprint, request, jsonify, render_template
from google_ai_integration import GoogleAIIntegration
from model_management import ModelManager
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create blueprint
model_bp = Blueprint('model', __name__)

# Initialize integrations
google_ai = GoogleAIIntegration()
model_manager = ModelManager()

@model_bp.route('/models')
def models_page():
    """Main models management page"""
    return render_template('models.html')

@model_bp.route('/api/models/google/status')
def google_ai_status():
    """Get Google AI integration status"""
    try:
        status = google_ai.get_status()
        return jsonify({"success": True, "status": status})
    except Exception as e:
        logger.error(f"Error getting Google AI status: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@model_bp.route('/api/models/google/generate_code', methods=['POST'])
def generate_code():
    """Generate code using Google's Codey model"""
    try:
        data = request.get_json()
        prompt = data.get('prompt', '')
        language = data.get('language', 'python')
        max_tokens = data.get('max_tokens', 2048)
        
        if not prompt:
            return jsonify({"success": False, "error": "Prompt is required"}), 400
        
        # Set D2 parameters if provided
        d2_params = data.get('d2_params', {})
        if d2_params:
            google_ai.set_d2_parameters(**d2_params)
        
        result = google_ai.generate_code(prompt, language, max_tokens)
        
        if result:
            return jsonify({"success": True, "result": result})
        else:
            return jsonify({"success": False, "error": "Code generation failed"}), 500
            
    except Exception as e:
        logger.error(f"Error generating code: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@model_bp.route('/api/models/google/generate_text', methods=['POST'])
def generate_text():
    """Generate text using Google AI models"""
    try:
        data = request.get_json()
        prompt = data.get('prompt', '')
        model = data.get('model', 'gemini-pro')
        max_tokens = data.get('max_tokens', 1024)
        
        if not prompt:
            return jsonify({"success": False, "error": "Prompt is required"}), 400
        
        # Set D2 parameters if provided
        d2_params = data.get('d2_params', {})
        if d2_params:
            google_ai.set_d2_parameters(**d2_params)
        
        result = google_ai.generate_text(prompt, model, max_tokens)
        
        if result:
            return jsonify({"success": True, "result": result})
        else:
            return jsonify({"success": False, "error": "Text generation failed"}), 500
            
    except Exception as e:
        logger.error(f"Error generating text: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@model_bp.route('/api/models/google/set_d2', methods=['POST'])
def set_d2_parameters():
    """Set D2 modulation parameters for Google AI"""
    try:
        data = request.get_json()
        
        activation = data.get('activation')
        creative_balance = data.get('creative_balance')
        stim_level = data.get('stim_level')
        entropy = data.get('entropy')
        
        google_ai.set_d2_parameters(activation, creative_balance, stim_level, entropy)
        
        return jsonify({
            "success": True, 
            "d2_params": google_ai.d2_params
        })
        
    except Exception as e:
        logger.error(f"Error setting D2 parameters: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@model_bp.route('/api/models/list')
def list_models():
    """List available models from all repositories"""
    try:
        ollama_models = model_manager.list_models("ollama")
        huggingface_models = model_manager.list_models("huggingface")
        github_models = model_manager.list_models("github")
        google_models = [
            {"name": "Codey (Code Bison)", "source": "google", "size": "N/A"},
            {"name": "Gemini Pro", "source": "google", "size": "N/A"},
            {"name": "Gemini Pro Vision", "source": "google", "size": "N/A"},
            {"name": "Text Bison", "source": "google", "size": "N/A"}
        ]
        
        return jsonify({
            "success": True,
            "models": {
                "ollama": ollama_models,
                "huggingface": huggingface_models,
                "github": github_models,
                "google": google_models
            }
        })
        
    except Exception as e:
        logger.error(f"Error listing models: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@model_bp.route('/api/models/download', methods=['POST'])
def download_model():
    """Download a model from specified repository"""
    try:
        data = request.get_json()
        model_name = data.get('model_name', '')
        repository = data.get('repository', 'ollama')
        
        if not model_name:
            return jsonify({"success": False, "error": "Model name is required"}), 400
        
        if repository == "google":
            return jsonify({
                "success": False, 
                "error": "Google AI models are accessed via API, no download required"
            }), 400
        
        task_info = model_manager.download_model(model_name, repository)
        
        return jsonify({"success": True, "task": task_info})
        
    except Exception as e:
        logger.error(f"Error downloading model: {e}")
        return jsonify({"success": False, "error": str(e)}), 500
