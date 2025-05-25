"""
Session Transparency System for NeuronasX

This module implements a comprehensive session transparency system for NeuronasX,
providing unique session identifiers, timestamps, and cryptographic hashes
for all system interactions to ensure auditability and ethical compliance.
"""

import logging
import uuid
import hashlib
import json
import time
from datetime import datetime, timedelta
import threading
from sqlalchemy import func, desc, asc
from models import db, User, QueryLog

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class SessionTransparency:
    """
    Session transparency system for tracking and verifying all interactions
    with the NeuronasX cognitive system.
    """
    
    def __init__(self, db_instance=None):
        """Initialize the session transparency system"""
        self.db = db_instance if db_instance else db
        self.active_sessions = {}
        self.session_locks = {}
        self._start_cleanup_thread()
        
    def _start_cleanup_thread(self):
        """Start background thread for session cleanup"""
        def cleanup_worker():
            while True:
                try:
                    self._cleanup_expired_sessions()
                except Exception as e:
                    logger.error(f"Error in session cleanup: {e}")
                time.sleep(3600)  # Run hourly
                
        cleanup_thread = threading.Thread(target=cleanup_worker, daemon=True)
        cleanup_thread.start()
        
    def _cleanup_expired_sessions(self):
        """Clean up expired sessions"""
        current_time = datetime.utcnow()
        expired_sessions = []
        
        for session_id, session_data in self.active_sessions.items():
            expiry = session_data.get('expiry')
            if expiry and current_time > expiry:
                expired_sessions.append(session_id)
                
        for session_id in expired_sessions:
            if session_id in self.session_locks:
                del self.session_locks[session_id]
            if session_id in self.active_sessions:
                del self.active_sessions[session_id]
                
        logger.info(f"Cleaned up {len(expired_sessions)} expired sessions")
        
    def create_session(self, user_id=None, source_info=None, expiry_hours=24):
        """
        Create a new transparent session
        
        Args:
            user_id (int, optional): User ID if authenticated
            source_info (dict, optional): Information about the session source
            expiry_hours (int): Hours until session expiry
            
        Returns:
            dict: Session information
        """
        # Generate unique session ID
        session_id = str(uuid.uuid4())
        
        # Create timestamp
        timestamp = datetime.utcnow()
        expiry = timestamp + timedelta(hours=expiry_hours)
        
        # Create session hash for integrity verification
        session_hash = self._create_session_hash(session_id, timestamp, user_id, source_info)
        
        # Store session information
        session_info = {
            'session_id': session_id,
            'user_id': user_id,
            'created_at': timestamp,
            'expiry': expiry,
            'session_hash': session_hash,
            'source_info': source_info or {},
            'interaction_count': 0,
            'last_activity': timestamp
        }
        
        # Add to active sessions
        self.active_sessions[session_id] = session_info
        self.session_locks[session_id] = threading.Lock()
        
        # Return session information (without internal tracking data)
        return {
            'session_id': session_id,
            'created_at': timestamp.isoformat(),
            'expiry': expiry.isoformat(),
            'session_hash': session_hash
        }
        
    def validate_session(self, session_id):
        """
        Validate a session ID
        
        Args:
            session_id (str): The session ID to validate
            
        Returns:
            bool: Whether the session is valid
        """
        if not session_id or session_id not in self.active_sessions:
            return False
            
        session_data = self.active_sessions.get(session_id)
        current_time = datetime.utcnow()
        
        # Check if session has expired
        if session_data.get('expiry') and current_time > session_data['expiry']:
            # Remove expired session
            if session_id in self.session_locks:
                del self.session_locks[session_id]
            if session_id in self.active_sessions:
                del self.active_sessions[session_id]
            return False
            
        return True
        
    def record_interaction(self, session_id, interaction_type, data=None, system_components=None):
        """
        Record an interaction with the system for transparency
        
        Args:
            session_id (str): Session ID
            interaction_type (str): Type of interaction
            data (dict, optional): Interaction data
            system_components (list, optional): System components involved
            
        Returns:
            dict: Interaction record with transparency information
        """
        # Validate session
        if not self.validate_session(session_id):
            # Create a new session if invalid
            session_info = self.create_session()
            session_id = session_info['session_id']
            
        # Get session lock
        lock = self.session_locks.get(session_id)
        
        # Record interaction with lock to prevent race conditions
        with lock:
            # Update session activity
            session_data = self.active_sessions[session_id]
            timestamp = datetime.utcnow()
            session_data['last_activity'] = timestamp
            session_data['interaction_count'] += 1
            
            # Create interaction hash for verification
            interaction_hash = self._create_interaction_hash(
                session_id, 
                interaction_type, 
                timestamp, 
                data
            )
            
            # Create interaction record
            interaction_record = {
                'interaction_id': str(uuid.uuid4()),
                'session_id': session_id,
                'timestamp': timestamp.isoformat(),
                'interaction_type': interaction_type,
                'system_components': system_components or [],
                'interaction_hash': interaction_hash,
                'sequence_number': session_data['interaction_count']
            }
            
            # Add data if provided
            if data:
                # Don't include sensitive data in the record
                safe_data = self._sanitize_data(data)
                interaction_record['data'] = safe_data
                
            return interaction_record
            
    def _sanitize_data(self, data):
        """Remove sensitive information from data"""
        if not data or not isinstance(data, dict):
            return data
            
        # Create a copy to avoid modifying the original
        safe_data = data.copy()
        
        # List of keys that might contain sensitive information
        sensitive_keys = [
            'password', 'token', 'secret', 'key', 'credential', 
            'auth', 'private', 'api_key', 'apikey'
        ]
        
        # Check each key at any level of nesting
        def sanitize_recursive(obj):
            if isinstance(obj, dict):
                for key in list(obj.keys()):
                    if any(sensitive in key.lower() for sensitive in sensitive_keys):
                        obj[key] = '***REDACTED***'
                    elif isinstance(obj[key], (dict, list)):
                        sanitize_recursive(obj[key])
            elif isinstance(obj, list):
                for item in obj:
                    if isinstance(item, (dict, list)):
                        sanitize_recursive(item)
                        
        sanitize_recursive(safe_data)
        return safe_data
        
    def get_session_info(self, session_id):
        """
        Get information about a session
        
        Args:
            session_id (str): Session ID
            
        Returns:
            dict: Session information
        """
        if not self.validate_session(session_id):
            return None
            
        session_data = self.active_sessions.get(session_id)
        
        # Return session information (without internal tracking data)
        return {
            'session_id': session_id,
            'created_at': session_data['created_at'].isoformat(),
            'last_activity': session_data['last_activity'].isoformat(),
            'expiry': session_data['expiry'].isoformat(),
            'interaction_count': session_data['interaction_count'],
            'session_hash': session_data['session_hash'],
            'user_id': session_data.get('user_id')
        }
        
    def get_session_interactions(self, session_id, limit=20):
        """
        Get interactions for a session from the database
        
        Args:
            session_id (str): Session ID
            limit (int): Maximum number of interactions to retrieve
            
        Returns:
            list: Session interactions
        """
        # Retrieve interactions from QueryLog
        interactions = QueryLog.query.filter_by(
            session_id=session_id
        ).order_by(
            desc(QueryLog.created_at)
        ).limit(limit).all()
        
        return [interaction.to_dict() for interaction in interactions]
        
    def _create_session_hash(self, session_id, timestamp, user_id, source_info):
        """Create a hash for session integrity verification"""
        # Create a string representation of the session data
        session_str = f"{session_id}|{timestamp.isoformat()}"
        
        if user_id:
            session_str += f"|{user_id}"
            
        if source_info:
            session_str += f"|{json.dumps(source_info, sort_keys=True)}"
            
        # Create a SHA-256 hash
        return hashlib.sha256(session_str.encode()).hexdigest()
        
    def _create_interaction_hash(self, session_id, interaction_type, timestamp, data):
        """Create a hash for interaction integrity verification"""
        # Create a string representation of the interaction data
        interaction_str = f"{session_id}|{interaction_type}|{timestamp.isoformat()}"
        
        if data:
            safe_data = self._sanitize_data(data)
            interaction_str += f"|{json.dumps(safe_data, sort_keys=True)}"
            
        # Create a SHA-256 hash
        return hashlib.sha256(interaction_str.encode()).hexdigest()
        
    def verify_interaction(self, interaction_record):
        """
        Verify the integrity of an interaction record
        
        Args:
            interaction_record (dict): The interaction record to verify
            
        Returns:
            bool: Whether the interaction record is valid
        """
        if not interaction_record or 'interaction_hash' not in interaction_record:
            return False
            
        # Extract data from the record
        session_id = interaction_record.get('session_id')
        interaction_type = interaction_record.get('interaction_type')
        timestamp_str = interaction_record.get('timestamp')
        data = interaction_record.get('data')
        recorded_hash = interaction_record.get('interaction_hash')
        
        if not all([session_id, interaction_type, timestamp_str, recorded_hash]):
            return False
            
        # Parse timestamp
        try:
            timestamp = datetime.fromisoformat(timestamp_str)
        except (ValueError, TypeError):
            return False
            
        # Recreate the hash
        computed_hash = self._create_interaction_hash(
            session_id, interaction_type, timestamp, data
        )
        
        # Compare hashes
        return computed_hash == recorded_hash
        
    def get_statistics(self):
        """Get statistics about sessions and interactions"""
        try:
            # Count active sessions
            active_count = len(self.active_sessions)
            
            # Count total sessions in database
            total_sessions = db.session.query(
                func.count(func.distinct(QueryLog.session_id))
            ).scalar() or 0
            
            # Count total interactions
            total_interactions = QueryLog.query.count()
            
            # Get interactions per session average
            if total_sessions > 0:
                avg_interactions = total_interactions / total_sessions
            else:
                avg_interactions = 0
                
            # Get most active sessions
            most_active = db.session.query(
                QueryLog.session_id,
                func.count(QueryLog.id).label('count')
            ).group_by(
                QueryLog.session_id
            ).order_by(
                desc('count')
            ).limit(5).all()
            
            most_active_sessions = [
                {'session_id': session_id, 'interaction_count': count}
                for session_id, count in most_active
            ]
            
            return {
                'active_sessions': active_count,
                'total_sessions': total_sessions,
                'total_interactions': total_interactions,
                'avg_interactions_per_session': avg_interactions,
                'most_active_sessions': most_active_sessions
            }
        except Exception as e:
            logger.error(f"Error getting session statistics: {e}")
            return {
                'active_sessions': active_count,
                'total_sessions': 0,
                'total_interactions': 0,
                'avg_interactions_per_session': 0,
                'most_active_sessions': []
            }