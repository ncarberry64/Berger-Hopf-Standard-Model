"""Materialize the BHSM v14.90 intrinsic dynamical momentum artifact."""

from pathlib import Path

from bhsm.interface.completion.intrinsic_full_preimage_dynamical_momentum_gate_v14_90 import materialize


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    print(materialize(root / "artifacts" / "BHSM_intrinsic_full_preimage_dynamical_momentum_gate_v14_90.json"))
