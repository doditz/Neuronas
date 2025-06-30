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
Cognitive Memory Manager for NeuronasX Tiered Dual Framework

This module implements a hemispheric memory management system following 
the RAID Cognitive Architecture with left and right hemisphere specialization.
"""
import os
import logging
import json
import time
import hashlib
from datetime import datetime, timedelta
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

# Setup logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class CognitiveMemoryManager:
    """
    Manages the dual hemispheric tiered memory system with specialized
    functions for analytical (left) and creative (right) processing.
    """
    
    def __init__(self, db_url=None):
        """
        Initialize the cognitive memory manager with database connection.
        
        Args:
            db_url (str, optional): Database connection URL. Defaults to environment variable.
        """
        self.db_url = db_url or os.environ.get('DATABASE_URL', 'sqlite:///neuronas.db')
        self.engine = create_engine(self.db_url)
        self.is_connected = False
        self.last_context_hash = None
        self.current_session_id = None
        
        try:
            with self.engine.connect() as conn:
                self.is_connected = True
                logger.info("Successfully connected to cognitive memory database")
        except SQLAlchemyError as e:
            logger.error(f"Failed to connect to cognitive memory database: {e}")
            
    def set_session_context(self, session_id):
        """Set the current session context for memory operations."""
        self.current_session_id = session_id
        
    def generate_context_hash(self, context_data):
        """
        Generate a hash to represent the current context for memory operations.
        
        Args:
            context_data (dict): Dictionary of context information
            
        Returns:
            str: Context hash
        """
        if isinstance(context_data, dict):
            context_str = json.dumps(context_data, sort_keys=True)
        else:
            context_str = str(context_data)
            
        context_hash = hashlib.md5(context_str.encode()).hexdigest()
        self.last_context_hash = context_hash
        return context_hash
        
    def store_L1(self, key, value, importance=0.5, expiration_minutes=20, context_hash=None):
        """
        Store item in Left Hemisphere Tier 1 (short-term analytical memory).
        
        Args:
            key (str): Memory identifier
            value (str): Memory content
            importance (float): Importance score (0.0-1.0)
            expiration_minutes (int): Minutes until expiration
            context_hash (str, optional): Context hash
            
        Returns:
            bool: Success status
        """
        try:
            # Set expiration time
            expiration = datetime.now() + timedelta(minutes=expiration_minutes)
            
            # Use provided context hash or last generated
            context_hash = context_hash or self.last_context_hash
            
            with self.engine.connect() as conn:
                stmt = text("""
                    INSERT INTO left_hemisphere.memory_tier_1
                    (key, value, importance, expiration, context_hash)
                    VALUES (:key, :value, :importance, :expiration, :context_hash)
                    ON CONFLICT (key) DO UPDATE SET
                    value = :value,
                    importance = GREATEST(left_hemisphere.memory_tier_1.importance, :importance),
                    access_count = left_hemisphere.memory_tier_1.access_count + 1,
                    last_accessed = CURRENT_TIMESTAMP,
                    expiration = :expiration
                """)
                
                result = conn.execute(stmt, {
                    'key': key,
                    'value': value,
                    'importance': importance,
                    'expiration': expiration,
                    'context_hash': context_hash
                })
                conn.commit()
                
                logger.debug(f"Stored in L1: {key} (importance: {importance})")
                return True
                
        except SQLAlchemyError as e:
            logger.error(f"Error storing in L1: {e}")
            return False
            
    def store_R1(self, key, value, novelty_score=0.5, d2_activation=0.5, context_hash=None):
        """
        Store item in Right Hemisphere Tier 1 (real-time adaptation memory).
        
        Args:
            key (str): Memory identifier
            value (str): Memory content
            novelty_score (float): Novelty score (0.0-1.0)
            d2_activation (float): Dopamine D2 activation level
            context_hash (str, optional): Context hash
            
        Returns:
            bool: Success status
        """
        try:
            # Use provided context hash or last generated
            context_hash = context_hash or self.last_context_hash
            
            with self.engine.connect() as conn:
                stmt = text("""
                    INSERT INTO right_hemisphere.memory_tier_1
                    (key, value, novelty_score, d2_activation, context_hash)
                    VALUES (:key, :value, :novelty_score, :d2_activation, :context_hash)
                    ON CONFLICT (key) DO UPDATE SET
                    value = :value,
                    novelty_score = GREATEST(right_hemisphere.memory_tier_1.novelty_score, :novelty_score),
                    d2_activation = GREATEST(right_hemisphere.memory_tier_1.d2_activation, :d2_activation),
                    access_count = right_hemisphere.memory_tier_1.access_count + 1,
                    last_accessed = CURRENT_TIMESTAMP
                """)
                
                result = conn.execute(stmt, {
                    'key': key,
                    'value': value,
                    'novelty_score': novelty_score,
                    'd2_activation': d2_activation,
                    'context_hash': context_hash
                })
                conn.commit()
                
                logger.debug(f"Stored in R1: {key} (novelty: {novelty_score}, D2: {d2_activation})")
                return True
                
        except SQLAlchemyError as e:
            logger.error(f"Error storing in R1: {e}")
            return False
            
    def retrieve_from_left(self, key, source_tier='auto'):
        """
        Retrieve memory from Left Hemisphere with automatic tier selection.
        
        Args:
            key (str): Memory key to retrieve
            source_tier (str): Tier to search ('1', '2', '3', or 'auto')
            
        Returns:
            dict: Memory data or None if not found
        """
        try:
            with self.engine.connect() as conn:
                if source_tier == 'auto':
                    # Try each tier in order: L1, L2, L3
                    for tier in ['1', '2', '3']:
                        result = self._retrieve_from_specific_tier(conn, 'left_hemisphere', tier, key)
                        if result:
                            # If found in L2 or L3, pull to L1 for faster future access
                            if tier in ['2', '3']:
                                self._pull_to_higher_tier(conn, 'left_hemisphere', tier, key)
                            return result
                    return None
                else:
                    # Search in the specified tier
                    result = self._retrieve_from_specific_tier(conn, 'left_hemisphere', source_tier, key)
                    
                    # If found in L3, pull to L1
                    if result and source_tier == '3':
                        self._pull_to_higher_tier(conn, 'left_hemisphere', '3', key)
                        
                    return result
                    
        except SQLAlchemyError as e:
            logger.error(f"Error retrieving from left hemisphere: {e}")
            return None
            
    def retrieve_from_right(self, key, source_tier='auto'):
        """
        Retrieve memory from Right Hemisphere with automatic tier selection.
        
        Args:
            key (str): Memory key to retrieve
            source_tier (str): Tier to search ('1', '2', '3', or 'auto')
            
        Returns:
            dict: Memory data or None if not found
        """
        try:
            with self.engine.connect() as conn:
                if source_tier == 'auto':
                    # Try each tier in order: R1, R2, R3
                    for tier in ['1', '2', '3']:
                        result = self._retrieve_from_specific_tier(conn, 'right_hemisphere', tier, key)
                        if result:
                            return result
                    return None
                else:
                    # Search in the specified tier
                    return self._retrieve_from_specific_tier(conn, 'right_hemisphere', source_tier, key)
                    
        except SQLAlchemyError as e:
            logger.error(f"Error retrieving from right hemisphere: {e}")
            return None
            
    def _retrieve_from_specific_tier(self, conn, hemisphere, tier, key):
        """Helper method to retrieve from a specific hemisphere and tier."""
        table = f"{hemisphere}.memory_tier_{tier}"
        stmt = text(f"""
            UPDATE {table}
            SET access_count = access_count + 1,
                last_accessed = CURRENT_TIMESTAMP
            WHERE key = :key
            RETURNING *
        """)
        
        result = conn.execute(stmt, {'key': key}).first()
        
        if result:
            # Log retrieval operation
            op_stmt = text("""
                INSERT INTO central.memory_operations
                (operation_type, source_hemisphere, source_tier, key, success)
                VALUES ('retrieve', :hemisphere, :tier, :key, TRUE)
            """)
            
            conn.execute(op_stmt, {
                'hemisphere': 'L' if hemisphere == 'left_hemisphere' else 'R',
                'tier': tier,
                'key': key
            })
            conn.commit()
            
            # Convert row to dict
            return {column: value for column, value in zip(result._mapping.keys(), result)}
        
        return None
        
    def _pull_to_higher_tier(self, conn, hemisphere, source_tier, key):
        """Pull memory from lower tiers to higher tiers (L3→L1 or L2→L1)."""
        if hemisphere == 'left_hemisphere' and source_tier == '3':
            # Use the pull_l3_to_l1 database function
            stmt = text("SELECT left_hemisphere.pull_l3_to_l1(:key, :context_hash)")
            conn.execute(stmt, {
                'key': key,
                'context_hash': self.last_context_hash
            })
            conn.commit()
            logger.debug(f"Pulled {key} from L3 to L1")
            
    def search_by_context(self, context_hash, hemisphere='both', limit=20):
        """
        Search for memories associated with a specific context hash.
        
        Args:
            context_hash (str): Context hash to search for
            hemisphere (str): Which hemisphere to search ('left', 'right', or 'both')
            limit (int): Maximum number of results per hemisphere
            
        Returns:
            dict: Results grouped by hemisphere and tier
        """
        results = {'left': {}, 'right': {}}
        
        try:
            with self.engine.connect() as conn:
                hemispheres = []
                if hemisphere in ['left', 'both']:
                    hemispheres.append('left_hemisphere')
                if hemisphere in ['right', 'both']:
                    hemispheres.append('right_hemisphere')
                    
                for h in hemispheres:
                    h_short = 'L' if h == 'left_hemisphere' else 'R'
                    results[h_short[0].lower()] = {}
                    
                    for tier in ['1', '2', '3']:
                        stmt = text(f"""
                            SELECT * FROM {h}.memory_tier_{tier}
                            WHERE context_hash = :context_hash
                            ORDER BY 
                                CASE WHEN :h = 'left_hemisphere' THEN importance ELSE 
                                     CASE WHEN :tier = '1' THEN novelty_score
                                          WHEN :tier = '2' THEN optimization_score
                                          ELSE synthesis_score END
                                END DESC,
                                last_accessed DESC
                            LIMIT :limit
                        """)
                        
                        result_rows = conn.execute(stmt, {
                            'context_hash': context_hash,
                            'h': h,
                            'tier': tier,
                            'limit': limit
                        }).fetchall()
                        
                        tier_results = []
                        for row in result_rows:
                            # Convert row to dict
                            item = {column: value for column, value in zip(row._mapping.keys(), row)}
                            tier_results.append(item)
                            
                        results[h_short[0].lower()][tier] = tier_results
                        
                # Also search central integration
                stmt = text("""
                    SELECT * FROM central.integration
                    WHERE context_hash = :context_hash
                    ORDER BY 
                        (left_hemisphere_contribution + right_hemisphere_contribution) / 2 DESC,
                        updated_at DESC
                    LIMIT :limit
                """)
                
                central_rows = conn.execute(stmt, {
                    'context_hash': context_hash,
                    'limit': limit
                }).fetchall()
                
                central_results = []
                for row in central_rows:
                    # Convert row to dict
                    item = {column: value for column, value in zip(row._mapping.keys(), row)}
                    central_results.append(item)
                    
                results['central'] = central_results
                
                return results
                
        except SQLAlchemyError as e:
            logger.error(f"Error searching by context: {e}")
            return results
            
    def run_memory_maintenance(self):
        """
        Run maintenance operations on the memory system:
        - Push memories between tiers based on criteria
        - Run central integration
        
        Returns:
            dict: Statistics about maintenance operations
        """
        stats = {
            'l1_to_l2': 0,
            'l2_to_l3': 0,
            'r1_to_r2': 0,
            'r2_to_r3': 0,
            'r3_to_l3': 0,
            'integration': 0
        }
        
        max_retries = 3
        retry_delay = 1  # seconds
        
        def execute_with_retry(conn, statement, operation_name):
            """Execute a statement with retry logic for connection issues"""
            for attempt in range(max_retries):
                try:
                    result = conn.execute(statement).scalar()
                    return result or 0
                except SQLAlchemyError as e:
                    if attempt < max_retries - 1:
                        logger.warning(f"Retrying {operation_name} after error: {e}")
                        time.sleep(retry_delay * (attempt + 1))  # Exponential backoff
                    else:
                        logger.error(f"Failed {operation_name} after {max_retries} attempts: {e}")
                        raise
        
        try:
            # Create a fresh connection for maintenance
            self.engine = create_engine(self.db_url, pool_pre_ping=True)
            
            with self.engine.connect() as conn:
                # Push from L1 to L2
                try:
                    stmt = text("SELECT left_hemisphere.push_l1_to_l2()")
                    stats['l1_to_l2'] = execute_with_retry(conn, stmt, "L1 to L2 push")
                except SQLAlchemyError:
                    # Already logged in execute_with_retry
                    pass
                
                # Push from L2 to L3
                try:
                    stmt = text("SELECT left_hemisphere.push_l2_to_l3()")
                    stats['l2_to_l3'] = execute_with_retry(conn, stmt, "L2 to L3 push")
                except SQLAlchemyError:
                    pass
                
                # Push from R1 to R2
                try:
                    stmt = text("SELECT right_hemisphere.push_r1_to_r2()")
                    stats['r1_to_r2'] = execute_with_retry(conn, stmt, "R1 to R2 push")
                except SQLAlchemyError:
                    pass
                
                # Push from R2 to R3
                try:
                    stmt = text("SELECT right_hemisphere.push_r2_to_r3()")
                    stats['r2_to_r3'] = execute_with_retry(conn, stmt, "R2 to R3 push")
                except SQLAlchemyError:
                    pass
                
                # Push from R3 to L3 (cross-hemispheric)
                try:
                    stmt = text("SELECT right_hemisphere.push_r3_to_l3()")
                    stats['r3_to_l3'] = execute_with_retry(conn, stmt, "R3 to L3 push")
                except SQLAlchemyError:
                    pass
                
                # Run central integration
                try:
                    # Pass valid parameters to avoid enum type errors (L/R hemisphere types)
                    stmt = text("SELECT central.integrate_hemispheres(0.5, 0.5, 'balanced')")
                    stats['integration'] = execute_with_retry(conn, stmt, "central integration")
                except SQLAlchemyError as e:
                    logger.warning(f"Central integration skipped: {e}")
                    stats['integration'] = 0
                
                try:
                    conn.commit()
                except SQLAlchemyError as e:
                    logger.warning(f"Commit failed during memory maintenance: {e}")
                
                logger.info(f"Memory maintenance completed: {stats}")
                return stats
                
        except SQLAlchemyError as e:
            logger.error(f"Error during memory maintenance: {e}")
            return stats
            
    def get_memory_statistics(self):
        """
        Get statistics about memory usage across hemispheres and tiers.
        
        Returns:
            dict: Memory statistics
        """
        stats = {
            'left': {'1': 0, '2': 0, '3': 0},
            'right': {'1': 0, '2': 0, '3': 0},
            'central': 0,
            'operations': {
                'push': 0,
                'pull': 0,
                'retrieve': 0,
                'integrate': 0
            }
        }
        
        try:
            with self.engine.connect() as conn:
                # Left hemisphere counts
                for tier in ['1', '2', '3']:
                    stmt = text(f"SELECT COUNT(*) FROM left_hemisphere.memory_tier_{tier}")
                    result = conn.execute(stmt).scalar()
                    stats['left'][tier] = result or 0
                    
                # Right hemisphere counts
                for tier in ['1', '2', '3']:
                    stmt = text(f"SELECT COUNT(*) FROM right_hemisphere.memory_tier_{tier}")
                    result = conn.execute(stmt).scalar()
                    stats['right'][tier] = result or 0
                    
                # Central integration count
                stmt = text("SELECT COUNT(*) FROM central.integration")
                result = conn.execute(stmt).scalar()
                stats['central'] = result or 0
                
                # Operation counts
                op_types = ['push', 'pull', 'retrieve', 'integrate']
                for op_type in op_types:
                    stmt = text(f"""
                        SELECT COUNT(*) FROM central.memory_operations 
                        WHERE operation_type LIKE :op_pattern
                    """)
                    result = conn.execute(stmt, {'op_pattern': f"%{op_type}%"}).scalar()
                    stats['operations'][op_type] = result or 0
                    
                return stats
                
        except SQLAlchemyError as e:
            logger.error(f"Error getting memory statistics: {e}")
            return stats