#!/usr/bin/env python3
"""
Neuronas Secure Key Web Server
=============================

Standalone web server for secure API key management with GUI interface.
"""

import os
import sys
import threading
import webbrowser
import time
from flask import Flask, render_template_string, redirect, url_for
import logging

# Suppress Flask development warning
import warnings
warnings.filterwarnings('ignore', message='This is a development server')

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import our modules
try:
    from secure_key_web_gui import integrate_key_gui_routes, SERVICES, KEY_MANAGER_TEMPLATE
    from simple_secure_keys import NeuronasKeyManager
    MODULES_AVAILABLE = True
except ImportError as e:
    logger.error(f"Required modules not available: {e}")
    MODULES_AVAILABLE = False

def create_app():
    """Create and configure Flask app"""
    app = Flask(__name__)
    app.secret_key = os.environ.get('SECRET_KEY', 'neuronas-dev-key-change-in-production')
    
    if not MODULES_AVAILABLE:
        @app.route('/')
        def error():
            return """
            <h1>Error</h1>
            <p>Required modules not available. Please run:</p>
            <pre>pip install flask cryptography requests</pre>
            """, 500
        return app
    
    # Integrate secure key GUI routes
    integrate_key_gui_routes(app)
    
    @app.route('/')
    def home():
        """Home page with navigation"""
        return render_template_string("""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>🔐 Neuronas Key Manager</title>
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
            <style>
                .hero-section {
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 60px 0;
                    text-align: center;
                }
                .feature-card {
                    transition: transform 0.2s;
                    border: none;
                    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                }
                .feature-card:hover {
                    transform: translateY(-5px);
                }
            </style>
        </head>
        <body>
            <!-- Hero Section -->
            <div class="hero-section">
                <div class="container">
                    <h1 class="display-4">🔐 Neuronas Secure Key Manager</h1>
                    <p class="lead">Secure, user-friendly API key management for your AI systems</p>
                    <a href="/api/keys/manager" class="btn btn-light btn-lg mt-3">
                        <i class="fas fa-key me-2"></i>Manage API Keys
                    </a>
                </div>
            </div>
            
            <!-- Features Section -->
            <div class="container my-5">
                <div class="row g-4">
                    <div class="col-md-4">
                        <div class="card feature-card h-100">
                            <div class="card-body text-center">
                                <div class="display-6 text-primary mb-3">🔒</div>
                                <h5 class="card-title">Secure Storage</h5>
                                <p class="card-text">Encrypted local storage with master password protection</p>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-4">
                        <div class="card feature-card h-100">
                            <div class="card-body text-center">
                                <div class="display-6 text-success mb-3">🎯</div>
                                <h5 class="card-title">Easy to Use</h5>
                                <p class="card-text">Intuitive web interface with real-time validation</p>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-4">
                        <div class="card feature-card h-100">
                            <div class="card-body text-center">
                                <div class="display-6 text-info mb-3">🚀</div>
                                <h5 class="card-title">AI Ready</h5>
                                <p class="card-text">Supports Perplexity, OpenAI, Claude, and Google AI</p>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="text-center mt-5">
                    <h3>Current Status</h3>
                    <div id="statusContainer" class="row justify-content-center">
                        <!-- Status will be loaded here -->
                    </div>
                </div>
            </div>
            
            <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
            <script>
                // Load current status
                fetch('/api/keys/status')
                    .then(response => response.json())
                    .then(data => {
                        const container = document.getElementById('statusContainer');
                        container.innerHTML = '';
                        
                        for (const [service, info] of Object.entries(data)) {
                            const isConfigured = info.configured;
                            const serviceInfo = info.service_info;
                            
                            const col = document.createElement('div');
                            col.className = 'col-auto mb-2';
                            
                            col.innerHTML = `
                                <span class="badge ${isConfigured ? 'bg-success' : 'bg-secondary'} fs-6">
                                    ${serviceInfo.icon} ${serviceInfo.name}: ${isConfigured ? 'Ready' : 'Not Set'}
                                </span>
                            `;
                            
                            container.appendChild(col);
                        }
                    })
                    .catch(error => {
                        console.error('Error loading status:', error);
                    });
            </script>
        </body>
        </html>
        """)
    
    @app.route('/test')
    def test_page():
        """Test page for API functionality"""
        return render_template_string("""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>🧪 API Test</title>
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        </head>
        <body>
            <div class="container my-5">
                <h1>🧪 API Test</h1>
                <p>Test your configured API keys</p>
                
                <div class="card">
                    <div class="card-body">
                        <h5>Perplexity API Test</h5>
                        <button class="btn btn-primary" onclick="testPerplexity()">Test Perplexity</button>
                        <div id="perplexityResult" class="mt-3"></div>
                    </div>
                </div>
                
                <a href="/" class="btn btn-secondary mt-3">← Back to Home</a>
            </div>
            
            <script>
                async function testPerplexity() {
                    const button = event.target;
                    const resultDiv = document.getElementById('perplexityResult');
                    
                    button.disabled = true;
                    button.textContent = 'Testing...';
                    resultDiv.innerHTML = '<div class="spinner-border" role="status"></div>';
                    
                    try {
                        const response = await fetch('/api/perplexity/research', {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json',
                            },
                            body: JSON.stringify({
                                query: 'What is the current date?',
                                model: 'fast'
                            })
                        });
                        
                        const result = await response.json();
                        
                        if (result.success) {
                            resultDiv.innerHTML = `
                                <div class="alert alert-success">
                                    <h6>✅ Test Successful!</h6>
                                    <p><strong>Response:</strong> ${result.response.substring(0, 200)}...</p>
                                    <p><small>Processing time: ${result.processing_time?.toFixed(2)}s</small></p>
                                </div>
                            `;
                        } else {
                            resultDiv.innerHTML = `
                                <div class="alert alert-danger">
                                    <h6>❌ Test Failed</h6>
                                    <p>${result.error}</p>
                                </div>
                            `;
                        }
                    } catch (error) {
                        resultDiv.innerHTML = `
                            <div class="alert alert-danger">
                                <h6>❌ Test Error</h6>
                                <p>${error.message}</p>
                            </div>
                        `;
                    }
                    
                    button.disabled = false;
                    button.textContent = 'Test Perplexity';
                }
            </script>
        </body>
        </html>
        """)
    
    # Register Perplexity routes if available
    try:
        from perplexity_routes import integrate_perplexity_routes
        integrate_perplexity_routes(app)
        logger.info("✅ Perplexity routes integrated")
    except ImportError as e:
        logger.warning(f"Perplexity routes not available: {e}")
    
    return app

