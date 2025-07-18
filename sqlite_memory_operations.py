"""
SQLite Memory Operations for Neuronas Tiered Memory System
=========================================================

This module provides SQLite-compatible functions to replace PostgreSQL
stored procedures for memory tier operations.
"""

import logging
import time
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class SQLiteMemoryOperations:
    """SQLite-compatible memory tier operations"""
    
    def __init__(self, connection):
        self.conn = connection
    
    def push_l1_to_l2(self):
        """
        Push expired/less important L1 memories to L2
        Returns: number of records moved
        """
        try:
            # Move expired or low-importance items from L1 to L2
            stmt = text("""
                INSERT INTO left_hemisphere_memory_tier_2 
                (key, value, importance, created_at, last_accessed, access_count, context_hash)
                SELECT 
                    key, value, importance, created_at, last_accessed, access_count, context_hash
                FROM left_hemisphere_memory_tier_1
                WHERE expiration < :current_time 
                   OR (importance < 0.5 AND access_count < 3)
                   OR (last_accessed < :old_access_threshold)
            """)
            
            current_time = datetime.now()
            old_access_threshold = current_time - timedelta(hours=2)
            
            result = self.conn.execute(stmt, {
                'current_time': current_time,
                'old_access_threshold': old_access_threshold
            })
            
            moved_count = result.rowcount
            
            # Remove moved items from L1
            if moved_count > 0:
                delete_stmt = text("""
                    DELETE FROM left_hemisphere_memory_tier_1
                    WHERE expiration < :current_time 
                       OR (importance < 0.5 AND access_count < 3)
                       OR (last_accessed < :old_access_threshold)
                """)
                
                self.conn.execute(delete_stmt, {
                    'current_time': current_time,
                    'old_access_threshold': old_access_threshold
                })
            
            logger.debug(f"Moved {moved_count} items from L1 to L2")
            return moved_count
            
        except SQLAlchemyError as e:
            logger.error(f"Error in push_l1_to_l2: {e}")
            return 0
    
    def push_l2_to_l3(self):
        """
        Push older L2 memories to L3 with compression
        Returns: number of records moved
        """
        try:
            # Move old or less accessed items from L2 to L3
            stmt = text("""
                INSERT INTO left_hemisphere_memory_tier_3 
                (key, value, importance, created_at, last_accessed, access_count, context_hash, compression_type)
                SELECT 
                    key, value, importance, created_at, last_accessed, access_count, context_hash, 'gzip'
                FROM left_hemisphere_memory_tier_2
                WHERE last_accessed < :old_threshold
                   OR access_count < 2
                ORDER BY importance ASC, last_accessed ASC
                LIMIT 1000
            """)
            
            old_threshold = datetime.now() - timedelta(hours=24)
            
            result = self.conn.execute(stmt, {
                'old_threshold': old_threshold
            })
            
            moved_count = result.rowcount
            
            # Remove moved items from L2
            if moved_count > 0:
                delete_stmt = text("""
                    DELETE FROM left_hemisphere_memory_tier_2
                    WHERE key IN (
                        SELECT key FROM left_hemisphere_memory_tier_2
                        WHERE last_accessed < :old_threshold
                           OR access_count < 2
                        ORDER BY importance ASC, last_accessed ASC
                        LIMIT 1000
                    )
                """)
                
                self.conn.execute(delete_stmt, {
                    'old_threshold': old_threshold
                })
            
            logger.debug(f"Moved {moved_count} items from L2 to L3")
            return moved_count
            
        except SQLAlchemyError as e:
            logger.error(f"Error in push_l2_to_l3: {e}")
            return 0
    
    def push_r1_to_r2(self):
        """
        Push R1 memories to R2 based on novelty and D2 activation
        Returns: number of records moved
        """
        try:
            # Move items with low novelty or D2 activation from R1 to R2
            stmt = text("""
                INSERT INTO right_hemisphere_memory_tier_2 
                (key, value, novelty_score, d2_activation, created_at, last_accessed, access_count, context_hash)
                SELECT 
                    key, value, novelty_score, d2_activation, created_at, last_accessed, access_count, context_hash
                FROM right_hemisphere_memory_tier_1
                WHERE (novelty_score < 0.5 AND d2_activation < 0.5)
                   OR last_accessed < :threshold
                   OR access_count < 2
            """)
            
            threshold = datetime.now() - timedelta(hours=1)
            
            result = self.conn.execute(stmt, {
                'threshold': threshold
            })
            
            moved_count = result.rowcount
            
            # Remove moved items from R1
            if moved_count > 0:
                delete_stmt = text("""
                    DELETE FROM right_hemisphere_memory_tier_1
                    WHERE (novelty_score < 0.5 AND d2_activation < 0.5)
                       OR last_accessed < :threshold
                       OR access_count < 2
                """)
                
                self.conn.execute(delete_stmt, {
                    'threshold': threshold
                })
            
            logger.debug(f"Moved {moved_count} items from R1 to R2")
            return moved_count
            
        except SQLAlchemyError as e:
            logger.error(f"Error in push_r1_to_r2: {e}")
            return 0
    
    def push_r2_to_r3(self):
        """
        Push R2 memories to R3 with consolidation
        Returns: number of records moved
        """
        try:
            # Move older items from R2 to R3
            stmt = text("""
                INSERT INTO right_hemisphere_memory_tier_3 
                (key, value, novelty_score, d2_activation, created_at, last_accessed, access_count, context_hash, compression_type)
                SELECT 
                    key, value, novelty_score, d2_activation, created_at, last_accessed, access_count, context_hash, 'gzip'
                FROM right_hemisphere_memory_tier_2
                WHERE last_accessed < :old_threshold
                ORDER BY d2_activation ASC, last_accessed ASC
                LIMIT 500
            """)
            
            old_threshold = datetime.now() - timedelta(hours=12)
            
            result = self.conn.execute(stmt, {
                'old_threshold': old_threshold
            })
            
            moved_count = result.rowcount
            
            # Remove moved items from R2
            if moved_count > 0:
                delete_stmt = text("""
                    DELETE FROM right_hemisphere_memory_tier_2
                    WHERE key IN (
                        SELECT key FROM right_hemisphere_memory_tier_2
                        WHERE last_accessed < :old_threshold
                        ORDER BY d2_activation ASC, last_accessed ASC
                        LIMIT 500
                    )
                """)
                
                self.conn.execute(delete_stmt, {
                    'old_threshold': old_threshold
                })
            
            logger.debug(f"Moved {moved_count} items from R2 to R3")
            return moved_count
            
        except SQLAlchemyError as e:
            logger.error(f"Error in push_r2_to_r3: {e}")
            return 0
    
    def push_r3_to_l3(self):
        """
        Cross-hemispheric transfer: Push significant R3 memories to L3
        Returns: number of records moved
        """
        try:
            # Transfer high-value creative insights to analytical long-term memory
            stmt = text("""
                INSERT INTO left_hemisphere_memory_tier_3 
                (key, value, importance, created_at, last_accessed, access_count, context_hash, compression_type, source_hemisphere)
                SELECT 
                    'R3_' || key, value, 
                    (novelty_score + d2_activation) / 2.0 as importance,
                    created_at, last_accessed, access_count, context_hash, 'lzma', 'right'
                FROM right_hemisphere_memory_tier_3
                WHERE (novelty_score > 0.7 OR d2_activation > 0.8)
                  AND access_count > 3
                  AND last_accessed > :recent_threshold
                ORDER BY (novelty_score + d2_activation) DESC
                LIMIT 100
            """)
            
            recent_threshold = datetime.now() - timedelta(days=1)
            
            result = self.conn.execute(stmt, {
                'recent_threshold': recent_threshold
            })
            
            moved_count = result.rowcount
            logger.debug(f"Cross-transferred {moved_count} items from R3 to L3")
            return moved_count
            
        except SQLAlchemyError as e:
            logger.error(f"Error in push_r3_to_l3: {e}")
            return 0
    
    def integrate_hemispheres(self, left_weight=0.5, right_weight=0.5, mode='balanced'):
        """
        Integrate hemispheric memory patterns
        Returns: integration score
        """
        try:
            # Count active memories in each hemisphere
            left_count_stmt = text("""
                SELECT 
                    (SELECT COUNT(*) FROM left_hemisphere_memory_tier_1) +
                    (SELECT COUNT(*) FROM left_hemisphere_memory_tier_2) +
                    (SELECT COUNT(*) FROM left_hemisphere_memory_tier_3) as total
            """)
            
            right_count_stmt = text("""
                SELECT 
                    (SELECT COUNT(*) FROM right_hemisphere_memory_tier_1) +
                    (SELECT COUNT(*) FROM right_hemisphere_memory_tier_2) +
                    (SELECT COUNT(*) FROM right_hemisphere_memory_tier_3) as total
            """)
            
            left_result = self.conn.execute(left_count_stmt).fetchone()
            right_result = self.conn.execute(right_count_stmt).fetchone()
            
            left_count = left_result[0] if left_result else 0
            right_count = right_result[0] if right_result else 0
            total_memories = left_count + right_count
            
            if total_memories == 0:
                return 0
            
            # Calculate integration score based on hemispheric balance
            balance_score = 1.0 - abs(left_count - right_count) / total_memories
            
            # Store integration metrics
            integration_stmt = text("""
                INSERT OR REPLACE INTO memory_integration_log 
                (timestamp, left_count, right_count, balance_score, mode, left_weight, right_weight)
                VALUES (:timestamp, :left_count, :right_count, :balance_score, :mode, :left_weight, :right_weight)
            """)
            
            self.conn.execute(integration_stmt, {
                'timestamp': datetime.now(),
                'left_count': left_count,
                'right_count': right_count,
                'balance_score': balance_score,
                'mode': mode,
                'left_weight': left_weight,
                'right_weight': right_weight
            })
            
            logger.debug(f"Hemispheric integration: L={left_count}, R={right_count}, balance={balance_score:.3f}")
            return balance_score
            
        except SQLAlchemyError as e:
            logger.error(f"Error in integrate_hemispheres: {e}")
            return 0


def execute_memory_operation_with_retry(conn, operation_name, operation_func, max_retries=3):
    """
    Execute memory operation with retry logic
    
    Args:
        conn: Database connection
        operation_name: Name of the operation for logging
        operation_func: Function to execute
        max_retries: Maximum retry attempts
        
    Returns:
        Result of the operation or 0 on failure
    """
    for attempt in range(max_retries):
        try:
            return operation_func()
        except SQLAlchemyError as e:
            logger.warning(f"{operation_name} attempt {attempt + 1} failed: {e}")
            if attempt == max_retries - 1:
                logger.error(f"{operation_name} failed after {max_retries} attempts")
                return 0
            time.sleep(0.1 * (attempt + 1))  # Exponential backoff
    
    return 0
