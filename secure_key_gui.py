"""
Secure GUI Popup for API Key Input - Neuronas
============================================

User-friendly secure popup for API key management with GUI interface.
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import threading
import logging
from typing import Optional, Dict, Any, Callable
import os
import sys
from pathlib import Path

# Import our secure key manager
try:
    from simple_secure_keys import NeuronasKeyManager
    SECURE_KEYS_AVAILABLE = True
except ImportError:
    SECURE_KEYS_AVAILABLE = False

logger = logging.getLogger(__name__)

class SecureKeyPopup:
    """
    Secure popup window for API key input and management
    """
    
    def __init__(self, parent=None):
        """Initialize the secure popup"""
        self.parent = parent
        self.result = None
        self.key_manager = NeuronasKeyManager() if SECURE_KEYS_AVAILABLE else None
        
        # Service configurations
        self.services = {
            'perplexity': {
                'name': 'Perplexity AI',
                'description': 'Advanced research and reasoning AI',
                'placeholder': 'pplx-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx',
                'validation': lambda k: k.startswith('pplx-') and len(k) > 20,
                'help_url': 'https://docs.perplexity.ai/docs/getting-started'
            },
            'openai': {
                'name': 'OpenAI',
                'description': 'GPT models and AI services',
                'placeholder': 'sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx',
                'validation': lambda k: k.startswith('sk-') and len(k) > 40,
                'help_url': 'https://platform.openai.com/api-keys'
            },
            'anthropic': {
                'name': 'Anthropic Claude',
                'description': 'Claude AI assistant',
                'placeholder': 'sk-ant-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx',
                'validation': lambda k: k.startswith('sk-ant-') and len(k) > 30,
                'help_url': 'https://console.anthropic.com/'
            },
            'google': {
                'name': 'Google AI',
                'description': 'Gemini and Google AI services',
                'placeholder': 'AIzaxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx',
                'validation': lambda k: k.startswith('AIza') and len(k) > 30,
                'help_url': 'https://console.cloud.google.com/apis/credentials'
            }
        }
    
    def show_key_input_popup(self, service: str, callback: Optional[Callable] = None) -> Optional[str]:
        """
        Show secure popup for API key input
        
        Args:
            service: Service name (e.g., 'perplexity', 'openai')
            callback: Optional callback function for async operations
            
        Returns:
            str: API key or None if cancelled
        """
        if service not in self.services:
            messagebox.showerror("Error", f"Unknown service: {service}")
            return None
        
        service_info = self.services[service]
        
        # Create popup window
        popup = tk.Toplevel(self.parent) if self.parent else tk.Tk()
        popup.title(f"🔐 Secure API Key Input - {service_info['name']}")
        popup.geometry("500x400")
        popup.resizable(False, False)
        
        # Center the window
        popup.transient(self.parent if self.parent else None)
        popup.grab_set()
        
        # Configure style
        style = ttk.Style()
        style.theme_use('clam')
        
        # Main frame
        main_frame = ttk.Frame(popup, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Title
        title_label = ttk.Label(
            main_frame, 
            text=f"🔑 {service_info['name']} API Key",
            font=('Arial', 14, 'bold')
        )
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 10))
        
        # Description
        desc_label = ttk.Label(
            main_frame,
            text=service_info['description'],
            font=('Arial', 10),
            foreground='gray'
        )
        desc_label.grid(row=1, column=0, columnspan=2, pady=(0, 15))
        
        # Security notice
        security_frame = ttk.LabelFrame(main_frame, text="🔒 Security Notice", padding="10")
        security_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 15))
        
        security_text = """• Your API key will be encrypted and stored securely
