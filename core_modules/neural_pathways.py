import logging
import random

# Set up logging
logger = logging.getLogger(__name__)

class NeuralPathwayRouter:
    """
    Routes cognitive processing through specialized neural pathways.
    Implements the D2Spin (Dopaminergic D2 Quantum Spin-Integrated Memory System).
    """
    def __init__(self):
        # Define available pathways for each hemisphere
        self.left_pathways = [
            "analytical_reasoning",
            "logical_deduction",
            "factual_retrieval",
            "numeric_processing",
            "structural_analysis"
        ]
        
        self.right_pathways = [
            "creative_divergence",
            "abstract_synthesis",
            "intuitive_reasoning",
            "narrative_generation",
            "conceptual_blending"
        ]
        
        # D2Spin activation level
        self.d2_activation = 0.5
        
        # Define hemisphere balancing weights
        self.hemisphere_bias = {
            'creative': {'L': 0.2, 'R': 0.8},
            'analytical': {'L': 0.8, 'R': 0.2},
            'factual': {'L': 0.7, 'R': 0.3}
        }
        
        self.initialized = True
        logger.info("Neural Pathway Router initialized")
    
    def route_neural_pathway(self, query, query_type):
        """
        Route query to appropriate hemisphere and neural pathway.
        
        Args:
            query (str): The user query
            query_type (str): Query classification
            
        Returns:
            tuple: (hemisphere, pathway) to be used for processing
        """
        # Get hemisphere weights for query type
        weights = self.hemisphere_bias.get(
            query_type, 
            {'L': 0.5, 'R': 0.5}  # Default to balanced
        )
        
        # Apply D2 activation adjustment to weights
        # Higher D2 activation favors right hemisphere
        d2_modifier = (self.d2_activation - 0.5) * 0.4
        weights['R'] += d2_modifier
        weights['L'] -= d2_modifier
        
        # Ensure weights remain valid probabilities
        weights['L'] = max(0.1, min(0.9, weights['L']))
        weights['R'] = max(0.1, min(0.9, weights['R']))
        
        # Choose hemisphere based on weights
        hemisphere = random.choices(
            ['L', 'R'], 
            weights=[weights['L'], weights['R']]
        )[0]
        
        # Select appropriate pathway for the hemisphere
        if hemisphere == 'L':
            pathway = self._select_left_pathway(query_type)
        else:
            pathway = self._select_right_pathway(query_type)
        
        logger.debug(f"Routed to {hemisphere} hemisphere using {pathway} pathway")
        return hemisphere, pathway
    
    def _select_left_pathway(self, query_type):
        """
        Select appropriate pathway in the left hemisphere.
        
        Args:
            query_type (str): Query classification
            
        Returns:
            str: Selected pathway
        """
        if query_type == 'factual':
            # Prioritize factual retrieval for factual queries
            weights = [0.1, 0.1, 0.6, 0.1, 0.1]
        elif query_type == 'analytical':
            # Prioritize analytical reasoning and logical deduction
            weights = [0.4, 0.3, 0.1, 0.1, 0.1]
        else:
            # Balanced for creative queries
            weights = [0.2, 0.2, 0.2, 0.2, 0.2]
        
        # Select pathway based on weights
        return random.choices(self.left_pathways, weights=weights)[0]
    
    def _select_right_pathway(self, query_type):
        """
        Select appropriate pathway in the right hemisphere.
        
        Args:
            query_type (str): Query classification
            
        Returns:
            str: Selected pathway
        """
        if query_type == 'creative':
            # Prioritize creative divergence and conceptual blending
            weights = [0.4, 0.1, 0.1, 0.1, 0.3]
        elif query_type == 'analytical':
            # Prioritize abstract synthesis and intuitive reasoning
            weights = [0.1, 0.4, 0.3, 0.1, 0.1]
        else:
            # Prioritize narrative generation for factual queries
            weights = [0.1, 0.2, 0.1, 0.5, 0.1]
        
        # Select pathway based on weights
        return random.choices(self.right_pathways, weights=weights)[0]
    
    def update_d2_activation(self, activation_level):
        """
        Update D2 activation level.
        
        Args:
            activation_level (float): New activation level (0.0-1.0)
            
        Returns:
            float: Updated activation level
        """
        # Ensure activation level is within bounds
        self.d2_activation = max(0.0, min(1.0, activation_level))
        logger.debug(f"D2 activation updated to {self.d2_activation}")
        return self.d2_activation

class D2SpinMemory:
    """
    Implements the D2Spin memory encoding system to handle token-level processing.
    """
    def __init__(self):
        self.memory = {}
        self.activation = 0.5
        logger.info("D2Spin Memory initialized")
    
    def encode(self, token):
        """
        Encode a token based on D2Spin principles.
        
        Args:
            token (str): Token to encode
            
        Returns:
            int: Encoding value (-1, 0, or 1)
        """
        # Simple encoding strategy:
        # 1: Important tokens (longer than 6 chars)
        # -1: Stop words/common words
        # 0: Neutral tokens
        
        if not token:
            return 0
            
        if len(token) > 6:
            return 1
        elif token.lower() in ["the", "and", "a", "of", "in", "to", "is", "it"]:
            return -1
        else:
            return 0
    
    def store_tokens(self, tokens):
        """
        Store tokens with their D2Spin encoding.
        
        Args:
            tokens (list): List of tokens to store
            
        Returns:
            dict: Token encodings
        """
        if not tokens:
            return {}
            
        # Encode each token
        encodings = {t: self.encode(t) for t in tokens}
        
        # Update memory with new encodings
        self.memory.update(encodings)
        
        return encodings
    
    def retrieve_by_encoding(self, encoding_value):
        """
        Retrieve tokens with a specific encoding value.
        
        Args:
            encoding_value (int): Encoding value to search for
            
        Returns:
            list: Matching tokens
        """
        # Find tokens with matching encoding
        matching_tokens = [
            token for token, encoding in self.memory.items()
            if encoding == encoding_value
        ]
        
        return matching_tokens
    
    def get_activation_level(self):
        """
        Get current D2Spin activation level.
        
        Returns:
            float: Current activation level
        """
        return self.activation
    
    def set_activation_level(self, level):
        """
        Set D2Spin activation level.
        
        Args:
            level (float): New activation level (0.0-1.0)
            
        Returns:
            float: Updated activation level
        """
        self.activation = max(0.0, min(1.0, level))
        return self.activation
