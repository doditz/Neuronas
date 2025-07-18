"""
Local Authentication Module for Neuronas
========================================

This module provides simple local authentication for the Neuronas system
without requiring external services like Replit or OAuth providers.
"""

import logging
from functools import wraps
from flask import session, g, current_app

# Set up logging
logger = logging.getLogger(__name__)

def require_login(f):
    """
    Simple local authentication decorator
    Creates a local user session if none exists
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            # Create a default local user session
            session['user_id'] = 'local_user'
            session['username'] = 'Local User'
            session['is_admin'] = True
            logger.info("Created local user session")
        
        # Set user in g for easy access
        g.user_id = session.get('user_id')
        g.username = session.get('username')
        g.is_admin = session.get('is_admin', False)
        
        return f(*args, **kwargs)
    return decorated_function

def get_current_user():
    """Get current user information from session"""
    return {
        'user_id': session.get('user_id', 'local_user'),
        'username': session.get('username', 'Local User'),
        'is_admin': session.get('is_admin', True)
    }

def init_local_auth(app):
    """Initialize local authentication system"""
    @app.before_request
    def before_request():
        """Initialize local user session if not exists"""
        if 'user_id' not in session:
            session['user_id'] = 'local_user'
            session['username'] = 'Local User'
            session['is_admin'] = True
            g.user_id = 'local_user'
        else:
            g.user_id = session.get('user_id')
    
    logger.info("Local authentication system initialized")
    return True

# For backward compatibility with existing code
def make_replit_blueprint():
    """Compatibility function - returns None for local mode"""
    logger.info("Replit blueprint disabled in local mode")
    return None

# Simple mock login manager for compatibility
class MockLoginManager:
    def __init__(self):
        self.login_view = None
    
    def init_app(self, app):
        pass
    
    def user_loader(self, f):
        return f

login_manager = MockLoginManager()
