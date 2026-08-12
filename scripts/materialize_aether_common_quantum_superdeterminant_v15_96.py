"""Materialize the deterministic BHSM v15.96 quantum determinant artifact."""

from pathlib import Path

from bhsm.interface.aether_common_quantum_superdeterminant_v15_96 import materialize


if __name__ == "__main__":
    repository = Path(__file__).resolve().parents[1]
    print(materialize(repository / "artifacts"))
