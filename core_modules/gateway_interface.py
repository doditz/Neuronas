import logging
import time
from datetime import datetime
import uuid

# Set up logging
logger = logging.getLogger(__name__)

class GatewayInterface:
    """
    Gateway interface for processing incoming queries and routing them through
    the appropriate cognitive pathways based on query classification.
    """
    def __init__(self):
        self.initialized = False
        logger.info("Gateway Interface initializing")
    
    def initialize(self, app):
        """
        Initialize the gateway with application context.
        
        Args:
            app: Flask application instance
        """
        from core_modules.query_processor import QueryProcessor
        from core_modules.neural_pathways import NeuralPathwayRouter
        from core_modules.modulation_engine import ModulationEngine
        
        self.query_processor = QueryProcessor()
        self.pathway_router = NeuralPathwayRouter()
        self.modulation_engine = ModulationEngine()
        self.app = app
        self.initialized = True
        logger.info("Gateway Interface initialized successfully")
    
    def process_query(self, query, session_id=None):
        """
        Process an incoming query through the cognitive pipeline.
        
        Args:
            query (str): The user query
            session_id (str): Optional session identifier
            
        Returns:
            dict: Processing results including response
        """
        if not self.initialized:
            from flask import current_app
            self.initialize(current_app)
        
        start_time = time.time()
        logger.debug(f"Processing query: {query[:50]}...")
        
        # Generate session ID if not provided
        if not session_id:
            session_id = str(uuid.uuid4())
        
        # 1. Classify query
        query_type, confidence = self.query_processor.classify_query(query)
        logger.debug(f"Classified as {query_type} with confidence {confidence}")
        
        # 2. Route through neural pathways
        hemisphere, pathway = self.pathway_router.route_neural_pathway(query, query_type)
        logger.debug(f"Routed to {hemisphere} hemisphere using pathway {pathway}")
        
        # 3. Apply appropriate D2 modulation
        if hemisphere == 'L':
            # Pin modulation for analytical processing
            modulation_mode = "pin"
            modulation_results = self.modulation_engine.modulate_d2(modulation_mode)
        else:
            # Stim modulation for creative processing
            modulation_mode = "stim"
            modulation_results = self.modulation_engine.modulate_d2(modulation_mode)
        
        # Store query context in memory
        self._store_context(query, query_type, hemisphere, session_id)
        
        # 4. Generate response based on hemisphere and pathway
        response = self._generate_response(query, query_type, hemisphere, pathway)
        
        # 5. Calculate metrics
        processing_time = time.time() - start_time
        d2_activation = modulation_results.get('d2_activation', 0.5)
        
        # 6. Log metrics to database
        self._log_metrics(query, query_type, processing_time, d2_activation, session_id)
        
        # 7. Prepare and return response
        result = {
            'response': response,
            'query_type': query_type,
            'hemisphere_used': hemisphere,
            'processing_time': round(processing_time, 4),
            'd2_activation': round(d2_activation, 4),
            'session_id': session_id
        }
        
        return result
    
    def _store_context(self, query, query_type, hemisphere, session_id):
        """
        Store query context in appropriate memory tier.
        
        Args:
            query (str): User query
            query_type (str): Query classification
            hemisphere (str): Processing hemisphere (L or R)
            session_id (str): Session identifier
        """
        from models import CognitiveMemory, db
        from core_modules.storage_manager import determine_importance
        
        # Determine importance for memory retention
        importance = determine_importance(query, query_type)
        
        # Initial tier is always 1 (short-term)
        tier = 1
        
        # Create memory entry
        memory = CognitiveMemory(
            hemisphere=hemisphere,
            tier=tier,
            key=f"query_{int(time.time())}",
            value=query,
            importance=importance,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        db.session.add(memory)
        db.session.commit()
        logger.debug(f"Stored query context in {hemisphere}{tier} with importance {importance}")
    
    def _generate_response(self, query, query_type, hemisphere, pathway):
        """
        Generate a response based on query type and processing hemisphere.
        
        Args:
            query (str): User query
            query_type (str): Query classification
            hemisphere (str): Processing hemisphere (L or R)
            pathway (str): Neural pathway used
            
        Returns:
            str: Generated response
        """
        from core_modules.ethical_framework import BronasEthicalFramework
        from core_modules.quantum_module import QronasOptimizer
        
        # First, retrieve relevant memory
        memories = self._retrieve_relevant_memories(query, hemisphere)
        
        # Initialize response generators
        bronas = BronasEthicalFramework()
        qronas = QronasOptimizer()
        
        # Generate response candidates based on hemisphere
        if hemisphere == 'L':
            # Analytical/factual processing
            response = f"Analytical response processed through {pathway}. "
            response += f"Based on analysis of your query about '{query[:30]}...', "
            
            # Add factual information
            if query_type == 'factual':
                response += "I've identified the key facts relevant to your question. "
            else:
                response += "I've analyzed the patterns and logical structure of your query. "
            
            # Add memory context if available
            if memories:
                response += f"This relates to {len(memories)} previous contexts we've discussed. "
        else:
            # Creative processing
            response = f"Creative response processed through {pathway}. "
            response += f"Exploring your query about '{query[:30]}...', "
            
            # Add creative elaboration
            response += "I've considered multiple perspectives and innovative approaches. "
            
            # Add memory context if available
            if memories:
                response += f"I've drawn inspiration from {len(memories)} related contexts. "
        
        # Apply ethical filter
        response = bronas.filter_content(response, query_type)
        
        # Optimize for relevance
        qronas_metrics = {
            'query_length': len(query),
            'response_length': len(response),
            'memory_count': len(memories)
        }
        optimization = qronas.optimize(qronas_metrics, 0.5)
        
        # Finalize response with optimization insights
        response += f"\n\nResponse optimized with confidence: {optimization['confidence']:.2f}"
        
        return response
    
    def _retrieve_relevant_memories(self, query, hemisphere):
        """
        Retrieve memories relevant to the current query.
        
        Args:
            query (str): User query
            hemisphere (str): Processing hemisphere
            
        Returns:
            list: Relevant memory entries
        """
        from models import CognitiveMemory
        from core_modules.storage_manager import semantic_search
        
        # Use semantic search to find relevant memories
        relevant_memories = semantic_search(query, hemisphere)
        
        return relevant_memories
    
    def _log_metrics(self, query, query_type, processing_time, d2_activation, session_id):
        """
        Log cognitive metrics to the database.
        
        Args:
            query (str): User query
            query_type (str): Query classification
            processing_time (float): Processing time in seconds
            d2_activation (float): D2 activation level
            session_id (str): Session identifier
        """
        from models import CognitiveMetrics, db
        
        # Create metrics entries
        metrics = [
            CognitiveMetrics(
                metric_name="processing_time",
                value=processing_time,
                session_id=session_id
            ),
            CognitiveMetrics(
                metric_name="d2_activation",
                value=d2_activation,
                session_id=session_id
            ),
            CognitiveMetrics(
                metric_name="query_length",
                value=len(query),
                session_id=session_id
            )
        ]
        
        # Add query type specific metric
        if query_type == 'creative':
            metrics.append(CognitiveMetrics(
                metric_name="creative_query",
                value=1.0,
                session_id=session_id
            ))
        elif query_type == 'analytical':
            metrics.append(CognitiveMetrics(
                metric_name="analytical_query",
                value=1.0,
                session_id=session_id
            ))
        elif query_type == 'factual':
            metrics.append(CognitiveMetrics(
                metric_name="factual_query",
                value=1.0,
                session_id=session_id
            ))
        
        # Add to database
        for metric in metrics:
            db.session.add(metric)
        
        db.session.commit()
        logger.debug(f"Logged {len(metrics)} metrics for session {session_id}")
