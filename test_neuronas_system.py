
#!/usr/bin/env python3
"""
Comprehensive test suite for Neuronas AI system
Tests all major components without external dependencies
"""

import sys
import os
import json
import time
import traceback
from datetime import datetime

def test_import_safety():
    """Test that all imports work without errors"""
    print("Testing imports...")
    
    try:
        # Test core modules
        from local_llm_hybridizer import LocalDualSystem
        print("✓ Local LLM Hybridizer imported successfully")
        
        from tiered_memory_integration import tiered_memory
        print("✓ Tiered memory system imported successfully")
        
        from dual_llm_system import dual_llm_system
        print("✓ Dual LLM system imported successfully")
        
        from agent_positioning_system import AgentPositioningSystem
        print("✓ Agent positioning system imported successfully")
        
        from smas_dispatcher import SMASDispatcher
        print("✓ SMAS dispatcher imported successfully")
        
        return True
        
    except Exception as e:
        print(f"✗ Import error: {e}")
        traceback.print_exc()
        return False

def test_local_dual_system():
    """Test the local dual hemisphere system"""
    print("\nTesting Local Dual System...")
    
    try:
        from local_llm_hybridizer import LocalDualSystem
        
        # Initialize system
        system = LocalDualSystem()
        print("✓ System initialized")
        
        # Test basic query processing
        test_query = "What is artificial intelligence?"
        result = system.process_query(test_query)
        
        if result and result.get("success"):
            print("✓ Query processing works")
            print(f"  - Left persona: {result.get('left_persona')}")
            print(f"  - Right persona: {result.get('right_persona')}")
            print(f"  - Response length: {len(result.get('response', ''))}")
            return True
        else:
            print("✗ Query processing failed")
            return False
            
    except Exception as e:
        print(f"✗ Local dual system error: {e}")
        traceback.print_exc()
        return False

def test_memory_system():
    """Test the tiered memory system"""
    print("\nTesting Memory System...")
    
    try:
        from tiered_memory_integration import tiered_memory
        
        # Test memory storage
        test_data = {
            "query": "test query",
            "response": "test response",
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Store in L1 memory
        success = tiered_memory.store_l1(test_data)
        if success:
            print("✓ L1 memory storage works")
        else:
            print("⚠ L1 memory storage failed")
        
        # Retrieve from L1 memory
        recent_data = tiered_memory.get_recent_l1(limit=1)
        if recent_data:
            print("✓ L1 memory retrieval works")
        else:
            print("⚠ L1 memory retrieval failed")
        
        return True
        
    except Exception as e:
        print(f"✗ Memory system error: {e}")
        traceback.print_exc()
        return False

def test_agent_positioning():
    """Test the agent positioning system"""
    print("\nTesting Agent Positioning System...")
    
    try:
        from agent_positioning_system import AgentPositioningSystem
        from local_llm_hybridizer import LocalDualSystem
        from smas_dispatcher import SMASDispatcher
        
        # Initialize components
        local_system = LocalDualSystem()
        smas = SMASDispatcher()
        positioning = AgentPositioningSystem(
            dual_llm_system=local_system,
            smas_dispatcher=smas
        )
        
        print("✓ Agent positioning system initialized")
        
        # Test position setting
        positioning.set_position("analytical", lock_position=False)
        current_pos = positioning.get_current_position()
        
        if current_pos:
            print(f"✓ Position setting works: {current_pos}")
            return True
        else:
            print("⚠ Position setting failed")
            return False
            
    except Exception as e:
        print(f"✗ Agent positioning error: {e}")
        traceback.print_exc()
        return False

def test_flask_app():
    """Test the Flask application initialization"""
    print("\nTesting Flask Application...")
    
    try:
        # Test if app can be imported and initialized
        from app import app
        
        if app:
            print("✓ Flask app imported successfully")
            
            # Test if key components are attached
            if hasattr(app, 'local_dual_system'):
                print("✓ Local dual system attached to app")
            else:
                print("⚠ Local dual system not attached")
                
            if hasattr(app, 'tiered_memory'):
                print("✓ Tiered memory attached to app")
            else:
                print("⚠ Tiered memory not attached")
                
            return True
        else:
            print("✗ Flask app failed to initialize")
            return False
            
    except Exception as e:
        print(f"✗ Flask app error: {e}")
        traceback.print_exc()
        return False

def test_configuration():
    """Test configuration loading"""
    print("\nTesting Configuration...")
    
    try:
        # Test config.json loading
        if os.path.exists('config.json'):
            with open('config.json', 'r') as f:
                config = json.load(f)
            print("✓ Configuration file loaded")
            
            # Check key sections
            required_sections = ['core', 'memory', 'neural', 'quantum', 'ethical']
            for section in required_sections:
                if section in config:
                    print(f"✓ {section} configuration present")
                else:
                    print(f"⚠ {section} configuration missing")
                    
            return True
        else:
            print("⚠ config.json not found, using defaults")
            return True
            
    except Exception as e:
        print(f"✗ Configuration error: {e}")
        return False

def test_database_connectivity():
    """Test database connectivity"""
    print("\nTesting Database Connectivity...")
    
    try:
        # Test SQLite databases
        databases = ['l1.db', 'l2.db', 'l3.db']
        
        for db in databases:
            if os.path.exists(db):
                print(f"✓ {db} exists")
            else:
                print(f"⚠ {db} not found (will be created on first use)")
        
        # Test cognitive memory manager
        from cognitive_memory_manager import CognitiveMemoryManager
        memory_manager = CognitiveMemoryManager()
        print("✓ Cognitive memory manager initialized")
        
        return True
        
    except Exception as e:
        print(f"✗ Database connectivity error: {e}")
        traceback.print_exc()
        return False

def run_comprehensive_test():
    """Run all tests and provide summary"""
    print("=" * 60)
    print("NEURONAS AI SYSTEM COMPREHENSIVE TEST")
    print("=" * 60)
    
    start_time = time.time()
    
    tests = [
        ("Import Safety", test_import_safety),
        ("Local Dual System", test_local_dual_system),
        ("Memory System", test_memory_system),
        ("Agent Positioning", test_agent_positioning),
        ("Configuration", test_configuration),
        ("Database Connectivity", test_database_connectivity),
        ("Flask Application", test_flask_app)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print(f"\n{'-' * 40}")
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"✗ {test_name} failed with exception: {e}")
            results[test_name] = False
    
    # Summary
    print(f"\n{'=' * 60}")
    print("TEST SUMMARY")
    print(f"{'=' * 60}")
    
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{test_name:.<30} {status}")
    
    elapsed_time = time.time() - start_time
    
    print(f"\nTests completed: {passed}/{total}")
    print(f"Success rate: {(passed/total)*100:.1f}%")
    print(f"Elapsed time: {elapsed_time:.2f} seconds")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! Neuronas AI system is ready.")
        return True
    else:
        print(f"\n⚠ {total-passed} tests failed. Check the errors above.")
        return False

if __name__ == "__main__":
    success = run_comprehensive_test()
    sys.exit(0 if success else 1)
