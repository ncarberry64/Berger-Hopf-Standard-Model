"""Materialize the BHSM v14.92 cross-level critical-value gate."""

from pathlib import Path

from bhsm.interface.completion.lorentzian_cross_level_critical_value_functor_v14_92 import (
    materialize,
)


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    print(
        materialize(
            root
            / "artifacts"
            / "BHSM_lorentzian_cross_level_critical_value_functor_gate_v14_92.json"
        )
    )
