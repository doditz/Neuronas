import logging
import math
import random

# Set up logging
logger = logging.getLogger(__name__)

class ModulationEngine:
    """
    Implements dopaminergic modulation to enhance or inhibit cognitive processing.
    Combines D2Stim and D2Pin capabilities for cognitive modulation.
    """
    def __init__(self):
        self.d2_activation = 0.5
        self.attention = 0.5
        self.working_memory = 0.5
        
        # Define modulation limits to prevent extreme values
        self.limits = {
            'd2_activation': (0.1, 1.0),
            'attention': (0.2, 1.0),
            'working_memory': (0.2, 0.8)
        }
        
        # Initialize modulation engine
        self.initialized = True
        logger.info("Modulation Engine initialized")
    
    def modulate_d2(self, mode, intensity=0.3):
        """
        Apply dopaminergic modulation based on specified mode.
        
        Args:
            mode (str): Modulation mode ('stim', 'pin', or 'baseline')
            intensity (float): Modulation intensity (0.0-1.0)
            
        Returns:
            dict: Updated cognitive state values
        """
        # Apply appropriate modulation
        if mode == "stim":
            return self.apply_stimulation(intensity)
        elif mode == "pin":
            return self.apply_inhibition(intensity)
        else:
            return self.reset_baseline()
    
    def apply_stimulation(self, intensity=0.3, region="prefrontal_cortex"):
        """
        Apply D2Stim stimulation to enhance cognitive processing.
        
        Args:
            intensity (float): Stimulation intensity (0.0-1.0)
            region (str): Target brain region (for future enhancement)
            
        Returns:
            dict: Updated cognitive state
        """
        # Increase D2 activation
        self.d2_activation = min(
            self.limits['d2_activation'][1], 
            self.d2_activation + intensity
        )
        
        # Enhance attention based on current D2 activation
        # with diminishing returns near activation extremes
        attention_modifier = intensity * (1 - abs(0.7 - self.d2_activation)) * 0.3
        self.attention = min(
            self.limits['attention'][1],
            self.attention + attention_modifier
        )
        
        # Decrease working memory capacity slightly (trade-off)
        self.working_memory = max(
            self.limits['working_memory'][0],
            self.working_memory - intensity * 0.2
        )
        
        logger.debug(f"Applied D2Stim with intensity {intensity}")
        return {
            "d2_activation": round(self.d2_activation, 2),
            "attention": round(self.attention, 2),
            "working_memory": round(self.working_memory, 2),
            "mode": "stim",
            "intensity": intensity
        }
    
    def apply_inhibition(self, intensity=0.3):
        """
        Apply D2Pin inhibition to focus cognitive processing.
        
        Args:
            intensity (float): Inhibition intensity (0.0-1.0)
            
        Returns:
            dict: Updated cognitive state
        """
        # Decrease D2 activation
        self.d2_activation = max(
            self.limits['d2_activation'][0], 
            self.d2_activation - intensity
        )
        
        # Increase working memory capacity
        self.working_memory = min(
            self.limits['working_memory'][1],
            self.working_memory + intensity * 0.2
        )
        
        # Modify attention based on current D2 activation
        attention_modifier = intensity * 0.15
        # Lower D2 activation leads to more focused attention
        if self.d2_activation < 0.3:
            self.attention = min(
                self.limits['attention'][1],
                self.attention + attention_modifier
            )
        else:
            self.attention = max(
                self.limits['attention'][0],
                self.attention - attention_modifier
            )
        
        logger.debug(f"Applied D2Pin with intensity {intensity}")
        return {
            "d2_activation": round(self.d2_activation, 2),
            "attention": round(self.attention, 2),
            "working_memory": round(self.working_memory, 2),
            "mode": "pin",
            "intensity": intensity
        }
    
    def reset_baseline(self):
        """
        Reset cognitive parameters to baseline values.
        
        Returns:
            dict: Baseline cognitive state
        """
        self.d2_activation = 0.5
        self.attention = 0.5
        self.working_memory = 0.5
        
        logger.debug("Reset to baseline cognitive state")
        return {
            "d2_activation": self.d2_activation,
            "attention": self.attention,
            "working_memory": self.working_memory,
            "mode": "baseline",
            "intensity": 0.0
        }

