"""
Perplexity API routes for Flask integration
==========================================

Flask routes for Perplexity AI research and reasoning capabilities.
"""

from flask import Blueprint, request, jsonify
import time
import logging

logger = logging.getLogger(__name__)

def integrate_perplexity_routes(app):
    """Integrate Perplexity API routes into Flask app"""
    
    try:
        from perplexity_integration import PerplexityAPI
        from simple_secure_keys import NeuronasKeyManager
        
        # Create blueprint
        perplexity_bp = Blueprint('perplexity', __name__, url_prefix='/api/perplexity')
        
        @perplexity_bp.route('/research', methods=['POST'])
        def research():
            """Research endpoint using Perplexity AI"""
            try:
                data = request.get_json()
                if not data:
                    return jsonify({'success': False, 'error': 'No JSON data provided'}), 400
                
                query = data.get('query', '').strip()
                if not query:
                    return jsonify({'success': False, 'error': 'Query is required'}), 400
                
                model = data.get('model', 'fast')  # fast, pro, or reasoning
                
                # Get API key
                key_manager = NeuronasKeyManager()
                api_key = key_manager.get_api_key('perplexity')
                
                if not api_key:
                    return jsonify({
                        'success': False, 
                        'error': 'Perplexity API key not configured. Please set it up first.'
                    }), 401
                
                # Initialize Perplexity API
                perplexity = PerplexityAPI(api_key)
                
                # Make request
                start_time = time.time()
                response = perplexity.research(query, model=model)
                processing_time = time.time() - start_time
                
                return jsonify({
                    'success': True,
                    'response': response,
                    'model_used': model,
                    'processing_time': processing_time,
                    'query': query
                })
                
            except Exception as e:
                logger.error(f"Perplexity research error: {e}")
                return jsonify({
                    'success': False,
                    'error': f'Research failed: {str(e)}'
                }), 500
        
        @perplexity_bp.route('/models', methods=['GET'])
        def get_models():
            """Get available Perplexity models"""
            return jsonify({
                'success': True,
                'models': {
                    'fast': {
                        'name': 'sonar',
                        'description': 'Fast web search and reasoning'
                    },
                    'pro': {
                        'name': 'sonar-pro',
                        'description': 'Enhanced reasoning with web search'
                    },
                    'reasoning': {
                        'name': 'sonar-reasoning',
                        'description': 'Advanced reasoning capabilities'
                    }
                }
            })
        
        @perplexity_bp.route('/status', methods=['GET'])
        def get_status():
            """Check Perplexity API status"""
            try:
                key_manager = NeuronasKeyManager()
                api_key = key_manager.get_api_key('perplexity')
                
                return jsonify({
                    'success': True,
                    'configured': bool(api_key),
                    'service': 'Perplexity AI'
                })
                
            except Exception as e:
                return jsonify({
                    'success': False,
                    'error': str(e)
                }), 500
        
        # Register blueprint
        app.register_blueprint(perplexity_bp)
        logger.info("✅ Perplexity routes registered successfully")
        
    except ImportError as e:
        logger.warning(f"Perplexity integration not available: {e}")
        
        # Create placeholder blueprint
        perplexity_bp = Blueprint('perplexity', __name__, url_prefix='/api/perplexity')
        
        @perplexity_bp.route('/research', methods=['POST'])
        def research_placeholder():
            return jsonify({
                'success': False,
                'error': 'Perplexity integration not available. Please check perplexity_integration.py'
            }), 503
        
        app.register_blueprint(perplexity_bp)
        logger.warning("⚠️ Perplexity placeholder routes registered")

@perplexity_bp.route('/status', methods=['GET'])
def perplexity_status():
    """Check Perplexity API status"""
    if not PERPLEXITY_AVAILABLE:
        return jsonify({
            'available': False,
            'error': 'Perplexity integration not installed'
        }), 503
    
    return jsonify({
        'available': perplexity.is_available(),
        'models': list(perplexity.models.keys()) if perplexity.is_available() else [],
        'status': 'ready' if perplexity.is_available() else 'api_key_needed'
    })

@perplexity_bp.route('/research', methods=['POST'])
def research_query():
    """Perform a research query using Perplexity"""
    if not PERPLEXITY_AVAILABLE or not perplexity.is_available():
        return jsonify({
            'success': False,
            'error': 'Perplexity API not available'
        }), 503
    
    try:
        data = request.get_json()
        
        if not data or 'query' not in data:
            return jsonify({
                'success': False,
                'error': 'Query parameter required'
            }), 400
        
        query = data['query']
        model = data.get('model', 'balanced')
        max_tokens = data.get('max_tokens', 1000)
        temperature = data.get('temperature', 0.2)
        
        # Perform the research query
        result = perplexity.research_query(
            query=query,
            model=model,
            max_tokens=max_tokens,
            temperature=temperature
        )
        
        # Log the query for session tracking
        if 'user_id' in session:
            logger.info(f"Perplexity research query by user {session['user_id']}: {query[:100]}...")
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Research query error: {e}")
        return jsonify({
            'success': False,
            'error': f'Internal error: {str(e)}'
        }), 500

