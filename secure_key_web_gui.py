"""
Secure Web Popup for API Key Input - Neuronas Flask Integration
==============================================================

Web-based secure popup for API key management that integrates with Flask.
"""

from flask import Blueprint, render_template, request, jsonify, session
import logging
from typing import Optional, Dict
import os

# Import secure key manager
try:
    from simple_secure_keys import NeuronasKeyManager
    SECURE_KEYS_AVAILABLE = True
except ImportError:
    SECURE_KEYS_AVAILABLE = False

logger = logging.getLogger(__name__)

# Create Blueprint for key management routes
key_gui_bp = Blueprint('key_gui', __name__, url_prefix='/api/keys')

# Initialize key manager
key_manager = NeuronasKeyManager() if SECURE_KEYS_AVAILABLE else None

# Service configurations
SERVICES = {
    'perplexity': {
        'name': 'Perplexity AI',
        'description': 'Advanced research and reasoning AI',
        'icon': '🧠',
        'placeholder': 'pplx-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx',
        'help_url': 'https://docs.perplexity.ai/docs/getting-started',
        'color': '#20B2AA'
    },
    'openai': {
        'name': 'OpenAI',
        'description': 'GPT models and AI services',
        'icon': '🤖',
        'placeholder': 'sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx',
        'help_url': 'https://platform.openai.com/api-keys',
        'color': '#10A37F'
    },
    'anthropic': {
        'name': 'Anthropic Claude',
        'description': 'Claude AI assistant',
        'icon': '🎭',
        'placeholder': 'sk-ant-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx',
        'help_url': 'https://console.anthropic.com/',
        'color': '#D97706'
    },
    'google': {
        'name': 'Google AI',
        'description': 'Gemini and Google AI services',
        'icon': '🌟',
        'placeholder': 'AIzaxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx',
        'help_url': 'https://console.cloud.google.com/apis/credentials',
        'color': '#4285F4'
    }
}

@key_gui_bp.route('/status')
def get_key_status():
    """Get status of all API keys"""
    status = {}
    
    for service_id, service_info in SERVICES.items():
        # Check secure storage
        if key_manager:
            key = key_manager.get_api_key(service_id)
            if key:
                status[service_id] = {
                    'configured': True,
                    'source': 'secure_storage',
                    'service_info': service_info
                }
                continue
        
        # Check environment
        env_key = os.getenv(f"{service_id.upper()}_API_KEY")
        status[service_id] = {
            'configured': bool(env_key),
            'source': 'environment' if env_key else 'none',
            'service_info': service_info
        }
    
    return jsonify(status)

@key_gui_bp.route('/validate/<service>', methods=['POST'])
def validate_key(service):
    """Validate API key format"""
    if service not in SERVICES:
        return jsonify({'valid': False, 'error': 'Unknown service'}), 400
    
    data = request.get_json()
    if not data or 'key' not in data:
        return jsonify({'valid': False, 'error': 'Key required'}), 400
    
    api_key = data['key'].strip()
    
    # Basic validation based on service
    if service == 'perplexity':
        valid = api_key.startswith('pplx-') and len(api_key) > 20
    elif service == 'openai':
        valid = api_key.startswith('sk-') and len(api_key) > 40
    elif service == 'anthropic':
        valid = api_key.startswith('sk-ant-') and len(api_key) > 30
    elif service == 'google':
        valid = api_key.startswith('AIza') and len(api_key) > 30
    else:
        valid = len(api_key) > 10
    
    return jsonify({
        'valid': valid,
        'message': 'Valid API key format' if valid else 'Invalid API key format'
    })

