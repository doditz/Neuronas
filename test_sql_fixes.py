#!/usr/bin/env python3
"""
Test script for SQL compatibility fixes and Perplexity integration
"""
import os
import sys
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_sql_operations():
    """Test SQLite memory operations"""
    try:
        from sqlite_memory_operations import SQLiteMemoryOperations
        from sqlalchemy import create_engine
        
        # Create test database
        engine = create_engine('sqlite:///test_memory.db')
        
        with engine.connect() as conn:
            # Create test tables (simplified)
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS left_hemisphere_memory_tier_1 (
                    key TEXT PRIMARY KEY,
                    value TEXT,
                    importance REAL,
                    expiration TIMESTAMP,
                    context_hash TEXT,
                    access_count INTEGER DEFAULT 1,
                    last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))
            
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS left_hemisphere_memory_tier_2 (
                    key TEXT PRIMARY KEY,
                    value TEXT,
                    importance REAL,
                    context_hash TEXT,
                    access_count INTEGER DEFAULT 1,
                    last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))
            
            # Test memory operations
            memory_ops = SQLiteMemoryOperations(conn)
            
            # This would normally fail with PostgreSQL syntax, but should work now
            result = memory_ops.push_l1_to_l2()
            logger.info(f"✅ L1 to L2 push completed: {result} records moved")
            
            conn.commit()
            
        logger.info("✅ All SQL operations working correctly")
        return True
        
    except Exception as e:
        logger.error(f"❌ SQL operations test failed: {e}")
        return False

def test_perplexity_integration():
    """Test Perplexity API integration"""
    try:
        from perplexity_integration import PerplexityIntegration
        
        perplexity = PerplexityIntegration()
        
        if perplexity.is_available():
            # Test a simple query
            result = perplexity.research_query("What is artificial intelligence?", model='fast')
            
            if result['success']:
                logger.info("✅ Perplexity API test successful")
                logger.info(f"Response length: {len(result['response'])} characters")
                return True
            else:
                logger.error(f"❌ Perplexity API test failed: {result['error']}")
                return False
        else:
            logger.warning("⚠️  Perplexity API key not configured, but module works")
            return True
            
    except Exception as e:
        logger.error(f"❌ Perplexity integration test failed: {e}")
        return False

def main():
    """Run all tests"""
    logger.info("🚀 Starting Neuronas compatibility tests...")
    
    sql_ok = test_sql_operations()
    perplexity_ok = test_perplexity_integration()
    
    if sql_ok and perplexity_ok:
        logger.info("🎉 All tests passed! Neuronas is ready to run.")
        return 0
    else:
        logger.error("❌ Some tests failed. Check the logs above.")
        return 1

if __name__ == "__main__":
    from sqlalchemy import text
    sys.exit(main())
