from datetime import datetime
import random
import math
import logging

# Set up logging
logger = logging.getLogger(__name__)

class CognitiveEngine:
    """
    Core cognitive processing engine that simulates striatum, cortex, and hippocampus functions.
    Implements the foundational cognitive processing capabilities of the Neuronas system.
    """
    def __init__(self):
        # Initialize the cognitive state with default values
        self.state = {
            "focus": 1.0,             # Attentional focus level
            "entropy": 0.2,           # System entropy/disorder
            "modulation": "balanced", # D2 modulation state
            "context_weight": 0.7,    # Context importance weighting
            "activation": {
                "left_hemisphere": 0.5,  # Left hemisphere (analytical) activation
                "right_hemisphere": 0.5, # Right hemisphere (creative) activation
                "central_integration": 0.3 # Central hemisphere integration strength
            }
        }
        self.initialized = True
        logger.info("Cognitive Engine initialized with default state")
    
    def modulate(self, mode):
        """
        Modulates cognitive state based on the specified mode.
        
        Args:
            mode (str): The modulation mode ('stim', 'pin', or 'balanced')
        """
        if mode == "stim":
            # D2Stim: Increase focus, decrease entropy
            self.state["focus"] += 0.1
            self.state["entropy"] -= 0.05
            # Stimulates right hemisphere (creative)
            self.state["activation"]["right_hemisphere"] += 0.1
        elif mode == "pin":
            # D2Pin: Decrease focus, increase entropy
            self.state["focus"] -= 0.05
            self.state["entropy"] += 0.1
            # Stimulates left hemisphere (analytical)
            self.state["activation"]["left_hemisphere"] += 0.1
        else:
            # Reset to balanced state
            self.state["focus"] = 1.0
            self.state["entropy"] = 0.2
            self.state["activation"]["left_hemisphere"] = 0.5
            self.state["activation"]["right_hemisphere"] = 0.5
        
        # Enforce bounds
        self.state["focus"] = max(0.1, min(2.0, self.state["focus"]))
        self.state["entropy"] = max(0.0, min(1.0, self.state["entropy"]))
        self.state["activation"]["left_hemisphere"] = max(0.1, min(1.0, self.state["activation"]["left_hemisphere"]))
        self.state["activation"]["right_hemisphere"] = max(0.1, min(1.0, self.state["activation"]["right_hemisphere"]))
        
        # Update modulation state
        self.state["modulation"] = mode
        
        logger.debug(f"Cognitive state modulated to {mode}")
        return self.state
    
    def analyze(self, text):
        """
        Analyzes the input text and returns cognitive metrics.
        
        Args:
            text (str): Input text to analyze
        
        Returns:
            dict: Analysis results including score and modulation mode
        """
        # Simple analysis based on text length and complexity
        if not text:
            return {"analysis_score": 0.0, "mode": self.state["modulation"]}
        
        # Word count score (basic analysis)
        word_count = len(text.split())
        score = word_count / 10.0
        
        # Apply focus and entropy modifiers
        score *= self.state["focus"]
        score *= (1.0 - self.state["entropy"] * 0.5)
        
        # Apply hemispheric activation
        hemisphere = "left" if self.state["activation"]["left_hemisphere"] > self.state["activation"]["right_hemisphere"] else "right"
        
        return {
            "analysis_score": round(score, 2), 
            "mode": self.state["modulation"],
            "dominant_hemisphere": hemisphere,
            "focus": round(self.state["focus"], 2),
            "entropy": round(self.state["entropy"], 2)
        }
    
    def reflect(self, data):
        """
        Performs reflective cognitive processing on the input data.
        
        Args:
            data (str): Input data for reflection
        
        Returns:
            str: Reflection output
        """
        # Generate a reflection based on the cognitive state
        reflection = f"Reflecting on input of length {len(data)} using mode: {self.state['modulation']}."
        reflection += f" Focus: {self.state['focus']:.2f}, Entropy: {self.state['entropy']:.2f}."
        
        # Determine which hemisphere is most active
        if self.state["activation"]["left_hemisphere"] > self.state["activation"]["right_hemisphere"]:
            reflection += " Processing analytically in left hemisphere."
        else:
            reflection += " Processing creatively in right hemisphere."
        
        return reflection
    
    def get_state(self):
        """Returns the current cognitive state"""
        return self.state
    
    def process_feedback(self, hypothesis, feedback_value):
        """
        Process feedback for reinforcement learning using BRONAS.
        
        Args:
            hypothesis (str): The hypothesis being evaluated
            feedback_value (float): Feedback score between -1.0 and 1.0
        """
        from models import ReinforcedHypotheses, db
        
        # Normalize feedback to 0.0-1.0 range
        normalized_feedback = (feedback_value + 1.0) / 2.0
        
        # Find or create hypothesis
        hypothesis_obj = ReinforcedHypotheses.query.filter_by(
            hypothesis=hypothesis
        ).first()
        
        if not hypothesis_obj:
            hypothesis_obj = ReinforcedHypotheses(
                hypothesis=hypothesis,
                confidence=0.5,
                feedback_count=0
            )
        
        # Update confidence using Bayesian-inspired update
        prior = hypothesis_obj.confidence
        posterior = (prior + normalized_feedback) / 2
        
        # Apply confidence update
        hypothesis_obj.confidence = posterior
        hypothesis_obj.feedback_count += 1
        
        # Save to database
        db.session.add(hypothesis_obj)
        db.session.commit()
        
        logger.debug(f"Updated hypothesis '{hypothesis}' confidence to {posterior}")
        return posterior

