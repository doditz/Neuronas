# Neuronas Cognitive Engine Blueprint

**Legal Notice**  
This work is licensed under CC BY-NC 4.0 International.
Commercial use requires prior written consent and compensation.
Contact: sebastienbrulotte@gmail.com | Attribution: Sebastien Brulotte aka [ Doditz ]

---

## Core System Modules

| Module | Role |
|--------|------|
| `main.py` | System bootstrap, activates SMAS and cognitive shell |
| `gateway_interface.py` | Initial query ingestion, input validation, flow routing |
| `module_loader.py` | Dynamic loading of personas and external modules |
| `config.json` | Core execution parameters, thresholds, weights |
| `quantum_module.py` | Qronas quantum optimization layer |
| `quantum_symbolic.py` | Symbolic alignment engine for QRONAS layer |

---

## Memory Tier Stack

- L1 → `/mnt/data/l1.db`
- R1 → `/mnt/data/r1.db`
- L2 → `/mnt/data/l2.db`
- R2 → `/mnt/data/r2.db`
- L3 → `/mnt/data/l3.db`
- R3 → `/mnt/data/r3.db`

---

## Self-Location Tracing

- Trace In: `Neuronas.Trace.In`
- Map: `Neuronas.Location.MapTrace`
- Active Personas: `SMAS.PersonaMix`
- Current Location Index: `Neuronas.Location.Index`
- Feedback Response: `Neuronas.Post.Reflect`

---

## Execution Flow

1. **User Input** (via `gateway_interface.py`)
2. **Sensory Mapping** (via QRONAS)
3. **Persona Activation** (via SMAS)
4. **Merged Decision Logic**
5. **Output Generation**
6. **PostThink Loop** for contradiction & feedback
7. **Reinjection or Completion**

