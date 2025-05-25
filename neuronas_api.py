
"""
Neuronas API - Interface for interacting with the Neuronas AI system
"""

import json
import time
import random
import logging
from core_modules.core_engine import CoreEngine
from core_modules.d2_receptor_modulation import D2ReceptorModulation
from core_modules.neural_pathway_router import NeuralPathwayRouter
from core_modules.d2stib_acceleration import D2STIBAccelerator
from core_modules.quantum_decision_system import QuantumDecisionSystem
from neuronas_architecture_config import neuronas_architecture

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NeuronasAPI:
    """API for interfacing with the Neuronas AI system"""
    
    def __init__(self, config_path=None):
        """Initialize the Neuronas API"""
        self.core_engine = CoreEngine(config_path)
        self.d2_modulation = D2ReceptorModulation()
        self.pathway_router = NeuralPathwayRouter()
        self.d2stib = D2STIBAccelerator()
        self.quantum_system = QuantumDecisionSystem()
        self.architecture = neuronas_architecture
        
        self.session_id = f"neuronas-{int(time.time())}"
        logger.info(f"Neuronas API initialized with session ID: {self.session_id}")
        
    def process_query(self, query_text, d2_params=None, context=None):
        """
        Process a query through the Neuronas system
        
        Args:
            query_text: The query text to process
            d2_params: Optional D2 modulation parameters (dict with stim/pin values)
            context: Optional context information
            
        Returns:
            Response with processing details
        """
        start_time = time.time()
        
        # 1. Classify query
        query_classification = self.pathway_router.classify_query(query_text)
        
        # 2. Set D2 modulation (or use suggested optimal values)
        if d2_params is None:
            suggested = self.d2_modulation.suggest_optimal_modulation(
                query_classification["classification"],
                random.uniform(0.3, 0.7)  # Random complexity for demo
            )
            d2_params = {
                "stim": suggested["suggested_stim"],
                "pin": suggested["suggested_pin"]
            }
            
        # 3. Process through core engine
        response = self.core_engine.process_input(query_text, context, d2_params)
        
        # 4. Prepare the final response
        processing_time = time.time() - start_time
        
        # Add system metrics
        response["session_id"] = self.session_id
        response["processing_time"] = processing_time
        response["query_classification"] = query_classification
        response["system_metrics"] = self.get_system_metrics()
        
        return response
    
    def set_d2_modulation(self, stim_level, pin_level):
        """Set D2 receptor modulation levels"""
        d2_activation = self.core_engine.set_d2_modulation(stim_level, pin_level)
        return {
            "d2_activation": d2_activation,
            "d2stim_level": self.core_engine.d2stim_level,
            "d2pin_level": self.core_engine.d2pin_level,
            "cognitive_effects": self.d2_modulation.get_cognitive_effects()
        }
    
    def adjust_attention(self, level):
        """Adjust system attention level"""
        attention = self.core_engine.adjust_attention(level)
        return {
            "attention": attention,
            "processing_efficiency": self.architecture.get_processing_efficiency()
        }
    
    def get_system_metrics(self):
        """Get comprehensive system metrics"""
        return self.core_engine.get_system_metrics()
    
    def get_memory_stats(self):
        """Get memory system statistics"""
        # In a full implementation, this would connect to storage_manager
        return {
            "tier_stats": {
                "L1": {"capacity": 20, "usage": random.uniform(0.3, 0.7)},
                "L2": {"capacity": 50, "usage": random.uniform(0.2, 0.5)},
                "L3": {"capacity": 100, "usage": random.uniform(0.1, 0.3)}
            },
            "compression_ratio": {
                "L1_to_L2": 0.9,
                "L2_to_L3": 0.75,
                "overall": 0.82
            },
            "retrieval_efficiency": random.uniform(0.85, 0.98)
        }
    
    def get_architecture_config(self):
        """Get the current architecture configuration"""
        return self.architecture.config
    
    def reset_system(self):
        """Reset the system to default state"""
        self.core_engine.set_d2_modulation(0.0, 0.0)
        self.core_engine.adjust_attention(1.0)
        self.d2stib.reset_stats()
        self.quantum_system.reset_quantum_states()
        self.pathway_router.reset_activations()
        
        return {
            "status": "reset_complete",
            "session_id": self.session_id,
            "d2_activation": self.core_engine.d2_activation,
            "attention": self.core_engine.attention
        }

# Create a singleton instance
neuronas = NeuronasAPI()
