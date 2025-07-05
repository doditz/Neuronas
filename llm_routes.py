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
Routes for the dual LLM system with hemispheric processing
"""

from flask import Blueprint, request, jsonify, current_app, session
from flask_login import current_user
import logging
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Create blueprint
llm_bp = Blueprint('llm', __name__)

@llm_bp.route('/process', methods=['POST'])
def process_with_dual_llm():
    """
    Process a query through the dual LLM system with hemispheric processing
    """
    data = request.json
    query = data.get('query')
    
    if not query:
        return jsonify({
            'success': False,
            'error': 'Query is required'
        }), 400
    
    # Get user settings if available
    user_settings = None
    if current_user.is_authenticated:
        user_settings = {
            'd2_activation': getattr(current_user, 'd2_temperature', 0.5),
            'hemisphere_balance': getattr(current_user, 'hemisphere_balance', 0.5),
            'creativity_weight': getattr(current_user, 'creativity_weight', 0.5),
            'analytical_weight': getattr(current_user, 'analytical_weight', 0.5)
        }
    
    # Get optional parameters
    d2_activation = data.get('d2_activation', 
                          user_settings.get('d2_activation', 0.5) if user_settings else 0.5)
    hemisphere_balance = data.get('hemisphere_balance', 
                               user_settings.get('hemisphere_balance', 0.5) if user_settings else 0.5)
    simulation_mode = data.get('simulation_mode', True)  # Default to simulation mode enabled
    ollama_url = data.get('ollama_url', 'http://localhost:11434')
    
    # Get model selection parameters
    left_model = data.get('left_model', 'nous-hermes2:7b')
    right_model = data.get('right_model', 'mixtral:latest')
    central_model = data.get('central_model', 'gemma:7b')
    left_persona = data.get('left_persona', 'Cognitiva')
    right_persona = data.get('right_persona', 'Metaphysica')
    model_focus = data.get('model_focus', 'Balanced')
    
    # Process through dual LLM system
    try:
        # Set D2 activation and hemisphere balance
        current_app.dual_llm.set_d2_activation(d2_activation)
        current_app.dual_llm.set_hemisphere_balance(hemisphere_balance)
        
        # Update Ollama URL and simulation mode
        if hasattr(current_app.dual_llm, 'set_simulation_mode'):
            current_app.dual_llm.set_simulation_mode(simulation_mode)
            
        if hasattr(current_app.dual_llm, 'set_ollama_url'):
            current_app.dual_llm.set_ollama_url(ollama_url)
            
        # Set model selections if the methods exist
        if hasattr(current_app.dual_llm, 'set_left_model'):
            current_app.dual_llm.set_left_model(left_model, left_persona)
            
        if hasattr(current_app.dual_llm, 'set_right_model'):
            current_app.dual_llm.set_right_model(right_model, right_persona)
            
        if hasattr(current_app.dual_llm, 'set_central_model'):
            current_app.dual_llm.set_central_model(central_model)
        
        # Process the query
        result = current_app.dual_llm.process_query(
            query,
            user_settings=user_settings
        )
        
        # Log query if successful
        if result.get('success'):
            try:
                # Create a query log
                from database import db
from models import QueryLog
                
                # Get hemisphere used
                hemisphere_used = 'C'  # Central/integrated by default
                if result.get('hemisphere_balance', 0.5) < 0.3:
                    hemisphere_used = 'L'  # Left-dominant
                elif result.get('hemisphere_balance', 0.5) > 0.7:
                    hemisphere_used = 'R'  # Right-dominant
                
                # Determine query type
                if hemisphere_used == 'L':
                    query_type = 'analytical'
                elif hemisphere_used == 'R':
                    query_type = 'creative'
                else:
                    query_type = 'integrated'
                
                # Calculate processing time
                processing_time = result.get('integrated_processing', {}).get('total_processing_time', 0)
                
                # Create and save query log
                query_log = QueryLog(
                    query=query,
                    response=result.get('response', ''),
                    query_type=query_type,
                    hemisphere_used=hemisphere_used,
                    processing_time=processing_time,
                    d2_activation=d2_activation,
                    session_id=session.get('session_id'),
                    user_id=current_user.id if current_user.is_authenticated else None
                )
                db.session.add(query_log)
                db.session.commit()
            except Exception as e:
                logger.error(f"Error logging query: {e}")
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error processing with dual LLM: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@llm_bp.route('/state', methods=['GET'])
def get_llm_state():
    """Get the current state of the dual LLM system"""
    try:
        state = current_app.dual_llm.get_system_state()
        return jsonify({
            'success': True,
            'state': state,
            'timestamp': datetime.utcnow().isoformat()
        })
    except Exception as e:
        logger.error(f"Error getting LLM state: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@llm_bp.route('/set_parameters', methods=['POST'])
def set_llm_parameters():
    """Set parameters for the dual LLM system"""
    data = request.json
    
    try:
        # Update D2 activation if provided
        if 'd2_activation' in data:
            d2_activation = float(data['d2_activation'])
            current_app.dual_llm.set_d2_activation(d2_activation)
            
        # Update hemisphere balance if provided
        if 'hemisphere_balance' in data:
            hemisphere_balance = float(data['hemisphere_balance'])
            current_app.dual_llm.set_hemisphere_balance(hemisphere_balance)
            
        # Get updated state
        state = current_app.dual_llm.get_system_state()
        
        # If user is authenticated, save preferences
        if current_user.is_authenticated:
            try:
                if 'd2_activation' in data:
                    current_user.d2_temperature = d2_activation
                    
                if 'hemisphere_balance' in data:
                    current_user.hemisphere_balance = hemisphere_balance
                    
                from database import db
                db.session.commit()
            except Exception as e:
                logger.error(f"Error saving user preferences: {e}")
        
        return jsonify({
            'success': True,
            'state': state,
            'message': 'Parameters updated successfully'
        })
        
    except Exception as e:
        logger.error(f"Error setting LLM parameters: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500