"""Materialize the BHSM v14.93 nonlinear encapsulation kill screen."""

from pathlib import Path

from bhsm.interface.completion.nonlinear_encapsulated_state_spectral_band_gate_v14_93 import (
    materialize,
)


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    print(materialize(root / "artifacts" / "BHSM_nonlinear_encapsulated_state_spectral_band_gate_v14_93.json"))
