from app import db
from datetime import datetime
import json
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class CognitiveMemory(db.Model):
    """Stores cognitive memory data across hemispheres and tiers"""
    id = db.Column(db.Integer, primary_key=True)
    hemisphere = db.Column(db.String(1))  # 'L' or 'R'
    tier = db.Column(db.Integer)  # 1, 2, or 3
    key = db.Column(db.String(255), index=True)
    value = db.Column(db.Text)
    importance = db.Column(db.Float, default=0.5)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    expiration = db.Column(db.DateTime, nullable=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'hemisphere': self.hemisphere,
            'tier': self.tier,
            'key': self.key,
            'value': self.value,
            'importance': self.importance,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'expiration': self.expiration.isoformat() if self.expiration else None
        }

class ExternalKnowledge(db.Model):
    """Stores external knowledge for reference"""
    id = db.Column(db.Integer, primary_key=True)
    source = db.Column(db.String(255))
    content = db.Column(db.Text)
    vector_embedding = db.Column(db.Text)  # JSON serialized vector
    relevance_score = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def set_embedding(self, vector):
        self.vector_embedding = json.dumps(vector)
    
    def get_embedding(self):
        return json.loads(self.vector_embedding) if self.vector_embedding else []

class StateOptimization(db.Model):
    """Stores optimization states for the system"""
    id = db.Column(db.Integer, primary_key=True)
    parameter = db.Column(db.String(255))
    value = db.Column(db.Float)
    context = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'parameter': self.parameter,
            'value': self.value,
            'context': self.context,
            'created_at': self.created_at.isoformat()
        }

class CognitiveMetrics(db.Model):
    """Tracks cognitive performance metrics"""
    id = db.Column(db.Integer, primary_key=True)
    metric_name = db.Column(db.String(255))
    value = db.Column(db.Float)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    session_id = db.Column(db.String(255))
    
    def to_dict(self):
        return {
            'id': self.id,
            'metric_name': self.metric_name,
            'value': self.value,
            'timestamp': self.timestamp.isoformat(),
            'session_id': self.session_id
        }

class ReinforcedHypotheses(db.Model):
    """Stores reinforced hypotheses for the BRONAS system"""
    id = db.Column(db.Integer, primary_key=True)
    hypothesis = db.Column(db.String(255))
    confidence = db.Column(db.Float, default=0.5)
    feedback_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'hypothesis': self.hypothesis,
            'confidence': self.confidence,
            'feedback_count': self.feedback_count,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class User(UserMixin, db.Model):
    """User model for authentication and preferences"""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256))
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime, nullable=True)
    
    # OAuth related fields
    oauth_provider = db.Column(db.String(20), nullable=True)  # 'google', 'github', etc.
    oauth_id = db.Column(db.String(100), nullable=True)
    
    # Neuronas settings
    d2_temperature = db.Column(db.Float, default=0.5)
    hemisphere_balance = db.Column(db.Float, default=0.5)  # 0=left, 1=right, 0.5=balanced
    creativity_weight = db.Column(db.Float, default=0.5)
    analytical_weight = db.Column(db.Float, default=0.5)
    
    # One-to-many relationship with user settings
    settings = db.relationship('UserSetting', backref='user', lazy='dynamic', cascade="all, delete-orphan")
    # One-to-many relationship with query logs
    queries = db.relationship('QueryLog', backref='user', lazy='dynamic', cascade="all, delete-orphan")
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'is_admin': self.is_admin,
            'created_at': self.created_at.isoformat(),
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'd2_temperature': self.d2_temperature,
            'hemisphere_balance': self.hemisphere_balance,
            'creativity_weight': self.creativity_weight,
            'analytical_weight': self.analytical_weight
        }

class UserSetting(db.Model):
    """Stores user-specific settings for Neuronas modules"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    module_name = db.Column(db.String(100))  # e.g. 'QRONAS', 'BRONAS', 'D2Stim'
    setting_key = db.Column(db.String(100))
    setting_value = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'module_name': self.module_name,
            'setting_key': self.setting_key,
            'setting_value': self.setting_value,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class QueryLog(db.Model):
    """Logs user queries and system responses"""
    id = db.Column(db.Integer, primary_key=True)
    query = db.Column(db.Text)
    response = db.Column(db.Text)
    query_type = db.Column(db.String(50))  # creative, analytical, factual
    hemisphere_used = db.Column(db.String(1))  # L, R, or C (central)
    processing_time = db.Column(db.Float)
    d2_activation = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    session_id = db.Column(db.String(255))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'query': self.query,
            'response': self.response,
            'query_type': self.query_type,
            'hemisphere_used': self.hemisphere_used,
            'processing_time': self.processing_time,
            'd2_activation': self.d2_activation,
            'created_at': self.created_at.isoformat(),
            'session_id': self.session_id,
            'user_id': self.user_id
        }