@key_gui_bp.route('/store/<service>', methods=['POST'])
def store_key(service):
    """Store API key securely"""
    if service not in SERVICES:
        return jsonify({'success': False, 'error': 'Unknown service'}), 400
    
    data = request.get_json()
    if not data or 'key' not in data:
        return jsonify({'success': False, 'error': 'Key required'}), 400
    
    api_key = data['key'].strip()
    
    try:
        if key_manager:
            # Store in secure storage
            success = key_manager.simple_keys.store_key(service, api_key, overwrite=True)
            if success:
                logger.info(f"API key stored securely for {service}")
                return jsonify({
                    'success': True,
                    'message': f'API key for {SERVICES[service]["name"]} stored securely',
                    'storage': 'secure'
                })
            else:
                return jsonify({'success': False, 'error': 'Failed to store key'}), 500
        else:
            # Fallback to environment (session only)
            os.environ[f"{service.upper()}_API_KEY"] = api_key
            return jsonify({
                'success': True,
                'message': f'API key for {SERVICES[service]["name"]} set for current session',
                'storage': 'environment'
            })
    
    except Exception as e:
        logger.error(f"Error storing key for {service}: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@key_gui_bp.route('/delete/<service>', methods=['DELETE'])
def delete_key(service):
    """Delete stored API key"""
    if service not in SERVICES:
        return jsonify({'success': False, 'error': 'Unknown service'}), 400
    
    try:
        if key_manager:
            success = key_manager.simple_keys.delete_key(service)
            return jsonify({
                'success': success,
                'message': f'API key for {SERVICES[service]["name"]} deleted' if success else 'Key not found'
            })
        else:
            # Remove from environment
            env_var = f"{service.upper()}_API_KEY"
            if env_var in os.environ:
                del os.environ[env_var]
                return jsonify({
                    'success': True,
                    'message': f'API key for {SERVICES[service]["name"]} removed from session'
                })
            else:
                return jsonify({
                    'success': False,
                    'message': 'Key not found in environment'
                })
    
    except Exception as e:
        logger.error(f"Error deleting key for {service}: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@key_gui_bp.route('/popup/<service>')
def show_key_popup(service):
    """Show key input popup for specific service"""
    if service not in SERVICES:
        return "Service not found", 404
    
    return render_template('key_popup.html', 
                         service=service, 
                         service_info=SERVICES[service])

@key_gui_bp.route('/manager')
def show_key_manager():
    """Show comprehensive key manager"""
    return render_template('key_manager.html', services=SERVICES)

# Template for key popup
KEY_POPUP_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🔐 {{ service_info.name }} API Key</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        .secure-popup {
            max-width: 500px;
            margin: 50px auto;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            border-radius: 15px;
            overflow: hidden;
        }
        .service-header {
            background: linear-gradient(135deg, {{ service_info.color }}, {{ service_info.color }}aa);
            color: white;
            padding: 20px;
            text-align: center;
        }
        .key-input {
            font-family: 'Courier New', monospace;
            letter-spacing: 1px;
        }
        .validation-feedback {
            font-size: 0.875rem;
            margin-top: 5px;
        }
        .security-badge {
            background: #28a745;
            color: white;
            padding: 5px 10px;
            border-radius: 15px;
            font-size: 0.8rem;
            display: inline-block;
            margin: 5px;
        }
        .btn-secure {
            background: {{ service_info.color }};
            border-color: {{ service_info.color }};
            color: white;
        }
        .btn-secure:hover {
            background: {{ service_info.color }}dd;
            border-color: {{ service_info.color }}dd;
            color: white;
        }
    </style>
</head>
<body class="bg-light">
    <div class="secure-popup">
        <!-- Header -->
        <div class="service-header">
            <div class="display-6">{{ service_info.icon }} {{ service_info.name }}</div>
            <p class="mb-0">{{ service_info.description }}</p>
        </div>
        
        <!-- Body -->
        <div class="card-body p-4">
            <!-- Security Notice -->
            <div class="alert alert-info border-0" role="alert">
                <i class="fas fa-shield-alt me-2"></i>
                <strong>Secure Storage:</strong> Your API key will be encrypted and stored locally.
                <div class="mt-2">
                    <span class="security-badge">🔒 Encrypted</span>
                    <span class="security-badge">🔑 Password Protected</span>
                    <span class="security-badge">🛡️ Local Only</span>
                </div>
            </div>
            
            <!-- API Key Input -->
            <div class="mb-3">
                <label for="apiKey" class="form-label fw-bold">
                    <i class="fas fa-key me-2"></i>API Key
                </label>
                <div class="input-group">
                    <input type="password" 
                           class="form-control key-input" 
                           id="apiKey" 
                           placeholder="{{ service_info.placeholder }}"
                           autocomplete="off">
                    <button class="btn btn-outline-secondary" 
                            type="button" 
                            id="toggleKey"
                            title="Show/Hide Key">
                        <i class="fas fa-eye"></i>
                    </button>
                </div>
                <div id="validation" class="validation-feedback"></div>
            </div>
            
            <!-- Actions -->
            <div class="d-grid gap-2 d-md-flex justify-content-md-between">
                <a href="{{ service_info.help_url }}" 
                   target="_blank" 
                   class="btn btn-outline-primary">
                    <i class="fas fa-external-link-alt me-2"></i>Get API Key
                </a>
                
                <div>
                    <button type="button" 
                            class="btn btn-outline-secondary me-2" 
                            onclick="window.close()">
                        Cancel
                    </button>
                    <button type="button" 
                            class="btn btn-secure" 
                            id="saveKey" 
                            disabled>
                        <i class="fas fa-save me-2"></i>Save Securely
                    </button>
                </div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        const apiKeyInput = document.getElementById('apiKey');
        const toggleKeyBtn = document.getElementById('toggleKey');
        const validationDiv = document.getElementById('validation');
        const saveBtn = document.getElementById('saveKey');
        
        // Toggle password visibility
        toggleKeyBtn.addEventListener('click', function() {
            const isPassword = apiKeyInput.type === 'password';
            apiKeyInput.type = isPassword ? 'text' : 'password';
            this.innerHTML = isPassword ? '<i class="fas fa-eye-slash"></i>' : '<i class="fas fa-eye"></i>';
        });
        
        // Real-time validation
        apiKeyInput.addEventListener('input', async function() {
            const key = this.value.trim();
            
            if (!key) {
                validationDiv.innerHTML = '<span class="text-muted">⏳ Enter API key to validate</span>';
                saveBtn.disabled = true;
                return;
            }
            
            try {
                const response = await fetch(`/api/keys/validate/{{ service }}`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ key: key })
                });
                
                const result = await response.json();
                
                if (result.valid) {
                    validationDiv.innerHTML = '<span class="text-success">✅ Valid API key format</span>';
                    saveBtn.disabled = false;
                } else {
                    validationDiv.innerHTML = '<span class="text-danger">❌ Invalid API key format</span>';
                    saveBtn.disabled = true;
                }
            } catch (error) {
                validationDiv.innerHTML = '<span class="text-warning">⚠️ Validation error</span>';
                saveBtn.disabled = true;
            }
        });
        
        // Save key
        saveBtn.addEventListener('click', async function() {
            const key = apiKeyInput.value.trim();
            
            if (!key) {
                alert('Please enter an API key');
                return;
            }
            
            this.disabled = true;
            this.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Saving...';
            
            try {
                const response = await fetch(`/api/keys/store/{{ service }}`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ key: key })
                });
                
                const result = await response.json();
                
                if (result.success) {
                    // Show success message
                    const successAlert = document.createElement('div');
                    successAlert.className = 'alert alert-success mt-3';
                    successAlert.innerHTML = `<i class="fas fa-check-circle me-2"></i>${result.message}`;
                    
                    validationDiv.parentNode.appendChild(successAlert);
                    
                    // Close window after delay
                    setTimeout(() => {
                        if (window.opener) {
                            window.opener.location.reload();
                        }
                        window.close();
                    }, 2000);
                } else {
                    alert(`Error: ${result.error}`);
                    this.disabled = false;
                    this.innerHTML = '<i class="fas fa-save me-2"></i>Save Securely';
                }
            } catch (error) {
                alert(`Error: ${error.message}`);
                this.disabled = false;
                this.innerHTML = '<i class="fas fa-save me-2"></i>Save Securely';
            }
        });
        
        // Handle Enter key
        apiKeyInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter' && !saveBtn.disabled) {
                saveBtn.click();
            }
        });
        
        // Focus on input
        apiKeyInput.focus();
    </script>