class NeuronasOptimizer:
    """
    Optimizes neural parameters and manages belief models.
    Implements the BRONAS (Bayesian Reinforcement Optimized Neural Adaptive System).
    """
    def __init__(self):
        self.history = []
        self.decay = 0.95
        self.beliefs = {}  # BRONAS belief model
    
    def optimize(self, metrics):
        """
        Optimize cognitive parameters based on input metrics.
        
        Args:
            metrics (list): List of numeric metrics to optimize
            
        Returns:
            dict: Optimization results
        """
        if not metrics:
            return {"optimized_value": 0.0, "beliefs": {}, "history_count": 0}
        
        # Calculate baseline from metrics
        baseline = sum(metrics) / len(metrics)
        
        # Apply temporal decay
        adjusted = baseline * self.decay
        
        # Store in history
        self.history.append(adjusted)
        
        # Update belief model
        self._update_beliefs(metrics)
        
        return {
            "optimized_value": round(adjusted, 4),
            "beliefs": self.beliefs,
            "history_count": len(self.history)
        }
    
    def _update_beliefs(self, metrics):
        """
        Update the belief model using Bayesian principles.
        
        Args:
            metrics (list): Metrics used to update beliefs
        """
        for i, val in enumerate(metrics):
            key = f"m{i}"
            if key not in self.beliefs:
                self.beliefs[key] = val
            else:
                # Bayesian-like update: weighted adjustment
                self.beliefs[key] = (self.beliefs[key] + val) / 2
    
    def reset(self):
        """Reset optimizer state"""
        self.history = []
        self.beliefs = {}
        return {"status": "reset_complete"}

class CognitiveProfile:
    """
    Manages and evaluates cognitive profiles and contexts.
    """
    def __init__(self):
        self.meta = {}
        self.activation_score = 1.0
    
    def update_context(self, context):
        """
        Update cognitive profile based on context.
        
        Args:
            context (str): Context information
            
        Returns:
            float: Updated activation score
        """
        if not context:
            return 0.0
        
        tokens = context.split()
        
        # Calculate activation score based on context size
        # with diminishing returns for very large contexts
        self.activation_score = min(2.0, len(tokens) / 50.0)
        
        # Store metadata
        self.meta["last_context_size"] = len(tokens)
        self.meta["context_timestamp"] = datetime.utcnow().isoformat()
        
        return self.activation_score
    
    def evaluate(self):
        """
        Evaluate the current cognitive profile.
        
        Returns:
            dict: Evaluation results
        """
        return {
            "contextual_weight": round(self.activation_score, 2), 
            "metadata": self.meta
        }
