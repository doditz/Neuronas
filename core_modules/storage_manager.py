import logging
import json
import time
import math
from datetime import datetime, timedelta
import random

# Set up logging
logger = logging.getLogger(__name__)

def determine_importance(content, context_type=None):
    """
    Determine the importance of content for memory retention.
    
    Args:
        content (str): The content to evaluate
        context_type (str): Optional type of content
        
    Returns:
        float: Importance score between 0.0 and 1.0
    """
    if not content:
        return 0.1
    
    # Basic importance based on content length
    base_importance = min(1.0, len(content) / 1000)
    
    # Adjust based on context type
    if context_type == 'factual':
        base_importance *= 1.2  # Factual content gets higher importance
    elif context_type == 'creative':
        base_importance *= 0.9  # Creative content slightly lower importance
    
    # Ensure bounds
    importance = max(0.1, min(1.0, base_importance))
    
    return importance

def compress_content(content, compression_ratio=0.7):
    """
    Compress content for storage based on compression ratio.
    
    Args:
        content (str): Content to compress
        compression_ratio (float): Compression ratio (0.0-1.0)
        
    Returns:
        str: Compressed content
    """
    if not content:
        return ""
    
    # Simple compression - reduce to a percentage of original
    if compression_ratio >= 1.0:
        return content
    
    # Split into sentences
    sentences = content.split('. ')
    
    # Calculate number of sentences to keep
    keep_count = max(1, int(len(sentences) * compression_ratio))
    
    # Keep the most important sentences (simple approach - first and last sentences, 
    # plus evenly distributed important ones)
    if keep_count >= len(sentences):
        return content
    
    if keep_count == 1:
        return sentences[0] + "."
    
    # Always keep first and last, distribute the rest
    kept_sentences = [sentences[0]]
    
    if keep_count > 2:
        step = len(sentences) / (keep_count - 1)
        for i in range(1, keep_count - 1):
            idx = min(len(sentences) - 1, int(i * step))
            kept_sentences.append(sentences[idx])
    
    kept_sentences.append(sentences[-1])
    
    # Join sentences back together
    compressed = '. '.join(kept_sentences)
    if not compressed.endswith('.'):
        compressed += '.'
    
    logger.debug(f"Compressed content from {len(content)} to {len(compressed)} chars")
    return compressed

def semantic_search(query, hemisphere=None, tier=None, limit=5):
    """
    Perform semantic search on stored memories.
    
    Args:
        query (str): Search query
        hemisphere (str): Optional hemisphere filter (L or R)
        tier (int): Optional tier filter (1, 2, or 3)
        limit (int): Maximum number of results
        
    Returns:
        list: Relevant memory entries
    """
    from models import CognitiveMemory
    
    # Create base query
    db_query = CognitiveMemory.query
    
    # Apply filters if provided
    if hemisphere:
        db_query = db_query.filter_by(hemisphere=hemisphere)
    if tier:
        db_query = db_query.filter_by(tier=tier)
    
    # Order by importance and recency
    db_query = db_query.order_by(
        CognitiveMemory.importance.desc(),
        CognitiveMemory.updated_at.desc()
    )
    
    # Get candidate memories
    candidate_memories = db_query.limit(limit * 5).all()
    
    # Simple relevance scoring - in a real system, this would use embeddings
    scored_memories = []
    for memory in candidate_memories:
        # Basic relevance: count word overlaps
        query_words = set(query.lower().split())
        memory_words = set(memory.value.lower().split())
        overlap = len(query_words.intersection(memory_words))
        relevance = overlap / max(1, len(query_words))
        
        # Apply importance multiplier
        final_score = relevance * memory.importance
        
        scored_memories.append((memory, final_score))
    
    # Sort by relevance score
    scored_memories.sort(key=lambda x: x[1], reverse=True)
    
    # Return the top memories
    return [item[0] for item in scored_memories[:limit]]

