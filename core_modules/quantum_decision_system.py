
"""
Quantum Decision System for Neuronas AI
Implements quantum superposition and collapse for probabilistic token decision making
"""

import numpy as np
import math
from collections import OrderedDict
import random

class QuantumDecisionSystem:
    def __init__(self, architecture_config=None):
        """Initialize the Quantum Decision System"""
        self.config = architecture_config or {}
        self.collapse_threshold = self.config.get("collapse_threshold", 0.7)
        self.spin_encoding_min = self.config.get("spin_encoding_probability_min", 0.3)
        self.spin_encoding_max = self.config.get("spin_encoding_probability_max", 0.9)
        self.entanglement_enabled = self.config.get("token_superposition_entanglement", True)
        self.entropy_reduction_target = self.config.get("quantum_entropy_reduction", 0.35)
        self.superposition_states = {}
        self.entanglement_matrix = {}
        
    def create_superposition(self, token_id, probabilities):
        """
        Create a quantum superposition state for a token
        
        Args:
            token_id: Unique identifier for the token
            probabilities: Dictionary of {outcome: probability} pairs
            
        Returns:
            Dictionary representing superposition state
        """
        # Normalize probabilities
        total = sum(probabilities.values())
        normalized = {k: v/total for k, v in probabilities.items()}
        
        # Create quantum state
        state = {
            'token_id': token_id,
            'superposition': normalized,
            'collapsed': False,
            'observed_value': None,
            'spin': self._initialize_spin(),
            'entangled_with': set()
        }
        
        self.superposition_states[token_id] = state
        return state
    
    def _initialize_spin(self):
        """Initialize quantum spin state"""
        # Randomize between spin-up (1) and spin-down (-1) with weighted probability
        spin_encoding_prob = random.uniform(self.spin_encoding_min, self.spin_encoding_max)
        return 1 if random.random() < spin_encoding_prob else -1
    
    def entangle_tokens(self, token_id1, token_id2, strength=0.5):
        """
        Create quantum entanglement between two tokens
        
        Args:
            token_id1, token_id2: IDs of tokens to entangle
            strength: Entanglement strength (0-1)
            
        Returns:
            Boolean indicating success
        """
        if not self.entanglement_enabled:
            return False
            
        if token_id1 not in self.superposition_states or token_id2 not in self.superposition_states:
            return False
            
        # Add to entanglement sets
        self.superposition_states[token_id1]['entangled_with'].add(token_id2)
        self.superposition_states[token_id2]['entangled_with'].add(token_id1)
        
        # Record entanglement strength
        entanglement_key = tuple(sorted([token_id1, token_id2]))
        self.entanglement_matrix[entanglement_key] = strength
        
        return True
    
    def collapse_state(self, token_id, uncertainty_level=None):
        """
        Collapse a quantum superposition into a definite state
        
        Args:
            token_id: ID of token to collapse
            uncertainty_level: Level of decision uncertainty (0-1)
            
        Returns:
            The observed value after collapse
        """
        if token_id not in self.superposition_states:
            return None
            
        state = self.superposition_states[token_id]
        
        # Skip if already collapsed
        if state['collapsed']:
            return state['observed_value']
            
        # Determine if collapse should occur based on uncertainty
        should_collapse = True
        if uncertainty_level is not None:
            should_collapse = uncertainty_level >= self.collapse_threshold
            
        if not should_collapse:
            return None
            
        # Perform measurement/collapse
        superposition = state['superposition']
        outcomes = list(superposition.keys())
        probabilities = list(superposition.values())
        
        # Apply quantum interference effects based on spin
        probabilities = self._apply_quantum_interference(probabilities, state['spin'])
        
        # Normalize probabilities after interference
        total = sum(probabilities)
        probabilities = [p/total for p in probabilities]
        
        # Select outcome based on probability distribution
        observed_value = np.random.choice(outcomes, p=probabilities)
        
        # Update state
        state['collapsed'] = True
        state['observed_value'] = observed_value
        
        # Propagate collapse to entangled tokens
        self._propagate_entanglement_collapse(token_id, observed_value)
        
        return observed_value
    
    def _apply_quantum_interference(self, probabilities, spin):
        """Apply quantum interference effects to probabilities based on spin"""
        # Simulating quantum interference by adjusting probabilities
        interference_factor = 0.2 * spin  # +0.2 or -0.2 based on spin
        
        # Apply interference
        adjusted = []
        for i, p in enumerate(probabilities):
            # Alternating adjustment simulates wave interference
            adjustment = interference_factor * math.sin(i * math.pi / len(probabilities))
            new_p = p + adjustment
            adjusted.append(max(0.001, new_p))  # Ensure no negative probabilities
            
        return adjusted
    
    def _propagate_entanglement_collapse(self, token_id, observed_value):
        """Propagate collapse effects to entangled tokens"""
        state = self.superposition_states[token_id]
        
        for entangled_id in state['entangled_with']:
            if entangled_id in self.superposition_states:
                entangled_state = self.superposition_states[entangled_id]
                
                # Skip if already collapsed
                if entangled_state['collapsed']:
                    continue
                    
                # Get entanglement strength
                entanglement_key = tuple(sorted([token_id, entangled_id]))
                strength = self.entanglement_matrix.get(entanglement_key, 0.5)
                
                # Adjust probabilities based on entanglement
                self._adjust_entangled_probabilities(entangled_state, observed_value, strength)
    
    def _adjust_entangled_probabilities(self, entangled_state, observed_value, strength):
        """Adjust probabilities of an entangled token based on observed value"""
        superposition = entangled_state['superposition']
        
        # Check if observed value exists in entangled token's possibilities
        if observed_value in superposition:
            # Increase probability of the same outcome
            for outcome in superposition:
                if outcome == observed_value:
                    superposition[outcome] = superposition[outcome] * (1 + strength)
                else:
                    superposition[outcome] = superposition[outcome] * (1 - strength/2)
                    
            # Normalize
            total = sum(superposition.values())
            for outcome in superposition:
                superposition[outcome] = superposition[outcome] / total
    
    def calculate_entropy(self, token_id):
        """Calculate Shannon entropy of a token's superposition state"""
        if token_id not in self.superposition_states:
            return 0
            
        state = self.superposition_states[token_id]
        if state['collapsed']:
            return 0  # No uncertainty in collapsed state
            
        # Calculate Shannon entropy: -sum(p_i * log2(p_i))
        entropy = 0
        for p in state['superposition'].values():
            if p > 0:  # Avoid log(0)
                entropy -= p * math.log2(p)
                
        return entropy
    
    def measure_entanglement_network(self):
        """Measure properties of the entanglement network"""
        if not self.entanglement_matrix:
            return {"size": 0, "avg_strength": 0, "density": 0}
            
        # Calculate network properties
        nodes = set()
        for k in self.entanglement_matrix:
            nodes.add(k[0])
            nodes.add(k[1])
            
        n_nodes = len(nodes)
        n_edges = len(self.entanglement_matrix)
        avg_strength = sum(self.entanglement_matrix.values()) / n_edges if n_edges > 0 else 0
        max_edges = n_nodes * (n_nodes - 1) / 2 if n_nodes > 1 else 1
        density = n_edges / max_edges if max_edges > 0 else 0
        
        return {
            "size": n_nodes,
            "edges": n_edges, 
            "avg_strength": avg_strength,
            "density": density
        }
    
    def reset_quantum_states(self):
        """Reset all quantum states"""
        self.superposition_states = {}
        self.entanglement_matrix = {}
        
    def get_system_metrics(self):
        """Get metrics about the quantum decision system"""
        # Count collapsed vs uncollapsed states
        total_states = len(self.superposition_states)
        collapsed_states = sum(1 for s in self.superposition_states.values() if s['collapsed'])
        
        # Calculate average entropy
        avg_entropy = 0
        if total_states > 0:
            avg_entropy = sum(self.calculate_entropy(tid) for tid in self.superposition_states) / total_states
            
        # Get entanglement network metrics
        entanglement_metrics = self.measure_entanglement_network()
        
        return {
            "total_states": total_states,
            "collapsed_states": collapsed_states,
            "uncollapsed_states": total_states - collapsed_states,
            "collapse_ratio": collapsed_states / total_states if total_states > 0 else 0,
            "average_entropy": avg_entropy,
            "entanglement_network": entanglement_metrics,
            "entropy_reduction": 1.0 - (avg_entropy / math.log2(4) if total_states > 0 else 1.0)  # Assuming average of 4 options
        }