• Keys are protected with master password encryption
• File permissions are set to owner-only access
• No key data is transmitted over network"""
        
        security_label = ttk.Label(
            security_frame,
            text=security_text,
            font=('Arial', 9),
            justify=tk.LEFT
        )
        security_label.grid(row=0, column=0, sticky=tk.W)
        
        # API Key input
        key_frame = ttk.LabelFrame(main_frame, text="API Key Input", padding="10")
        key_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 15))
        
        ttk.Label(key_frame, text="API Key:").grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        
        key_var = tk.StringVar()
        key_entry = ttk.Entry(
            key_frame,
            textvariable=key_var,
            show="*",  # Hide characters
            width=60,
            font=('Courier', 10)
        )
        key_entry.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Show/Hide toggle
        show_var = tk.BooleanVar()
        show_check = ttk.Checkbutton(
            key_frame,
            text="Show API key",
            variable=show_var,
            command=lambda: key_entry.config(show="" if show_var.get() else "*")
        )
        show_check.grid(row=2, column=0, sticky=tk.W)
        
        # Placeholder hint
        hint_label = ttk.Label(
            key_frame,
            text=f"Format: {service_info['placeholder']}",
            font=('Arial', 8),
            foreground='gray'
        )
        hint_label.grid(row=3, column=0, sticky=tk.W, pady=(5, 0))
        
        # Validation indicator
        validation_var = tk.StringVar(value="⏳ Enter API key to validate")
        validation_label = ttk.Label(
            key_frame,
            textvariable=validation_var,
            font=('Arial', 9)
        )
        validation_label.grid(row=4, column=0, sticky=tk.W, pady=(5, 0))
        
        # Real-time validation
        def validate_key(*args):
            key = key_var.get().strip()
            if not key:
                validation_var.set("⏳ Enter API key to validate")
                validation_label.config(foreground='gray')
            elif service_info['validation'](key):
                validation_var.set("✅ API key format valid")
                validation_label.config(foreground='green')
            else:
                validation_var.set("❌ Invalid API key format")
                validation_label.config(foreground='red')
        
        key_var.trace('w', validate_key)
        
        # Buttons frame
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=4, column=0, columnspan=2, pady=(10, 0))
        
        # Help button
        def open_help():
            import webbrowser
            webbrowser.open(service_info['help_url'])
        
        help_btn = ttk.Button(
            button_frame,
            text="📖 Get API Key",
            command=open_help
        )
        help_btn.grid(row=0, column=0, padx=(0, 10))
        
        # Test button
        def test_key():
            key = key_var.get().strip()
            if not key:
                messagebox.showwarning("Warning", "Please enter an API key first")
                return
            
            if not service_info['validation'](key):
                messagebox.showerror("Error", "Invalid API key format")
                return
            
            # TODO: Add actual API test here
            messagebox.showinfo("Test", f"API key format is valid for {service_info['name']}")
        
        test_btn = ttk.Button(
            button_frame,
            text="🧪 Test Key",
            command=test_key
        )
        test_btn.grid(row=0, column=1, padx=(0, 10))
        
        # Cancel button
        def cancel():
            popup.result = None
            popup.destroy()
        
        cancel_btn = ttk.Button(
            button_frame,
            text="❌ Cancel",
            command=cancel
        )
        cancel_btn.grid(row=0, column=2, padx=(0, 10))
        
        # Save button
        def save_key():
            key = key_var.get().strip()
            
            if not key:
                messagebox.showwarning("Warning", "Please enter an API key")
                return
            
            if not service_info['validation'](key):
                messagebox.showerror("Error", "Invalid API key format")
                return
            
            # Save the key securely
            if self.key_manager:
                try:
                    success = self.key_manager.simple_keys.store_key(service, key, overwrite=True)
                    if success:
                        messagebox.showinfo("Success", f"✅ API key for {service_info['name']} saved securely!")
                        popup.result = key
                        
                        # Call callback if provided
                        if callback:
                            callback(service, key)
                        
                        popup.destroy()
                    else:
                        messagebox.showerror("Error", "Failed to save API key")
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to save API key: {str(e)}")
            else:
                # Fallback to environment variable
                os.environ[f"{service.upper()}_API_KEY"] = key
                messagebox.showinfo("Success", f"✅ API key for {service_info['name']} set for current session!")
                popup.result = key
                
                if callback:
                    callback(service, key)
                
                popup.destroy()
        
        save_btn = ttk.Button(
            button_frame,
            text="💾 Save Securely",
            command=save_key,
            style='Accent.TButton'
        )
        save_btn.grid(row=0, column=3)
        
        # Configure button style
        style.configure('Accent.TButton', foreground='white', background='#0078d4')
        
        # Focus on entry
        key_entry.focus()
        
        # Handle window close
        popup.protocol("WM_DELETE_WINDOW", cancel)
        
        # Handle Enter key
        popup.bind('<Return>', lambda e: save_key())
        popup.bind('<Escape>', lambda e: cancel())
        
        # Show popup and wait for result
        popup.wait_window()
        
        return getattr(popup, 'result', None)
    
    def show_key_manager_popup(self):
        """Show comprehensive key management popup"""
        popup = tk.Toplevel(self.parent) if self.parent else tk.Tk()
        popup.title("🔐 Neuronas API Key Manager")
        popup.geometry("600x500")
        popup.resizable(True, True)
        
        # Center the window
        popup.transient(self.parent if self.parent else None)
        popup.grab_set()
        
        # Main frame with scrollbar
        main_frame = ttk.Frame(popup, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        popup.columnconfigure(0, weight=1)
        popup.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Title
        title_label = ttk.Label(
            main_frame,
            text="🔑 API Key Management Center",
            font=('Arial', 16, 'bold')
        )
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Services frame
        services_frame = ttk.LabelFrame(main_frame, text="Available Services", padding="10")
        services_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        services_frame.columnconfigure(1, weight=1)
        
        row = 0
        for service_id, service_info in self.services.items():
            # Service icon and name
            service_label = ttk.Label(
                services_frame,
                text=f"🔗 {service_info['name']}",
                font=('Arial', 11, 'bold')
            )
            service_label.grid(row=row, column=0, sticky=tk.W, padx=(0, 10), pady=5)
            
            # Status
            if self.key_manager:
                key = self.key_manager.get_api_key(service_id)
                status = "✅ Configured" if key else "❌ Not set"
                status_color = 'green' if key else 'red'
            else:
                env_key = os.getenv(f"{service_id.upper()}_API_KEY")
                status = "✅ Environment" if env_key else "❌ Not set"
                status_color = 'blue' if env_key else 'red'
            
            status_label = ttk.Label(
                services_frame,
                text=status,
                foreground=status_color,
                font=('Arial', 9)
            )
            status_label.grid(row=row, column=1, sticky=tk.W, pady=5)
            
            # Configure button
            def make_configure_cmd(service_id):
                return lambda: self.show_key_input_popup(service_id)
            
            config_btn = ttk.Button(
                services_frame,
                text="⚙️ Configure",
                command=make_configure_cmd(service_id)
            )
            config_btn.grid(row=row, column=2, padx=(10, 0), pady=5)
            
            row += 1
        
        # Action buttons
        action_frame = ttk.Frame(main_frame)
        action_frame.grid(row=2, column=0, columnspan=2, pady=(20, 0))
        
        def refresh_status():
            popup.destroy()
            self.show_key_manager_popup()
        
        refresh_btn = ttk.Button(
            action_frame,
            text="🔄 Refresh",
            command=refresh_status
        )
        refresh_btn.grid(row=0, column=0, padx=(0, 10))
        
        def show_help():
            help_text = """🔐 Neuronas API Key Manager Help

