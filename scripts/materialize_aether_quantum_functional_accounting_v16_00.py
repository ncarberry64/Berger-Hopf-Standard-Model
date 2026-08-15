"""Materialize the deterministic BHSM v16.00 quantum accounting artifact."""

from pathlib import Path

from bhsm.interface.aether_quantum_functional_accounting_v16_00 import materialize


if __name__ == "__main__":
    repository = Path(__file__).resolve().parents[1]
    print(materialize(repository / "artifacts"))
