"""Materialize the BHSM v14.91 degree-one full-preimage artifact."""

from pathlib import Path

from bhsm.interface.completion.degree_one_lorentzian_full_preimage_phase_space_v14_91 import (
    materialize,
)


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    print(
        materialize(
            root
            / "artifacts"
            / "BHSM_degree_one_lorentzian_full_preimage_phase_space_gate_v14_91.json"
        )
    )
