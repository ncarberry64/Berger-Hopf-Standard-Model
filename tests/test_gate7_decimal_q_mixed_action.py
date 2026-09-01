from __future__ import annotations

from pathlib import Path

import numpy as np

from bhsm.interface.aether_gate7_decimal_q_mixed_action import (
    decimal_q_gradient_and_reduced_q_hessian,
)
from bhsm.interface.aether_n3_exact_full_local_action_jet_v17_60 import (
    exact_full_action_jet_at_state,
)


ROOT = Path(__file__).resolve().parents[1]
CENTER = ROOT / (
    "artifacts/flagship_integration/"
    "BHSM_N12_C2_STOP_HIGH_ORDER_QUARTER_STEP_RETAINED_RECONNAISSANCE.npz"
)


def _decimal_array(values: object) -> np.ndarray:
    if isinstance(values, list) and values and isinstance(values[0], list):
        return np.asarray([[float(item) for item in row] for row in values])
    return np.asarray([float(item) for item in values])


def test_decimal_q_and_mixed_blocks_reproduce_retained_action() -> None:
    with np.load(CENTER) as source:
        weights = np.asarray(source["state_weights"], dtype=float)
        centers = np.asarray(
            source["fine_grid_augmented_action_values"], dtype=float,
        )[[80, 300], :-1] / weights

    for state in centers:
        decimal = decimal_q_gradient_and_reduced_q_hessian(
            12, state[:37], state[37:74], state[74:],
            points=96, precision=60,
        )
        binary = exact_full_action_jet_at_state(
            12, state[:37], state[37:74], state[74:], points=96,
        )
        gradient = _decimal_array(decimal["gradient_configuration"])
        mixed = _decimal_array(decimal["hessian_reduced_configuration"])
        expected_gradient = np.asarray(binary.gradient, dtype=float)[:37]
        expected_mixed = np.asarray(binary.hessian, dtype=float)[37:, :37]
        gradient_relative = np.linalg.norm(gradient - expected_gradient) / max(
            np.linalg.norm(gradient), 1.0e-300,
        )
        mixed_relative = np.linalg.norm(mixed - expected_mixed) / max(
            np.linalg.norm(mixed), 1.0e-300,
        )
        assert gradient_relative < 4.0e-14
        assert mixed_relative < 4.0e-14
        assert decimal["unchanged_retained_action"] is True
        assert decimal["points"] == 96
        assert decimal["precision"] == 60

