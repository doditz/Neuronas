import logging
import math
import numpy as np
from datetime import datetime

# Set up logging
logger = logging.getLogger(__name__)

class HebdenIntegrator:
    """
    Implements Hebden integration for synaptic-inspired learning and adaptation.
    Integrates with the Fibonacci-based pattern recognition system.
    """
    def __init__(self):
        self.learning_rate = 0.2
        self.connection_weights = {}
        self.activation_history = {}
        self.hebbian_decay = 0.95
        logger.info("Hebden Integrator initialized")
    
    def update_connections(self, input_nodes, output_nodes, activation_values):
        """
        Update connection weights using Hebbian learning.
        
        Args:
            input_nodes (list): List of input node IDs
            output_nodes (list): List of output node IDs
            activation_values (dict): Node activation values
            
        Returns:
            dict: Updated connection metrics
        """
        if not input_nodes or not output_nodes or not activation_values:
            return {"updated": 0, "created": 0}
        
        # Track metrics
        updates = 0
        created = 0
        
        # Update connection weights using Hebbian learning
        for input_node in input_nodes:
            for output_node in output_nodes:
                connection_key = f"{input_node}:{output_node}"
                
                # Get activation values
                input_activation = activation_values.get(input_node, 0.0)
                output_activation = activation_values.get(output_node, 0.0)
                
                # Hebbian learning rule: neurons that fire together, wire together
                activation_product = input_activation * output_activation
                
                # Update weight
                if connection_key in self.connection_weights:
                    # Update existing connection
                    old_weight = self.connection_weights[connection_key]
                    
                    # Apply learning with decay
                    new_weight = old_weight * self.hebbian_decay + activation_product * self.learning_rate
                    self.connection_weights[connection_key] = new_weight
                    updates += 1
                else:
                    # Create new connection
                    self.connection_weights[connection_key] = activation_product * self.learning_rate
                    created += 1
                
                # Store activation history
                if input_node not in self.activation_history:
                    self.activation_history[input_node] = []
                if len(self.activation_history[input_node]) >= 10:
                    self.activation_history[input_node].pop(0)
                self.activation_history[input_node].append(input_activation)
        
        logger.debug(f"Updated {updates} connections, created {created} new connections")
        return {"updated": updates, "created": created}
    
    def propagate_activation(self, input_activations):
        """
        Propagate activation through the network.
        
        Args:
            input_activations (dict): Initial activation values for input nodes
            
        Returns:
            dict: Resulting activation values for all nodes
        """
        if not input_activations or not self.connection_weights:
            return input_activations
        
        # Initialize all activations with input values
        all_activations = input_activations.copy()
        
        # Create set of all nodes
        all_nodes = set()
        for connection in self.connection_weights:
            input_node, output_node = connection.split(':')
            all_nodes.add(input_node)
            all_nodes.add(output_node)
        
        # Initialize missing nodes with zero activation
        for node in all_nodes:
            if node not in all_activations:
                all_activations[node] = 0.0
        
        # Propagate activations through connections
        for connection, weight in self.connection_weights.items():
            input_node, output_node = connection.split(':')
            
            # Skip if input node not activated
            if input_node not in all_activations:
                continue
            
            # Propagate activation
            input_activation = all_activations[input_node]
            activation_delta = input_activation * weight
            
            # Update output node activation
            current_output = all_activations.get(output_node, 0.0)
            all_activations[output_node] = current_output + activation_delta
        
        # Apply activation function to all nodes (sigmoid)
        for node in all_activations:
            all_activations[node] = self._sigmoid(all_activations[node])
        
        return all_activations
    
    def _sigmoid(self, x):
        """
        Sigmoid activation function.
        
        Args:
            x (float): Input value
            
        Returns:
            float: Sigmoid output (0.0-1.0)
        """
        return 1.0 / (1.0 + math.exp(-x))
    
    def get_strongest_connections(self, limit=10):
        """
        Get the strongest connections in the network.
        
        Args:
            limit (int): Maximum number of connections to return
            
        Returns:
            list: Strongest connections with weights
        """
        # Sort connections by weight
        sorted_connections = sorted(
            self.connection_weights.items(),
            key=lambda x: abs(x[1]),
            reverse=True
        )
        
        # Return top connections
        return [{
            "connection": conn,
            "weight": weight,
            "nodes": conn.split(':')
        } for conn, weight in sorted_connections[:limit]]

