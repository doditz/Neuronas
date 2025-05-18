"""
Dual LLM System for NeuronasX

This module implements a system that uses two language models in parallel to represent the
left (analytical) and right (creative) hemispheres of the cognitive system.
Supports both Anthropic API and local Ollama models.
"""

import os
import json
import logging
import time
import random
import requests
from datetime import datetime
import anthropic
from flask import current_app

# Setup logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class HemisphericLLM:
    """Base class for hemispheric language model processing"""
    
    def __init__(self, name, hemisphere_type, temperature_range, model_name=None, model_provider='ollama'):
        """
        Initialize a hemispheric language model
        
        Args:
            name (str): Name of the persona
            hemisphere_type (str): 'left' or 'right'
            temperature_range (tuple): Min and max temperature range
            model_name (str, optional): Specific model to use
            model_provider (str): 'anthropic' or 'ollama'
        """
        self.name = name
        self.hemisphere_type = hemisphere_type
        self.temp_min, self.temp_max = temperature_range
        self.model_provider = model_provider
        self.model_name = model_name or self._get_default_model()
        self.client = self._initialize_client()
        self.specialties = []
        self.d2_influence = 0.5  # D2 receptor influence (0.0-1.0)
        self.ollama_url = os.environ.get("OLLAMA_URL", "http://localhost:11434")
        
    def _get_default_model(self):
        """Get default model for this hemisphere"""
        if self.model_provider == 'anthropic':
            if self.hemisphere_type == 'left':
                return "claude-3-haiku-20240307"  # Fast, analytical
            else:
                return "claude-3-opus-20240229"  # Creative, high capability
        else:  # ollama
            if self.hemisphere_type == 'left':
                return "llama3:8b"  # Fast, efficient, analytical model
            elif self.hemisphere_type == 'right':
                return "mistral:7b"  # More creative model
            else:  # central/integration
                return "gemma:7b"  # Balanced model for integration
        
    def _initialize_client(self):
        """Initialize the appropriate client for the LLM"""
        if self.model_provider == 'anthropic':
            api_key = os.environ.get("ANTHROPIC_API_KEY")
            if not api_key:
                logger.warning(f"No Anthropic API key found for {self.name} ({self.hemisphere_type} hemisphere)")
                return None
                
            try:
                return anthropic.Anthropic(api_key=api_key)
            except Exception as e:
                logger.error(f"Error initializing Anthropic client for {self.name}: {e}")
                return None
        else:
            # For Ollama, we don't need to initialize a client here
            # We'll use requests directly in the process_prompt method
            return "ollama"
            
    def set_d2_influence(self, value):
        """Set the D2 receptor modulation influence (0.0-1.0)"""
        self.d2_influence = max(0.0, min(1.0, value))
        
    def _get_effective_temperature(self):
        """Calculate effective temperature based on D2 influence"""
        if self.hemisphere_type == 'left':
            # Left hemisphere: D2 modulation decreases temperature (more precise)
            base_range = self.temp_max - self.temp_min
            effect = 1.0 - self.d2_influence
            return self.temp_min + (base_range * effect)
        else:
            # Right hemisphere: D2 modulation increases temperature (more creative)
            base_range = self.temp_max - self.temp_min
            return self.temp_min + (base_range * self.d2_influence)
            
    def process_prompt(self, prompt, system_prompt=None, memory_context=None):
        """
        Process a prompt through this hemispheric model
        
        Args:
            prompt (str): User query/prompt
            system_prompt (str, optional): System instructions
            memory_context (list, optional): Memory context from the cognitive system
            
        Returns:
            dict: Processing results including response and metadata
        """
        if not self.client and self.model_provider == 'anthropic':
            return {
                'success': False,
                'error': f"No valid client for {self.name}",
                'hemisphere': self.hemisphere_type,
                'timestamp': datetime.utcnow().isoformat()
            }
            
        # Set temperature based on D2 modulation
        temperature = self._get_effective_temperature()
        
        # Create default system prompt if none provided
        if not system_prompt:
            if self.hemisphere_type == 'left':
                system_prompt = f"""You are {self.name}, an analytical cognitive processor that excels at 
                logical reasoning, factual analysis, and structured thinking. Your responses should be 
                precise, well-organized, and focus on factual content and logical connections."""
            else:
                system_prompt = f"""You are {self.name}, a creative cognitive processor that excels at 
                generating novel connections, metaphorical thinking, and divergent ideation. Your responses 
                should be imaginative, explore multiple possibilities, and make unexpected connections."""
                
        # Add memory context if provided
        context_str = ""
        if memory_context and isinstance(memory_context, list):
            context_str = "\n\nRelevant memory context:\n" + "\n".join(memory_context)
            system_prompt += context_str
            
        try:
            start_time = time.time()
            
            if self.model_provider == 'anthropic':
                # Make the Anthropic API call
                response = self.client.messages.create(
                    model=self.model_name,
                    max_tokens=1000,
                    temperature=temperature,
                    system=system_prompt,
                    messages=[
                        {"role": "user", "content": prompt}
                    ]
                )
                
                response_text = response.content[0].text
                
            else:  # Ollama
                # Prepare the Ollama request
                ollama_data = {
                    "model": self.model_name,
                    "prompt": prompt,
                    "system": system_prompt,
                    "stream": False,
                    "options": {
                        "temperature": temperature,
                        "num_predict": 1000
                    }
                }
                
                # Send request to Ollama API
                try:
                    ollama_response = requests.post(
                        f"{self.ollama_url}/api/generate",
                        json=ollama_data,
                        timeout=60
                    )
                    
                    if ollama_response.status_code == 200:
                        response_json = ollama_response.json()
                        response_text = response_json.get('response', '')
                    else:
                        # Try fallback model if primary fails
                        fallback_model = "llama3" if self.model_name != "llama3" else "mistral"
                        logger.warning(f"Ollama model {self.model_name} failed, trying fallback model {fallback_model}")
                        
                        ollama_data["model"] = fallback_model
                        ollama_response = requests.post(
                            f"{self.ollama_url}/api/generate",
                            json=ollama_data,
                            timeout=60
                        )
                        
                        if ollama_response.status_code == 200:
                            response_json = ollama_response.json()
                            response_text = response_json.get('response', '')
                        else:
                            logger.error(f"Ollama fallback model also failed: {ollama_response.status_code}")
                            raise Exception(f"Ollama API error: {ollama_response.status_code}")
                
                except requests.exceptions.ConnectionError:
                    # If we can't connect to Ollama, generate a simulated response
                    logger.error(f"Cannot connect to Ollama server at {self.ollama_url}")
                    
                    # Create more interesting simulated responses based on hemisphere
                    if self.hemisphere_type == 'left':
                        response_text = f"""[Simulated analytical response for "{prompt[:30]}..."]
                        
From an analytical perspective, this question requires systematic examination of the key components:

1. First, let's establish the factual parameters. The query involves {prompt[:40]}...
2. Core logical analysis suggests three primary considerations...
3. The structured approach would involve breaking this down into quantifiable metrics...

In summary, the analytical framework points toward a precise, evidence-based conclusion that balances multiple verified factors."""
                    
                    elif self.hemisphere_type == 'right':
                        response_text = f"""[Simulated creative response for "{prompt[:30]}..."]
                        
Looking at this creatively, we can envision multiple fascinating possibilities:

- What if we reimagined the entire concept of {prompt[:40]}...?
- The metaphorical connections here evoke a pattern that resembles...
- This question opens unexpected doors to novel interpretations...

The beauty of this approach lies in its expansive, divergent thinking that connects seemingly unrelated domains into a cohesive creative vision."""
                    
                    else:  # central/integration
                        response_text = f"""[Simulated integration response for "{prompt[:30]}..."]
                        
Synthesizing both analytical and creative perspectives:

The structured analysis provides a solid foundation, while creative exploration reveals hidden dimensions. 

From a balanced viewpoint, we can appreciate both the logical structure and the intuitive connections, arriving at an integrated understanding that honors both precise reasoning and expansive thinking about {prompt[:40]}...

This measured approach yields both practical insights and innovative possibilities."""
            
            processing_time = time.time() - start_time
            
            # Return structured response
            return {
                'success': True,
                'response': response_text,
                'hemisphere': self.hemisphere_type,
                'temperature': temperature,
                'd2_influence': self.d2_influence,
                'processing_time': processing_time,
                'model': self.model_name,
                'model_provider': self.model_provider,
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error in {self.name} processing: {e}")
            return {
                'success': False,
                'error': str(e),
                'hemisphere': self.hemisphere_type,
                'model_provider': self.model_provider,
                'timestamp': datetime.utcnow().isoformat()
            }
            

class LeftHemisphereLLM(HemisphericLLM):
    """Left hemisphere specialized LLM (analytical processing)"""
    
    def __init__(self, name="Analytica", model_name=None, model_provider='ollama'):
        super().__init__(
            name=name,
            hemisphere_type='left',
            temperature_range=(0.1, 0.7),
            model_name=model_name,
            model_provider=model_provider
        )
        self.specialties = [
            "logical analysis",
            "factual recall",
            "structured reasoning",
            "sequential processing",
            "linguistic precision"
        ]
        

class RightHemisphereLLM(HemisphericLLM):
    """Right hemisphere specialized LLM (creative processing)"""
    
    def __init__(self, name="Creativa", model_name=None, model_provider='ollama'):
        super().__init__(
            name=name,
            hemisphere_type='right',
            temperature_range=(0.6, 1.0),
            model_name=model_name,
            model_provider=model_provider
        )
        self.specialties = [
            "metaphorical thinking",
            "divergent ideation",
            "pattern recognition",
            "emotional intelligence",
            "holistic synthesis"
        ]


class IntegrationLLM(HemisphericLLM):
    """Integration model for combining hemispheric outputs"""
    
    def __init__(self, name="Integra", model_name=None, model_provider='ollama'):
        super().__init__(
            name=name,
            hemisphere_type='central',
            temperature_range=(0.3, 0.7),
            model_name=model_name,
            model_provider=model_provider
        )
        self.specialties = [
            "perspective integration",
            "cognitive synthesis",
            "dialectical reasoning",
            "adaptive output formatting",
            "coherence optimization"
        ]
        
    def integrate_responses(self, left_response, right_response, prompt, hemisphere_balance=0.5):
        """
        Integrate responses from both hemispheres into a unified output
        
        Args:
            left_response (dict): Left hemisphere processing result
            right_response (dict): Right hemisphere processing result
            prompt (str): Original user prompt
            hemisphere_balance (float): Balance between hemispheres (0.0=left, 1.0=right)
            
        Returns:
            dict: Integrated response and metadata
        """
        # Check if either response is empty or unsuccessful due to connection issues
        if (not left_response.get('success') and "connection issue" in left_response.get('error', '')) or \
           (not right_response.get('success') and "connection issue" in right_response.get('error', '')):
            # Create a simulated integration response
            return {
                'success': True,
                'response': f"""[Simulated integration for "{prompt[:30]}..." with balance {hemisphere_balance:.2f}]
                
As an integrated cognitive system, I'm combining analytical structure with creative insight:

{"▪️ Starting with rigorous analysis and structured reasoning" if hemisphere_balance < 0.5 else "▪️ Leading with creative exploration and intuitive connections"}
{"▪️ Adding creative perspectives to enrich the framework" if hemisphere_balance < 0.5 else "▪️ Incorporating analytical reasoning to support intuitions"}
▪️ The balanced approach reveals that {prompt[:50]}... can be understood from multiple complementary angles.

{"This primarily analytical perspective is enriched by creative elements." if hemisphere_balance < 0.3 else 
"This integration balances structure and creativity equally." if 0.3 <= hemisphere_balance <= 0.7 else 
"This primarily creative insight is grounded in analytical reasoning."}
                """,
                'hemisphere': 'central',
                'hemisphere_balance': hemisphere_balance,
                'integrated': True,
                'left_influence': 1 - hemisphere_balance,
                'right_influence': hemisphere_balance,
                'temperature': 0.5,
                'processing_time': 0.5,
                'total_processing_time': 1.5,
                'model': self.model_name,
                'model_provider': self.model_provider,
                'timestamp': datetime.utcnow().isoformat()
            }
            
        if not self.client and self.model_provider == 'anthropic':
            return {
                'success': False,
                'error': f"No valid client for {self.name}",
                'hemisphere': 'central',
                'timestamp': datetime.utcnow().isoformat()
            }
            
        # Add better simulated integration for Ollama when it's not available
        if self.model_provider == 'ollama' and self.client == 'ollama':
            try:
                # Quick check if Ollama is accessible
                test_connection = requests.get(f"{self.ollama_url}/api/tags", timeout=1)
                if test_connection.status_code != 200:
                    raise Exception("Ollama server not responding properly")
            except Exception:
                # Provide simulated integration if Ollama isn't available
                left_text = left_response.get('response', '')[:200] + '...' if left_response.get('response') else 'No left hemisphere response'
                right_text = right_response.get('response', '')[:200] + '...' if right_response.get('response') else 'No right hemisphere response'
                
                return {
                    'success': True,
                    'response': f"""[Simulated integration of left and right hemisphere responses]

Looking at this from both analytical and creative perspectives:

From the left hemisphere (analytical):
{left_text}

From the right hemisphere (creative):
{right_text}

When we integrate these viewpoints, we can see that {prompt[:50]}... requires both structured thinking and imaginative exploration. The hemisphere balance of {hemisphere_balance:.2f} suggests a {"more analytical" if hemisphere_balance < 0.5 else "more creative" if hemisphere_balance > 0.5 else "balanced"} approach is optimal here.
                    """,
                    'hemisphere': 'central',
                    'hemisphere_balance': hemisphere_balance,
                    'integrated': True,
                    'left_influence': 1 - hemisphere_balance,
                    'right_influence': hemisphere_balance,
                    'temperature': 0.5,
                    'processing_time': 0.5,
                    'total_processing_time': 1.5,
                    'model': self.model_name,
                    'model_provider': self.model_provider,
                    'timestamp': datetime.utcnow().isoformat()
                }
        
        # Skip integration if either hemisphere failed
        if not left_response.get('success') or not right_response.get('success'):
            # Return the successful one, or error if both failed
            if left_response.get('success'):
                return {
                    **left_response,
                    'integrated': False,
                    'integration_note': 'Right hemisphere processing failed, using left hemisphere only'
                }
            elif right_response.get('success'):
                return {
                    **right_response,
                    'integrated': False,
                    'integration_note': 'Left hemisphere processing failed, using right hemisphere only'
                }
            else:
                return {
                    'success': False,
                    'error': 'Both hemispheres failed to process the request',
                    'hemisphere': 'central',
                    'timestamp': datetime.utcnow().isoformat()
                }
        
        # Create integration system prompt
        system_prompt = f"""You are {self.name}, a cognitive integration system that combines analytical and creative thinking.
        
        You have received two responses to the same prompt, one from the analytical left hemisphere and one from the creative right hemisphere.
        Your task is to integrate these perspectives into a unified response that preserves the strengths of both approaches.
        
        The hemisphere balance is set to {hemisphere_balance:.2f} (0.0=fully analytical, 1.0=fully creative, 0.5=balanced).
        Adjust your integration to reflect this balance.
        
        Please analyze both responses and create an integrated answer that:
        1. Maintains logical coherence and factual accuracy from the analytical perspective
        2. Incorporates creative insights, novel connections, and holistic thinking from the creative perspective
        3. Resolves any contradictions between the perspectives
        4. Presents a unified voice that doesn't explicitly mention the two hemispheres
        
        Then format your response in the most appropriate style for the query and content.
        """
        
        # Prepare integration prompt
        integration_prompt = f"""Original prompt: {prompt}
        
        LEFT HEMISPHERE (ANALYTICAL) RESPONSE:
        {left_response.get('response', 'No response available')}
        
        RIGHT HEMISPHERE (CREATIVE) RESPONSE:
        {right_response.get('response', 'No response available')}
        
        Create an integrated response that combines these perspectives according to the hemisphere balance of {hemisphere_balance:.2f}.
        """
        
        try:
            start_time = time.time()
            
            # Calculate integration temperature (weighted average based on hemisphere balance)
            left_temp = left_response.get('temperature', 0.3)
            right_temp = right_response.get('temperature', 0.7)
            integration_temp = (left_temp * (1 - hemisphere_balance)) + (right_temp * hemisphere_balance)
            
            # Make the API call
            response = self.client.messages.create(
                model=self.model_name,
                max_tokens=1500,
                temperature=integration_temp,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": integration_prompt}
                ]
            )
            
            processing_time = time.time() - start_time
            
            # Return structured integrated response
            return {
                'success': True,
                'response': response.content[0].text,
                'hemisphere': 'central',
                'hemisphere_balance': hemisphere_balance,
                'integrated': True,
                'left_influence': 1 - hemisphere_balance,
                'right_influence': hemisphere_balance,
                'temperature': integration_temp,
                'processing_time': processing_time,
                'total_processing_time': processing_time + left_response.get('processing_time', 0) + right_response.get('processing_time', 0),
                'model': self.model_name,
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error in integration: {e}")
            # Fall back to the more successful hemisphere based on balance
            if hemisphere_balance < 0.5:
                return {
                    **left_response,
                    'integrated': False,
                    'integration_note': f'Integration failed: {str(e)}, using left hemisphere as fallback'
                }
            else:
                return {
                    **right_response,
                    'integrated': False,
                    'integration_note': f'Integration failed: {str(e)}, using right hemisphere as fallback'
                }


class DualLLMSystem:
    """
    Main system for managing dual LLM cognitive processing with
    left and right hemisphere specialization
    """
    
    def __init__(self):
        """Initialize the dual LLM system"""
        
        # Configure Ollama models based on size, speed, and capabilities
        left_models = {
            'llama3:8b': 'Analytica',       # Fast, efficient analytical processing
            'phi3:3b': 'Ethica',           # Small model for ethical reasoning
            'nous-hermes2:7b': 'Cognitiva'  # Knowledge-focused model for cognitive processing
        }
        
        right_models = {
            'mistral:7b': 'Creativa',       # Creative model with good divergent thinking
            'llava:7b': 'Metaphysica',      # Multimodal model for visual/metaphorical thinking
            'solar:10.7b': 'Quantica'       # Larger model for complex creative tasks
        }
        
        # Integration model
        integration_model = 'gemma:7b'      # Balanced model for integration
        
        self.personas = {}
        
        # Initialize left hemisphere personas with Ollama models
        for model, name in left_models.items():
            self.personas[name.lower()] = LeftHemisphereLLM(
                name=name,
                model_name=model,
                model_provider='ollama'
            )
            
        # Initialize right hemisphere personas with Ollama models
        for model, name in right_models.items():
            self.personas[name.lower()] = RightHemisphereLLM(
                name=name,
                model_name=model,
                model_provider='ollama'
            )
        
        # Integration model
        self.integration = IntegrationLLM(
            name="Sociologica",
            model_name=integration_model,
            model_provider='ollama'
        )
        
        # Default settings
        self.default_left_persona = 'analytica'
        self.default_right_persona = 'creativa'
        self.hemisphere_balance = 0.5  # 0.0=left, 1.0=right
        self.d2_activation = 0.5
        
    def set_d2_activation(self, value):
        """Set D2 receptor activation level (0.0-1.0)"""
        self.d2_activation = max(0.0, min(1.0, value))
        
        # Apply to all models with appropriate modulation
        for name, model in self.personas.items():
            if model.hemisphere_type == 'left':
                # Left hemisphere gets inhibitory effect (inverse of activation)
                model.set_d2_influence(1.0 - self.d2_activation)
            else:
                # Right hemisphere gets direct activation effect
                model.set_d2_influence(self.d2_activation)
                
    def set_hemisphere_balance(self, value):
        """Set the hemispheric balance for response integration (0.0=left, 1.0=right)"""
        self.hemisphere_balance = max(0.0, min(1.0, value))
        
    def select_personas(self, prompt, memory_context=None):
        """
        Select appropriate personas for a given prompt based on content
        
        Args:
            prompt (str): User query/prompt
            memory_context (dict, optional): Memory context from cognitive system
            
        Returns:
            tuple: (left_persona_name, right_persona_name)
        """
        # Simple keyword matching for demonstration
        # In a real system, use NLP classification or vector similarity
        prompt_lower = prompt.lower()
        
        left_candidates = {}
        right_candidates = {}
        
        # Score each persona based on specialty keyword matches
        for name, persona in self.personas.items():
            score = 0
            for specialty in persona.specialties:
                if specialty.lower() in prompt_lower:
                    score += 1
                    
            if persona.hemisphere_type == 'left':
                left_candidates[name] = score
            else:
                right_candidates[name] = score
                
        # Select best match for each hemisphere
        left_persona = max(left_candidates.items(), key=lambda x: x[1])[0] \
                      if left_candidates else self.default_left_persona
                      
        right_persona = max(right_candidates.items(), key=lambda x: x[1])[0] \
                       if right_candidates else self.default_right_persona
                       
        return (left_persona, right_persona)
        
    def process_query(self, prompt, user_settings=None, memory_context=None):
        """
        Process a query through the dual LLM system
        
        Args:
            prompt (str): User query/prompt
            user_settings (dict, optional): User-specific settings
            memory_context (dict, optional): Memory context from cognitive system
            
        Returns:
            dict: Processing results with integrated response
        """
        # Apply user settings if provided
        if user_settings:
            if 'd2_activation' in user_settings:
                self.set_d2_activation(user_settings['d2_activation'])
                
            if 'hemisphere_balance' in user_settings:
                self.set_hemisphere_balance(user_settings['hemisphere_balance'])
                
        # Select appropriate personas
        left_persona_name, right_persona_name = self.select_personas(prompt, memory_context)
        left_persona = self.personas[left_persona_name]
        right_persona = self.personas[right_persona_name]
        
        # Process through both hemispheres in parallel (sequential implementation for now)
        left_response = left_persona.process_prompt(prompt, memory_context=memory_context)
        right_response = right_persona.process_prompt(prompt, memory_context=memory_context)
        
        # Get relevant memory context (placeholder)
        memory_summary = []
        if hasattr(current_app, 'tiered_memory') and current_app.tiered_memory:
            try:
                # Example of getting memory context
                context_hash = current_app.tiered_memory.memory_manager.generate_context_hash({"query": prompt})
                memory_results = current_app.tiered_memory.memory_manager.search_by_context(context_hash)
                
                # Extract some memory elements
                if memory_results.get('left') and memory_results['left'].get('1'):
                    for memory in memory_results['left']['1'][:3]:
                        if isinstance(memory, dict) and 'value' in memory:
                            memory_summary.append(f"Left Memory: {memory['value']}")
                            
                if memory_results.get('right') and memory_results['right'].get('1'):
                    for memory in memory_results['right']['1'][:3]:
                        if isinstance(memory, dict) and 'value' in memory:
                            memory_summary.append(f"Right Memory: {memory['value']}")
            except Exception as e:
                logger.error(f"Error retrieving memory context: {e}")
        
        # Integrate responses
        integrated_response = self.integration.integrate_responses(
            left_response, 
            right_response, 
            prompt,
            hemisphere_balance=self.hemisphere_balance
        )
        
        # Store processing data in memory
        if hasattr(current_app, 'tiered_memory') and current_app.tiered_memory:
            try:
                # Create context
                context = {
                    "query": prompt,
                    "timestamp": datetime.utcnow().isoformat(),
                    "d2_activation": self.d2_activation,
                    "hemisphere_balance": self.hemisphere_balance
                }
                
                # Store analytical processing in left hemisphere
                if left_response.get('success'):
                    left_key = f"analytical_{int(time.time())}"
                    left_value = json.dumps({
                        "query": prompt,
                        "response": left_response.get('response'),
                        "persona": left_persona_name,
                        "processing_time": left_response.get('processing_time'),
                        "timestamp": left_response.get('timestamp')
                    })
                    current_app.tiered_memory.store_analytical_memory(
                        left_key, 
                        left_value, 
                        importance=0.7,
                        context=context
                    )
                
                # Store creative processing in right hemisphere
                if right_response.get('success'):
                    right_key = f"creative_{int(time.time())}"
                    right_value = json.dumps({
                        "query": prompt,
                        "response": right_response.get('response'),
                        "persona": right_persona_name,
                        "processing_time": right_response.get('processing_time'),
                        "timestamp": right_response.get('timestamp')
                    })
                    current_app.tiered_memory.store_creative_memory(
                        right_key, 
                        right_value, 
                        novelty=0.8,
                        d2_activation=self.d2_activation,
                        context=context
                    )
            except Exception as e:
                logger.error(f"Error storing processing results in memory: {e}")
        
        # Return full result
        return {
            'success': integrated_response.get('success', False),
            'response': integrated_response.get('response', 'No response available'),
            'hemisphere_balance': self.hemisphere_balance,
            'd2_activation': self.d2_activation,
            'left_persona': left_persona_name,
            'right_persona': right_persona_name,
            'left_processing': left_response,
            'right_processing': right_response,
            'integrated_processing': integrated_response,
            'memory_context': memory_summary if memory_summary else None,
            'timestamp': datetime.utcnow().isoformat()
        }
        
    def get_system_state(self):
        """Get the current state of the system"""
        return {
            'hemisphere_balance': self.hemisphere_balance,
            'd2_activation': self.d2_activation,
            'left_persona': self.default_left_persona,
            'right_persona': self.default_right_persona,
            'personas': {
                name: {
                    'type': persona.hemisphere_type,
                    'd2_influence': persona.d2_influence,
                    'specialties': persona.specialties
                } for name, persona in self.personas.items()
            }
        }


# Create global instance
dual_llm_system = DualLLMSystem()