import logging
import re
import random
import math

# Set up logging
logger = logging.getLogger(__name__)

class QueryProcessor:
    """
    Classifies and processes incoming queries to determine their type and characteristics.
    """
    def __init__(self):
        # Initialize pattern matching for query classification
        self.patterns = {
            'creative': [
                r'create', r'design', r'imagine', r'generate', r'suggest',
                r'innovative', r'creative', r'new ideas', r'brainstorm',
                r'what if', r'could you come up with', r'novel'
            ],
            'analytical': [
                r'analyze', r'evaluate', r'compare', r'explain why', 
                r'how does', r'what causes', r'relationship between',
                r'pros and cons', r'advantages', r'disadvantages',
                r'implications', r'reasoning'
            ],
            'factual': [
                r'who is', r'what is', r'when did', r'where is', r'how many',
                r'define', r'list', r'tell me about', r'information on',
                r'facts', r'history of', r'data on'
            ]
        }
        self.initialized = True
        logger.info("Query Processor initialized")
    
    def classify_query(self, query):
        """
        Classify the query type based on content and patterns.
        
        Args:
            query (str): The user query
            
        Returns:
            tuple: (query_type, confidence)
        """
        if not query:
            return 'unknown', 0.0
        
        # Convert to lowercase for pattern matching
        query_lower = query.lower()
        
        # Count pattern matches for each type
        matches = {
            'creative': 0,
            'analytical': 0,
            'factual': 0
        }
        
        # Check for pattern matches
        for query_type, patterns in self.patterns.items():
            for pattern in patterns:
                if re.search(pattern, query_lower):
                    matches[query_type] += 1
        
        # Get query type with highest number of matches
        if max(matches.values()) == 0:
            # No clear pattern matches, use heuristics
            return self._classify_by_heuristics(query)
        
        # Get the query type with the most matches
        query_type = max(matches, key=matches.get)
        
        # Calculate confidence based on match distribution
        total_matches = sum(matches.values())
        confidence = matches[query_type] / max(1, total_matches)
        
        logger.debug(f"Classified query as {query_type} with confidence {confidence:.2f}")
        return query_type, round(confidence, 2)
    
    def _classify_by_heuristics(self, query):
        """
        Classify query using heuristics when pattern matching is insufficient.
        
        Args:
            query (str): The user query
            
        Returns:
            tuple: (query_type, confidence)
        """
        # Simple heuristics:
        # - Question marks suggest factual queries
        # - Short queries tend to be factual
        # - Longer, complex queries tend to be analytical
        # - Queries with certain sentence structures suggest creative tasks
        
        # Check for question mark
        if '?' in query:
            return 'factual', 0.6
        
        # Check query length
        tokens = query.split()
        if len(tokens) < 5:
            return 'factual', 0.5
        elif len(tokens) > 15:
            return 'analytical', 0.5
        
        # Default to slightly creative with low confidence
        return 'creative', 0.4
    
    def extract_entities(self, query):
        """
        Extract key entities from the query.
        
        Args:
            query (str): The user query
            
        Returns:
            list: Extracted entities
        """
        # Simple entity extraction:
        # 1. Remove common words
        # 2. Identify potential noun phrases
        # 3. Return the most likely entities
        
        if not query:
            return []
        
        # Split into tokens
        tokens = query.split()
        
        # Remove common words (simple stopword filtering)
        stopwords = {'a', 'an', 'the', 'and', 'or', 'but', 'if', 'then', 'is', 'are',
                     'was', 'were', 'be', 'been', 'being', 'in', 'on', 'at', 'to', 'for',
                     'with', 'by', 'about', 'of', 'this', 'that', 'these', 'those'}
        
        filtered_tokens = [t for t in tokens if t.lower() not in stopwords]
        
        # Simple entity extraction (consecutive capitalized words)
        entities = []
        current_entity = []
        
        for token in filtered_tokens:
            if token and token[0].isupper():
                current_entity.append(token)
            else:
                if current_entity:
                    entities.append(' '.join(current_entity))
                    current_entity = []
        
        # Add final entity if any
        if current_entity:
            entities.append(' '.join(current_entity))
        
        # Add single nouns (simplified)
        for token in filtered_tokens:
            if token.lower() not in [e.lower() for e in entities] and len(token) > 3:
                entities.append(token)
        
        return entities[:5]  # Limit to top 5 entities
    
    def estimate_complexity(self, query):
        """
        Estimate query complexity for routing decisions.
        
        Args:
            query (str): The user query
            
        Returns:
            float: Complexity score (0.0-1.0)
        """
        if not query:
            return 0.0
        
        # Factors that contribute to complexity:
        # 1. Query length
        # 2. Vocabulary diversity
        # 3. Presence of complex logical structures
        # 4. Multiple sub-questions or requirements
        
        # Calculate length complexity
        tokens = query.split()
        length_score = min(1.0, len(tokens) / 50.0)
        
        # Calculate vocabulary diversity
        unique_tokens = set(token.lower() for token in tokens)
        diversity_score = min(1.0, len(unique_tokens) / max(1, len(tokens)))
        
        # Check for logical connectors and complex structures
        complex_indicators = ['if', 'then', 'because', 'therefore', 'however', 
                              'nevertheless', 'although', 'despite', 'while', 
                              'whereas', 'furthermore', 'moreover']
        
        structure_score = min(1.0, sum(1 for word in tokens 
                               if word.lower() in complex_indicators) / 5.0)
        
        # Check for multiple questions
        question_count = query.count('?')
        multi_question_score = min(1.0, question_count / 3.0)
        
        # Calculate weighted complexity score
        complexity = (
            length_score * 0.3 +
            diversity_score * 0.3 +
            structure_score * 0.3 +
            multi_question_score * 0.1
        )
        
        return round(min(1.0, complexity), 2)

