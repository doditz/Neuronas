"""
This work is licensed under CC BY-NC 4.0 International.
Commercial use requires prior written consent and compensation.
Contact: sebastienbrulotte@gmail.com
Attribution: Sebastien Brulotte aka [ Doditz ]

This document is part of the NEURONAS cognitive system.
Core modules referenced: BRONAS (Ethical Reflex Filter) and QRONAS (Probabilistic Symbolic Vector Engine).
All outputs are subject to integrity validation and ethical compliance enforced by BRONAS.
"""

import logging
import json
import time
import math
from datetime import datetime, timedelta
import random
import numpy as np
from collections import OrderedDict, defaultdict
import sqlite3
import os

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

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TieredMemoryManager:
    """Manages the tiered memory system for Neuronas AI"""

    def __init__(self, config=None):
        """Initialize the tiered memory manager"""
        self.config = config or {
            "tiers": {
                "L1": {"capacity": 20, "db_path": "l1.db", "decay_rate": 0.05},
                "L2": {"capacity": 50, "db_path": "l2.db", "decay_rate": 0.02},
                "L3": {"capacity": 100, "db_path": "l3.db", "decay_rate": 0.005}
            },
            "compression": {
                "L1_to_L2": 0.9,  # 10% compression
                "L2_to_L3": 0.75,  # 25% compression
                "L3_to_disk": 0.5   # 50% compression
            }
        }

        # Initialize database connections
        self.connections = {}
        self._initialize_tiers()

        # Memory stats
        self.stats = {
            "tier_counts": {"L1": 0, "L2": 0, "L3": 0},
            "total_retrievals": {"L1": 0, "L2": 0, "L3": 0},
            "successful_retrievals": {"L1": 0, "L2": 0, "L3": 0},
            "compression_events": {"L1_to_L2": 0, "L2_to_L3": 0, "L3_to_disk": 0},
            "cross_tier_retrievals": 0
        }

        logger.info("Storage Manager initialized")

    def _initialize_tiers(self):
        """Initialize all memory tiers"""
        for tier, config in self.config["tiers"].items():
            db_path = config["db_path"]
            self._initialize_tier_db(tier, db_path)

            # Connect to the database
            self.connections[tier] = sqlite3.connect(db_path, check_same_thread=False)

            # Update stats
            self.stats["tier_counts"][tier] = self._count_memories(tier)

    def _initialize_tier_db(self, tier, db_path):
        """Initialize a specific tier database"""
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Create memories table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS memories (
            id INTEGER PRIMARY KEY,
            content TEXT,
            metadata TEXT,
            timestamp REAL,
            priority REAL,
            activation_count INTEGER DEFAULT 0,
            last_accessed REAL,
            compressed INTEGER DEFAULT 0
        )
        ''')

        # Create connections table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS connections (
            id INTEGER PRIMARY KEY,
            source_id INTEGER,
            target_id INTEGER,
            strength REAL,
            type TEXT,
            FOREIGN KEY (source_id) REFERENCES memories (id),
            FOREIGN KEY (target_id) REFERENCES memories (id)
        )
        ''')

        # Create embeddings table for semantic search
        if tier == "L3":
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS embeddings (
                memory_id INTEGER PRIMARY KEY,
                embedding BLOB,
                FOREIGN KEY (memory_id) REFERENCES memories (id)
            )
            ''')

        conn.commit()
        conn.close()

    def _count_memories(self, tier):
        """Count memories in a tier"""
        conn = self.connections[tier]
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM memories")
        count = cursor.fetchone()[0]
        return count

    def store_memory(self, content, tier="L1", metadata=None, priority=0.5):
        """
        Store a memory in the specified tier

        Args:
            content: Memory content
            tier: Memory tier (L1, L2, L3)
            metadata: Additional metadata
            priority: Memory priority (0-1)

        Returns:
            Memory ID
        """
        if tier not in self.connections:
            raise ValueError(f"Invalid tier: {tier}")

        conn = self.connections[tier]
        cursor = conn.cursor()

        timestamp = time.time()
        metadata_json = json.dumps(metadata) if metadata else '{}'

        cursor.execute(
            "INSERT INTO memories (content, metadata, timestamp, priority, last_accessed) VALUES (?, ?, ?, ?, ?)",
            (content, metadata_json, timestamp, priority, timestamp)
        )

        memory_id = cursor.lastrowid
        conn.commit()

        # Update stats
        self.stats["tier_counts"][tier] += 1

        # Check if tier is at capacity and needs compression
        self._check_tier_capacity(tier)

        return memory_id

    def retrieve_memory(self, memory_id, tier="L1"):
        """Retrieve a specific memory by ID from a tier"""
        if tier not in self.connections:
            raise ValueError(f"Invalid tier: {tier}")

        self.stats["total_retrievals"][tier] += 1

        conn = self.connections[tier]
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM memories WHERE id = ?", (memory_id,))
        memory = cursor.fetchone()

        if memory:
            # Update access metrics
            cursor.execute(
                "UPDATE memories SET activation_count = activation_count + 1, last_accessed = ? WHERE id = ?",
                (time.time(), memory_id)
            )
            conn.commit()

            self.stats["successful_retrievals"][tier] += 1

            return {
                "id": memory[0],
                "content": memory[1],
                "metadata": json.loads(memory[2]),
                "timestamp": memory[3],
                "priority": memory[4],
                "activation_count": memory[5],
                "last_accessed": memory[6],
                "compressed": bool(memory[7]),
                "tier": tier
            }

        # If not found in specified tier, try to find in other tiers
        for other_tier in self.connections:
            if other_tier == tier:
                continue

            other_conn = self.connections[other_tier]
            other_cursor = other_conn.cursor()

            other_cursor.execute("SELECT * FROM memories WHERE id = ?", (memory_id,))
            other_memory = other_cursor.fetchone()

            if other_memory:
                # Update access metrics
                other_cursor.execute(
                    "UPDATE memories SET activation_count = activation_count + 1, last_accessed = ? WHERE id = ?",
                    (time.time(), memory_id)
                )
                other_conn.commit()

                self.stats["cross_tier_retrievals"] += 1

                return {
                    "id": other_memory[0],
                    "content": other_memory[1],
                    "metadata": json.loads(other_memory[2]),
                    "timestamp": other_memory[3],
                    "priority": other_memory[4],
                    "activation_count": other_memory[5],
                    "last_accessed": other_memory[6],
                    "compressed": bool(other_memory[7]),
                    "tier": other_tier
                }

        return None

    def search_memories(self, query, tier="L1", limit=10):
        """Search memories by content in a specific tier"""
        if tier not in self.connections:
            raise ValueError(f"Invalid tier: {tier}")

        conn = self.connections[tier]
        cursor = conn.cursor()

        # Simple LIKE query - in a real system this would use more advanced search
        cursor.execute(
            "SELECT * FROM memories WHERE content LIKE ? ORDER BY priority DESC, last_accessed DESC LIMIT ?",
            (f"%{query}%", limit)
        )
        memories = cursor.fetchall()

        results = []
        for memory in memories:
            # Update access metrics
            cursor.execute(
                "UPDATE memories SET activation_count = activation_count + 1, last_accessed = ? WHERE id = ?",
                (time.time(), memory[0])
            )

            results.append({
                "id": memory[0],
                "content": memory[1],
                "metadata": json.loads(memory[2]),
                "timestamp": memory[3],
                "priority": memory[4],
                "activation_count": memory[5],
                "last_accessed": memory[6],
                "compressed": bool(memory[7]),
                "tier": tier
            })

        conn.commit()
        return results

    def search_all_tiers(self, query, limit=10):
        """Search across all memory tiers"""
        all_results = []

        for tier in ["L1", "L2", "L3"]:
            tier_results = self.search_memories(query, tier, limit)
            all_results.extend(tier_results)

        # Sort by priority and recency
        all_results.sort(key=lambda x: (x["priority"], x["last_accessed"]), reverse=True)

        return all_results[:limit]

    def create_connection(self, source_id, target_id, tier="L1", strength=0.5, type="association"):
        """Create a connection between memories in a tier"""
        if tier not in self.connections:
            raise ValueError(f"Invalid tier: {tier}")

        conn = self.connections[tier]
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO connections (source_id, target_id, strength, type) VALUES (?, ?, ?, ?)",
            (source_id, target_id, strength, type)
        )

        connection_id = cursor.lastrowid
        conn.commit()

        return connection_id

    def get_connected_memories(self, memory_id, tier="L1", connection_type=None):
        """Get memories connected to a specific memory in a tier"""
        if tier not in self.connections:
            raise ValueError(f"Invalid tier: {tier}")

        conn = self.connections[tier]
        cursor = conn.cursor()

        if connection_type:
            cursor.execute(
                """
                SELECT m.* FROM memories m
                JOIN connections c ON m.id = c.target_id
                WHERE c.source_id = ? AND c.type = ?
                UNION
                SELECT m.* FROM memories m
                JOIN connections c ON m.id = c.source_id
                WHERE c.target_id = ? AND c.type = ?
                """,
                (memory_id, connection_type, memory_id, connection_type)
            )
        else:
            cursor.execute(
                """
                SELECT m.* FROM memories m
                JOIN connections c ON m.id = c.target_id
                WHERE c.source_id = ?
                UNION
                SELECT m.* FROM memories m
                JOIN connections c ON m.id = c.source_id
                WHERE c.target_id = ?
                """,
                (memory_id, memory_id)
            )

        memories = cursor.fetchall()

        results = []
        for memory in memories:
            results.append({
                "id": memory[0],
                "content": memory[1],
                "metadata": json.loads(memory[2]),
                "timestamp": memory[3],
                "priority": memory[4],
                "activation_count": memory[5],
                "last_accessed": memory[6],
                "compressed": bool(memory[7]),
                "tier": tier
            })

        return results

    def _check_tier_capacity(self, tier):
        """Check if a tier is at capacity and needs compression/migration"""
        capacity = self.config["tiers"][tier]["capacity"]
        current_count = self.stats["tier_counts"][tier]

        if current_count > capacity:
            if tier == "L1":
                self._compress_and_migrate("L1", "L2")
            elif tier == "L2":
                self._compress_and_migrate("L2", "L3")
            elif tier == "L3":
                self._compress_l3()

    def _compress_and_migrate(self, source_tier, target_tier):
        """Compress and migrate memories from one tier to another"""
        source_conn = self.connections[source_tier]
        source_cursor = source_conn.cursor()

        target_conn = self.connections[target_tier]
        target_cursor = target_conn.cursor()

        # Get least accessed memories from source tier
        source_cursor.execute(
            """
            SELECT * FROM memories 
            ORDER BY priority ASC, last_accessed ASC, activation_count ASC 
            LIMIT ?
            """,
            (int(self.config["tiers"][source_tier]["capacity"] * 0.2),)  # Migrate 20% of capacity
        )

        memories_to_migrate = source_cursor.fetchall()
        compression_ratio = self.config["compression"][f"{source_tier}_to_{target_tier}"]

        migrated_count = 0
        for memory in memories_to_migrate:
            memory_id = memory[0]
            content = memory[1]
            metadata = memory[2]
            timestamp = memory[3]
            priority = memory[4]
            activation_count = memory[5]
            last_accessed = memory[6]

            # Apply compression
            compressed_content = self._compress_content(content, compression_ratio)

            # Insert into target tier
            target_cursor.execute(
                """
                INSERT INTO memories 
                (content, metadata, timestamp, priority, activation_count, last_accessed, compressed) 
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (compressed_content, metadata, timestamp, priority, activation_count, last_accessed, 1)
            )

            # Get connections for this memory
            source_cursor.execute(
                "SELECT * FROM connections WHERE source_id = ? OR target_id = ?",
                (memory_id, memory_id)
            )
            connections = source_cursor.fetchall()

            # Migrate connections
            for connection in connections:
                conn_id = connection[0]
                source_id = connection[1]
                target_id = connection[2]
                strength = connection[3]
                conn_type = connection[4]

                # Map memory IDs
                if source_id == memory_id:
                    source_id = target_cursor.lastrowid
                if target_id == memory_id:
                    target_id = target_cursor.lastrowid

                # Insert connection in target tier
                target_cursor.execute(
                    "INSERT INTO connections (source_id, target_id, strength, type) VALUES (?, ?, ?, ?)",
                    (source_id, target_id, strength, conn_type)
                )

            # Delete from source tier
            source_cursor.execute("DELETE FROM memories WHERE id = ?", (memory_id,))
            source_cursor.execute("DELETE FROM connections WHERE source_id = ? OR target_id = ?", (memory_id, memory_id))

            migrated_count += 1

        source_conn.commit()
        target_conn.commit()

        # Update stats
        self.stats["tier_counts"][source_tier] -= migrated_count
        self.stats["tier_counts"][target_tier] += migrated_count
        self.stats["compression_events"][f"{source_tier}_to_{target_tier}"] += 1

        logger.info(f"Migrated {migrated_count} memories from {source_tier} to {target_tier}")

    def _compress_l3(self):
        """Compress L3 memories to disk or archive"""
        # In a real system, this would move to disk archive
        # Here we'll just prune old memories
        conn = self.connections["L3"]
        cursor = conn.cursor()

        # Get oldest, least accessed memories
        cursor.execute(
            """
            SELECT id FROM memories 
            ORDER BY priority ASC, last_accessed ASC, activation_count ASC 
            LIMIT ?
            """,
            (int(self.config["tiers"]["L3"]["capacity"] * 0.2),)  # Prune 20% of capacity
        )

        memories_to_prune = cursor.fetchall()
        pruned_count = 0

        for memory in memories_to_prune:
            memory_id = memory[0]

            # Delete connections
            cursor.execute("DELETE FROM connections WHERE source_id = ? OR target_id = ?", (memory_id, memory_id))

            # Delete embeddings if they exist
            cursor.execute("DELETE FROM embeddings WHERE memory_id = ?", (memory_id,))

            # Delete memory
            cursor.execute("DELETE FROM memories WHERE id = ?", (memory_id,))

            pruned_count += 1

        conn.commit()

        # Update stats
        self.stats["tier_counts"]["L3"] -= pruned_count
        self.stats["compression_events"]["L3_to_disk"] += 1

        logger.info(f"Pruned {pruned_count} memories from L3")

    def _compress_content(self, content, ratio):
        """Compress content by specified ratio"""
        # This is a simplified simulation of compression
        # In a real system, this would use semantic compression

        if ratio >= 1.0:
            return content

        # Simple compression by truncating and adding compression indicator
        words = content.split()
        keep_words = max(3, int(len(words) * ratio))  # Keep at least 3 words

        compressed = " ".join(words[:keep_words])
        if keep_words < len(words):
            compressed += " [...]"

        return compressed

    def get_memory_stats(self):
        """Get statistics about memory usage"""
        # Update counts to ensure accuracy
        for tier in self.connections:
            self.stats["tier_counts"][tier] = self._count_memories(tier)

        tier_capacities = {tier: config["capacity"] for tier, config in self.config["tiers"].items()}
        tier_usage = {tier: count / tier_capacities[tier] for tier, count in self.stats["tier_counts"].items()}

        # Calculate retrieval efficiency
        retrieval_efficiency = {}
        for tier in self.stats["total_retrievals"]:
            total = self.stats["total_retrievals"][tier]
            if total > 0:
                retrieval_efficiency[tier] = self.stats["successful_retrievals"][tier] / total
            else:
                retrieval_efficiency[tier] = 0

        return {
            "tier_counts": self.stats["tier_counts"],
            "tier_capacities": tier_capacities,
            "tier_usage": tier_usage,
            "compression_events": self.stats["compression_events"],
            "cross_tier_retrievals": self.stats["cross_tier_retrievals"],
            "retrieval_efficiency": retrieval_efficiency
        }

    def maintain_memory(self):
        """Perform memory maintenance tasks"""
        # Apply decay to memory priorities
        maintenance_stats = {"l1_to_l2": 0, "l2_to_l3": 0, "r1_to_r2": 0, 
                            "r2_to_r3": 0, "r3_to_l3": 0, "integration": 0}

        for tier, config in self.config["tiers"].items():
            conn = self.connections[tier]
            cursor = conn.cursor()

            # Get memories that haven't been accessed recently
            now = time.time()
            decay_threshold = now - (86400 * 7)  # 7 days
            decay_rate = config["decay_rate"]

            cursor.execute(
                "UPDATE memories SET priority = priority * ? WHERE last_accessed < ?",
                (1 - decay_rate, decay_threshold)
            )

            affected = cursor.rowcount
            conn.commit()

            if tier == "L1" and affected > 0:
                maintenance_stats["l1_to_l2"] += self._migrate_decayed_memories(tier, "L2", affected)
            elif tier == "L2" and affected > 0:
                maintenance_stats["l2_to_l3"] += self._migrate_decayed_memories(tier, "L3", affected)

        return maintenance_stats

    def _migrate_decayed_memories(self, source_tier, target_tier, max_count):
        """Migrate decayed memories to a lower tier"""
        # Only migrate if target tier has space
        target_capacity = self.config["tiers"][target_tier]["capacity"]
        target_count = self.stats["tier_counts"][target_tier]

        if target_count >= target_capacity:
            return 0

        # Calculate how many memories to migrate
        available_space = target_capacity - target_count
        to_migrate = min(max_count, available_space)

        if to_migrate <= 0:
            return 0

        # Get decayed memories
        source_conn = self.connections[source_tier]
        source_cursor = source_conn.cursor()

        source_cursor.execute(
            "SELECT * FROM memories ORDER BY priority ASC LIMIT ?",
            (to_migrate,)
        )

        memories = source_cursor.fetchall()
        migrated = self._migrate_memories(memories, source_tier, target_tier)

        return migrated

    def _migrate_memories(self, memories, source_tier, target_tier):
        """Migrate a list of memories between tiers"""
        source_conn = self.connections[source_tier]
        source_cursor = source_conn.cursor()

        target_conn = self.connections[target_tier]
        target_cursor = target_conn.cursor()

        compression_ratio = self.config["compression"][f"{source_tier}_to_{target_tier}"]
        migrated = 0

        for memory in memories:
            memory_id = memory[0]
            content = memory[1]
            metadata = memory[2]
            timestamp = memory[3]
            priority = memory[4]
            activation_count = memory[5]
            last_accessed = memory[6]

            # Apply compression
            compressed_content = self._compress_content(content, compression_ratio)

            # Insert into target tier
            target_cursor.execute(
                """
                INSERT INTO memories 
                (content, metadata, timestamp, priority, activation_count, last_accessed, compressed) 
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (compressed_content, metadata, timestamp, priority, activation_count, last_accessed, 1)
            )

            # Delete from source tier
            source_cursor.execute("DELETE FROM memories WHERE id = ?", (memory_id,))

            migrated += 1

        source_conn.commit()
        target_conn.commit()

        # Update stats
        self.stats["tier_counts"][source_tier] -= migrated
        self.stats["tier_counts"][target_tier] += migrated

        return migrated

    def clear_tier(self, tier):
        """Clear all memories from a tier (for testing/reset)"""
        if tier not in self.connections:
            raise ValueError(f"Invalid tier: {tier}")

        conn = self.connections[tier]
        cursor = conn.cursor()

        cursor.execute("DELETE FROM connections")
        cursor.execute("DELETE FROM memories")

        if tier == "L3":
            cursor.execute("DELETE FROM embeddings")

        conn.commit()

        # Update stats
        self.stats["tier_counts"][tier] = 0

        return True

    def close(self):
        """Close all database connections"""
        for conn in self.connections.values():
            conn.close()

# Backwards compatibility
class StorageManager(TieredMemoryManager):
    """Legacy compatibility class"""

    def __init__(self, db_path="cognitive_memory.db"):
        """Initialize with tiered memory system"""
        # Initialize stats before calling super init
        self.stats = {
            "tier_counts": {"L1": 0, "L2": 0, "L3": 0},
            "total_retrievals": {"L1": 0, "L2": 0, "L3": 0},
            "successful_retrievals": {"L1": 0, "L2": 0, "L3": 0},
            "compression_events": {"L1_to_L2": 0, "L2_to_L3": 0, "L3_to_disk": 0},
            "cross_tier_retrievals": 0
        }
        super().__init__()