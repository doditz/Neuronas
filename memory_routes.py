"""
Memory system API routes for the NeuronasX dual hemispheric framework.
"""

import logging
import json
from flask import Blueprint, request, jsonify, current_app, session

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Create a blueprint for memory routes
memory_bp = Blueprint('memory', __name__)

@memory_bp.route('/stats', methods=['GET'])
def get_memory_stats():
    """Get statistics about the tiered memory system."""
    try:
        memory_system = current_app.tiered_memory
        stats = memory_system.get_statistics()
        return jsonify(stats)
    except Exception as e:
        logger.error(f"Error retrieving memory statistics: {e}")
        return jsonify({
            'error': f"Failed to retrieve memory statistics: {str(e)}"
        }), 500

@memory_bp.route('/store/analytical', methods=['POST'])
def store_analytical_memory():
    """Store memory in the analytical (left) hemisphere."""
    data = request.json
    
    if not data or 'key' not in data or 'value' not in data:
        return jsonify({
            'success': False,
            'error': 'Missing required fields (key, value)'
        }), 400
    
    try:
        memory_system = current_app.tiered_memory
        
        # Set the session context if available
        if session.get('session_id'):
            memory_system.memory_manager.set_session_context(session.get('session_id'))
        
        # Store in left hemisphere (analytical)
        importance = float(data.get('score', 0.5))
        context = data.get('context')
        
        success = memory_system.store_analytical_memory(
            data['key'], 
            data['value'], 
            importance=importance,
            context=context
        )
        
        if success:
            return jsonify({'success': True})
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to store memory in analytical hemisphere'
            }), 500
            
    except Exception as e:
        logger.error(f"Error storing analytical memory: {e}")
        return jsonify({
            'success': False,
            'error': f"Error: {str(e)}"
        }), 500

@memory_bp.route('/store/creative', methods=['POST'])
def store_creative_memory():
    """Store memory in the creative (right) hemisphere."""
    data = request.json
    
    if not data or 'key' not in data or 'value' not in data:
        return jsonify({
            'success': False,
            'error': 'Missing required fields (key, value)'
        }), 400
    
    try:
        memory_system = current_app.tiered_memory
        
        # Set the session context if available
        if session.get('session_id'):
            memory_system.memory_manager.set_session_context(session.get('session_id'))
        
        # Store in right hemisphere (creative)
        novelty = float(data.get('score', 0.5))
        d2_activation = float(data.get('d2_activation', 0.5))
        context = data.get('context')
        
        success = memory_system.store_creative_memory(
            data['key'], 
            data['value'], 
            novelty=novelty,
            d2_activation=d2_activation,
            context=context
        )
        
        if success:
            return jsonify({'success': True})
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to store memory in creative hemisphere'
            }), 500
            
    except Exception as e:
        logger.error(f"Error storing creative memory: {e}")
        return jsonify({
            'success': False,
            'error': f"Error: {str(e)}"
        }), 500

@memory_bp.route('/retrieve', methods=['GET'])
def retrieve_memory():
    """Retrieve memory from the specified hemisphere."""
    key = request.args.get('key')
    hemisphere = request.args.get('hemisphere', 'both')
    
    if not key:
        return jsonify({
            'success': False,
            'error': 'Memory key is required'
        }), 400
    
    try:
        memory_system = current_app.tiered_memory
        
        # Retrieve memory
        result = memory_system.retrieve_memory(key, hemisphere)
        
        if result:
            return jsonify({
                'success': True,
                'memory': result
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Memory not found'
            }), 404
            
    except Exception as e:
        logger.error(f"Error retrieving memory: {e}")
        return jsonify({
            'success': False,
            'error': f"Error: {str(e)}"
        }), 500

@memory_bp.route('/search', methods=['GET'])
def search_by_context():
    """Search for memories by context."""
    context_str = request.args.get('context')
    hemisphere = request.args.get('hemisphere', 'both')
    
    if not context_str:
        return jsonify({
            'success': False,
            'error': 'Context is required'
        }), 400
    
    try:
        memory_system = current_app.tiered_memory
        
        # Parse context JSON
        try:
            context = json.loads(context_str)
        except json.JSONDecodeError:
            context = {"raw_context": context_str}
        
        # Generate context hash and search
        context_hash = memory_system.memory_manager.generate_context_hash(context)
        results = memory_system.memory_manager.search_by_context(context_hash, hemisphere)
        
        return jsonify({
            'success': True,
            'results': results
        })
            
    except Exception as e:
        logger.error(f"Error searching memory by context: {e}")
        return jsonify({
            'success': False,
            'error': f"Error: {str(e)}"
        }), 500

@memory_bp.route('/maintenance', methods=['POST'])
def run_maintenance():
    """Manually trigger memory maintenance operations."""
    try:
        memory_system = current_app.tiered_memory
        stats = memory_system.run_manual_maintenance()
        
        return jsonify({
            'success': True,
            'stats': stats
        })
            
    except Exception as e:
        logger.error(f"Error running memory maintenance: {e}")
        return jsonify({
            'success': False,
            'error': f"Error: {str(e)}"
        }), 500