@perplexity_bp.route('/reasoning', methods=['POST'])
def complex_reasoning():
    """Perform complex reasoning task"""
    if not PERPLEXITY_AVAILABLE or not perplexity.is_available():
        return jsonify({
            'success': False,
            'error': 'Perplexity API not available'
        }), 503
    
    try:
        data = request.get_json()
        
        if not data or 'problem' not in data:
            return jsonify({
                'success': False,
                'error': 'Problem parameter required'
            }), 400
        
        problem = data['problem']
        context = data.get('context')
        reasoning_type = data.get('reasoning_type', 'analytical')
        
        # Perform complex reasoning
        result = perplexity.complex_reasoning(
            problem=problem,
            context=context,
            reasoning_type=reasoning_type
        )
        
        # Log the reasoning request
        if 'user_id' in session:
            logger.info(f"Complex reasoning by user {session['user_id']}: {reasoning_type} - {problem[:100]}...")
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Complex reasoning error: {e}")
        return jsonify({
            'success': False,
            'error': f'Internal error: {str(e)}'
        }), 500

@perplexity_bp.route('/multi-perspective', methods=['POST'])
def multi_perspective_analysis():
    """Analyze topic from multiple perspectives"""
    if not PERPLEXITY_AVAILABLE or not perplexity.is_available():
        return jsonify({
            'success': False,
            'error': 'Perplexity API not available'
        }), 503
    
    try:
        data = request.get_json()
        
        if not data or 'topic' not in data:
            return jsonify({
                'success': False,
                'error': 'Topic parameter required'
            }), 400
        
        topic = data['topic']
        perspectives = data.get('perspectives')
        
        # Perform multi-perspective analysis
        result = perplexity.multi_perspective_analysis(
            topic=topic,
            perspectives=perspectives
        )
        
        # Log the analysis request
        if 'user_id' in session:
            logger.info(f"Multi-perspective analysis by user {session['user_id']}: {topic[:100]}...")
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Multi-perspective analysis error: {e}")
        return jsonify({
            'success': False,
            'error': f'Internal error: {str(e)}'
        }), 500

@perplexity_bp.route('/fact-check', methods=['POST'])
def fact_check():
    """Fact-check and verify claims"""
    if not PERPLEXITY_AVAILABLE or not perplexity.is_available():
        return jsonify({
            'success': False,
            'error': 'Perplexity API not available'
        }), 503
    
    try:
        data = request.get_json()
        
        if not data or 'claim' not in data:
            return jsonify({
                'success': False,
                'error': 'Claim parameter required'
            }), 400
        
        claim = data['claim']
        context = data.get('context')
        
        # Perform fact-checking
        result = perplexity.fact_check_and_verify(
            claim=claim,
            context=context
        )
        
        # Log the fact-check request
        if 'user_id' in session:
            logger.info(f"Fact-check by user {session['user_id']}: {claim[:100]}...")
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Fact-check error: {e}")
        return jsonify({
            'success': False,
            'error': f'Internal error: {str(e)}'
        }), 500

@perplexity_bp.route('/models', methods=['GET'])
def get_available_models():
    """Get list of available Perplexity models"""
    if not PERPLEXITY_AVAILABLE or not perplexity.is_available():
        return jsonify({
            'success': False,
            'error': 'Perplexity API not available'
        }), 503
    
    return jsonify({
        'success': True,
        'models': perplexity.models,
        'default': 'balanced'
    })

# Integration function for main app
def integrate_perplexity_routes(app, memory_system=None):
    """
    Integrate Perplexity routes with the main Flask app
    
    Args:
        app: Flask application instance
        memory_system: Optional memory system for storing interactions
    """
    # Register the blueprint
    app.register_blueprint(perplexity_bp)
    
    # Store integration info
    if PERPLEXITY_AVAILABLE and perplexity and perplexity.is_available():
        app.perplexity = perplexity
        logger.info("✅ Perplexity routes integrated successfully")
        
        # Store in memory system if available
        if memory_system and hasattr(memory_system, 'store_L1'):
            memory_system.store_L1(
                'perplexity_routes_status',
                'Perplexity API routes active and ready',
                importance=0.8
            )
    else:
        logger.warning("⚠️  Perplexity routes registered but API not available")

# Example usage for development
def test_perplexity_routes():
    """Test function for development"""
    if not PERPLEXITY_AVAILABLE:
        print("❌ Perplexity integration not available")
        return False
    
    if not perplexity.is_available():
        print("⚠️  Perplexity routes work but API key needed")
        return True
    
    # Test a simple query
    result = perplexity.research_query("Test query for route integration")
    
    if result['success']:
        print("✅ Perplexity routes working correctly")
        return True
    else:
        print(f"❌ Perplexity routes test failed: {result['error']}")
        return False

if __name__ == "__main__":
    test_perplexity_routes()
