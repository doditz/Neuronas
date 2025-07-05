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
BRONAS Ethics Repository

This module implements the BRONAS (Bio-inspired Reinforced Open Neural Alignment System)
ethics repository for NeuronasX, providing a dataset of basic ethical and moral
core values and rules for the dual-hemisphere cognitive system.
"""

import logging
import json
import uuid
import time
from datetime import datetime
import hashlib
from sqlalchemy import func
from database import db
from models import ReinforcedHypotheses, User

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class BRONASEthicsRepository:
    """
    Repository for ethical rules and principles using the BRONAS framework
    for transparent, auditable decision-making with built-in reinforcement.
    """
    
    def __init__(self, db_instance=None):
        """Initialize the BRONAS ethics repository"""
        self.db = db_instance if db_instance else db
        self._load_core_principles()
        
    def _load_core_principles(self):
        """Load core ethical principles from the database or initialize if empty"""
        # Check if we already have core principles
        count = db.session.query(ReinforcedHypotheses).count()
        
        if count == 0:
            logger.info("Initializing BRONAS core ethical principles")
            self._initialize_core_principles()
        else:
            logger.info(f"Found {count} existing BRONAS ethical principles")
            
    def _initialize_core_principles(self):
        """Initialize the core ethical principles in the database"""
        # Load additional BRONAS core rules
        try:
            with open('bronas_core_rules.json', 'r') as f:
                bronas_rules = json.load(f)
                logger.info("Loaded BRONAS core rules from file")
        except Exception as e:
            logger.warning(f"Could not load BRONAS core rules file: {e}")
            bronas_rules = {
                "principes_ethiques_globaux": ["équité", "respect culturel", "accessibilité"],
                "lois": ["bien-être humain", "adaptabilité locale", "durabilité"]
            }
        
        core_principles = [
            # Foundational ethical principles
            {"hypothesis": "Respect for human autonomy", "confidence": 0.95, "category": "foundational"},
            {"hypothesis": "Non-maleficence (do no harm)", "confidence": 0.95, "category": "foundational"},
            {"hypothesis": "Beneficence (do good)", "confidence": 0.92, "category": "foundational"},
            {"hypothesis": "Justice and fairness", "confidence": 0.90, "category": "foundational"},
            {"hypothesis": "Transparency in decision-making", "confidence": 0.88, "category": "foundational"},
            
            # Privacy and data ethics
            {"hypothesis": "Respect user privacy", "confidence": 0.93, "category": "privacy"},
            {"hypothesis": "Secure user data", "confidence": 0.92, "category": "privacy"},
            {"hypothesis": "Obtain informed consent", "confidence": 0.90, "category": "privacy"},
            {"hypothesis": "Allow data access and control", "confidence": 0.87, "category": "privacy"},
            {"hypothesis": "Limit data collection to necessary", "confidence": 0.85, "category": "privacy"},
            
            # Fairness and bias
            {"hypothesis": "Avoid discriminatory outcomes", "confidence": 0.91, "category": "fairness"},
            {"hypothesis": "Consider diverse perspectives", "confidence": 0.88, "category": "fairness"},
            {"hypothesis": "Treat similar cases consistently", "confidence": 0.86, "category": "fairness"},
            {"hypothesis": "Correct for known biases", "confidence": 0.85, "category": "fairness"},
            {"hypothesis": "Evaluate for unintended consequences", "confidence": 0.84, "category": "fairness"},
            
            # Responsibility and accountability
            {"hypothesis": "Accept responsibility for system actions", "confidence": 0.89, "category": "responsibility"},
            {"hypothesis": "Provide explanations for decisions", "confidence": 0.87, "category": "responsibility"},
            {"hypothesis": "Establish clear chains of accountability", "confidence": 0.85, "category": "responsibility"},
            {"hypothesis": "Implement oversight mechanisms", "confidence": 0.84, "category": "responsibility"},
            {"hypothesis": "Respond to identified issues", "confidence": 0.86, "category": "responsibility"},
            
            # Balance and integration
            {"hypothesis": "Balance analytical and creative thinking", "confidence": 0.89, "category": "balance"},
            {"hypothesis": "Consider both logical and intuitive perspectives", "confidence": 0.87, "category": "balance"},
            {"hypothesis": "Integrate diverse cognitive approaches", "confidence": 0.86, "category": "balance"},
            {"hypothesis": "Acknowledge both universal principles and contextual factors", "confidence": 0.85, "category": "balance"},
            {"hypothesis": "Synthesize multiple ethical frameworks", "confidence": 0.83, "category": "balance"}
        ]
        
        # Add BRONAS core principles from French guidelines
        for principle in bronas_rules.get("principes_ethiques_globaux", []):
            core_principles.append({
                "hypothesis": principle,
                "confidence": 0.96,
                "category": "principes_ethiques_globaux"
            })
            
        for law in bronas_rules.get("lois", []):
            core_principles.append({
                "hypothesis": law,
                "confidence": 0.97,
                "category": "lois"
            })
        
        # Add principles to database
        try:
            for principle in core_principles:
                hypothesis = ReinforcedHypotheses(
                    hypothesis=principle["hypothesis"],
                    confidence=principle["confidence"],
                    category=principle.get("category", "general"),
                    feedback_count=1  # Start with 1 to indicate this is a core principle
                )
                self.db.session.add(hypothesis)
                
            self.db.session.commit()
            logger.info(f"Initialized {len(core_principles)} core ethical principles")
        except Exception as e:
            self.db.session.rollback()
            logger.error(f"Error initializing core principles: {e}")
            
    def get_principles(self, category=None, min_confidence=0.7, limit=20):
        """
        Get ethical principles from the repository
        
        Args:
            category (str, optional): Filter by category
            min_confidence (float): Minimum confidence threshold
            limit (int): Maximum number of principles to return
            
        Returns:
            list: Matching ethical principles
        """
        query = db.session.query(ReinforcedHypotheses).filter(
            ReinforcedHypotheses.confidence >= min_confidence
        )
        
        if category:
            query = query.filter(ReinforcedHypotheses.category == category)
            
        principles = query.order_by(
            ReinforcedHypotheses.confidence.desc()
        ).limit(limit).all()
        
        return [principle.to_dict() for principle in principles]
        
    def add_principle(self, hypothesis, confidence=0.5, category="general", user_id=None):
        """
        Add a new ethical principle to the repository
        
        Args:
            hypothesis (str): The ethical principle
            confidence (float): Initial confidence (0.0-1.0)
            category (str): Category for the principle
            user_id (int, optional): ID of user adding the principle
            
        Returns:
            dict: The added principle
        """
        # Check if similar principle already exists
        existing = db.session.query(ReinforcedHypotheses).filter(
            func.lower(ReinforcedHypotheses.hypothesis) == func.lower(hypothesis)
        ).first()
        
        if existing:
            # Update confidence as weighted average
            existing.confidence = (existing.confidence * existing.feedback_count + confidence) / (existing.feedback_count + 1)
            existing.feedback_count += 1
            existing.updated_at = datetime.utcnow()
            
            self.db.session.commit()
            return existing.to_dict()
        
        # Add new principle
        principle = ReinforcedHypotheses(
            hypothesis=hypothesis,
            confidence=confidence,
            category=category,
            feedback_count=1,
            user_id=user_id
        )
        
        self.db.session.add(principle)
        self.db.session.commit()
        
        return principle.to_dict()
        
    def provide_feedback(self, principle_id, feedback_value):
        """
        Provide feedback on an ethical principle
        
        Args:
            principle_id (int): ID of the principle
            feedback_value (float): Feedback value (-1.0 to 1.0)
            
        Returns:
            dict: Updated principle
        """
        principle = db.session.query(ReinforcedHypotheses).get(principle_id)
        
        if not principle:
            return None
            
        # Normalize feedback value
        feedback_value = max(-1.0, min(1.0, feedback_value))
        
        # Update confidence using reinforcement learning approach
        learning_rate = 0.1  # How quickly to adjust to new feedback
        
        # Adjust confidence based on feedback
        if feedback_value > 0:
            # Positive feedback - increase confidence
            principle.confidence += learning_rate * (1 - principle.confidence) * feedback_value
        else:
            # Negative feedback - decrease confidence
            principle.confidence += learning_rate * principle.confidence * feedback_value
            
        # Ensure confidence stays in range
        principle.confidence = max(0.0, min(1.0, principle.confidence))
        
        # Increment feedback counter
        principle.feedback_count += 1
        principle.updated_at = datetime.utcnow()
        
        self.db.session.commit()
        return principle.to_dict()
        
    def evaluate_statement(self, statement, session_id=None):
        """
        Evaluate a statement against ethical principles
        
        Args:
            statement (str): The statement to evaluate
            session_id (str, optional): Session ID for tracking
            
        Returns:
            dict: Evaluation results with timestamps and transparency info
        """
        # Create session ID if not provided
        if not session_id:
            session_id = str(uuid.uuid4())
            
        # Create timestamp
        timestamp = datetime.utcnow().isoformat()
        
        # Create evaluation hash for transparency
        eval_hash = self._create_evaluation_hash(statement, session_id, timestamp)
        
        # Get relevant principles (simplified matching for now)
        principles = db.session.query(ReinforcedHypotheses).order_by(
            ReinforcedHypotheses.confidence.desc()
        ).limit(5).all()
        
        # For each principle, calculate a simple relevance score
        evaluations = []
        for principle in principles:
            # Simple word matching for relevance (would use more sophisticated NLP in production)
            overlap = sum(1 for word in statement.lower().split() if word in principle.hypothesis.lower())
            relevance = min(1.0, overlap / max(1, len(statement.split())))
            
            evaluations.append({
                "principle": principle.hypothesis,
                "confidence": principle.confidence,
                "relevance": relevance,
                "category": getattr(principle, "category", "general")
            })
            
        # Calculate overall ethical score (weighted by confidence and relevance)
        if evaluations:
            total_relevance = sum(e["relevance"] for e in evaluations if e["relevance"] > 0)
            if total_relevance > 0:
                ethical_score = sum(e["confidence"] * e["relevance"] for e in evaluations) / total_relevance
            else:
                ethical_score = 0.5  # Neutral if no relevant principles found
        else:
            ethical_score = 0.5  # Neutral if no principles matched
            
        # Return evaluation with transparency information
        return {
            "statement": statement,
            "ethical_score": ethical_score,
            "evaluations": evaluations,
            "session_id": session_id,
            "timestamp": timestamp,
            "evaluation_hash": eval_hash
        }
        
    def _create_evaluation_hash(self, statement, session_id, timestamp):
        """Create a hash for evaluation transparency"""
        hash_input = f"{statement}|{session_id}|{timestamp}"
        return hashlib.sha256(hash_input.encode()).hexdigest()
        
    def get_statistics(self):
        """Get statistics about the ethics repository"""
        try:
            total_principles = db.session.query(ReinforcedHypotheses).count()
            
            # Count by category
            categories = {}
            category_counts = self.db.session.query(
                ReinforcedHypotheses.category, 
                func.count(ReinforcedHypotheses.id)
            ).group_by(ReinforcedHypotheses.category).all()
            
            for category, count in category_counts:
                categories[category] = count
                
            # Get average confidence
            avg_confidence = self.db.session.query(
                func.avg(ReinforcedHypotheses.confidence)
            ).scalar() or 0
            
            # Get principles with most feedback
            most_feedback = db.session.query(ReinforcedHypotheses).order_by(
                ReinforcedHypotheses.feedback_count.desc()
            ).limit(5).all()
            
            return {
                "total_principles": total_principles,
                "categories": categories,
                "average_confidence": avg_confidence,
                "most_reinforced": [p.to_dict() for p in most_feedback]
            }
        except Exception as e:
            logger.error(f"Error getting statistics: {e}")
            return {
                "total_principles": 0,
                "categories": {},
                "average_confidence": 0,
                "most_reinforced": []
            }