"""
This work is licensed under CC BY-NC 4.0 International.
Commercial use requires prior written consent and compensation.
Contact: sebastienbrulotte@gmail.com
Attribution: Sebastien Brulotte aka [ Doditz ]

This document is part of the NEURONAS cognitive system.
Core modules referenced: BRONAS (Ethical Reflex Filter) and QRONAS (Probabilistic Symbolic Vector Engine).
All outputs are subject to integrity validation and ethical compliance enforced by BRONAS.
"""

import logging
import math
import random
from datetime import datetime

# Set up logging
logger = logging.getLogger(__name__)

class QronasOptimizer:
    """
    Implements QRONAS (Quantum Recursive Optimization Neural Adaptive System)
    for decision optimization and quantum-inspired probability processing.
    """
    def __init__(self, max_depth=5):
        self.max_depth = max_depth
        self.decision_states = {}
        self.quantum_states = []
        self.optimization_history = []
        logger.info("Qronas Optimizer initialized with max_depth={}".format(max_depth))
    
    def optimize(self, metrics, context_entropy):
        """
        Optimize decision based on metrics and context entropy.
        
        Args:
            metrics (dict): Metric values to optimize
            context_entropy (float): Current entropy level
            
        Returns:
            dict: Optimization results
        """
        if not metrics:
            return {"error": "No metrics provided"}
        
        # Convert metrics dict to list for processing
        if isinstance(metrics, dict):
            metrics_list = list(metrics.values())
        else:
            metrics_list = metrics
        
        # Create decision space based on metrics
        decision_space = self._create_decision_space(metrics_list)
        
        # Find optimal decision
        optimal_decision = min(decision_space, key=lambda x: abs(context_entropy - x))
        
        # Calculate confidence based on the distance from optimal
        distances = [abs(d - optimal_decision) for d in decision_space]
        avg_distance = sum(distances) / len(distances) if distances else 0
        confidence = max(0.0, min(1.0, 1.0 - avg_distance))
        
        # Store optimization result
        self.optimization_history.append({
            "timestamp": datetime.utcnow().isoformat(),
            "optimal_decision": optimal_decision,
            "context_entropy": context_entropy,
            "confidence": confidence
        })
        
        return {
            "optimal_decision": round(optimal_decision, 4),
            "confidence": round(confidence, 4),
            "entropy": round(context_entropy, 4),
            "decision_space_size": len(decision_space)
        }
    
    def _create_decision_space(self, metrics):
        """
        Create a quantum-inspired decision space from metrics.
        
        Args:
            metrics (list): Metrics to use for decision space
            
        Returns:
            list: Decision space values
        """
        # Ensure at least one metric
        if not metrics:
            return [0.5]  # Default decision value
        
        # Normalize metrics to 0.0-1.0 range
        min_val = min(metrics)
        max_val = max(metrics)
        
        if min_val == max_val:
            normalized = [0.5 for _ in metrics]
        else:
            normalized = [(m - min_val) / (max_val - min_val) for m in metrics]
        
        # Create superposition states from normalized metrics
        superposition = []
        for i, val in enumerate(normalized):
            # Create quantum-inspired multiple states for each metric
            amplitude = math.sqrt(val)  # Quantum amplitude is square root of probability
            phase = 2 * math.pi * i / len(normalized)  # Distributed phases
            
            # Add multiple states with varying phases
            for d in range(self.max_depth):
                phase_shift = phase + d * math.pi / self.max_depth
                superposition.append(amplitude * math.cos(phase_shift))
        
        # Store these quantum states for later reference
        self.quantum_states = superposition
        
        return superposition
    
    def collapse_probability_tree(self, decision_tree, collapse_threshold=0.7):
        """
        Collapse a probability tree to make a decision.
        
        Args:
            decision_tree (dict): Decision tree with probabilities
            collapse_threshold (float): Threshold for collapsing
            
        Returns:
            dict: Collapsed decision tree
        """
        if not decision_tree:
            return {}
        
        # Recursive tree collapsing (simplified quantum decision making)
        def _collapse_node(node, depth=0):
            if isinstance(node, dict):
                # Handle nested decisions
                if depth >= self.max_depth:
                    # Max depth reached, collapse to highest probability
                    return max(node.items(), key=lambda x: x[1])[0]
                
                # Recursively collapse children
                collapsed = {}
                for key, value in node.items():
                    if isinstance(value, (dict, list)) and random.random() < collapse_threshold:
                        # Collapse this branch
                        collapsed[key] = _collapse_node(value, depth + 1)
                    else:
                        # Keep as is
                        collapsed[key] = value
                return collapsed
            elif isinstance(node, list):
                # Handle list of options - collapse to single most likely
                if node and random.random() < collapse_threshold:
                    weights = [1/len(node)] * len(node)  # Equal weights by default
                    return random.choices(node, weights=weights)[0]
                return node
            else:
                # Leaf node, return as is
                return node
        
        # Start collapsing from root
        return _collapse_node(decision_tree)
    
    def get_optimization_history(self, limit=10):
        """
        Get recent optimization history.
        
        Args:
            limit (int): Maximum number of entries to return
            
        Returns:
            list: Recent optimization entries
        """
        return self.optimization_history[-limit:]

