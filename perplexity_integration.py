"""
Perplexity API Integration for Neuronas
=======================================

This module integrates Perplexity AI for complex reasoning tasks
in the Neuronas cognitive system.
"""

import os
import json
import logging
import requests
import time
from typing import Dict, List, Any, Optional
from datetime import datetime

# Import secure key management
try:
    from simple_secure_keys import NeuronasKeyManager
    SECURE_KEYS_AVAILABLE = True
except ImportError:
    SECURE_KEYS_AVAILABLE = False
    logging.warning("Secure key management not available")

# Set up logging
logger = logging.getLogger(__name__)

class PerplexityIntegration:
    """
    Perplexity AI integration for complex reasoning and research tasks
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Perplexity integration with secure key management
        
        Args:
            api_key: Perplexity API key (optional, will use secure key manager if not provided)
        """
        # Try secure key manager first, then environment, then provided key
        if SECURE_KEYS_AVAILABLE and not api_key:
            key_manager = NeuronasKeyManager()
            self.api_key = key_manager.get_api_key('perplexity')
        else:
            self.api_key = api_key or os.getenv('PERPLEXITY_API_KEY')
        
        self.base_url = "https://api.perplexity.ai"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # Updated available models based on current Perplexity API
        self.models = {
            'fast': 'sonar',
            'balanced': 'sonar-pro', 
            'research': 'sonar-reasoning'
        }
        
        # Validate API key
        if not self.api_key:
            if SECURE_KEYS_AVAILABLE:
                logger.warning("No Perplexity API key found. Run 'python simple_secure_keys.py setup' to configure.")
            else:
                logger.warning("No Perplexity API key found. Set PERPLEXITY_API_KEY environment variable.")
    
    def is_available(self) -> bool:
        """Check if Perplexity API is available"""
        return bool(self.api_key)
    
    def research_query(self, query: str, model: str = 'balanced', 
                      max_tokens: int = 1000, temperature: float = 0.2) -> Dict[str, Any]:
        """
        Perform a research query using Perplexity's online models
        
        Args:
            query: Research question or prompt
            model: Model type ('fast', 'balanced', 'research')
            max_tokens: Maximum tokens in response
            temperature: Creativity level (0.0-2.0)
            
        Returns:
            Dictionary with response data
        """
        if not self.is_available():
            return {
                'success': False,
                'error': 'Perplexity API not available',
                'response': ''
            }
        
        try:
            model_name = self.models.get(model, self.models['balanced'])
            
            payload = {
                "model": model_name,
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a helpful research assistant with access to current information. Provide accurate, well-sourced responses."
                    },
                    {
                        "role": "user", 
                        "content": query
                    }
                ],
                "max_tokens": max_tokens,
                "temperature": temperature,
                "top_p": 0.9,
                "return_related_questions": True,
                "search_mode": "web"
            }
            
            start_time = time.time()
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=self.headers,
                json=payload,
                timeout=30
            )
            processing_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                
                return {
                    'success': True,
                    'response': data['choices'][0]['message']['content'],
                    'model': model_name,
                    'usage': data.get('usage', {}),
                    'citations': data.get('citations', []),
                    'search_results': data.get('search_results', []),
                    'processing_time': processing_time,
                    'timestamp': datetime.utcnow().isoformat()
                }
            else:
                logger.error(f"Perplexity API error: {response.status_code} - {response.text}")
                return {
                    'success': False,
                    'error': f"API error: {response.status_code}",
                    'response': ''
                }
                
        except requests.RequestException as e:
            logger.error(f"Request error: {e}")
            return {
                'success': False,
                'error': f"Request failed: {str(e)}",
                'response': ''
            }
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return {
                'success': False,
                'error': f"Unexpected error: {str(e)}",
                'response': ''
            }
    
    def complex_reasoning(self, problem: str, context: Optional[str] = None,
                         reasoning_type: str = 'analytical') -> Dict[str, Any]:
        """
        Perform complex reasoning tasks
        
        Args:
            problem: Complex problem to solve
            context: Additional context or background information
            reasoning_type: Type of reasoning ('analytical', 'creative', 'research')
            
        Returns:
            Dictionary with reasoning response
        """
        # Construct enhanced prompt based on reasoning type
        if reasoning_type == 'analytical':
            system_prompt = """You are an analytical reasoning expert. Break down complex problems step-by-step using logical analysis, mathematical reasoning, and systematic evaluation. Provide clear reasoning chains and justify your conclusions."""
            
        elif reasoning_type == 'creative':
            system_prompt = """You are a creative problem-solving expert. Approach problems with innovative thinking, consider unconventional solutions, and explore novel connections. Use lateral thinking and imaginative approaches."""
            
        elif reasoning_type == 'research':
            system_prompt = """You are a research analyst with access to current information. Thoroughly investigate the problem, gather relevant data, analyze multiple perspectives, and provide evidence-based conclusions with proper citations."""
            
        else:
            system_prompt = """You are a comprehensive reasoning assistant. Combine analytical, creative, and research approaches to provide well-rounded solutions to complex problems."""
        
        # Build the query
        query_parts = [problem]
        if context:
            query_parts.insert(0, f"Context: {context}")
        
        full_query = "\n\n".join(query_parts)
        
        # Use research model for complex reasoning
        return self.research_query(
            query=full_query,
            model='research',
            max_tokens=1500,
            temperature=0.3 if reasoning_type == 'analytical' else 0.7
        )
    
    def multi_perspective_analysis(self, topic: str, perspectives: List[str] = None) -> Dict[str, Any]:
        """
        Analyze a topic from multiple perspectives
        
        Args:
            topic: Topic to analyze
            perspectives: List of perspectives to consider
            
        Returns:
            Dictionary with multi-perspective analysis
        """
        if not perspectives:
            perspectives = ['technical', 'ethical', 'economic', 'social', 'environmental']
        
        query = f"""
        Analyze the following topic from multiple perspectives:
        
        Topic: {topic}
        
        Please provide analysis from these perspectives:
        {', '.join(perspectives)}
        
        For each perspective, provide:
        1. Key considerations
        2. Potential impacts
        3. Relevant evidence or data
        4. Conclusions or recommendations
        
        Finally, provide an integrated summary that synthesizes insights from all perspectives.
        """
        
        return self.research_query(
            query=query,
            model='research',
            max_tokens=2000,
            temperature=0.4
        )
    
    def fact_check_and_verify(self, claim: str, context: Optional[str] = None) -> Dict[str, Any]:
        """
        Fact-check and verify claims using current information
        
        Args:
            claim: Claim to fact-check
            context: Additional context
            
        Returns:
            Dictionary with fact-check results
        """
        query = f"""
        Please fact-check the following claim using current, reliable sources:
        
        Claim: {claim}
        """
        
        if context:
            query += f"\n\nContext: {context}"
        
        query += """
        
        Please provide:
        1. Verification status (True/False/Partially True/Unclear)
        2. Supporting evidence with sources
        3. Contradicting evidence (if any)
        4. Overall assessment and confidence level
        5. Relevant citations
        """
        
        return self.research_query(
            query=query,
            model='research',
            max_tokens=1200,
            temperature=0.1  # Low temperature for accuracy
        )

