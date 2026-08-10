"""Materialize the BHSM v15.8 backward-closure audit."""
from pathlib import Path

from bhsm.interface.aether_backward_closure_existing_answer_audit_v15_8 import materialize


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    for written in materialize(root / "artifacts"):
        print(written)
