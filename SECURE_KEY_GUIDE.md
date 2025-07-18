# 🔐 Neuronas Secure Key Management Guide

## Quick Start

### 1. 🚀 One-Command Setup
```bash
./neuronas-keys setup
```

### 2. 🖥️ GUI Interface
```bash
./neuronas-key-gui
```

### 3. 🌐 Web Interface
Add to your Flask app:
```python
from secure_key_web_gui import integrate_key_gui_routes
integrate_key_gui_routes(app)
# Visit: http://localhost:5000/api/keys/manager
```

## Available Methods

### 🔧 Command Line
- `./neuronas-keys setup` - Interactive setup
- `./neuronas-keys store <service>` - Store a key
- `./neuronas-keys list` - List configured services
- `./neuronas-keys validate` - Validate configuration

### 🖥️ Desktop GUI (Tkinter)
- `./neuronas-key-gui` - Launch key manager
- `python3 secure_key_gui.py manager` - Direct launch
- `python3 secure_key_gui.py input perplexity` - Configure specific service

### 🌐 Web GUI (Flask)
- Visit `/api/keys/manager` in your app
- Secure popup for each service
- Real-time validation
- Modern responsive interface

### 🐍 Python API
```python
from simple_secure_keys import NeuronasKeyManager

km = NeuronasKeyManager()
api_key = km.get_api_key('perplexity')

# Or quick popup
from secure_key_gui import quick_key_input
key = quick_key_input('openai')
```

## Security Features

- 🔒 **Encrypted Storage**: XOR + SHA256 encryption
- 🔑 **Master Password**: Protected with PBKDF2
- 🛡️ **File Permissions**: Owner-only access (chmod 600)
- 🏠 **Local Storage**: No network transmission
- ✅ **Key Validation**: Format verification
- 🔄 **Fallback Chain**: Secure storage → Environment → Prompt

## Supported Services

- 🧠 **Perplexity AI** - Research and reasoning
- 🤖 **OpenAI** - GPT models
- 🎭 **Anthropic Claude** - Advanced AI assistant
- 🌟 **Google AI** - Gemini models

## Testing

```bash
./test-secure-keys
```

## Troubleshooting

### GUI Not Working?
- Install tkinter: `sudo apt-get install python3-tk` (Linux)
- Use web interface: Visit `/api/keys/manager`

### Permission Errors?
- Check directory: `ls -la ~/.neuronas`
- Should show: `drwx------` (700 permissions)

### Integration Issues?
- Restart Flask app after key configuration
- Check logs for integration status

## Why This Approach?

✅ **Better than .NET**: No runtime dependencies, native Python integration
✅ **User Friendly**: Multiple interfaces (CLI, GUI, Web)
✅ **Secure**: Industry-standard encryption without complexity
✅ **Flexible**: Works standalone or integrated
✅ **Maintainable**: Single language ecosystem

Ready to use! 🎉