class StorageManager:
    """
    Manages the multi-tier memory system with compression and promotion/demotion logic.
    """
    def __init__(self):
        self.retention_periods = {
            1: 20,  # L1/R1: short-term (20 cycles)
            2: 50,  # L2/R2: medium-term (50 cycles)
            3: 100  # L3/R3: long-term (100 cycles)
        }
        self.initialization_status = "initialized"
        logger.info("Storage Manager initialized")
    
    def store(self, hemisphere, tier, key, value, importance=0.5):
        """
        Store content in the specified memory tier.
        
        Args:
            hemisphere (str): Hemisphere (L or R)
            tier (int): Memory tier (1, 2, or 3)
            key (str): Storage key
            value (str): Content to store
            importance (float): Importance score
            
        Returns:
            dict: Storage operation result
        """
        from models import CognitiveMemory, db
        
        # Validate inputs
        if hemisphere not in ['L', 'R']:
            return {"error": "Invalid hemisphere"}
        if tier not in [1, 2, 3]:
            return {"error": "Invalid tier"}
        
        # Apply compression based on tier
        compression_ratio = 1.0 if tier == 1 else (0.8 if tier == 2 else 0.6)
        compressed_value = compress_content(value, compression_ratio)
        
        # Set expiration based on retention period
        retention_days = self.retention_periods[tier]
        expiration = datetime.utcnow() + timedelta(days=retention_days)
        
        # Create or update memory
        memory = CognitiveMemory.query.filter_by(
            hemisphere=hemisphere,
            tier=tier,
            key=key
        ).first()
        
        if memory:
            # Update existing memory
            memory.value = compressed_value
            memory.importance = importance
            memory.updated_at = datetime.utcnow()
            memory.expiration = expiration
        else:
            # Create new memory
            memory = CognitiveMemory(
                hemisphere=hemisphere,
                tier=tier,
                key=key,
                value=compressed_value,
                importance=importance,
                expiration=expiration
            )
        
        # Save to database
        db.session.add(memory)
        db.session.commit()
        
        logger.debug(f"Stored {len(compressed_value)} bytes to {hemisphere}{tier} with key {key}")
        return {
            "status": "success",
            "id": memory.id,
            "key": key,
            "compression_ratio": compression_ratio,
            "expiration": expiration.isoformat()
        }
    
    def retrieve(self, hemisphere, tier, key):
        """
        Retrieve content from the specified memory tier.
        
        Args:
            hemisphere (str): Hemisphere (L or R)
            tier (int): Memory tier (1, 2, or 3)
            key (str): Storage key
            
        Returns:
            dict: Retrieved content or error
        """
        from models import CognitiveMemory
        
        # Find memory entry
        memory = CognitiveMemory.query.filter_by(
            hemisphere=hemisphere,
            tier=tier,
            key=key
        ).first()
        
        if not memory:
            return {"error": "Memory not found"}
        
        # Check expiration
        if memory.expiration and memory.expiration < datetime.utcnow():
            return {"error": "Memory expired"}
        
        # Return memory data
        return {
            "value": memory.value,
            "importance": memory.importance,
            "created_at": memory.created_at.isoformat(),
            "updated_at": memory.updated_at.isoformat(),
            "expiration": memory.expiration.isoformat() if memory.expiration else None
        }
    
    def promote(self, memory_id):
        """
        Promote memory to a higher tier for longer retention.
        
        Args:
            memory_id (int): Memory entry ID
            
        Returns:
            dict: Promotion result
        """
        from models import CognitiveMemory, db
        
        # Find memory
        memory = CognitiveMemory.query.get(memory_id)
        if not memory:
            return {"error": "Memory not found"}
        
        # Check if already at highest tier
        if memory.tier == 3:
            return {"error": "Already at highest tier"}
        
        # Create new memory at higher tier with increased retention
        new_tier = memory.tier + 1
        
        # Apply additional compression for higher tier
        compression_ratio = 0.8 if new_tier == 2 else 0.6
        compressed_value = compress_content(memory.value, compression_ratio)
        
        # Set new expiration
        retention_days = self.retention_periods[new_tier]
        expiration = datetime.utcnow() + timedelta(days=retention_days)
        
        # Create memory in higher tier
        new_memory = CognitiveMemory(
            hemisphere=memory.hemisphere,
            tier=new_tier,
            key=memory.key,
            value=compressed_value,
            importance=memory.importance * 1.2,  # Increase importance
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            expiration=expiration
        )
        
        # Save to database
        db.session.add(new_memory)
        db.session.commit()
        
        logger.debug(f"Promoted memory {memory_id} from tier {memory.tier} to tier {new_tier}")
        return {
            "status": "success",
            "from_tier": memory.tier,
            "to_tier": new_tier,
            "new_id": new_memory.id,
            "expiration": expiration.isoformat()
        }
    
    def clean_expired(self):
        """
        Clean expired memories from all tiers.
        
        Returns:
            dict: Cleaning operation result
        """
        from models import CognitiveMemory, db
        
        # Find expired memories
        expired = CognitiveMemory.query.filter(
            CognitiveMemory.expiration < datetime.utcnow()
        ).all()
        
        # Delete expired memories
        count = 0
        for memory in expired:
            db.session.delete(memory)
            count += 1
        
        # Commit changes
        db.session.commit()
        
        logger.info(f"Cleaned {count} expired memories")
        return {
            "status": "success",
            "cleaned": count
        }

