"""Materialize the BHSM v14.94 finite-time encapsulation gate."""

from pathlib import Path

from bhsm.interface.completion.local_environment_finite_time_encapsulation_gate_v14_94 import materialize


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    print(materialize(root / "artifacts" / "BHSM_local_environment_finite_time_encapsulation_gate_v14_94.json"))