class QuACEngine:
    """
    Implements Quantum Adaptive Caching (QuAC) for memory management.
    """
    def __init__(self):
        self.cache = {}
        self.tier_thresholds = {
            'L1': 0.9,  # Very high importance for L1
            'L2': 0.6,  # Medium importance for L2
            'L3': 0.0   # Everything else goes to L3
        }
        logger.info("QuAC Engine initialized")
    
    def cache_data(self, key, value, importance):
        """
        Cache data with adaptive tier selection based on importance.
        
        Args:
            key (str): Cache key
            value (any): Data to cache
            importance (float): Importance score (0.0-1.0)
            
        Returns:
            str: Selected memory tier
        """
        # Select tier based on importance
        if importance > self.tier_thresholds['L1']:
            tier = "L1"
        elif importance > self.tier_thresholds['L2']:
            tier = "L2"
        else:
            tier = "L3"
        
        # Store in cache
        self.cache[key] = (value, tier, importance)
        
        logger.debug(f"Cached data with key {key} to tier {tier}")
        return tier
    
    def retrieve_data(self, key):
        """
        Retrieve data from cache.
        
        Args:
            key (str): Cache key
            
        Returns:
            tuple: (value, tier, importance) or None if not found
        """
        if key in self.cache:
            return self.cache[key]
        return None
    
    def get_tier_data(self, tier):
        """
        Get all data from a specific tier.
        
        Args:
            tier (str): Memory tier (L1, L2, L3)
            
        Returns:
            dict: Data from the specified tier
        """
        return {
            k: v for k, (v, t, i) in self.cache.items()
            if t == tier
        }

class QDACache:
    """
    Implements Quantum Dopaminergic Adaptive Caching (QDAC) for advanced memory scoring.
    """
    def __init__(self):
        self.memory = {}
        self.scoring_weights = {
            'length': 0.3,
            'd2_level': 0.4,
            'recency': 0.3
        }
        logger.info("QDAC Engine initialized")
    
    def score_entry(self, data, d2_level):
        """
        Score a memory entry based on content and D2 level.
        
        Args:
            data (str): Memory content
            d2_level (float): Current D2 activation level
            
        Returns:
            float: Memory score
        """
        if not data:
            return 0.0
        
        # Calculate base score from content length
        length_score = min(1.0, len(data) / 1000) * self.scoring_weights['length']
        
        # Calculate D2 modulated score - higher D2 favors certain content types
        d2_mod = math.sin(d2_level * math.pi) * self.scoring_weights['d2_level']
        
        # Recency is set to maximum for new entries
        recency_score = 1.0 * self.scoring_weights['recency']
        
        # Calculate total score
        total_score = length_score + d2_mod + recency_score
        
        return round(total_score, 3)
    
    def store_scored_memory(self, key, data, d2_level):
        """
        Store memory with QDAC scoring.
        
        Args:
            key (str): Memory key
            data (str): Memory content
            d2_level (float): Current D2 activation level
            
        Returns:
            float: Memory score
        """
        # Calculate score
        score = self.score_entry(data, d2_level)
        
        # Store in memory with timestamp
        import time
        self.memory[key] = {
            'data': data,
            'score': score,
            'd2_level': d2_level,
            'timestamp': time.time()
        }
        
        logger.debug(f"Stored memory with key {key} and score {score}")
        return score
    
    def decay_scores(self, decay_rate=0.05):
        """
        Apply time-based decay to memory scores.
        
        Args:
            decay_rate (float): Rate of score decay
            
        Returns:
            int: Number of entries affected
        """
        count = 0
        for key in self.memory:
            self.memory[key]['score'] *= (1 - decay_rate)
            count += 1
        
        logger.debug(f"Applied decay to {count} memory entries")
        return count
    
    def get_top_memories(self, limit=10):
        """
        Get top-scoring memories.
        
        Args:
            limit (int): Maximum number of entries to return
            
        Returns:
            list: Top memory entries
        """
        # Sort by score
        sorted_memories = sorted(
            self.memory.items(), 
            key=lambda x: x[1]['score'],
            reverse=True
        )
        
        # Return top entries
        return sorted_memories[:limit]