class QkismModel:
    """
    Implements Qkism (Quantum-Kernel Integrated Symbolic Machine) for symbolic processing.
    """
    def __init__(self):
        self.knowledge = {}
        self.symbolic_relations = {}
        self.truth_thresholds = {
            'high': 0.8,
            'medium': 0.5,
            'low': 0.2
        }
        logger.info("Qkism Model initialized")
    
    def add_rule(self, concept, truth=1.0):
        """
        Add a symbolic rule to the knowledge base.
        
        Args:
            concept (str): Concept or rule
            truth (float): Truth value (0.0-1.0)
            
        Returns:
            float: Assigned truth value
        """
        # Store rule with truth value
        self.knowledge[concept] = max(0.0, min(1.0, truth))
        logger.debug(f"Added rule '{concept}' with truth {truth}")
        return truth
    
    def query(self, concept):
        """
        Query the truth value of a concept.
        
        Args:
            concept (str): Concept to query
            
        Returns:
            float: Truth value or 0.0 if not found
        """
        return self.knowledge.get(concept, 0.0)
    
    def add_symbolic_relation(self, concept1, relation, concept2, strength=1.0):
        """
        Add a symbolic relation between concepts.
        
        Args:
            concept1 (str): First concept
            relation (str): Relation type
            concept2 (str): Second concept
            strength (float): Relation strength (0.0-1.0)
            
        Returns:
            dict: Added relation
        """
        # Create relation key
        relation_key = f"{concept1}:{relation}:{concept2}"
        
        # Store relation
        self.symbolic_relations[relation_key] = max(0.0, min(1.0, strength))
        
        logger.debug(f"Added symbolic relation '{relation_key}' with strength {strength}")
        return {
            "concept1": concept1,
            "relation": relation,
            "concept2": concept2,
            "strength": strength
        }
    
    def query_relation(self, concept1, relation, concept2):
        """
        Query the strength of a relation between concepts.
        
        Args:
            concept1 (str): First concept
            relation (str): Relation type
            concept2 (str): Second concept
            
        Returns:
            float: Relation strength or 0.0 if not found
        """
        relation_key = f"{concept1}:{relation}:{concept2}"
        return self.symbolic_relations.get(relation_key, 0.0)
    
    def get_related_concepts(self, concept, relation=None):
        """
        Get concepts related to the given concept.
        
        Args:
            concept (str): The concept to query
            relation (str): Optional relation filter
            
        Returns:
            list: Related concepts with relation info
        """
        related = []
        
        for relation_key, strength in self.symbolic_relations.items():
            parts = relation_key.split(':')
            if len(parts) != 3:
                continue
            
            c1, rel, c2 = parts
            
            if c1 == concept and (relation is None or rel == relation):
                related.append({
                    "concept": c2,
                    "relation": rel,
                    "strength": strength
                })
            elif c2 == concept and (relation is None or rel == relation):
                related.append({
                    "concept": c1,
                    "relation": rel,
                    "strength": strength,
                    "inverse": True
                })
        
        return related