class FibonacciMemoryOptimizer:
    """
    Applies Fibonacci principles to memory optimization and consolidation.
    """
    def __init__(self):
        # Fibonacci sequence for memory growth pattern
        self.fibonacci_sequence = [1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89]
        self.golden_ratio = 1.618
    
    def optimize_memory_structure(self, memories, target_count):
        """
        Optimize memory structure using Fibonacci principles.
        
        Args:
            memories (list): List of memory items
            target_count (int): Target number of memories to keep
            
        Returns:
            list: Optimized memory list
        """
        if not memories:
            return []
        
        if len(memories) <= target_count:
            return memories
        
        # Sort by importance
        sorted_memories = sorted(memories, key=lambda x: x.importance, reverse=True)
        
        # Determine Fibonacci-based retention pattern
        pattern = []
        total = 0
        for i in range(len(self.fibonacci_sequence)):
            if total + self.fibonacci_sequence[i] > target_count:
                break
            pattern.append(self.fibonacci_sequence[i])
            total += self.fibonacci_sequence[i]
        
        # Fill remaining spots
        remaining = target_count - total
        if remaining > 0:
            pattern.append(remaining)
        
        # Apply pattern to create groups
        optimized = []
        idx = 0
        
        # Always keep the most important memories
        top_n = pattern[0]
        optimized.extend(sorted_memories[:top_n])
        idx += top_n
        
        # Distribute the rest according to Fibonacci pattern
        for group_size in pattern[1:]:
            available = len(sorted_memories) - idx
            if available <= 0:
                break
                
            # For each group, select evenly distributed items
            if available <= group_size:
                optimized.extend(sorted_memories[idx:])
                break
                
            # Calculate step size for even distribution
            step = available / group_size
            for i in range(group_size):
                pos = idx + int(i * step)
                if pos < len(sorted_memories):
                    optimized.append(sorted_memories[pos])
        
        return optimized
    
    def consolidate_memories(self, memories, compression_ratio=0.7):
        """
        Consolidate similar memories using Fibonacci principles.
        
        Args:
            memories (list): List of memory items
            compression_ratio (float): Target compression ratio
            
        Returns:
            list: Consolidated memory list
        """
        if not memories or len(memories) <= 1:
            return memories
        
        # Group similar memories (simplified approach)
        groups = {}
        for memory in memories:
            # Use first 3 words as simplistic grouping key
            words = memory.value.split()
            key = " ".join(words[:min(3, len(words))])
            
            if key not in groups:
                groups[key] = []
            groups[key].append(memory)
        
        # Consolidate groups with multiple memories
        consolidated = []
        for key, group in groups.items():
            if len(group) == 1:
                consolidated.append(group[0])
            else:
                # Combine similar memories
                combined_value = "\n".join([m.value for m in group])
                compressed = compress_content(combined_value, compression_ratio)
                
                # Create new consolidated memory
                from models import CognitiveMemory
                
                # Use the highest importance and latest expiration
                max_importance = max(m.importance for m in group)
                latest_expiration = max(m.expiration for m in group if m.expiration)
                
                # Create consolidated memory (not saved to DB)
                consolidated_memory = CognitiveMemory(
                    hemisphere=group[0].hemisphere,
                    tier=group[0].tier,
                    key=f"consolidated_{int(time.time())}",
                    value=compressed,
                    importance=max_importance,
                    expiration=latest_expiration
                )
                
                consolidated.append(consolidated_memory)
        
        return consolidated
