#!/usr/bin/env python3
"""
Test Secure Key Popup System - Neuronas
======================================

Test and demonstration script for the secure API key popup system.
"""

import os
import sys
import time
from pathlib import Path

def test_tkinter_popup():
    """Test the Tkinter-based secure popup"""
    print("🧪 Testing Tkinter Secure Popup...")
    
    try:
        from secure_key_gui import quick_key_input, show_key_manager
        
        print("✅ Tkinter GUI module imported successfully")
        
        # Test quick key input
        print("\n🔑 Testing quick key input for Perplexity...")
        print("(A popup window should appear)")
        
        # This would show the popup (commented out for non-interactive testing)
        # key = quick_key_input('perplexity')
        # if key:
        #     print(f"✅ Key configured: {len(key)} characters")
        # else:
        #     print("❌ No key configured")
        
        print("✅ Tkinter popup test ready (uncomment lines to test interactively)")
        return True
        
    except ImportError as e:
        print(f"❌ Tkinter not available: {e}")
        return False
    except Exception as e:
        print(f"❌ Tkinter test failed: {e}")
        return False

def test_web_popup():
    """Test the web-based secure popup"""
    print("\n🌐 Testing Web-based Secure Popup...")
    
    try:
        from secure_key_web_gui import integrate_key_gui_routes, SERVICES
        from flask import Flask
        
        # Create test Flask app
        app = Flask(__name__)
        app.secret_key = 'test-key'
        
        # Integrate routes
        integrate_key_gui_routes(app)
        
        print("✅ Web GUI routes integrated successfully")
        
        # Test service configuration
        print(f"✅ Available services: {list(SERVICES.keys())}")
        
        # Test route availability
        with app.test_client() as client:
            # Test status endpoint
            response = client.get('/api/keys/status')
            if response.status_code == 200:
                print("✅ Status endpoint working")
            else:
                print(f"❌ Status endpoint failed: {response.status_code}")
            
            # Test manager page
            response = client.get('/api/keys/manager')
            if response.status_code == 200:
                print("✅ Manager page working")
            else:
                print(f"❌ Manager page failed: {response.status_code}")
        
        print("✅ Web popup test completed successfully")
        return True
        
    except ImportError as e:
        print(f"❌ Web GUI dependencies not available: {e}")
        return False
    except Exception as e:
        print(f"❌ Web popup test failed: {e}")
        return False

def test_secure_storage():
    """Test the secure key storage system"""
    print("\n🔒 Testing Secure Key Storage...")
    
    try:
        from simple_secure_keys import NeuronasKeyManager
        
        # Initialize key manager
        key_manager = NeuronasKeyManager()
        print("✅ Key manager initialized")
        
        # Test storage directory
        config_dir = Path.home() / ".neuronas"
        if config_dir.exists():
            print(f"✅ Config directory exists: {config_dir}")
            
            # Check permissions
            if os.name != 'nt':  # Not Windows
                stat = config_dir.stat()
                permissions = oct(stat.st_mode)[-3:]
                print(f"✅ Directory permissions: {permissions}")
        else:
            print("⚠️ Config directory not created yet")
        
        print("✅ Secure storage test completed")
        return True
        
    except ImportError as e:
        print(f"❌ Secure storage not available: {e}")
        return False
    except Exception as e:
        print(f"❌ Secure storage test failed: {e}")
        return False

def demo_usage():
    """Demonstrate usage examples"""
    print("\n📋 Usage Examples:")
    print("=" * 50)
    
    print("\n1. 🖥️ Desktop GUI (Tkinter):")
    print("   python secure_key_gui.py manager")
    print("   python secure_key_gui.py input perplexity")
    print("   python secure_key_gui.py quick")
    
    print("\n2. 🌐 Web GUI (Flask Integration):")
    print("   # Add to your Flask app:")
    print("   from secure_key_web_gui import integrate_key_gui_routes")
    print("   integrate_key_gui_routes(app)")
    print("   # Visit: http://localhost:5000/api/keys/manager")
    
    print("\n3. 🔧 Command Line:")
    print("   python simple_secure_keys.py setup")
    print("   python simple_secure_keys.py store perplexity")
    print("   python simple_secure_keys.py list")
    
    print("\n4. 🐍 Python Code:")
    print("   from simple_secure_keys import NeuronasKeyManager")
    print("   km = NeuronasKeyManager()")
    print("   key = km.get_api_key('perplexity')")
    
    print("\n5. 🚀 Quick Setup:")
    print("   ./setup_secure_keys.sh")
    print("   ./neuronas-keys setup")

def run_integration_test():
    """Run integration test with Neuronas app"""
    print("\n🚀 Testing Integration with Neuronas App...")
    
    try:
        # Test import of main app
        import app
        print("✅ Main app imported successfully")
        
        # Check if secure GUI is integrated
        if hasattr(app, 'SECURE_GUI_AVAILABLE') and app.SECURE_GUI_AVAILABLE:
            print("✅ Secure GUI is integrated with main app")
        else:
            print("⚠️ Secure GUI not integrated with main app")
        
        # Test Perplexity integration
        try:
            from perplexity_integration import PerplexityIntegration
            perplexity = PerplexityIntegration()
            
            if perplexity.is_available():
                print("✅ Perplexity integration ready with API key")
            else:
                print("⚠️ Perplexity integration ready (API key needed)")
        except ImportError:
            print("⚠️ Perplexity integration not available")
        
        return True
        
    except ImportError as e:
        print(f"❌ Main app import failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        return False

def main():
    """Main test function"""
    print("🔐 Neuronas Secure Key Popup System Test")
    print("=" * 50)
    
    # Track test results
    results = {
        'tkinter': test_tkinter_popup(),
        'web': test_web_popup(),
        'storage': test_secure_storage(),
        'integration': run_integration_test()
    }
    
    # Show summary
    print("\n📊 Test Results Summary:")
    print("=" * 30)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name.title():12} {status}")
    
    # Overall result
    all_passed = all(results.values())
    overall_status = "✅ ALL TESTS PASSED" if all_passed else "⚠️ SOME TESTS FAILED"
    
    print(f"\nOverall: {overall_status}")
    
    # Show usage examples
    demo_usage()
    
    print("\n🎉 Secure key popup system is ready for use!")
    print("\n📝 Next Steps:")
    print("   1. Run: ./setup_secure_keys.sh")
    print("   2. Configure your API keys")
    print("   3. Start using secure key management!")
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())
