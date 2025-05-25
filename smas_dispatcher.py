"""
SMAS (System Management and Synchronization) Dispatcher

This module implements the central SMAS dispatcher for the NeuronasX system,
providing control over hemisphere synchronization, agent coordination, and
system-wide parameter tuning.
"""

import logging
import time
import json
import random
import math
from datetime import datetime
from enum import Enum

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class DispatchMode(Enum):
    """Enum for dispatch modes"""
    CENTRAL = "central"  # Central dispatcher mode (balanced)
    LEFT = "left"        # Left hemisphere priority
    RIGHT = "right"      # Right hemisphere priority
    AGENT = "agent"      # Agent-driven mode (autonomous)
    
class PositionType(Enum):
    """Enum for agent position types"""
    CENTRAL = "central"  # Central position (dispatcher)
    LEFT = "left"        # Left hemisphere position
    RIGHT = "right"      # Right hemisphere position
    HYBRID = "hybrid"    # Hybrid position (flexible)

class SMASDispatcher:
    """
    Central dispatcher for the NeuronasX system that manages communication
    between hemispheres, controls agent positioning, and tunes system parameters.
    """
    
    def __init__(self):
        """Initialize the SMAS dispatcher"""
        # Default settings
        self.dispatch_mode = DispatchMode.CENTRAL
        self.agent_position = PositionType.CENTRAL
        self.d2_level = 0.5
        self.synchronization_rate = 0.5
        self.cognitive_entropy = 0.33
        self.agent_autonomy = 0.5
        
        # System state
        self.active_modules = {
            "D2Stim": True,
            "QRONAS": True,
            "BRONAS": True,
            "QuAC": True,
            "D2Spin": True,
            "QkISM": True,
            "SMAS": True
        }
        
        # Performance metrics
        self.metrics = {
            "left_activation": 0.47,
            "right_activation": 0.53,
            "processing_efficiency": 0.85,
            "synchronization_quality": 0.78,
            "response_coherence": 0.92
        }
        
        # Initialize history
        self.dispatch_history = []
        self.last_update = datetime.utcnow().isoformat()
        
    def set_dispatch_mode(self, mode):
        """
        Set the dispatch mode
        
        Args:
            mode (DispatchMode): The dispatch mode to set
        """
        if isinstance(mode, str):
            try:
                mode = DispatchMode(mode)
            except ValueError:
                logger.error(f"Invalid dispatch mode: {mode}")
                return False
                
        self.dispatch_mode = mode
        logger.info(f"Dispatch mode set to {mode.value}")
        
        # Update related parameters
        if mode == DispatchMode.LEFT:
            self.d2_level = 0.25
            self.agent_position = PositionType.LEFT
        elif mode == DispatchMode.RIGHT:
            self.d2_level = 0.75
            self.agent_position = PositionType.RIGHT
        elif mode == DispatchMode.AGENT:
            self.agent_autonomy = 0.8
            # Position remains flexible in agent mode
        else:  # CENTRAL
            self.d2_level = 0.5
            self.agent_position = PositionType.CENTRAL
            
        self._update_metrics()
        return True
        
    def set_agent_position(self, position):
        """
        Set the agent position
        
        Args:
            position (PositionType): The position type for the agent
        """
        if isinstance(position, str):
            try:
                position = PositionType(position)
            except ValueError:
                logger.error(f"Invalid position type: {position}")
                return False
                
        self.agent_position = position
        logger.info(f"Agent position set to {position.value}")
        
        # Update related parameters
        if position == PositionType.LEFT:
            # Adjust parameters for left hemisphere positioning
            self.d2_level = max(0.1, self.d2_level - 0.2)
        elif position == PositionType.RIGHT:
            # Adjust parameters for right hemisphere positioning
            self.d2_level = min(0.9, self.d2_level + 0.2)
        elif position == PositionType.HYBRID:
            # Dynamic positioning based on query content
            self.agent_autonomy = 0.7
            
        self._update_metrics()
        return True
        
    def set_d2_level(self, level):
        """
        Set the D2 dopamine receptor activation level
        
        Args:
            level (float): D2 level between 0.0 and 1.0
        """
        level = max(0.0, min(1.0, float(level)))
        self.d2_level = level
        
        # Update dispatch mode based on D2 level
        if level < 0.3:
            self.dispatch_mode = DispatchMode.LEFT
        elif level > 0.7:
            self.dispatch_mode = DispatchMode.RIGHT
        else:
            self.dispatch_mode = DispatchMode.CENTRAL
            
        logger.info(f"D2 level set to {level:.2f}")
        self._update_metrics()
        return True
        
    def toggle_module(self, module_name, active=None):
        """
        Toggle a module's active state
        
        Args:
            module_name (str): Name of the module to toggle
            active (bool, optional): If provided, set to this state
        
        Returns:
            bool: Success status
        """
        if module_name not in self.active_modules:
            logger.error(f"Unknown module: {module_name}")
            return False
            
        if active is None:
            # Toggle current state
            self.active_modules[module_name] = not self.active_modules[module_name]
        else:
            # Set to specified state
            self.active_modules[module_name] = bool(active)
            
        status = "activated" if self.active_modules[module_name] else "deactivated"
        logger.info(f"Module {module_name} {status}")
        return True
        
    def _update_metrics(self):
        """Update system metrics based on current settings"""
        # Calculate left/right activation based on D2 level
        self.metrics["left_activation"] = max(0.1, 1.0 - self.d2_level - random.uniform(0, 0.1))
        self.metrics["right_activation"] = max(0.1, self.d2_level - random.uniform(0, 0.1))
        
        # Normalize to percentages
        total = self.metrics["left_activation"] + self.metrics["right_activation"]
        self.metrics["left_activation"] = self.metrics["left_activation"] / total
        self.metrics["right_activation"] = self.metrics["right_activation"] / total
        
        # Calculate entropy based on balance
        balance = self.metrics["left_activation"] / (self.metrics["left_activation"] + self.metrics["right_activation"])
        self.cognitive_entropy = -1 * (balance * math.log2(balance) + (1 - balance) * math.log2(1 - balance)) / math.log2(2)
        
        # Calculate synchronization quality
        closer_to_balanced = 1.0 - 2.0 * abs(0.5 - balance)
        self.synchronization_rate = 0.3 + (0.7 * closer_to_balanced)
        
        # Update last update timestamp
        self.last_update = datetime.utcnow().isoformat()
        
    def process_dispatch(self, query, context=None):
        """
        Process a query through the dispatcher
        
        Args:
            query (str): The user query
            context (dict, optional): Additional context
            
        Returns:
            dict: Dispatch results with routing information
        """
        # Record start time
        start_time = time.time()
        
        # Determine dispatch target based on mode and content
        if self.dispatch_mode == DispatchMode.LEFT:
            target_hemisphere = "left"
            confidence = 0.8 + random.uniform(0, 0.15)
        elif self.dispatch_mode == DispatchMode.RIGHT:
            target_hemisphere = "right"
            confidence = 0.8 + random.uniform(0, 0.15)
        elif self.dispatch_mode == DispatchMode.AGENT:
            # In agent mode, the agent decides where to process
            if self.agent_position == PositionType.LEFT:
                target_hemisphere = "left"
            elif self.agent_position == PositionType.RIGHT:
                target_hemisphere = "right"
            else:
                # Use content analysis to determine target
                target_hemisphere = self._analyze_query_content(query)
            confidence = 0.7 + random.uniform(0, 0.2)
        else:  # CENTRAL mode
            # Use balanced routing
            target_hemisphere = "central"
            confidence = 0.9 + random.uniform(0, 0.09)
        
        # Calculate processing time
        processing_time = time.time() - start_time
        
        # Create dispatch result
        dispatch_result = {
            "query": query,
            "target_hemisphere": target_hemisphere,
            "confidence": confidence,
            "dispatch_mode": self.dispatch_mode.value,
            "agent_position": self.agent_position.value,
            "d2_level": self.d2_level,
            "processing_time": processing_time,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Add to history
        self.dispatch_history.append(dispatch_result)
        
        # Limit history size
        if len(self.dispatch_history) > 20:
            self.dispatch_history = self.dispatch_history[-20:]
            
        return dispatch_result
        
    def _analyze_query_content(self, query):
        """
        Analyze query content to determine optimal hemisphere routing
        
        Args:
            query (str): The user query
            
        Returns:
            str: Target hemisphere ("left", "right", or "central")
        """
        query_lower = query.lower()
        
        # Check for analytical keywords
        analytical_keywords = [
            "analyze", "explain", "logic", "reason", "calculate", "define",
            "compare", "evidence", "facts", "data", "process", "function"
        ]
        
        # Check for creative keywords
        creative_keywords = [
            "imagine", "create", "envision", "feel", "design", "innovate",
            "dream", "metaphor", "pattern", "intuition", "vision", "sense"
        ]
        
        # Count matches
        analytical_count = sum(1 for word in analytical_keywords if word in query_lower)
        creative_count = sum(1 for word in creative_keywords if word in query_lower)
        
        # Make decision
        if analytical_count > creative_count:
            return "left"
        elif creative_count > analytical_count:
            return "right"
        else:
            return "central"
            
    def get_system_state(self):
        """
        Get the current state of the SMAS system
        
        Returns:
            dict: Current system state
        """
        return {
            "dispatch_mode": self.dispatch_mode.value,
            "agent_position": self.agent_position.value,
            "d2_level": self.d2_level,
            "synchronization_rate": self.synchronization_rate,
            "cognitive_entropy": self.cognitive_entropy,
            "agent_autonomy": self.agent_autonomy,
            "active_modules": self.active_modules,
            "metrics": self.metrics,
            "last_update": self.last_update
        }
        
    def get_hemisphere_metrics(self):
        """
        Get metrics for both hemispheres
        
        Returns:
            dict: Hemisphere metrics
        """
        # Get memory stats if available
        memory_stats = {
            "L1": random.randint(3, 8),
            "L2": random.randint(2, 10),
            "L3": random.randint(8, 25),
            "R1": random.randint(4, 12),
            "R2": random.randint(2, 8),
            "R3": random.randint(15, 35)
        }
        
        # Performance metrics
        performance = {
            "left_efficiency": round(0.7 + random.uniform(0, 0.25), 2),
            "right_efficiency": round(0.6 + random.uniform(0, 0.35), 2),
            "left_activation": round(self.metrics["left_activation"], 2),
            "right_activation": round(self.metrics["right_activation"], 2),
            "synchronization": round(self.synchronization_rate, 2)
        }
        
        return {
            "memory": memory_stats,
            "performance": performance,
            "d2_level": self.d2_level,
            "cognitive_entropy": self.cognitive_entropy
        }