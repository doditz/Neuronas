
"""
D2 Receptor Modulation System for Neuronas AI
Implements D2Stim and D2Pin modulation for cognitive adaptability
"""

import numpy as np
import random
from collections import deque

class D2ReceptorModulation:
    def __init__(self, config=None):
        """Initialize the D2 Receptor Modulation System"""
        self.config = config or {}
        
        # D2Stim configuration (focus/executive function)
        self.d2stim_config = {
            "focus_enhancement": self.config.get("focus_enhancement", 0.7),
            "executive_boost": self.config.get("executive_function_boost", 0.65),
            "activation_threshold": self.config.get("activation_threshold", 0.4)
        }
        
        # D2Pin configuration (creativity/flexibility)
        self.d2pin_config = {
            "creativity_enhancement": self.config.get("creativity_enhancement", 0.8),
            "flexibility_boost": self.config.get("cognitive_flexibility_boost", 0.75),
            "activation_threshold": self.config.get("activation_threshold", 0.35)
        }
        
        # Current modulation levels
        self.d2stim_level = 0.0
        self.d2pin_level = 0.0
        self.d2_activation = 0.5  # Balanced state
        
        # History tracking
        self.history = deque(maxlen=10)
        self.activation_history = deque(maxlen=100)
        
        # Metrics
        self.metrics = {
            "stim_activations": 0,
            "pin_activations": 0,
            "balanced_states": 0,
            "max_stim_level": 0.0,
            "max_pin_level": 0.0,
            "cumulative_focus": 0.0,
            "cumulative_creativity": 0.0
        }
    
    def set_modulation(self, stim_level=None, pin_level=None):
        """
        Set D2 receptor modulation levels
        
        Args:
            stim_level: D2Stim level (0-1)
            pin_level: D2Pin level (0-1)
            
        Returns:
            Current D2 activation level
        """
        # Update levels if provided
        if stim_level is not None:
            self.d2stim_level = max(0.0, min(1.0, stim_level))
        
        if pin_level is not None:
            self.d2pin_level = max(0.0, min(1.0, pin_level))
        
        # Calculate overall D2 activation
        # Higher values favor focus, lower values favor creativity
        self.d2_activation = 0.5 + (self.d2stim_level - self.d2pin_level) / 2
        
        # Record history
        self.history.append({
            "stim_level": self.d2stim_level,
            "pin_level": self.d2pin_level,
            "activation": self.d2_activation
        })
        
        self.activation_history.append(self.d2_activation)
        
        # Update metrics
        if self.d2stim_level > self.d2pin_level + 0.2:
            self.metrics["stim_activations"] += 1
        elif self.d2pin_level > self.d2stim_level + 0.2:
            self.metrics["pin_activations"] += 1
        else:
            self.metrics["balanced_states"] += 1
            
        self.metrics["max_stim_level"] = max(self.metrics["max_stim_level"], self.d2stim_level)
        self.metrics["max_pin_level"] = max(self.metrics["max_pin_level"], self.d2pin_level)
        
        return self.d2_activation
    
    def get_cognitive_effects(self):
        """
        Calculate cognitive effects based on current modulation levels
        
        Returns:
            Dictionary of cognitive effects
        """
        # Base cognitive parameters
        cognitive_params = {
            "focus": 0.5,
            "executive_function": 0.5,
            "creativity": 0.5,
            "cognitive_flexibility": 0.5,
            "working_memory": 0.5,
            "pattern_recognition": 0.5,
            "divergent_thinking": 0.5,
            "convergent_thinking": 0.5
        }
        
        # Apply D2Stim effects (focus/executive function)
        if self.d2stim_level >= self.d2stim_config["activation_threshold"]:
            stim_factor = self.d2stim_level - self.d2stim_config["activation_threshold"]
            normalized_stim = stim_factor / (1 - self.d2stim_config["activation_threshold"])
            
            # Enhance focus and executive function
            cognitive_params["focus"] += normalized_stim * self.d2stim_config["focus_enhancement"]
            cognitive_params["executive_function"] += normalized_stim * self.d2stim_config["executive_boost"]
            cognitive_params["convergent_thinking"] += normalized_stim * 0.4
            cognitive_params["working_memory"] += normalized_stim * 0.3
            
            # Reduce parameters that may be inhibited
            cognitive_params["divergent_thinking"] -= normalized_stim * 0.2
            
        # Apply D2Pin effects (creativity/flexibility)
        if self.d2pin_level >= self.d2pin_config["activation_threshold"]:
            pin_factor = self.d2pin_level - self.d2pin_config["activation_threshold"]
            normalized_pin = pin_factor / (1 - self.d2pin_config["activation_threshold"])
            
            # Enhance creativity and cognitive flexibility
            cognitive_params["creativity"] += normalized_pin * self.d2pin_config["creativity_enhancement"]
            cognitive_params["cognitive_flexibility"] += normalized_pin * self.d2pin_config["flexibility_boost"]
            cognitive_params["divergent_thinking"] += normalized_pin * 0.5
            cognitive_params["pattern_recognition"] += normalized_pin * 0.3
            
            # Reduce parameters that may be inhibited
            cognitive_params["focus"] -= normalized_pin * 0.1
            
        # Ensure all parameters are in valid range
        for param in cognitive_params:
            cognitive_params[param] = max(0.1, min(1.0, cognitive_params[param]))
            
        # Update cumulative metrics
        self.metrics["cumulative_focus"] += cognitive_params["focus"]
        self.metrics["cumulative_creativity"] += cognitive_params["creativity"]
            
        return cognitive_params
    
    def apply_modulation_to_content(self, content, cognitive_params):
        """
        Apply cognitive modulation effects to content
        
        Args:
            content: Content to process
            cognitive_params: Cognitive parameters from get_cognitive_effects
            
        Returns:
            Modulated content
        """
        # In a real system, this would apply the cognitive effects to content generation
        # This is a placeholder - actual implementation would depend on the content type
        return content
    
    def suggest_optimal_modulation(self, query_type, context_complexity, user_state=None):
        """
        Suggest optimal D2 modulation levels based on query and context
        
        Args:
            query_type: Type of query (creative, analytical, factual)
            context_complexity: Complexity level (0-1)
            user_state: Optional user state information
            
        Returns:
            Suggested modulation levels
        """
        # Default balanced state
        suggested_stim = 0.5
        suggested_pin = 0.5
        
        # Adjust based on query type
        if query_type == "creative":
            # Creative queries benefit from higher D2Pin
            suggested_stim = 0.3
            suggested_pin = 0.7 + (context_complexity * 0.2)
        elif query_type == "analytical":
            # Analytical queries benefit from higher D2Stim
            suggested_stim = 0.7 + (context_complexity * 0.2)
            suggested_pin = 0.3
        elif query_type == "factual":
            # Factual queries benefit from balanced but slightly higher D2Stim
            suggested_stim = 0.6
            suggested_pin = 0.4
        else:
            # Unknown query type - use balanced state
            suggested_stim = 0.5
            suggested_pin = 0.5
            
        # Adjust for context complexity
        if context_complexity > 0.7:
            # Very complex contexts benefit from more executive function
            suggested_stim = min(suggested_stim + 0.1, 1.0)
            
        # Incorporate user state if available
        if user_state and "preferred_modulation" in user_state:
            # Blend with user preferences
            user_stim = user_state["preferred_modulation"].get("stim", 0.5)
            user_pin = user_state["preferred_modulation"].get("pin", 0.5)
            
            # 70% suggestion, 30% user preference
            suggested_stim = (suggested_stim * 0.7) + (user_stim * 0.3)
            suggested_pin = (suggested_pin * 0.7) + (user_pin * 0.3)
            
        # Ensure valid ranges
        suggested_stim = max(0.0, min(1.0, suggested_stim))
        suggested_pin = max(0.0, min(1.0, suggested_pin))
            
        return {
            "suggested_stim": suggested_stim,
            "suggested_pin": suggested_pin,
            "resulting_activation": 0.5 + (suggested_stim - suggested_pin) / 2,
            "query_type": query_type,
            "context_complexity": context_complexity
        }
    
    def get_activation_metrics(self):
        """Get metrics about activation patterns"""
        # Calculate activation stability
        stability = 0.0
        if len(self.activation_history) > 1:
            differences = [abs(self.activation_history[i] - self.activation_history[i-1]) 
                          for i in range(1, len(self.activation_history))]
            stability = 1.0 - (sum(differences) / len(differences) if differences else 0)
            
        return {
            "stim_activations": self.metrics["stim_activations"],
            "pin_activations": self.metrics["pin_activations"],
            "balanced_states": self.metrics["balanced_states"],
            "max_stim_level": self.metrics["max_stim_level"],
            "max_pin_level": self.metrics["max_pin_level"],
            "current_stim": self.d2stim_level,
            "current_pin": self.d2pin_level,
            "current_activation": self.d2_activation,
            "activation_stability": stability,
            "focus_creativity_ratio": (self.metrics["cumulative_focus"] / self.metrics["cumulative_creativity"] 
                                     if self.metrics["cumulative_creativity"] > 0 else 1.0)
        }
    
    def reset_modulation(self):
        """Reset modulation to balanced state"""
        self.d2stim_level = 0.0
        self.d2pin_level = 0.0
        self.d2_activation = 0.5
        return self.d2_activation
