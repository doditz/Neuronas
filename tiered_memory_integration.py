"""
This work is licensed under CC BY-NC 4.0 International.
Commercial use requires prior written consent and compensation.
Contact: sebastienbrulotte@gmail.com
Attribution: Sebastien Brulotte aka [ Doditz ]

This document is part of the NEURONAS cognitive system.
Core modules referenced: BRONAS (Ethical Reflex Filter) and QRONAS (Probabilistic Symbolic Vector Engine).
All outputs are subject to integrity validation and ethical compliance enforced by BRONAS.
"""

"""
Tiered Memory Integration Module for NeuronasX

This module integrates the dual hemispheric memory system with the core cognitive engine.
"""

import logging
import threading
import time
from datetime import datetime
from cognitive_memory_manager import CognitiveMemoryManager

# Setup logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class TieredMemorySystem:
    """
    Manages integration between the NeuronasX cognitive engine and 
    the dual hemispheric tiered memory framework.
    """
    
    def __init__(self, maintenance_interval=300):
        """
        Initialize the tiered memory system.
        
        Args:
            maintenance_interval (int): Seconds between memory maintenance operations
        """
        self.memory_manager = CognitiveMemoryManager()
        self.maintenance_interval = maintenance_interval
        self.maintenance_thread = None
        self.running = False
        self.last_maintenance = None
        self.stats = None
        
    def start_maintenance_thread(self):
        """Start background thread for automatic memory maintenance."""
        if self.maintenance_thread is None or not self.maintenance_thread.is_alive():
            self.running = True
            self.maintenance_thread = threading.Thread(
                target=self._maintenance_worker,
                daemon=True
            )
            self.maintenance_thread.start()
            logger.info("Memory maintenance thread started")
            
    def stop_maintenance_thread(self):
        """Stop the background maintenance thread."""
        self.running = False
        if self.maintenance_thread and self.maintenance_thread.is_alive():
            self.maintenance_thread.join(timeout=1.0)
            logger.info("Memory maintenance thread stopped")
            
    def _maintenance_worker(self):
        """Background worker that performs periodic memory maintenance."""
        while self.running:
            try:
                self.stats = self.memory_manager.run_memory_maintenance()
                self.last_maintenance = datetime.now()
                logger.info(f"Memory maintenance completed: {self.stats}")
            except Exception as e:
                logger.error(f"Error in memory maintenance: {e}")
                
            # Sleep for the maintenance interval
            for _ in range(self.maintenance_interval):
                if not self.running:
                    break
                time.sleep(1)
                
    def store_analytical_memory(self, key, value, importance=0.5, context=None):
        """
        Store memory in the analytical (left) hemisphere.
        
        Args:
            key (str): Memory identifier
            value (str): Memory content
            importance (float): Importance score (0.0-1.0)
            context (dict, optional): Context data
            
        Returns:
            bool: Success status
        """
        context_hash = None
        if context:
            context_hash = self.memory_manager.generate_context_hash(context)
            
        return self.memory_manager.store_L1(key, value, importance, context_hash=context_hash)
        
    def store_creative_memory(self, key, value, novelty=0.5, d2_activation=0.5, context=None):
        """
        Store memory in the creative (right) hemisphere.
        
        Args:
            key (str): Memory identifier
            value (str): Memory content
            novelty (float): Novelty score (0.0-1.0) 
            d2_activation (float): D2 receptor activation level
            context (dict, optional): Context data
            
        Returns:
            bool: Success status
        """
        context_hash = None
        if context:
            context_hash = self.memory_manager.generate_context_hash(context)
            
        return self.memory_manager.store_R1(key, value, novelty, d2_activation, context_hash=context_hash)
        
    def retrieve_memory(self, key, hemisphere='both'):
        """
        Retrieve memory from either hemisphere.
        
        Args:
            key (str): Memory identifier
            hemisphere (str): Which hemisphere to search ('left', 'right', or 'both')
            
        Returns:
            dict: Memory data or None if not found
        """
        result = None
        
        if hemisphere in ['left', 'both']:
            result = self.memory_manager.retrieve_from_left(key)
            if result:
                return {'hemisphere': 'left', 'data': result}
                
        if hemisphere in ['right', 'both'] and not result:
            result = self.memory_manager.retrieve_from_right(key)
            if result:
                return {'hemisphere': 'right', 'data': result}
                
        return None
        
    def search_by_context(self, context, hemisphere='both'):
        """
        Search for memories associated with a specific context.
        
        Args:
            context (dict): Context information
            hemisphere (str): Which hemisphere to search ('left', 'right', or 'both')
            
        Returns:
            dict: Results grouped by hemisphere and tier
        """
        context_hash = self.memory_manager.generate_context_hash(context)
        return self.memory_manager.search_by_context(context_hash, hemisphere)
        
    def get_statistics(self):
        """
        Get statistics about memory usage.
        
        Returns:
            dict: Combined statistics including maintenance stats
        """
        current_stats = self.memory_manager.get_memory_statistics()
        
        # Add maintenance stats if available
        if self.stats:
            current_stats['maintenance'] = self.stats
            
        if self.last_maintenance:
            current_stats['last_maintenance'] = self.last_maintenance.isoformat()
            
        return current_stats
        
    def run_manual_maintenance(self):
        """
        Manually trigger memory maintenance operations.
        
        Returns:
            dict: Statistics about maintenance operations
        """
        self.stats = self.memory_manager.run_memory_maintenance()
        self.last_maintenance = datetime.now()
        return self.stats

# Create singleton instance
tiered_memory = TieredMemorySystem()