from pathlib import Path

from bhsm.interface.aether_quantum_cone_repair_gate_v15_95 import materialize


if __name__ == "__main__":
    print(materialize(Path("artifacts")))
