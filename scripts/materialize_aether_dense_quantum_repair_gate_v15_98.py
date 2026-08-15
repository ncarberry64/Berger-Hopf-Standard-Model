"""Materialize the deterministic dense BHSM v15.98 quantum gate."""

from pathlib import Path

from bhsm.interface.aether_dense_quantum_repair_gate_v15_98 import materialize


if __name__ == "__main__":
    repository = Path(__file__).resolve().parents[1]
    print(materialize(repository / "artifacts"))
