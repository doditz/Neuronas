
import hashlib
import math

class SymbolicEncoder:
    def __init__(self):
        self.vocab = {}

    def encode(self, text):
        tokens = text.split()
        vector = [len(t)**2 for t in tokens]
        return self._normalize(vector)

    def _normalize(self, vec):
        norm = math.sqrt(sum(v**2 for v in vec)) or 1
        return [round(v / norm, 4) for v in vec]

class QuantumKernel:
    def __init__(self):
        pass

    def compute(self, vec1, vec2):
        return round(sum(a*b for a, b in zip(vec1, vec2)), 4)

class QkismEngine:
    def __init__(self):
        self.encoder = SymbolicEncoder()
        self.kernel = QuantumKernel()

    def compare(self, t1, t2):
        v1 = self.encoder.encode(t1)
        v2 = self.encoder.encode(t2)
        return {
            "similarity": self.kernel.compute(v1, v2),
            "v1": v1,
            "v2": v2
        }
