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
    Implements the QRONAS (Quantum Recursive Optimization Neural Adaptive System).
    Uses quantum-inspired principles for optimal decision making and probability processing.
    """
    def __init__(self, max_depth=5):
        self.max_depth = max_depth
        self.complex_amplitudes = []
        self.optimization_history = []
        self.collapse_bias = 0.5
        logger.info("Qronas Optimizer initialized")
    
    def optimize(self, metrics, context_entropy):
        """
        Optimize decision making using quantum-inspired algorithms.
        
        Args:
            metrics (dict): Input metrics for optimization
            context_entropy (float): Current context entropy level
            
        Returns:
            dict: Optimization results
        """
        if not metrics or not isinstance(metrics, dict):
            dummy_metrics = {"default": 0.5}
            metrics = dummy_metrics
        
        # Extract metric values
        values = list(metrics.values())
        
        # Create quantum-inspired state space
        state_vectors = self._create_state_vectors(values)
        
        # Store complex amplitudes for future reference
        self.complex_amplitudes = state_vectors
        
        # Find optimal decision point
        optimal_decision = self._find_optimal_state(state_vectors, context_entropy)
        
        # Calculate confidence based on superposition state quality
        confidence = self._calculate_confidence(state_vectors, optimal_decision)
        
        # Store optimization result in history
        self.optimization_history.append({
            "timestamp": datetime.utcnow().isoformat(),
            "metrics": metrics,
            "entropy": context_entropy,
            "decision": optimal_decision,
            "confidence": confidence
        })
        
        return {
            "decision": round(optimal_decision, 4),
            "confidence": round(confidence, 4),
            "state_count": len(state_vectors),
            "entropy": round(context_entropy, 4)
        }
    
    def _create_state_vectors(self, values):
        """
        Create quantum-inspired state vectors from metric values.
        
        Args:
            values (list): Metric values to transform
            
        Returns:
            list: State vectors with complex amplitudes
        """
        # Normalize input values to 0.0-1.0 range
        min_val = min(values) if values else 0
        max_val = max(values) if values else 1
        
        if min_val == max_val:
            normalized = [0.5 for _ in values]
        else:
            normalized = [(v - min_val) / (max_val - min_val) for v in values]
        
        # Create quantum-inspired state vectors
        state_vectors = []
        for i, probability in enumerate(normalized):
            # Quantum amplitude is square root of probability
            amplitude = math.sqrt(probability)
            
            # Create multiple phase-shifted states for each value
            for d in range(self.max_depth):
                # Calculate phase based on position and depth
                phase = 2 * math.pi * i / len(normalized) + d * math.pi / self.max_depth
                
                # Store as complex amplitude (real, imaginary)
                real_part = amplitude * math.cos(phase)
                imag_part = amplitude * math.sin(phase)
                
                state_vectors.append((real_part, imag_part))
        
        return state_vectors
    
    def _find_optimal_state(self, state_vectors, target_entropy):
        """
        Find the optimal state based on target entropy.
        
        Args:
            state_vectors (list): Quantum-inspired state vectors
            target_entropy (float): Target entropy level
            
        Returns:
            float: Optimal decision value
        """
        if not state_vectors:
            return 0.5
        
        # Calculate state probabilities
        probabilities = [
            real**2 + imag**2 for real, imag in state_vectors
        ]
        
        # Normalize probabilities
        total_prob = sum(probabilities)
        if total_prob > 0:
            normalized_probs = [p / total_prob for p in probabilities]
        else:
            normalized_probs = [1.0 / len(probabilities)] * len(probabilities)
        
        # Calculate entropy for each state
        entropies = [
            -p * math.log(p, 2) if p > 0 else 0 
            for p in normalized_probs
        ]
        
        # Find state with entropy closest to target
        closest_idx = min(range(len(entropies)), 
                          key=lambda i: abs(entropies[i] - target_entropy))
        
        # Convert to decision value (0.0-1.0 range)
        optimal_decision = normalized_probs[closest_idx]
        
        return optimal_decision
    
    def _calculate_confidence(self, state_vectors, decision):
        """
        Calculate confidence in the optimization decision.
        
        Args:
            state_vectors (list): Quantum-inspired state vectors
            decision (float): The optimization decision
            
        Returns:
            float: Confidence level (0.0-1.0)
        """
        if not state_vectors:
            return 0.5
        
        # Calculate state amplitudes
        amplitudes = [
            math.sqrt(real**2 + imag**2) for real, imag in state_vectors
        ]
        
        # Find maximum amplitude
        max_amplitude = max(amplitudes) if amplitudes else 0
        
        # Calculate decision concentration
        values_near_decision = sum(
            1 for amp in amplitudes 
            if abs(amp - decision) < 0.2
        )
        
        # Calculate concentration ratio
        concentration = values_near_decision / len(amplitudes) if amplitudes else 0
        
        # Weighted confidence calculation
        confidence = 0.4 * max_amplitude + 0.6 * concentration
        
        return max(0.0, min(1.0, confidence))
    
    def collapse_tree(self, decision_tree, collapse_bias=None):
        """
        Collapse a decision tree to a single outcome.
        
        Args:
            decision_tree (dict): Decision tree with probabilities
            collapse_bias (float): Optional bias for collapsing (0.0-1.0)
            
        Returns:
            dict: Collapsed decision tree
        """
        if not decision_tree:
            return {}
        
        # Use provided collapse bias or instance default
        bias = collapse_bias if collapse_bias is not None else self.collapse_bias
        
        # Recursive tree collapsing function
        def _collapse_branch(branch, depth=0):
            if depth >= self.max_depth:
                # Max depth reached, return as is
                return branch
            
            if isinstance(branch, dict):
                # Process dictionary branch
                result = {}
                for key, value in branch.items():
                    # Determine whether to collapse this branch
                    if random.random() < bias:
                        # Collapse by recursion
                        result[key] = _collapse_branch(value, depth + 1)
                    else:
                        # Keep as is
                        result[key] = value
                return result
            elif isinstance(branch, list):
                # Process list branch
                if not branch:
                    return branch
                
                # Determine whether to collapse list to single item
                if random.random() < bias:
                    # Select one item based on position weights
                    weights = [1/(i+1) for i in range(len(branch))]
                    total = sum(weights)
                    normalized_weights = [w/total for w in weights]
                    
                    # Select item based on weights and collapse recursively
                    selected = random.choices(
                        branch, 
                        weights=normalized_weights
                    )[0]
                    
                    return _collapse_branch(selected, depth + 1)
                else:
                    # Collapse each item in the list
                    return [_collapse_branch(item, depth + 1) for item in branch]
            else:
                # Base case: simple value
                return branch
        
        # Start collapsing from the root
        collapsed = _collapse_branch(decision_tree)
        
        return collapsed
    
    def get_recent_optimizations(self, limit=5):
        """
        Get recent optimization history.
        
        Args:
            limit (int): Maximum number of entries to return
            
        Returns:
            list: Recent optimization history
        """
        return self.optimization_history[-limit:]

class QuantumNode:
    """
    Implements a quantum-inspired node for tree-based decision making.
    """
    def __init__(self, state, amplitude=1.0):
        self.state = state
        self.amplitude = amplitude
        self.children = []
        self.probability = amplitude ** 2  # Quantum probability from amplitude
    
    def add_child(self, state, amplitude):
        """
        Add a child node to this node.
        
        Args:
            state: Child node state
            amplitude (float): Quantum amplitude for the child
            
        Returns:
            QuantumNode: The created child node
        """
        child = QuantumNode(state, amplitude)
        self.children.append(child)
        return child
    
    def get_probability(self):
        """
        Get the probability of this quantum state.
        
        Returns:
            float: Quantum probability
        """
        return self.amplitude ** 2
    
    def collapse(self):
        """
        Collapse this node's quantum state to a classical outcome.
        
        Returns:
            The collapsed state
        """
        if not self.children:
            return self.state
        
        # Create probability distribution from child amplitudes
        probabilities = [child.get_probability() for child in self.children]
        
        # Normalize probabilities
        total_prob = sum(probabilities)
        if total_prob > 0:
            normalized_probs = [p / total_prob for p in probabilities]
        else:
            normalized_probs = [1.0 / len(self.children)] * len(self.children)
        
        # Select child based on probabilities
        selected_child = random.choices(
            self.children,
            weights=normalized_probs
        )[0]
        
        # Recursively collapse the selected child
        return selected_child.collapse()

class QuantumTree:
    """
    Implements a quantum-inspired decision tree.
    """
    def __init__(self):
        self.root = None
        self.entanglement_map = {}  # Maps node pairs that are quantum-entangled
        logger.info("Quantum Tree initialized")
    
    def create_root(self, state, amplitude=1.0):
        """
        Create the root node of the tree.
        
        Args:
            state: Root node state
            amplitude (float): Quantum amplitude
            
        Returns:
            QuantumNode: The created root node
        """
        self.root = QuantumNode(state, amplitude)
        return self.root
    
    def add_entanglement(self, node1, node2, strength=1.0):
        """
        Create quantum entanglement between two nodes.
        
        Args:
            node1 (QuantumNode): First node
            node2 (QuantumNode): Second node
            strength (float): Entanglement strength
            
        Returns:
            tuple: The entangled node pair
        """
        # Create entanglement pair
        key = (id(node1), id(node2))
        self.entanglement_map[key] = strength
        
        logger.debug(f"Created entanglement between nodes with strength {strength}")
        return (node1, node2)
    
    def collapse_tree(self):
        """
        Collapse the entire quantum tree to a classical outcome.
        
        Returns:
            The collapsed outcome
        """
        if not self.root:
            return None
        
        # Collapse starting from the root
        return self.root.collapse()
    
    def measure_entanglement(self, node1, node2):
        """
        Measure the entanglement between two nodes.
        
        Args:
            node1 (QuantumNode): First node
            node2 (QuantumNode): Second node
            
        Returns:
            float: Entanglement strength or 0.0 if not entangled
        """
        key = (id(node1), id(node2))
        reverse_key = (id(node2), id(node1))
        
        # Check both directions for entanglement
        if key in self.entanglement_map:
            return self.entanglement_map[key]
        elif reverse_key in self.entanglement_map:
            return self.entanglement_map[reverse_key]
        else:
            return 0.0