class BiasAttenuation:
    """
    Implements bias attenuation mechanism with multi-perspective response generation.
    """
    def __init__(self):
        self.perspective_types = ["neutral", "opposing", "alternative"]
        self.distribution = {
            "neutral": 0.33,
            "opposing": 0.33,
            "alternative": 0.34
        }
        logger.info("Bias Attenuation initialized")
    
    def select_perspective(self, query_type=None):
        """
        Select a balanced perspective type for response generation.
        
        Args:
            query_type (str): Optional query type to influence selection
            
        Returns:
            str: Selected perspective type
        """
        # Adjust distribution based on query type
        adjusted_distribution = self.distribution.copy()
        
        if query_type == "factual":
            # Factual queries should prioritize neutral perspective
            adjusted_distribution = {
                "neutral": 0.6,
                "opposing": 0.2,
                "alternative": 0.2
            }
        elif query_type == "analytical":
            # Analytical queries should balance perspectives
            adjusted_distribution = {
                "neutral": 0.3,
                "opposing": 0.4,
                "alternative": 0.3
            }
        
        # Select perspective based on adjusted distribution
        perspective = random.choices(
            self.perspective_types,
            weights=[adjusted_distribution[p] for p in self.perspective_types]
        )[0]
        
        logger.debug(f"Selected {perspective} perspective for response")
        return perspective
    
    def generate_multi_perspective_response(self, query, base_response):
        """
        Generate a response that incorporates multiple perspectives.
        
        Args:
            query (str): User query
            base_response (str): Base response to enhance
            
        Returns:
            str: Multi-perspective response
        """
        # Select primary perspective
        primary = self.select_perspective()
        
        # Generate response with perspective framing
        if primary == "neutral":
            framing = "Considering this question objectively, "
            response = f"{framing}{base_response}"
        elif primary == "opposing":
            framing = "While some might think differently, an alternative perspective is that "
            response = f"{framing}{base_response}"
        else:  # alternative
            framing = "Looking at this from a different angle, "
            response = f"{framing}{base_response}"
        
        return response