# Integration with Neuronas cognitive system
def integrate_perplexity_with_neuronas(app, memory_system):
    """
    Integrate Perplexity API with Neuronas memory and cognitive systems
    
    Args:
        app: Flask application instance
        memory_system: Neuronas memory system
    """
    perplexity = PerplexityIntegration()
    
    if perplexity.is_available():
        app.perplexity = perplexity
        logger.info("Perplexity integration enabled")
        
        # Store integration info in memory
        if hasattr(memory_system, 'store_analytical_memory'):
            memory_system.store_analytical_memory(
                'perplexity_integration',
                json.dumps({
                    'status': 'enabled',
                    'models': list(perplexity.models.keys()),
                    'timestamp': datetime.utcnow().isoformat()
                }),
                importance=0.8
            )
    else:
        logger.warning("Perplexity integration not available - API key missing")

# Example usage functions for development
def test_perplexity_integration():
    """Test function for development"""
    perplexity = PerplexityIntegration()
    
    if not perplexity.is_available():
        print("❌ Perplexity API not available")
        return False
    
    # Test basic research query
    result = perplexity.research_query("What are the latest developments in quantum computing?")
    
    if result['success']:
        print("✅ Perplexity integration working")
        print(f"Response length: {len(result['response'])} characters")
        print(f"Processing time: {result['processing_time']:.2f}s")
        return True
    else:
        print(f"❌ Perplexity test failed: {result['error']}")
        return False

if __name__ == "__main__":
    test_perplexity_integration()