def open_browser():
    """Open browser after a short delay"""
    time.sleep(1.5)
    webbrowser.open('http://localhost:5555')

def main():
    """Main function to run the web server"""
    print("🚀 Starting Neuronas Secure Key Web Server...")
    print("=" * 50)
    
    if not MODULES_AVAILABLE:
        print("❌ Required modules not available")
        print("Please run: pip install flask cryptography requests")
        return 1
    
    # Create app
    app = create_app()
    
    # Print startup info
    print("🌐 Web server starting...")
    print("📋 Available endpoints:")
    print("   • Home: http://localhost:5555/")
    print("   • Key Manager: http://localhost:5555/api/keys/manager")
    print("   • API Test: http://localhost:5555/test")
    print()
    print("🔐 Features:")
    print("   ✅ Secure API key storage")
    print("   ✅ Interactive key management")
    print("   ✅ Real-time validation")
    print("   ✅ Perplexity API integration")
    print()
    print("⚡ Opening browser in 1.5 seconds...")
    print("🛑 Press Ctrl+C to stop the server")
    print()
    
    # Open browser in background
    browser_thread = threading.Thread(target=open_browser)
    browser_thread.daemon = True
    browser_thread.start()
    
    try:
        # Run the Flask app
        app.run(
            host='127.0.0.1',
            port=5555,
            debug=False,
            use_reloader=False,
            threaded=True
        )
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
        return 0
    except Exception as e:
        print(f"❌ Server error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