🔑 How to use:
1. Click 'Configure' next to any service
2. Enter your API key in the secure popup
3. Keys are encrypted and stored safely

🛡️ Security features:
• Master password protection
• Local file encryption
• Secure file permissions
• No network transmission

📖 Getting API keys:
• Click 'Get API Key' in each service popup
• Visit the service's official website
• Follow their API key generation guide

💡 Tips:
• Keep your API keys secret
• Don't share them with others
• Use environment variables for automation
"""
            
            help_popup = tk.Toplevel(popup)
            help_popup.title("📖 Help")
            help_popup.geometry("400x300")
            
            help_text_widget = tk.Text(
                help_popup,
                wrap=tk.WORD,
                padx=10,
                pady=10,
                font=('Arial', 10)
            )
            help_text_widget.pack(fill=tk.BOTH, expand=True)
            help_text_widget.insert(tk.END, help_text)
            help_text_widget.config(state=tk.DISABLED)
        
        help_btn = ttk.Button(
            action_frame,
            text="📖 Help",
            command=show_help
        )
        help_btn.grid(row=0, column=1, padx=(0, 10))
        
        close_btn = ttk.Button(
            action_frame,
            text="✅ Close",
            command=popup.destroy
        )
        close_btn.grid(row=0, column=2)
        
        # Show popup
        popup.wait_window()


def quick_key_input(service: str, parent=None) -> Optional[str]:
    """
    Quick function to show key input popup
    
    Args:
        service: Service name
        parent: Parent window (optional)
        
    Returns:
        str: API key or None
    """
    popup = SecureKeyPopup(parent)
    return popup.show_key_input_popup(service)


def show_key_manager(parent=None):
    """
    Quick function to show key manager
    
    Args:
        parent: Parent window (optional)
    """
    popup = SecureKeyPopup(parent)
    popup.show_key_manager_popup()


# CLI interface for GUI
def main():
    """Main CLI interface"""
    import sys
    
    if len(sys.argv) < 2:
        print("Neuronas Secure Key GUI")
        print("Usage:")
        print("  python secure_key_gui.py manager          - Show key manager")
        print("  python secure_key_gui.py input <service>  - Input key for service")
        print("  python secure_key_gui.py quick            - Quick setup wizard")
        return
    
    action = sys.argv[1]
    
    if action == "manager":
        show_key_manager()
    
    elif action == "input" and len(sys.argv) > 2:
        service = sys.argv[2]
        key = quick_key_input(service)
        if key:
            print(f"✅ API key configured for {service}")
        else:
            print("❌ No key configured")
    
    elif action == "quick":
        # Quick setup wizard
        root = tk.Tk()
        root.withdraw()  # Hide main window
        
        services = ['perplexity', 'openai']
        configured = []
        
        for service in services:
            result = messagebox.askyesno(
                "Quick Setup",
                f"Would you like to configure {service.title()} API key?"
            )
            
            if result:
                key = quick_key_input(service, root)
                if key:
                    configured.append(service)
        
        if configured:
            messagebox.showinfo(
                "Setup Complete",
                f"✅ Configured API keys for: {', '.join(configured)}"
            )
        else:
            messagebox.showinfo("Setup", "No API keys were configured")
        
        root.destroy()
    
    else:
        print("❌ Invalid action")


if __name__ == "__main__":
    main()
