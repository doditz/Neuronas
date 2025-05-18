
from module_loader import load_module
import os
import json

class GatewayInterface:
    def __init__(self):
        base = os.path.dirname(__file__)
        self.engine = load_module(os.path.join(base, "core_engine.py"), "core_engine").CognitiveEngine()
        self.optimizer = load_module(os.path.join(base, "core_engine.py"), "core_engine").NeuronasOptimizer()
        self.profile = load_module(os.path.join(base, "core_engine.py"), "core_engine").CognitiveProfile()
        self.quantum = load_module(os.path.join(base, "quantum_module.py"), "quantum_module").QuantumCognition()
        self.qkism = load_module(os.path.join(base, "quantum_symbolic.py"), "quantum_symbolic").QkismEngine()
        self.config = self._load_config()

    def _load_config(self):
        try:
            config_path = os.path.join(os.path.dirname(__file__), "config.json")
            with open(config_path, "r") as f:
                config = json.load(f)
        except Exception:
            config = {}

        config.setdefault("storage", {})
        config["storage"].setdefault("compression", {
            "L1": {"algorithm": "none"},
            "L2": {"algorithm": "gzip"},
            "L3": {"algorithm": "lzma"},
            "backup": {"algorithm": "bz2"}
        })
        config["storage"].setdefault("importance", {"min_threshold": 0.5})
        return config

    def run_command(self, command, data=""):
        if command == "analyze":
            return self.engine.analyze(data)
        elif command == "reflect":
            return self.engine.reflect(data)
        elif command == "modulate":
            self.engine.modulate(data)
            return {"modulated_to": data}
        elif command == "optimize":
            metrics = [float(x) for x in data.split(",") if x.strip()]
            return self.optimizer.optimize(metrics)
        elif command == "profile":
            self.profile.update_context(data)
            return self.profile.evaluate()
        elif command == "quantum":
            return self.quantum.process(data)
        elif command == "qkism":
            if "::" in data:
                t1, t2 = data.split("::")
            else:
                t1 = t2 = data
            return self.qkism.compare(t1.strip(), t2.strip())
        else:
            return {"error": f"Commande inconnue: {command}"}
