import sqlite3
import json
import gzip
import lzma
import bz2
import pickle
import os
from typing import Dict, Any, Optional, Union, List
import numpy as np

class NeuroRNASStorageManager:
    """Advanced storage manager with multi-format compression and database support"""
    
    def __init__(self, db_path: str = 'neuronas.db', compression_level: int = 9):
        self.db_path = db_path
        self.compression_level = compression_level
        self._initialize_db()
        self.compression_methods = {
            'none': self._no_compression,
            'gzip': self._gzip_compression,
            'lzma': self._lzma_compression,
            'bz2': self._bz2_compression
        }
        
    def _initialize_db(self) -> None:
        """Initialize SQLite database with required tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create memory tables for different tiers
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS memory_l1 (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            timestamp REAL,
            data BLOB,
            score REAL,
            compression TEXT,
            metadata TEXT
        )
        ''')
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS memory_l2 (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            timestamp REAL,
            data BLOB,
            score REAL,
            compression TEXT,
            access_count INTEGER,
            metadata TEXT
        )
        ''')
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS memory_l3 (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            timestamp REAL,
            data BLOB,
            score REAL,
            compression TEXT,
            access_count INTEGER,
            embedding BLOB,
            metadata TEXT
        )
        ''')
        
        # Create D2 receptor state table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS d2_receptor_state (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp REAL,
            region TEXT,
            d2_activation REAL,
            data BLOB,
            compression TEXT
        )
        ''')
        
        # Create optimization parameters table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS optimization_params (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp REAL,
            decay_factor REAL,
            max_layers INTEGER,
            d2_activation REAL,
            attention REAL,
            working_memory REAL,
            learning_rate REAL,
            score REAL
        )
        ''')
        
        # Create indexes for faster retrieval
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_memory_l1_user ON memory_l1(user_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_memory_l2_user ON memory_l2(user_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_memory_l3_user ON memory_l3(user_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_memory_l3_score ON memory_l3(score)')
        
        conn.commit()
        conn.close()
    
    def _no_compression(self, data: Dict) -> bytes:
        """No compression, just pickle the data"""
        return pickle.dumps(data)
        
    def _gzip_compression(self, data: Dict) -> bytes:
        """Compress data using gzip"""
        return gzip.compress(pickle.dumps(data), compresslevel=self.compression_level)
        
    def _lzma_compression(self, data: Dict) -> bytes:
        """Compress data using LZMA (high compression ratio)"""
        return lzma.compress(pickle.dumps(data), preset=self.compression_level)
        
    def _bz2_compression(self, data: Dict) -> bytes:
        """Compress data using BZ2"""
        return bz2.compress(pickle.dumps(data), compresslevel=self.compression_level)
    
    def _decompress(self, data: bytes, compression: str) -> Dict:
        """Decompress data based on compression method"""
        if compression == 'none':
            return pickle.loads(data)
        elif compression == 'gzip':
            return pickle.loads(gzip.decompress(data))
        elif compression == 'lzma':
            return pickle.loads(lzma.decompress(data))
        elif compression == 'bz2':
            return pickle.loads(bz2.decompress(data))
        else:
            raise ValueError(f"Unknown compression method: {compression}")
    
    def save_memory(self, tier: str, user_id: str, data: Dict, score: float, 
                    compression: str = 'gzip', metadata: Optional[Dict] = None) -> int:
        """Save memory data to specified tier with compression"""
        if tier not in ['L1', 'L2', 'L3']:
            raise ValueError(f"Unknown memory tier: {tier}")
            
        if compression not in self.compression_methods:
            raise ValueError(f"Unknown compression method: {compression}")
        
        # Compress data
        compressed_data = self.compression_methods[compression](data)
        
        # Generate embedding for L3 tier (for semantic search)
        embedding_blob = None
        if tier == 'L3' and 'query' in data:
            # Simple embedding simulation - in a real implementation,
            # this would use a proper embedding model
            embedding = np.random.random(384).astype(np.float32)  # 384-dim embedding
            embedding_blob = embedding.tobytes()
        
        # Connect to database
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Insert into appropriate table
        table_name = f"memory_{tier.lower()}"
        if tier == 'L1':
            cursor.execute(
                f"INSERT INTO {table_name} (user_id, timestamp, data, score, compression, metadata) "
                f"VALUES (?, ?, ?, ?, ?, ?)",
                (user_id, time.time(), compressed_data, score, compression, 
                 json.dumps(metadata) if metadata else None)
            )
        elif tier == 'L2':
            cursor.execute(
                f"INSERT INTO {table_name} (user_id, timestamp, data, score, compression, access_count, metadata) "
                f"VALUES (?, ?, ?, ?, ?, ?, ?)",
                (user_id, time.time(), compressed_data, score, compression, 1,
                 json.dumps(metadata) if metadata else None)
            )
        elif tier == 'L3':
            cursor.execute(
                f"INSERT INTO {table_name} (user_id, timestamp, data, score, compression, access_count, embedding, metadata) "
                f"VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (user_id, time.time(), compressed_data, score, compression, 1, embedding_blob,
                 json.dumps(metadata) if metadata else None)
            )
        
        # Get the ID of the inserted row
        row_id = cursor.lastrowid
        
        # Implement size limits - remove oldest entries if table exceeds size limit
        if tier == 'L1':
            cursor.execute(f"SELECT COUNT(*) FROM {table_name} WHERE user_id = ?", (user_id,))
            count = cursor.fetchone()[0]
            if count > 20:  # L1 limit per user
                cursor.execute(
                    f"DELETE FROM {table_name} WHERE id IN "
                    f"(SELECT id FROM {table_name} WHERE user_id = ? ORDER BY timestamp ASC LIMIT ?)",
                    (user_id, count - 20)
                )
        elif tier == 'L2':
            cursor.execute(f"SELECT COUNT(*) FROM {table_name} WHERE user_id = ?", (user_id,))
            count = cursor.fetchone()[0]
            if count > 50:  # L2 limit per user
                cursor.execute(
                    f"DELETE FROM {table_name} WHERE id IN "
                    f"(SELECT id FROM {table_name} WHERE user_id = ? ORDER BY score ASC, timestamp ASC LIMIT ?)",
                    (user_id, count - 50)
                )
        elif tier == 'L3':
            cursor.execute(f"SELECT COUNT(*) FROM {table_name} WHERE user_id = ?", (user_id,))
            count = cursor.fetchone()[0]
            if count > 100:  # L3 limit per user
                cursor.execute(
                    f"DELETE FROM {table_name} WHERE id IN "
                    f"(SELECT id FROM {table_name} WHERE user_id = ? ORDER BY score ASC LIMIT ?)",
                    (user_id, count - 100)
                )
        
        conn.commit()
        conn.close()
        
        return row_id
    
    def load_memory(self, tier: str, user_id: str, limit: int = 10, 
                    min_score: Optional[float] = None) -> List[Dict]:
        """Load memory data from specified tier"""
        if tier not in ['L1', 'L2', 'L3']:
            raise ValueError(f"Unknown memory tier: {tier}")
        
        # Connect to database
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Query the appropriate table
        table_name = f"memory_{tier.lower()}"
        query = f"SELECT id, timestamp, data, score, compression, metadata FROM {table_name} WHERE user_id = ?"
        params = [user_id]
        
        if min_score is not None:
            query += " AND score >= ?"
            params.append(min_score)
        
        query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)
        
        cursor.execute(query, params)
        results = cursor.fetchall()
        
        # Update access count for L2 and L3
        if tier in ['L2', 'L3'] and results:
            ids = [row[0] for row in results]
            placeholders = ','.join('?' for _ in ids)
            cursor.execute(
                f"UPDATE {table_name} SET access_count = access_count + 1 "
                f"WHERE id IN ({placeholders})",
                ids
            )
            conn.commit()
        
        # Decompress and return results
        memory_entries = []
        for row in results:
            id, timestamp, compressed_data, score, compression, metadata_json = row
            data = self._decompress(compressed_data, compression)
            entry = {
                'id': id,
                'timestamp': timestamp,
                'data': data,
                'score': score,
                'metadata': json.loads(metadata_json) if metadata_json else {}
            }
            memory_entries.append(entry)
        
        conn.close()
        return memory_entries
    
    def save_d2_state(self, region: str, d2_activation: float, state_data: Dict, 
                       compression: str = 'gzip') -> int:
        """Save D2 receptor state with compression"""
        if compression not in self.compression_methods:
            compression = 'gzip'
        
        # Compress data
        compressed_data = self.compression_methods[compression](state_data)
        
        # Connect to database
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Insert state
        cursor.execute(
            "INSERT INTO d2_receptor_state (timestamp, region, d2_activation, data, compression) "
            "VALUES (?, ?, ?, ?, ?)",
            (time.time(), region, d2_activation, compressed_data, compression)
        )
        
        row_id = cursor.lastrowid
        
        # Limit number of stored states
        cursor.execute("SELECT COUNT(*) FROM d2_receptor_state")
        count = cursor.fetchone()[0]
        if count > 100:
            cursor.execute(
                "DELETE FROM d2_receptor_state WHERE id IN "
                "(SELECT id FROM d2_receptor_state ORDER BY timestamp ASC LIMIT ?)",
                (count - 100,)
            )
        
        conn.commit()
        conn.close()
        
        return row_id
    
    def load_d2_state(self, region: Optional[str] = None) -> Optional[Dict]:
        """Load most recent D2 receptor state"""
        # Connect to database
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Query for most recent state
        if region:
            cursor.execute(
                "SELECT timestamp, region, d2_activation, data, compression FROM d2_receptor_state "
                "WHERE region = ? ORDER BY timestamp DESC LIMIT 1",
                (region,)
            )
        else:
            cursor.execute(
                "SELECT timestamp, region, d2_activation, data, compression FROM d2_receptor_state "
                "ORDER BY timestamp DESC LIMIT 1"
            )
        
        result = cursor.fetchone()
        conn.close()
        
        if not result:
            return None
        
        timestamp, region, d2_activation, compressed_data, compression = result
        state_data = self._decompress(compressed_data, compression)
        
        return {
            'timestamp': timestamp,
            'region': region,
            'd2_activation': d2_activation,
            'state_data': state_data
        }
    
    def save_optimization_params(self, params: Dict) -> int:
        """Save optimization parameters"""
        # Connect to database
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Insert parameters
        cursor.execute(
            "INSERT INTO optimization_params (timestamp, decay_factor, max_layers, "
            "d2_activation, attention, working_memory, learning_rate, score) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (time.time(), params.get('decay_factor'), params.get('max_layers'),
             params.get('d2_activation'), params.get('attention'),
             params.get('working_memory'), params.get('learning_rate'),
             params.get('score', 0.0))
        )
        
        row_id = cursor.lastrowid
        
        # Limit stored parameters
        cursor.execute("SELECT COUNT(*) FROM optimization_params")
        count = cursor.fetchone()[0]
        if count > 50:
            cursor.execute(
                "DELETE FROM optimization_params WHERE id IN "
                "(SELECT id FROM optimization_params ORDER BY score ASC, timestamp ASC LIMIT ?)",
                (count - 50,)
            )
        
        conn.commit()
        conn.close()
        
        return row_id
    
    def load_best_optimization_params(self) -> Optional[Dict]:
        """Load best optimization parameters"""
        # Connect to database
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Query for best parameters
        cursor.execute(
            "SELECT timestamp, decay_factor, max_layers, d2_activation, "
            "attention, working_memory, learning_rate, score "
            "FROM optimization_params ORDER BY score DESC LIMIT 1"
        )
        
        result = cursor.fetchone()
        conn.close()
        
        if not result:
            return None
        
        timestamp, decay_factor, max_layers, d2_activation, attention, working_memory, learning_rate, score = result
        
        return {
            'timestamp': timestamp,
            'decay_factor': decay_factor,
            'max_layers': max_layers,
            'd2_activation': d2_activation,
            'attention': attention,
            'working_memory': working_memory,
            'learning_rate': learning_rate,
            'score': score
        }
    
    def semantic_search(self, query_embedding: np.ndarray, limit: int = 5) -> List[Dict]:
        """
        Perform semantic search on L3 memory using vector similarity
        (Simulated function - in reality would need proper embeddings)
        """
        # In a full implementation, this would use vector similarity search
        # Here we'll simulate by returning the highest scoring L3 memories
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT id, timestamp, data, score, compression, metadata FROM memory_l3 "
            "ORDER BY score DESC LIMIT ?",
            (limit,)
        )
        
        results = cursor.fetchall()
        conn.close()
        
        # Decompress and return results
        memory_entries = []
        for row in results:
            id, timestamp, compressed_data, score, compression, metadata_json = row
            data = self._decompress(compressed_data, compression)
            entry = {
                'id': id,
                'timestamp': timestamp,
                'data': data,
                'score': score,
                'metadata': json.loads(metadata_json) if metadata_json else {},
                'similarity': 0.8 + 0.2 * random.random()  # Simulated similarity score
            }
            memory_entries.append(entry)
        
        return sorted(memory_entries, key=lambda x: x['similarity'], reverse=True)
    
    def get_db_stats(self) -> Dict:
        """Get database statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        stats = {}
        
        # Get size of each table
        for table in ['memory_l1', 'memory_l2', 'memory_l3', 'd2_receptor_state', 'optimization_params']:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            stats[f"{table}_count"] = cursor.fetchone()[0]
        
        # Get database file size
        if os.path.exists(self.db_path):
            stats['db_size_bytes'] = os.path.getsize(self.db_path)
            stats['db_size_mb'] = os.path.getsize(self.db_path) / (1024 * 1024)
        
        conn.close()
        return stats
    
    def vacuum_db(self) -> None:
        """Optimize database by running VACUUM"""
        conn = sqlite3.connect(self.db_path)
        conn.execute("VACUUM")
        conn.close()
