from app import db
from datetime import datetime
import json

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
            'session_id': self.session_id
        }
