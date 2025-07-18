#!/bin/bash

# Neuronas Secure API Key Management Setup
# ========================================

echo "🔐 Setting up secure API key management for Neuronas..."
echo ""

# Install required Python packages
echo "📦 Installing required packages..."
pip install cryptography requests

# Check if packages are installed
python3 -c "
try:
    from cryptography.fernet import Fernet
    print('✅ Cryptography package installed')
except ImportError:
    print('❌ Cryptography package not available')
    exit(1)

try:
    import requests
    print('✅ Requests package installed')
except ImportError:
    print('❌ Requests package not available')
    exit(1)
"

if [ $? -ne 0 ]; then
    echo "❌ Required packages not installed. Please install manually:"
    echo "   pip install cryptography requests"
    exit 1
fi

# Create secure directory
echo ""
echo "📁 Setting up secure directory structure..."
mkdir -p ~/.neuronas/secure
chmod 700 ~/.neuronas

echo "✅ Secure directory created at ~/.neuronas"

# Test the secure key manager
echo ""
echo "🧪 Testing secure key management..."
python3 -c "
import sys
sys.path.append('.')

try:
    from simple_secure_keys import NeuronasKeyManager
    print('✅ Secure key manager imported successfully')
    
    # Test initialization
    km = NeuronasKeyManager()
    print('✅ Key manager initialized')
    
except Exception as e:
    print(f'❌ Error: {e}')
    exit(1)
"

if [ $? -ne 0 ]; then
    echo "❌ Secure key manager test failed"
    exit 1
fi

# Create convenient CLI script
echo ""
echo "🔧 Creating CLI tools..."

cat > neuronas-keys << 'EOF'
#!/bin/bash
# Neuronas Key Management CLI
cd "$(dirname "$0")"
python3 simple_secure_keys.py "$@"
EOF

chmod +x neuronas-keys

echo "✅ Created 'neuronas-keys' CLI tool"

# Display usage information
echo ""
echo "🎉 Setup complete! Here's how to use secure key management:"
echo ""
echo "📋 Available Methods:"
echo ""
echo "1. 📱 Simple Setup (Recommended):"
echo "   ./neuronas-keys setup"
echo ""
echo "2. 🔐 Store Individual Keys:"
echo "   ./neuronas-keys store perplexity"
echo "   ./neuronas-keys store openai"
echo ""
echo "3. 🔍 Check Keys:"
echo "   ./neuronas-keys list"
echo "   ./neuronas-keys validate"
echo ""
echo "4. 🌍 Environment Variables (Alternative):"
echo "   export PERPLEXITY_API_KEY='your_key_here'"
echo "   export OPENAI_API_KEY='your_key_here'"
echo ""
echo "🔒 Security Features:"
echo "   ✅ Master password protection"
echo "   ✅ File encryption (XOR + SHA256)"
echo "   ✅ Secure file permissions (600)"
echo "   ✅ Key integrity validation"
echo "   ✅ Environment variable fallback"
echo ""
echo "🚀 Next Steps:"
echo "   1. Run: ./neuronas-keys setup"
echo "   2. Configure your API keys"
echo "   3. Start using Neuronas with secure key management!"
echo ""

# Test Perplexity integration with secure keys
echo "🧪 Testing Perplexity integration..."
python3 -c "
import sys
sys.path.append('.')

try:
    from perplexity_integration import PerplexityIntegration
    perplexity = PerplexityIntegration()
    
    if perplexity.is_available():
        print('✅ Perplexity integration ready with API key')
    else:
        print('⚠️  Perplexity integration ready (API key needed)')
        print('   Run: ./neuronas-keys setup')
    
except Exception as e:
    print(f'⚠️  Perplexity integration note: {e}')
"

echo ""
echo "✨ Secure key management is now ready!"