</body>
</html>
"""

# Template for key manager
KEY_MANAGER_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🔐 Neuronas API Key Manager</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        .service-card {
            transition: transform 0.2s, box-shadow 0.2s;
            border: none;
            border-radius: 15px;
            overflow: hidden;
        }
        .service-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 25px rgba(0,0,0,0.1);
        }
        .service-header {
            padding: 15px;
            color: white;
            text-align: center;
        }
        .status-badge {
            position: absolute;
            top: 10px;
            right: 10px;
            padding: 5px 10px;
            border-radius: 15px;
            font-size: 0.75rem;
            font-weight: bold;
        }
        .configured {
            background: #28a745;
            color: white;
        }
        .not-configured {
            background: #dc3545;
            color: white;
        }
    </style>
</head>
<body class="bg-light">
    <div class="container my-5">
        <div class="text-center mb-5">
            <h1 class="display-4">🔐 API Key Manager</h1>
            <p class="lead text-muted">Secure management for your Neuronas API keys</p>
        </div>
        
        <div id="servicesContainer" class="row g-4">
            <!-- Services will be loaded here -->
        </div>
        
        <div class="text-center mt-5">
            <button class="btn btn-primary btn-lg" onclick="refreshStatus()">
                <i class="fas fa-sync-alt me-2"></i>Refresh Status
            </button>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        async function loadServices() {
            try {
                const response = await fetch('/api/keys/status');
                const services = await response.json();
                
                const container = document.getElementById('servicesContainer');
                container.innerHTML = '';
                
                for (const [serviceId, data] of Object.entries(services)) {
                    const card = createServiceCard(serviceId, data);
                    container.appendChild(card);
                }
            } catch (error) {
                console.error('Error loading services:', error);
            }
        }
        
        function createServiceCard(serviceId, data) {
            const col = document.createElement('div');
            col.className = 'col-md-6 col-lg-4';
            
            const isConfigured = data.configured;
            const service = data.service_info;
            
            col.innerHTML = `
                <div class="card service-card h-100">
                    <div class="service-header" style="background: linear-gradient(135deg, ${service.color}, ${service.color}aa);">
                        <div class="status-badge ${isConfigured ? 'configured' : 'not-configured'}">
                            ${isConfigured ? '✅ Active' : '❌ Not Set'}
                        </div>
                        <div class="fs-1 mb-2">${service.icon}</div>
                        <h5 class="mb-0">${service.name}</h5>
                    </div>
                    <div class="card-body d-flex flex-column">
                        <p class="text-muted mb-3">${service.description}</p>
                        <div class="mt-auto">
                            <div class="d-grid gap-2">
                                <button class="btn btn-primary" onclick="configureKey('${serviceId}')">
                                    <i class="fas fa-cog me-2"></i>Configure
                                </button>
                                ${isConfigured ? `
                                <button class="btn btn-outline-danger btn-sm" onclick="deleteKey('${serviceId}')">
                                    <i class="fas fa-trash me-2"></i>Remove
                                </button>
                                ` : ''}
                            </div>
                        </div>
                    </div>
                </div>
            `;
            
            return col;
        }
        
        function configureKey(serviceId) {
            const popup = window.open(
                `/api/keys/popup/${serviceId}`,
                'configureKey',
                'width=600,height=700,scrollbars=yes,resizable=yes'
            );
            
            // Refresh when popup closes
            const checkClosed = setInterval(() => {
                if (popup.closed) {
                    clearInterval(checkClosed);
                    loadServices();
                }
            }, 1000);
        }
        
        async function deleteKey(serviceId) {
            if (!confirm(`Are you sure you want to remove the API key for this service?`)) {
                return;
            }
            
            try {
                const response = await fetch(`/api/keys/delete/${serviceId}`, {
                    method: 'DELETE'
                });
                
                const result = await response.json();
                
                if (result.success) {
                    loadServices();
                } else {
                    alert(`Error: ${result.message}`);
                }
            } catch (error) {
                alert(`Error: ${error.message}`);
            }
        }
        
        function refreshStatus() {
            loadServices();
        }
        
        // Load services on page load
        loadServices();
    </script>
</body>
</html>
"""

# Function to integrate with Flask app
def integrate_key_gui_routes(app):
    """
    Integrate key GUI routes with Flask app
    
    Args:
        app: Flask application instance
    """
    # Register blueprint
    app.register_blueprint(key_gui_bp)
    
    # Add templates
    if not os.path.exists('templates'):
        os.makedirs('templates')
    
    with open('templates/key_popup.html', 'w') as f:
        f.write(KEY_POPUP_TEMPLATE)
    
    with open('templates/key_manager.html', 'w') as f:
        f.write(KEY_MANAGER_TEMPLATE)
    
    logger.info("✅ Secure key GUI routes integrated")

if __name__ == "__main__":
    # Standalone Flask app for testing
    from flask import Flask
    
    app = Flask(__name__)
    app.secret_key = 'dev-key-change-in-production'
    
    integrate_key_gui_routes(app)
    
    @app.route('/')
    def home():
        return '<h1>Neuronas Key Manager</h1><a href="/api/keys/manager">Manage API Keys</a>'
    
    print("🔐 Starting Neuronas Key Manager...")
    print("🌐 Open: http://localhost:5000/api/keys/manager")
    
    app.run(debug=True, port=5000)
