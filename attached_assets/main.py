
from module_loader import load_module
import os

def boot_neuronas():
    print("🚀 Initialisation de Neuronas...")

    base_path = os.path.dirname(__file__)
    engine = load_module(os.path.join(base_path, "core_engine.py"), "core_engine")
    quantum = load_module(os.path.join(base_path, "quantum_module.py"), "quantum_module")
    qkism = load_module(os.path.join(base_path, "quantum_symbolic.py"), "quantum_symbolic")
    storage = load_module(os.path.join(base_path, "storage_manager.py"), "storage_manager")
    gateway = load_module(os.path.join(base_path, "gateway_interface.py"), "gateway_interface")

    Gateway = gateway.GatewayInterface
    gateway_instance = Gateway()

    print("✅ Neuronas prêt.")
    return gateway_instance, storage

def run_console_mode():
    gateway, _ = boot_neuronas()
    print("\nTape une commande (analyze, reflect, modulate, optimize, profile, quantum, qkism) ou 'exit' pour quitter.")
    while True:
        cmd = input("Commande > ").strip()
        if cmd == "exit":
            break
        data = input("Donnée > ").strip()
        result = gateway.run_command(cmd, data)
        print("↪ Résultat:", result)

if __name__ == "__main__":
    run_console_mode()