class FibonacciOptimizer:
    """
    Implements Fibonacci-based optimization for memory and pattern recognition.
    Optimizes memory structure and encoding using Fibonacci principles.
    """
    def __init__(self, max_depth=10):
        # Generate Fibonacci sequence
        self.fibonacci_sequence = self._generate_fibonacci(max_depth)
        self.golden_ratio = 1.618033988749895
        self.compression_pattern = {}
        logger.info(f"Fibonacci Optimizer initialized with sequence: {self.fibonacci_sequence}")
    
    def _generate_fibonacci(self, n):
        """
        Generate Fibonacci sequence.
        
        Args:
            n (int): Number of elements to generate
            
        Returns:
            list: Fibonacci sequence
        """
        sequence = [1, 1]
        for i in range(2, n):
            sequence.append(sequence[i-1] + sequence[i-2])
        return sequence
    
    def optimize_memory_structure(self, data_points, target_size):
        """
        Optimize memory structure using Fibonacci principles.
        
        Args:
            data_points (list): Data points to optimize
            target_size (int): Target size after optimization
            
        Returns:
            list: Optimized data structure
        """
        if not data_points:
            return []
        
        if len(data_points) <= target_size:
            return data_points
        
        # Calculate Fibonacci-based distribution
        distribution = self._fibonacci_distribution(target_size)
        
        # Distribute items according to Fibonacci pattern
        optimized = []
        current_idx = 0
        
        for segment_size in distribution:
            segment_range = len(data_points) // len(distribution)
            segment = data_points[current_idx:current_idx + segment_range]
            
            # Select items from this segment
            if segment:
                step = len(segment) / segment_size
                for i in range(segment_size):
                    idx = min(len(segment) - 1, int(i * step))
                    optimized.append(segment[idx])
            
            current_idx += segment_range
        
        logger.debug(f"Optimized {len(data_points)} data points to {len(optimized)} using Fibonacci distribution")
        return optimized
    
    def _fibonacci_distribution(self, target_size):
        """
        Create a Fibonacci-based distribution for target size.
        
        Args:
            target_size (int): Target size
            
        Returns:
            list: Distribution of elements per segment
        """
        # Find best Fibonacci numbers that sum to target_size
        distribution = []
        remaining = target_size
        
        # Start with largest Fibonacci numbers
        for num in reversed(self.fibonacci_sequence):
            while remaining >= num:
                distribution.append(num)
                remaining -= num
        
        # Handle any remainder
        if remaining > 0:
            distribution.append(remaining)
        
        return distribution
    
    def optimize_compression(self, data, importance_scores):
        """
        Optimize data compression using Fibonacci principles.
        
        Args:
            data (list): Data to compress
            importance_scores (list): Importance score for each data point
            
        Returns:
            list: Compressed data
        """
        if not data or not importance_scores:
            return []
        
        # Ensure equal lengths
        min_length = min(len(data), len(importance_scores))
        data = data[:min_length]
        importance_scores = importance_scores[:min_length]
        
        # Create data-importance pairs
        pairs = list(zip(data, importance_scores))
        
        # Sort by importance
        sorted_pairs = sorted(pairs, key=lambda x: x[1], reverse=True)
        
        # Determine compression ratio based on Fibonacci
        # Higher importance = lower compression
        compressed_data = []
        for item, importance in sorted_pairs:
            # Determine compression level using golden ratio
            compression_level = max(0.1, min(1.0, importance * self.golden_ratio / 2))
            
            # Apply compression
            if isinstance(item, str):
                # Text compression - keep portion based on importance
                keep_length = max(1, int(len(item) * compression_level))
                compressed_item = item[:keep_length]
            elif isinstance(item, list):
                # List compression - keep Fibonacci-distributed elements
                target_size = max(1, int(len(item) * compression_level))
                compressed_item = self.optimize_memory_structure(item, target_size)
            else:
                # Default - no compression
                compressed_item = item
            
            compressed_data.append(compressed_item)
        
        return compressed_data
    
    def get_golden_ratio_points(self, start, end, count):
        """
        Get points distributed according to golden ratio.
        
        Args:
            start (float): Start value
            end (float): End value
            count (int): Number of points
            
        Returns:
            list: Points distributed by golden ratio
        """
        if count <= 1:
            return [start]
        if count == 2:
            return [start, end]
        
        points = [start]
        range_size = end - start
        
        for i in range(1, count - 1):
            # Calculate position using golden ratio
            position = start + range_size * (1 - 1 / (self.golden_ratio ** i))
            points.append(position)
        
        points.append(end)
        return points

