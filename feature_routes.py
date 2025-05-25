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
API Routes for NeuronasX Features

This module provides API routes for BRONAS ethics, geolocation adaptation,
session transparency, and progress tracking features.
"""

from flask import Blueprint, request, jsonify, session, current_app
import logging
import uuid
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Create blueprints
bronas_bp = Blueprint('bronas', __name__, url_prefix='/api/bronas')
geo_bp = Blueprint('geolocation', __name__, url_prefix='/api/geolocation')
session_bp = Blueprint('session', __name__, url_prefix='/api/session')
progress_bp = Blueprint('progress', __name__, url_prefix='/api/progress')

# --------------------------------
# BRONAS Ethics Repository Routes
# --------------------------------

@bronas_bp.route('/principles', methods=['GET'])
def get_principles():
    """Get ethical principles from the BRONAS repository"""
    try:
        # Initialize BRONAS if needed
        if not hasattr(current_app, 'bronas'):
            from bronas_ethics import BRONASEthicsRepository
            from models import db
            current_app.bronas = BRONASEthicsRepository(db)
            
        # Get parameters
        category = request.args.get('category')
        min_confidence = request.args.get('min_confidence', 0.0, type=float)
        limit = request.args.get('limit', 20, type=int)
        
        # Get principles
        principles = current_app.bronas.get_principles(
            category=category,
            min_confidence=min_confidence,
            limit=limit
        )
        
        return jsonify({
            'success': True,
            'principles': principles
        })
        
    except Exception as e:
        logger.error(f"Error getting principles: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
        
@bronas_bp.route('/add', methods=['POST'])
def add_principle():
    """Add a new ethical principle to the BRONAS repository"""
    try:
        # Get request data
        data = request.json
        
        if not data or 'hypothesis' not in data:
            return jsonify({
                'success': False,
                'error': 'Hypothesis is required'
            }), 400
            
        # Get parameters
        hypothesis = data.get('hypothesis')
        confidence = data.get('confidence', 0.5)
        category = data.get('category', 'general')
        
        # Get user ID if authenticated
        from flask_login import current_user
        user_id = current_user.id if hasattr(current_user, 'id') and current_user.is_authenticated else None
        
        # Initialize BRONAS if needed
        if not hasattr(current_app, 'bronas'):
            from bronas_ethics import BRONASEthicsRepository
            from models import db
            current_app.bronas = BRONASEthicsRepository(db)
            
        # Add principle
        principle = current_app.bronas.add_principle(
            hypothesis=hypothesis,
            confidence=confidence,
            category=category,
            user_id=user_id
        )
        
        return jsonify({
            'success': True,
            'principle': principle
        })
        
    except Exception as e:
        logger.error(f"Error adding principle: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
        
@bronas_bp.route('/evaluate', methods=['POST'])
def evaluate_statement():
    """Evaluate a statement against ethical principles"""
    try:
        # Get request data
        data = request.json
        
        if not data or 'statement' not in data:
            return jsonify({
                'success': False,
                'error': 'Statement is required'
            }), 400
            
        # Get parameters
        statement = data.get('statement')
        session_id = session.get('session_id', str(uuid.uuid4()))
        
        # Initialize BRONAS if needed
        if not hasattr(current_app, 'bronas'):
            from bronas_ethics import BRONASEthicsRepository
            from models import db
            current_app.bronas = BRONASEthicsRepository(db)
            
        # Evaluate statement
        evaluation = current_app.bronas.evaluate_statement(
            statement=statement,
            session_id=session_id
        )
        
        return jsonify({
            'success': True,
            'evaluation': evaluation
        })
        
    except Exception as e:
        logger.error(f"Error evaluating statement: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
        
@bronas_bp.route('/stats', methods=['GET'])
def get_stats():
    """Get statistics about the BRONAS ethics repository"""
    try:
        # Initialize BRONAS if needed
        if not hasattr(current_app, 'bronas'):
            from bronas_ethics import BRONASEthicsRepository
            from models import db
            current_app.bronas = BRONASEthicsRepository(db)
            
        # Get statistics
        stats = current_app.bronas.get_statistics()
        
        return jsonify({
            'success': True,
            'stats': stats
        })
        
    except Exception as e:
        logger.error(f"Error getting BRONAS stats: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# --------------------------------
# Geolocation Adaptation Routes
# --------------------------------

@geo_bp.route('/info', methods=['GET'])
def get_cultural_info():
    """Get cultural context information based on location"""
    try:
        # Get country code from query parameter or detect from IP
        country_code = request.args.get('country')
        
        # Initialize geolocation service if needed
        if not hasattr(current_app, 'geolocation'):
            from geolocation_service import GeolocationService
            current_app.geolocation = GeolocationService()
            
        # Get cultural context
        cultural_data = current_app.geolocation.get_cultural_context(country_code)
        
        return jsonify({
            'success': True,
            'country_code': cultural_data.get('country_code'),
            'context': cultural_data.get('context')
        })
        
    except Exception as e:
        logger.error(f"Error getting cultural info: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
        
@geo_bp.route('/adapt', methods=['POST'])
def adapt_response():
    """Adapt a response based on cultural context"""
    try:
        # Get request data
        data = request.json
        
        if not data or 'response' not in data:
            return jsonify({
                'success': False,
                'error': 'Response text is required'
            }), 400
            
        # Get parameters
        response_text = data.get('response')
        country_code = data.get('country_code')
        
        # Initialize geolocation service if needed
        if not hasattr(current_app, 'geolocation'):
            from geolocation_service import GeolocationService
            current_app.geolocation = GeolocationService()
            
        # Adapt response
        adapted = current_app.geolocation.adapt_response(
            response=response_text,
            country_code=country_code
        )
        
        return jsonify({
            'success': True,
            'adaptation': adapted
        })
        
    except Exception as e:
        logger.error(f"Error adapting response: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# --------------------------------
# Session Transparency Routes
# --------------------------------

@session_bp.route('/info', methods=['GET'])
def get_session_info():
    """Get information about the current session"""
    try:
        # Initialize session transparency if needed
        if not hasattr(current_app, 'session_transparency'):
            from session_transparency import SessionTransparency
            from models import db
            current_app.session_transparency = SessionTransparency(db)
            
        # Get or create session ID
        session_id = session.get('session_id')
        
        if not session_id:
            # Create a new session
            source_info = {
                'ip': request.remote_addr,
                'user_agent': request.headers.get('User-Agent', '')
            }
            
            session_info = current_app.session_transparency.create_session(
                source_info=source_info
            )
            
            # Store session ID in Flask session
            session['session_id'] = session_info['session_id']
            session_id = session_info['session_id']
            
            return jsonify({
                'success': True,
                'session_id': session_id,
                'created_at': session_info['created_at'],
                'expiry': session_info['expiry'],
                'session_hash': session_info['session_hash'],
                'new_session': True
            })
        else:
            # Get existing session
            session_info = current_app.session_transparency.get_session_info(session_id)
            
            if not session_info:
                # Session not found or expired, create a new one
                source_info = {
                    'ip': request.remote_addr,
                    'user_agent': request.headers.get('User-Agent', '')
                }
                
                session_info = current_app.session_transparency.create_session(
                    source_info=source_info
                )
                
                # Store session ID in Flask session
                session['session_id'] = session_info['session_id']
                session_id = session_info['session_id']
                
                return jsonify({
                    'success': True,
                    'session_id': session_id,
                    'created_at': session_info['created_at'],
                    'expiry': session_info['expiry'],
                    'session_hash': session_info['session_hash'],
                    'new_session': True
                })
            
            return jsonify({
                'success': True,
                'session_id': session_id,
                'created_at': session_info['created_at'],
                'last_activity': session_info['last_activity'],
                'expiry': session_info['expiry'],
                'interaction_count': session_info['interaction_count'],
                'session_hash': session_info['session_hash'],
                'new_session': False
            })
            
    except Exception as e:
        logger.error(f"Error getting session info: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
        
@session_bp.route('/interactions', methods=['GET'])
def get_session_interactions():
    """Get interactions for the current session"""
    try:
        # Initialize session transparency if needed
        if not hasattr(current_app, 'session_transparency'):
            from session_transparency import SessionTransparency
            from models import db
            current_app.session_transparency = SessionTransparency(db)
            
        # Get session ID
        session_id = session.get('session_id')
        
        if not session_id:
            return jsonify({
                'success': False,
                'error': 'No active session'
            }), 400
            
        # Get limit parameter
        limit = request.args.get('limit', 20, type=int)
        
        # Get interactions
        interactions = current_app.session_transparency.get_session_interactions(
            session_id=session_id,
            limit=limit
        )
        
        return jsonify({
            'success': True,
            'session_id': session_id,
            'interactions': interactions
        })
        
    except Exception as e:
        logger.error(f"Error getting session interactions: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
        
@session_bp.route('/record', methods=['POST'])
def record_interaction():
    """Record an interaction with the system"""
    try:
        # Get request data
        data = request.json
        
        if not data or 'interaction_type' not in data:
            return jsonify({
                'success': False,
                'error': 'Interaction type is required'
            }), 400
            
        # Get parameters
        interaction_type = data.get('interaction_type')
        interaction_data = data.get('data')
        system_components = data.get('system_components')
        
        # Initialize session transparency if needed
        if not hasattr(current_app, 'session_transparency'):
            from session_transparency import SessionTransparency
            from models import db
            current_app.session_transparency = SessionTransparency(db)
            
        # Get session ID
        session_id = session.get('session_id')
        
        if not session_id:
            # Create a new session
            source_info = {
                'ip': request.remote_addr,
                'user_agent': request.headers.get('User-Agent', '')
            }
            
            session_info = current_app.session_transparency.create_session(
                source_info=source_info
            )
            
            # Store session ID in Flask session
            session['session_id'] = session_info['session_id']
            session_id = session_info['session_id']
            
        # Record interaction
        interaction = current_app.session_transparency.record_interaction(
            session_id=session_id,
            interaction_type=interaction_type,
            data=interaction_data,
            system_components=system_components
        )
        
        return jsonify({
            'success': True,
            'interaction': interaction
        })
        
    except Exception as e:
        logger.error(f"Error recording interaction: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# --------------------------------
# Progress Tracking Routes
# --------------------------------

@progress_bp.route('/summary', methods=['GET'])
def get_progress_summary():
    """Get a summary of project progress"""
    try:
        # Initialize progress tracker if needed
        if not hasattr(current_app, 'progress_tracker'):
            from progress_tracker import ProgressTracker
            current_app.progress_tracker = ProgressTracker()
            
        # Get summary
        summary = current_app.progress_tracker.get_progress_summary()
        
        return jsonify({
            'success': True,
            'summary': summary
        })
        
    except Exception as e:
        logger.error(f"Error getting progress summary: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
        
@progress_bp.route('/roadmap', methods=['GET'])
def get_roadmap():
    """Get the project roadmap"""
    try:
        # Initialize progress tracker if needed
        if not hasattr(current_app, 'progress_tracker'):
            from progress_tracker import ProgressTracker
            current_app.progress_tracker = ProgressTracker()
            
        # Get roadmap
        roadmap = current_app.progress_tracker.get_roadmap()
        
        return jsonify({
            'success': True,
            'roadmap': roadmap
        })
        
    except Exception as e:
        logger.error(f"Error getting roadmap: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
        
@progress_bp.route('/changes', methods=['GET'])
def get_changes():
    """Get logged changes to the system"""
    try:
        # Initialize progress tracker if needed
        if not hasattr(current_app, 'progress_tracker'):
            from progress_tracker import ProgressTracker
            current_app.progress_tracker = ProgressTracker()
            
        # Get parameters
        component = request.args.get('component')
        change_type = request.args.get('change_type')
        limit = request.args.get('limit', 20, type=int)
        
        # Get changes
        changes = current_app.progress_tracker.get_changes(
            component=component,
            change_type=change_type,
            limit=limit
        )
        
        return jsonify({
            'success': True,
            'changes': changes
        })
        
    except Exception as e:
        logger.error(f"Error getting changes: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# Add route to view the BRONAS interface
def register_routes(app):
    """Register feature routes with the application"""
    from flask import render_template
    
    # Register blueprints
    app.register_blueprint(bronas_bp)
    app.register_blueprint(geo_bp)
    app.register_blueprint(session_bp)
    app.register_blueprint(progress_bp)
    
    # Add route for BRONAS view
    @app.route('/bronas')
    def bronas_view():
        """View the BRONAS ethics repository"""
        return render_template('bronas_view.html')
        
    return app