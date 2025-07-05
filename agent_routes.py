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
Routes for agent positioning and SMAS dispatcher functionalities
"""

from flask import Blueprint, request, jsonify, current_app, session
from flask_login import current_user
import logging
from datetime import datetime

# Import positioning components
from smas_dispatcher import SMASDispatcher, PositionType, DispatchMode
from agent_positioning_system import AgentPositioningSystem

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Create blueprint
agent_bp = Blueprint('agent', __name__)

@agent_bp.route('/position', methods=['POST'])
def set_agent_position():
    """Set the agent's position within the system"""
    data = request.json
    
    if not data or 'position' not in data:
        return jsonify({
            'success': False,
            'error': 'Position is required'
        }), 400
        
    position = data.get('position')
    lock_position = data.get('lock_position', False)
    
    try:
        # Ensure we have a positioning system
        if not hasattr(current_app, 'agent_positioning'):
            # Create new positioning system if needed
            current_app.agent_positioning = AgentPositioningSystem(
                dual_llm_system=current_app.dual_llm if hasattr(current_app, 'dual_llm') else None
            )
            
        # Set the position
        success = current_app.agent_positioning.set_position(position, lock_position)
        
        if success:
            # Get updated state
            state = current_app.agent_positioning.get_positioning_state()
            
            return jsonify({
                'success': True,
                'message': f'Agent position set to {position}',
                'state': state
            })
        else:
            return jsonify({
                'success': False,
                'error': f'Invalid position: {position}'
            }), 400
            
    except Exception as e:
        logger.error(f"Error setting agent position: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@agent_bp.route('/state', methods=['GET'])
def get_agent_state():
    """Get the current state of the agent positioning system"""
    try:
        # Ensure we have a positioning system
        if not hasattr(current_app, 'agent_positioning'):
            # Create new positioning system
            current_app.agent_positioning = AgentPositioningSystem(
                dual_llm_system=current_app.dual_llm if hasattr(current_app, 'dual_llm') else None
            )
            
        # Get the state
        state = current_app.agent_positioning.get_positioning_state()
        
        return jsonify({
            'success': True,
            'state': state,
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error getting agent state: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@agent_bp.route('/process', methods=['POST'])
def process_with_agent():
    """Process a query through the agent positioning system"""
    data = request.json
    
    if not data or 'query' not in data:
        return jsonify({
            'success': False,
            'error': 'Query is required'
        }), 400
        
    query = data.get('query')
    context = data.get('context')
    
    try:
        # Ensure we have a positioning system
        if not hasattr(current_app, 'agent_positioning'):
            # Create new positioning system
            current_app.agent_positioning = AgentPositioningSystem(
                dual_llm_system=current_app.dual_llm if hasattr(current_app, 'dual_llm') else None
            )
            
        # Process the query
        result = current_app.agent_positioning.process_with_positioning(query, context)
        
        # Log the query if successful
        if result.get('success'):
            try:
                # Create a query log
                from database import db
from models import QueryLog
                
                # Get agent position
                position = result.get('agent_position', 'central')
                
                # Get hemisphere used
                hemisphere_used = result.get('hemisphere_used', 'C')
                
                # Determine query type based on position and hemisphere
                if position == 'left' or hemisphere_used == 'L':
                    query_type = 'analytical'
                elif position == 'right' or hemisphere_used == 'R':
                    query_type = 'creative'
                else:
                    query_type = 'balanced'
                
                # Create and save query log
                query_log = QueryLog(
                    query=query,
                    response=result.get('response', ''),
                    query_type=query_type,
                    hemisphere_used=hemisphere_used,
                    processing_time=result.get('processing_time', 0),
                    d2_activation=result.get('d2_activation', 0.5),
                    session_id=session.get('session_id'),
                    user_id=current_user.id if current_user.is_authenticated else None
                )
                db.session.add(query_log)
                db.session.commit()
            except Exception as e:
                logger.error(f"Error logging query: {e}")
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error processing with agent: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@agent_bp.route('/smas/state', methods=['GET'])
def get_smas_state():
    """Get the current state of the SMAS dispatcher"""
    try:
        # Ensure we have a positioning system
        if not hasattr(current_app, 'agent_positioning'):
            # Create new positioning system
            current_app.agent_positioning = AgentPositioningSystem(
                dual_llm_system=current_app.dual_llm if hasattr(current_app, 'dual_llm') else None
            )
            
        # Get SMAS state
        smas_state = current_app.agent_positioning.smas.get_system_state()
        
        return jsonify({
            'success': True,
            'state': smas_state,
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error getting SMAS state: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@agent_bp.route('/smas/mode', methods=['POST'])
def set_smas_mode():
    """Set the SMAS dispatcher mode"""
    data = request.json
    
    if not data or 'mode' not in data:
        return jsonify({
            'success': False,
            'error': 'Mode is required'
        }), 400
        
    mode = data.get('mode')
    
    try:
        # Ensure we have a positioning system
        if not hasattr(current_app, 'agent_positioning'):
            # Create new positioning system
            current_app.agent_positioning = AgentPositioningSystem(
                dual_llm_system=current_app.dual_llm if hasattr(current_app, 'dual_llm') else None
            )
            
        # Set the mode
        success = current_app.agent_positioning.smas.set_dispatch_mode(mode)
        
        if success:
            # Get updated state
            state = current_app.agent_positioning.smas.get_system_state()
            
            return jsonify({
                'success': True,
                'message': f'SMAS dispatch mode set to {mode}',
                'state': state
            })
        else:
            return jsonify({
                'success': False,
                'error': f'Invalid mode: {mode}'
            }), 400
            
    except Exception as e:
        logger.error(f"Error setting SMAS mode: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@agent_bp.route('/smas/module', methods=['POST'])
def toggle_smas_module():
    """Toggle a SMAS module"""
    data = request.json
    
    if not data or 'module' not in data:
        return jsonify({
            'success': False,
            'error': 'Module name is required'
        }), 400
        
    module = data.get('module')
    active = data.get('active')
    
    try:
        # Ensure we have a positioning system
        if not hasattr(current_app, 'agent_positioning'):
            # Create new positioning system
            current_app.agent_positioning = AgentPositioningSystem(
                dual_llm_system=current_app.dual_llm if hasattr(current_app, 'dual_llm') else None
            )
            
        # Toggle the module
        success = current_app.agent_positioning.smas.toggle_module(module, active)
        
        if success:
            # Get updated state
            state = current_app.agent_positioning.smas.get_system_state()
            
            status = "activated" if state['active_modules'].get(module, False) else "deactivated"
            
            return jsonify({
                'success': True,
                'message': f'Module {module} {status}',
                'state': state
            })
        else:
            return jsonify({
                'success': False,
                'error': f'Invalid module: {module}'
            }), 400
            
    except Exception as e:
        logger.error(f"Error toggling SMAS module: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500