class PatternRecognition:
    """
    Implements pattern recognition using Fibonacci principles and Hebden integration.
    Core component of the bio-inspired cognitive engine.
    """
    def __init__(self, hebden_integrator=None, fibonacci_optimizer=None):
        self.hebden = hebden_integrator or HebdenIntegrator()
        self.fibonacci = fibonacci_optimizer or FibonacciOptimizer()
        self.pattern_templates = {}
        self.recognition_threshold = 0.7
        logger.info("Pattern Recognition initialized")
    
    def recognize_pattern(self, data_sequence):
        """
        Recognize patterns in data sequence.
        
        Args:
            data_sequence (list): Sequence of data points
            
        Returns:
            dict: Recognition results
        """
        if not data_sequence:
            return {"recognized": False, "confidence": 0.0}
        
        # Check against all templates
        best_match = None
        best_score = 0.0
        
        for pattern_id, template in self.pattern_templates.items():
            # Calculate match score
            match_score = self._calculate_match(data_sequence, template["sequence"])
            
            # Update best match
            if match_score > best_score:
                best_score = match_score
                best_match = pattern_id
        
        # Determine if pattern is recognized
        recognized = best_score >= self.recognition_threshold
        
        result = {
            "recognized": recognized,
            "confidence": best_score,
            "pattern_id": best_match if recognized else None
        }
        
        if recognized:
            logger.debug(f"Recognized pattern {best_match} with confidence {best_score:.2f}")
        
        return result
    
    def _calculate_match(self, sequence1, sequence2):
        """
        Calculate match score between sequences.
        
        Args:
            sequence1 (list): First sequence
            sequence2 (list): Second sequence
            
        Returns:
            float: Match score (0.0-1.0)
        """
        # Handle different sequence lengths
        min_length = min(len(sequence1), len(sequence2))
        
        if min_length == 0:
            return 0.0
        
        # Calculate Fibonacci-based comparison points
        if len(sequence1) > len(sequence2):
            # Downsample sequence1
            comparison_points = self.fibonacci.get_golden_ratio_points(0, len(sequence1) - 1, len(sequence2))
            comparison_points = [int(p) for p in comparison_points]
            seq1_samples = [sequence1[i] for i in comparison_points]
            seq2_samples = sequence2
        else:
            # Downsample sequence2
            comparison_points = self.fibonacci.get_golden_ratio_points(0, len(sequence2) - 1, len(sequence1))
            comparison_points = [int(p) for p in comparison_points]
            seq1_samples = sequence1
            seq2_samples = [sequence2[i] for i in comparison_points]
        
        # Calculate similarity
        total_similarity = 0.0
        
        for i in range(len(seq1_samples)):
            # Handle different data types
            if isinstance(seq1_samples[i], (int, float)) and isinstance(seq2_samples[i], (int, float)):
                # Numerical comparison
                max_val = max(abs(seq1_samples[i]), abs(seq2_samples[i]))
                if max_val == 0:
                    similarity = 1.0
                else:
                    similarity = 1.0 - min(1.0, abs(seq1_samples[i] - seq2_samples[i]) / max_val)
            elif isinstance(seq1_samples[i], str) and isinstance(seq2_samples[i], str):
                # String comparison
                if seq1_samples[i] == seq2_samples[i]:
                    similarity = 1.0
                else:
                    # Simple string similarity
                    common_length = len(set(seq1_samples[i]).intersection(set(seq2_samples[i])))
                    total_length = len(set(seq1_samples[i]).union(set(seq2_samples[i])))
                    similarity = common_length / total_length if total_length > 0 else 0.0
            else:
                # Different types
                similarity = 0.0
            
            total_similarity += similarity
        
        # Calculate average similarity
        return total_similarity / len(seq1_samples)
    
    def add_pattern_template(self, pattern_id, sequence, metadata=None):
        """
        Add a pattern template for recognition.
        
        Args:
            pattern_id (str): Pattern identifier
            sequence (list): Pattern sequence
            metadata (dict): Optional pattern metadata
            
        Returns:
            bool: Success status
        """
        if not sequence:
            return False
        
        # Store pattern template
        self.pattern_templates[pattern_id] = {
            "sequence": sequence,
            "length": len(sequence),
            "added_timestamp": datetime.utcnow().isoformat(),
            "metadata": metadata or {}
        }
        
        logger.debug(f"Added pattern template '{pattern_id}' with {len(sequence)} elements")
        return True
    
    def extract_patterns(self, data_sequence, min_length=3, max_length=10):
        """
        Extract recurring patterns from data sequence.
        
        Args:
            data_sequence (list): Data sequence
            min_length (int): Minimum pattern length
            max_length (int): Maximum pattern length
            
        Returns:
            list: Extracted patterns
        """
        if not data_sequence or len(data_sequence) < min_length:
            return []
        
        patterns = []
        
        # Check for patterns of different lengths
        for length in range(min_length, min(max_length + 1, len(data_sequence))):
            # Scan through sequence
            for start in range(len(data_sequence) - length + 1):
                candidate = data_sequence[start:start + length]
                occurrences = self._find_occurrences(data_sequence, candidate)
                
                # Consider it a pattern if it occurs multiple times
                if len(occurrences) > 1:
                    # Check if similar pattern already extracted
                    is_new = True
                    for existing in patterns:
                        if self._calculate_match(candidate, existing["pattern"]) > 0.8:
                            is_new = False
                            break
                    
                    if is_new:
                        patterns.append({
                            "pattern": candidate,
                            "occurrences": occurrences,
                            "length": length
                        })
        
        # Sort by number of occurrences
        patterns.sort(key=lambda x: len(x["occurrences"]), reverse=True)
        
        return patterns
    
    def _find_occurrences(self, sequence, pattern):
        """
        Find all occurrences of a pattern in a sequence.
        
        Args:
            sequence (list): Data sequence
            pattern (list): Pattern to find
            
        Returns:
            list: Starting indices of pattern occurrences
        """
        occurrences = []
        
        # Scan through sequence
        for i in range(len(sequence) - len(pattern) + 1):
            subsequence = sequence[i:i + len(pattern)]
            
            # Check for match
            if self._calculate_match(subsequence, pattern) > self.recognition_threshold:
                occurrences.append(i)
        
        return occurrences
