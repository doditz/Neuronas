
#!/usr/bin/env python3
"""
Script to pull recommended Ollama models for Neuronas dual-hemisphere processing
"""

import subprocess
import sys
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Recommended models for dual processing
RECOMMENDED_MODELS = {
    "creative": [
        "nous-hermes2:7b",      # Creative, metaphorical thinking
        "mistral:7b",           # General creative tasks
        "gemma:7b",             # Alternative creative model
        "dolphin-mixtral:8x7b", # Uncensored creative model
        "nous-hermes2-mixtral:8x7b" # Advanced uncensored creative
    ],
    "logical": [
        "llama3:8b",            # Analytical, structured reasoning
        "phi3:3b",              # Lightweight logical processing
        "deepseek-coder:6.7b",  # Specialized coding model
        "codellama:7b",         # Meta's coding specialist
        "wizard-vicuna-uncensored:7b" # Uncensored logical reasoning
    ],
    "specialized": [
        "deepseek-coder:33b",   # Advanced coding specialist
        "starcoder2:15b",       # Code generation specialist
        "magicoder:7b",         # Code-focused model
        "codestral:22b",        # Mistral's coding model
        "nemotron-mini:4b"      # Small Nemotron model (if available)
    ],
    "uncensored": [
        "wizard-vicuna-uncensored:13b", # Large uncensored model
        "dolphin-llama3:8b",            # Uncensored Llama3 variant
        "nous-capybara:7b",             # Unfiltered conversational
        "airoboros:7b"                  # Uncensored reasoning
    ]
}

def pull_model(model_name):
    """Pull a single model using Ollama"""
    try:
        logger.info(f"Pulling model: {model_name}")
        result = subprocess.run(
            ["ollama", "pull", model_name],
            capture_output=True,
            text=True,
            timeout=1800  # 30 minute timeout
        )
        
        if result.returncode == 0:
            logger.info(f"✓ Successfully pulled {model_name}")
            return True
        else:
            logger.error(f"✗ Failed to pull {model_name}: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        logger.error(f"✗ Timeout pulling {model_name}")
        return False
    except FileNotFoundError:
        logger.error("✗ Ollama not found. Please install Ollama first.")
        return False
    except Exception as e:
        logger.error(f"✗ Error pulling {model_name}: {e}")
        return False

def main():
    """Pull all recommended models"""
    print("Neuronas AI - Ollama Model Installer")
    print("=" * 40)
    
    # Check if Ollama is available
    try:
        subprocess.run(["ollama", "--version"], capture_output=True, check=True)
        logger.info("✓ Ollama is available")
    except (subprocess.CalledProcessError, FileNotFoundError):
        logger.error("✗ Ollama is not installed or not in PATH")
        print("\nPlease install Ollama first:")
        print("curl -fsSL https://ollama.ai/install.sh | sh")
        sys.exit(1)
    
    # Pull models by category
    success_count = 0
    total_count = 0
    
    for category, models in RECOMMENDED_MODELS.items():
        if category == "creative":
            print(f"\n{category.upper()} HEMISPHERE MODELS:")
        elif category == "logical":
            print(f"\n{category.upper()} HEMISPHERE MODELS:")
        elif category == "specialized":
            print(f"\n{category.upper()} CODING MODELS:")
        elif category == "uncensored":
            print(f"\n{category.upper()} UNFILTERED MODELS:")
        print("-" * 40)
        
        for model in models:
            total_count += 1
            if pull_model(model):
                success_count += 1
    
    # Summary
    print(f"\n{'='*40}")
    print(f"SUMMARY: {success_count}/{total_count} models pulled successfully")
    
    if success_count == total_count:
        print("✓ All models ready for dual-hemisphere processing!")
    else:
        print("⚠ Some models failed to download. Check the logs above.")
    
    # Show disk usage estimate
    print(f"\nEstimated disk usage: ~80-120 GB (all models)")
    print("Models are stored in Ollama's local cache.")
    print("\nModel Categories:")
    print("- Creative: Metaphorical, artistic thinking")
    print("- Logical: Analytical, structured reasoning") 
    print("- Specialized: Advanced coding specialists")
    print("- Uncensored: Unfiltered, unrestricted models")

if __name__ == "__main__":
    main()
