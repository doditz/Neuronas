"""
Agent Positioning System for NeuronasX

This module implements the agent positioning capabilities for the NeuronasX system,
allowing the AI agent to function in different roles:
- As a central SMAS dispatcher
- Embedded within the left hemisphere (analytical)
- Embedded within the right hemisphere (creative)
- In a hybrid mode that can dynamically shift

The positioning system serves as a bridge between the SMAS dispatcher and
the dual LLM system, influencing how queries are processed.
"""

import logging
import time
import json
import random
from datetime import datetime
from enum import Enum

# Import other system components
from smas_dispatcher import SMASDispatcher, PositionType, DispatchMode

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class AgentPositioningSystem:
    """
    System for managing agent positioning within the NeuronasX architecture,
    allowing the agent to take different roles and perspectives.
    """
    
    def __init__(self, dual_llm_system=None, smas_dispatcher=None):
        """
        Initialize the agent positioning system
        
        Args:
            dual_llm_system: The dual LLM system instance
            smas_dispatcher: The SMAS dispatcher instance
        """
        self.dual_llm = dual_llm_system
        self.smas = smas_dispatcher if smas_dispatcher else SMASDispatcher()
        
        # Current position settings
        self.current_position = PositionType.CENTRAL
        self.position_locked = False
        self.position_bias = 0.5  # 0.0=left, 1.0=right
        
        # Agent characteristics
        self.analytical_weight = 0.5
        self.creative_weight = 0.5
        self.adaptive_threshold = 0.6  # Threshold for position changes
        
        # History tracking
        self.position_history = []
        self.adaptive_moves = 0
        
    def set_position(self, position, lock_position=False):
        """
        Set the agent's position within the system
        
        Args:
            position (PositionType or str): The position to set
            lock_position (bool): Whether to lock the position
            
        Returns:
            bool: Success status
        """
        # Convert string to enum if needed
        if isinstance(position, str):
            try:
                position = PositionType(position)
            except ValueError:
                logger.error(f"Invalid position: {position}")
                return False
                
        # Update position
        self.current_position = position
        self.position_locked = lock_position
        
        # Update SMAS dispatcher
        self.smas.set_agent_position(position)
        
        # Update position bias based on position
        if position == PositionType.LEFT:
            self.position_bias = 0.2
            # Update weights
            self.analytical_weight = 0.8
            self.creative_weight = 0.2
        elif position == PositionType.RIGHT:
            self.position_bias = 0.8
            # Update weights
            self.analytical_weight = 0.2
            self.creative_weight = 0.8
        elif position == PositionType.HYBRID:
            self.position_bias = 0.5
            # Balance weights
            self.analytical_weight = 0.5
            self.creative_weight = 0.5
        else:  # CENTRAL
            self.position_bias = 0.5
            # Balance weights
            self.analytical_weight = 0.5
            self.creative_weight = 0.5
            
        # Record in history
        self.position_history.append({
            "position": position.value,
            "locked": lock_position,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        # Limit history size
        if len(self.position_history) > 20:
            self.position_history = self.position_history[-20:]
            
        logger.info(f"Agent position set to {position.value} (locked: {lock_position})")
        return True
        
    def adjust_position_for_query(self, query):
        """
        Automatically adjust agent position based on query content
        if not locked
        
        Args:
            query (str): The user query
            
        Returns:
            PositionType: The adjusted position
        """
        if self.position_locked:
            return self.current_position
            
        # Only adjust if in HYBRID mode
        if self.current_position != PositionType.HYBRID:
            return self.current_position
            
        # Analyze query content to determine position
        query_lower = query.lower()
        
        # Check for analytical indicators
        analytical_keywords = [
            "analyze", "explain", "logic", "reason", "calculate", "define",
            "compare", "evidence", "facts", "data", "process", "function"
        ]
        
        # Check for creative indicators
        creative_keywords = [
            "imagine", "create", "envision", "feel", "design", "innovate",
            "dream", "metaphor", "pattern", "intuition", "vision", "sense"
        ]
        
        # Count matches
        analytical_count = sum(1 for word in analytical_keywords if word in query_lower)
        creative_count = sum(1 for word in creative_keywords if word in query_lower)
        
        # Determine position adjustment
        if analytical_count > creative_count and analytical_count >= 2:
            new_position = PositionType.LEFT
            self.adaptive_moves += 1
        elif creative_count > analytical_count and creative_count >= 2:
            new_position = PositionType.RIGHT
            self.adaptive_moves += 1
        else:
            # Not enough clear indicators, maintain hybrid or use dispatch
            new_position = PositionType.HYBRID
            
        return new_position
        
    def process_with_positioning(self, query, context=None):
        """
        Process a query with agent positioning applied
        
        Args:
            query (str): The user query
            context (dict, optional): Additional context
            
        Returns:
            dict: Processing result with positioning information
        """
        # Start timing
        start_time = time.time()
        
        # Save original position in case we need to restore it
        original_position = self.current_position
        
        # Check for position adjustment
        adjusted_position = self.adjust_position_for_query(query)
        if adjusted_position != self.current_position and not self.position_locked:
            # Temporarily adjust position for this query
            self.set_position(adjusted_position, lock_position=False)
            position_adjusted = True
        else:
            position_adjusted = False
        
        # Configure dispatch based on position
        if self.current_position == PositionType.LEFT:
            # Left hemisphere focus
            dispatch_mode = DispatchMode.LEFT
            hemisphere_balance = 0.2
        elif self.current_position == PositionType.RIGHT:
            # Right hemisphere focus
            dispatch_mode = DispatchMode.RIGHT
            hemisphere_balance = 0.8
        elif self.current_position == PositionType.HYBRID:
            # Hybrid mode - dynamic balance
            dispatch_mode = DispatchMode.AGENT
            # Calculate dynamic balance based on content
            hemisphere_balance = self.position_bias
        else:  # CENTRAL
            # Balanced dispatch
            dispatch_mode = DispatchMode.CENTRAL
            hemisphere_balance = 0.5
            
        # Set dispatch mode
        self.smas.set_dispatch_mode(dispatch_mode)
        
        # Get dispatch info
        dispatch_info = self.smas.process_dispatch(query, context)
        
        # Process through dual LLM system if available
        if self.dual_llm:
            # Set hemisphere balance
            self.dual_llm.set_hemisphere_balance(hemisphere_balance)
            
            # Set D2 activation based on dispatch
            self.dual_llm.set_d2_activation(self.smas.d2_level)
            
            # Process the query
            result = self.dual_llm.process_query(query, {
                "hemisphere_balance": hemisphere_balance,
                "d2_activation": self.smas.d2_level,
                "analytical_weight": self.analytical_weight,
                "creative_weight": self.creative_weight
            })
        else:
            # No dual LLM system, return simulated result
            result = self._simulate_processing(query, hemisphere_balance)
            
        # Calculate processing time
        processing_time = time.time() - start_time
        
        # Add positioning information to result
        result.update({
            "agent_position": self.current_position.value,
            "position_adjusted": position_adjusted,
            "dispatch_info": dispatch_info,
            "position_bias": self.position_bias,
            "processing_time": processing_time
        })
        
        # Restore original position if temporarily adjusted
        if position_adjusted:
            self.set_position(original_position, lock_position=False)
            
        return result
        
    def _simulate_processing(self, query, hemisphere_balance):
        """
        Simulate processing when dual LLM system is not available
        
        Args:
            query (str): The user query
            hemisphere_balance (float): Balance between hemispheres
            
        Returns:
            dict: Simulated processing result
        """
        # Simple simulation with placeholder responses
        if hemisphere_balance < 0.3:
            response = f"[Simulated analytical response with LEFT hemisphere bias]\n\nAnalytical perspective on '{query[:30]}...'\n\nThis query can be approached systematically by examining the core components and logical relationships."
            hemisphere = "left"
        elif hemisphere_balance > 0.7:
            response = f"[Simulated creative response with RIGHT hemisphere bias]\n\nCreative perspective on '{query[:30]}...'\n\nThis query invites us to explore multiple possibilities and connect ideas in novel ways."
            hemisphere = "right"
        else:
            response = f"[Simulated balanced response with CENTRAL integration]\n\nBalanced perspective on '{query[:30]}...'\n\nThis query benefits from both structured analysis and creative exploration, allowing us to see both the logical framework and imaginative possibilities."
            hemisphere = "central"
            
        return {
            "success": True,
            "response": response,
            "hemisphere_balance": hemisphere_balance,
            "hemisphere_used": hemisphere,
            "d2_activation": self.smas.d2_level,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    def get_positioning_state(self):
        """
        Get the current positioning state
        
        Returns:
            dict: Current positioning state
        """
        return {
            "current_position": self.current_position.value,
            "position_locked": self.position_locked,
            "position_bias": self.position_bias,
            "analytical_weight": self.analytical_weight,
            "creative_weight": self.creative_weight,
            "adaptive_threshold": self.adaptive_threshold,
            "adaptive_moves": self.adaptive_moves,
            "position_history": self.position_history[-5:],  # Last 5 positions
            "smas_state": self.smas.get_system_state()
        }