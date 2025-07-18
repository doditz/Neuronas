#!/usr/bin/env python3
"""
Quick Test Script for Neuronas Secure Key Pipeline
=================================================

Interactive test to verify the complete secure key management system.
"""

import os
import sys
import getpass
from datetime import datetime

def test_key_storage_and_retrieval():
    """Test the complete key storage and retrieval pipeline"""
    print("🔐 Testing Neuronas Secure Key Pipeline")
    print("=" * 50)
    
    try:
        from simple_secure_keys import NeuronasKeyManager
        
        # Initialize key manager
        km = NeuronasKeyManager()
        print("✅ Key manager initialized successfully")
        
        # Test service
        service = 'perplexity'
        
        print(f"\n🧪 Testing with {service.title()} service...")
        
        # Check current status
        print(f"\n📋 Current status for {service}:")
        
        # Try to get existing key (non-interactive first)
        existing_key = km.get_api_key(service, interactive=False)
        
        if existing_key:
            print(f"✅ Found existing {service} key (length: {len(existing_key)} characters)")
            
            # Ask if user wants to test with existing or enter new
            print(f"\n🔄 Options:")
            print(f"1. Test with existing {service} key")
            print(f"2. Update {service} key") 
            print(f"3. Skip {service} and test another service")
            
            while True:
                choice = input("Choose option (1/2/3): ").strip()
                if choice == '1':
                    api_key = existing_key
                    print(f"✅ Using existing {service} key for testing")
                    break
                elif choice == '2':
                    api_key = getpass.getpass(f"Enter new {service} API key: ")
                    if api_key:
                        success = km.simple_keys.store_key(service, api_key, overwrite=True)
                        if success:
                            print(f"✅ {service} key updated successfully")
                        else:
                            print(f"❌ Failed to update {service} key")
                            return False
                    else:
                        print("❌ No key entered")
                        return False
                    break
                elif choice == '3':
                    print("⚠️ Skipping test")
                    return True
                else:
                    print("Please enter 1, 2, or 3")
        else:
            print(f"❌ No existing {service} key found")
            
            # Ask user to enter key
            api_key = getpass.getpass(f"Enter your {service} API key to test: ")
            if not api_key:
                print("❌ No key entered, cannot test")
                return False
            
            # Store the key
            print(f"\n💾 Storing {service} key securely...")
            success = km.simple_keys.store_key(service, api_key)
            if not success:
                print(f"❌ Failed to store {service} key")
                return False
        
        # Test retrieval
        print(f"\n🔍 Testing key retrieval...")
        retrieved_key = km.get_api_key(service, interactive=False)
        
        if retrieved_key:
            print(f"✅ Successfully retrieved {service} key")
            
            # Verify it's the same key
            if retrieved_key == api_key:
                print("✅ Key integrity verified (matches original)")
            else:
                print("❌ Key integrity failed (doesn't match original)")
                return False
        else:
            print(f"❌ Failed to retrieve {service} key")
            return False
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def test_perplexity_integration():
    """Test Perplexity API integration with stored key"""
    print(f"\n🧠 Testing Perplexity API Integration")
    print("=" * 40)
    
    try:
        from perplexity_integration import PerplexityIntegration
        
        # Initialize Perplexity (should use secure key manager)
        perplexity = PerplexityIntegration()
        
        if not perplexity.is_available():
            print("❌ Perplexity API key not available")
            return False
        
        print("✅ Perplexity integration initialized with API key")
        
        # Test a simple query
        print("\n🔍 Testing API call...")
        result = perplexity.research_query(
            "What is the current date?", 
            model='fast',
            max_tokens=100
        )
        
        if result['success']:
            print("✅ API call successful!")
            print(f"📊 Response length: {len(result['response'])} characters")
            print(f"⏱️ Processing time: {result.get('processing_time', 0):.2f}s")
            print(f"📝 Response preview: {result['response'][:100]}...")
            return True
        else:
            print(f"❌ API call failed: {result.get('error', 'Unknown error')}")
            return False
            
    except ImportError as e:
        print(f"❌ Perplexity integration not available: {e}")
        return False
    except Exception as e:
        print(f"❌ Perplexity test failed: {e}")
        return False

def test_web_gui_integration():
    """Test web GUI integration"""
    print(f"\n🌐 Testing Web GUI Integration")
    print("=" * 35)
    
    try:
        from secure_key_web_gui import integrate_key_gui_routes, SERVICES
        from flask import Flask
        
        # Create test app
        app = Flask(__name__)
        app.secret_key = 'test-key'
        
        # Integrate routes
        integrate_key_gui_routes(app)
        print("✅ Web GUI routes integrated")
        
        # Test endpoints
        with app.test_client() as client:
            # Test status endpoint
            response = client.get('/api/keys/status')
            if response.status_code == 200:
                data = response.get_json()
                print(f"✅ Status endpoint working ({len(data)} services)")
                
                # Show status for each service
                for service, info in data.items():
                    status = "✅ Configured" if info['configured'] else "❌ Not set"
                    print(f"   {service.title()}: {status}")
            else:
                print(f"❌ Status endpoint failed: {response.status_code}")
                return False
            
            # Test manager page
            response = client.get('/api/keys/manager')
            if response.status_code == 200:
                print("✅ Manager page accessible")
            else:
                print(f"❌ Manager page failed: {response.status_code}")
                return False
        
        print("✅ Web GUI integration working")
        print("🌐 Access at: http://localhost:5000/api/keys/manager")
        return True
        
    except ImportError as e:
        print(f"❌ Web GUI not available: {e}")
        return False
    except Exception as e:
        print(f"❌ Web GUI test failed: {e}")
        return False

def main():
    """Run complete pipeline test"""
    print("🚀 Neuronas Secure Key Pipeline Test")
    print("=" * 45)
    print(f"📅 Test started at: {datetime.now()}")
    print()
    
    # Run tests
    tests = [
        ("Key Storage & Retrieval", test_key_storage_and_retrieval),
        ("Perplexity Integration", test_perplexity_integration),
        ("Web GUI Integration", test_web_gui_integration)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print(f"\n{'='*60}")
        try:
            results[test_name] = test_func()
        except KeyboardInterrupt:
            print(f"\n⚠️ Test interrupted by user")
            results[test_name] = False
            break
        except Exception as e:
            print(f"\n❌ Test crashed: {e}")
            results[test_name] = False
    
    # Show summary
    print(f"\n{'='*60}")
    print("📊 TEST SUMMARY")
    print("=" * 20)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:25} {status}")
    
    # Overall result
    passed = sum(results.values())
    total = len(results)
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! Your secure key pipeline is working perfectly!")
        print("\n🚀 Next steps:")
        print("   • Your API keys are securely stored")
        print("   • Perplexity integration is working")
        print("   • Web GUI is ready to use")
        print("   • Visit: http://localhost:5000/api/keys/manager")
    else:
        print("⚠️ Some tests failed. Check the output above for details.")
    
    print(f"\n📅 Test completed at: {datetime.now()}")
    return 0 if passed == total else 1

if __name__ == "__main__":
    sys.exit(main())
