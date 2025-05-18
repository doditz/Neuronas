
import sqlite3
import json
import gzip
import lzma
import os
import time

class TieredStorageManager:
    def __init__(self, config_path, db_paths):
        with open(config_path, "r") as f:
            self.config = json.load(f)
        self.dbs = {
            "L1": db_paths["L1"],
            "L2": db_paths["L2"],
            "L3": db_paths["L3"]
        }
        self.connections = {}
        for tier, path in self.dbs.items():
            self.connections[tier] = sqlite3.connect(path)
        self.compression = {
            "none": lambda x: x.encode("utf-8"),
            "gzip": lambda x: gzip.compress(x.encode("utf-8")),
            "lzma": lambda x: lzma.compress(x.encode("utf-8")),
        }
        self.decompression = {
            "none": lambda x: x.decode("utf-8"),
            "gzip": lambda x: gzip.decompress(x).decode("utf-8"),
            "lzma": lambda x: lzma.decompress(x).decode("utf-8"),
        }

        # QuAC - RAM-based cache for L1
        self.ram_cache_l1 = {}
        self.ram_ttl = 60  # seconds

    def insert(self, tier, table, data, importance=1.0):
        compression_algo = self.config["storage"]["compression"][tier]["algorithm"]
        conn = self.connections[tier]
        cursor = conn.cursor()
        compressed = self.compression[compression_algo](json.dumps(data))
        try:
            # Validate table name against a whitelist to prevent SQL injection
            valid_tables = ["memory", "knowledge", "metrics", "settings", "hypotheses"]
            if table not in valid_tables:
                raise ValueError(f"Invalid table name: {table}")
            
            cursor.execute(f"INSERT INTO {table} (data) VALUES (?)", (compressed,))
            conn.commit()
        except Exception:
            conn.rollback()

        # QDAC: log importance for future use (placeholder logic)
        if tier == "L3":
            score = importance
            if "importance" in self.config["storage"]:
                threshold = self.config["storage"]["importance"].get("min_threshold", 0.5)
                if score < threshold:
                    print("QDAC: Entry too weak to prioritize in L3")

        # QuAC: cache in memory if tier is L1
        if tier == "L1":
            self.ram_cache_l1[time.time()] = data
            # Clean cache
            self._cleanup_cache()

    def retrieve_all(self, tier, table):
        # Validate table name against a whitelist to prevent SQL injection
        valid_tables = ["memory", "knowledge", "metrics", "settings", "hypotheses"]
        if table not in valid_tables:
            raise ValueError(f"Invalid table name: {table}")
            
        compression_algo = self.config["storage"]["compression"][tier]["algorithm"]
        conn = self.connections[tier]
        cursor = conn.cursor()
        # Table names cannot be parameterized, but we've validated against a whitelist above
        query = f"SELECT data FROM {table}"
        cursor.execute(query)
        results = []
        for (data,) in cursor.fetchall():
            try:
                decompressed = self.decompression[compression_algo](data)
                results.append(json.loads(decompressed))
            except Exception:
                continue

        # Add QuAC RAM cache if L1
        if tier == "L1":
            self._cleanup_cache()
            results += list(self.ram_cache_l1.values())

        return results

    def _cleanup_cache(self):
        now = time.time()
        self.ram_cache_l1 = {k: v for k, v in self.ram_cache_l1.items() if now - k < self.ram_ttl}

    def close(self):
        for conn in self.connections.values():
            conn.close()
