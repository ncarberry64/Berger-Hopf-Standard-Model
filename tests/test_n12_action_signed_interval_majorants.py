from __future__ import annotations

import os
from pathlib import Path
import sys

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
os.environ["BHSM_N12_CERTIFICATE_BALL"] = "1.0"

from derive_n12_action_signed_interval_majorants import action_bound  # noqa: E402


CENTER = ROOT / (
    "artifacts/intrinsic_state_selection/"
    "BHSM_N12_FIRST_CHORD_HIGH_PRECISION_HERMITE_CENTER.npz"
)


def _fixture() -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    with np.load(CENTER) as data:
        weights = np.asarray(data["action_weights"], dtype=float)
        state = np.asarray(data["action_states"][0], dtype=float) / weights
    generator = np.random.default_rng(773)
    output = generator.normal(size=(weights.size, 3))
    first = generator.normal(size=weights.size)
    second = generator.normal(size=weights.size)
    return state, output, first, second


def test_exact_signed_vector_output_equals_separated_columns() -> None:
    state, output, first, second = _fixture()
    for directions in ([output, first], [output, first, second]):
        combined = np.asarray(action_bound(
            state,
            mixed_directions=directions,
            exact_signed_output_index=0,
        ).d[-1], dtype=float)
        separated = np.asarray([
            action_bound(
                state,
                mixed_directions=[output[:, column], *directions[1:]],
                exact_signed_output_index=0,
            ).d[-1]
            for column in range(output.shape[1])
        ], dtype=float)
        np.testing.assert_allclose(
            combined, separated, rtol=2.0e-14, atol=5.0e-12,
        )


def test_directed_interval_output_encloses_exact_samples() -> None:
    state, output, direction, _ = _fixture()
    state_radius = 2.0e-10 * np.maximum(1.0, abs(state))
    direction_radius = 2.0e-10 * np.maximum(1.0, abs(direction))
    enclosure = action_bound(
        state,
        mixed_directions=[output[:, :2], direction],
        interval_state_bounds=(state - state_radius, state + state_radius),
        interval_direction_bounds=[
            None,
            (direction - direction_radius, direction + direction_radius),
        ],
        interval_signed_output_index=0,
    ).d[-1]
    lower = np.asarray(enclosure.lo, dtype=float)
    upper = np.asarray(enclosure.hi, dtype=float)
    for sign in (-1.0, 0.0, 1.0):
        sample = np.asarray(action_bound(
            state + sign * state_radius,
            mixed_directions=[
                output[:, :2], direction - sign * direction_radius,
            ],
            exact_signed_output_index=0,
        ).d[-1], dtype=float)
        assert np.all(lower <= sample)
        assert np.all(sample <= upper)


def test_signed_modes_are_mutually_exclusive() -> None:
    state, output, direction, _ = _fixture()
    try:
        action_bound(
            state,
            mixed_directions=[output, direction],
            exact_signed_output_index=0,
            interval_signed_output_index=0,
        )
    except ValueError as error:
        assert "mutually exclusive" in str(error)
    else:
        raise AssertionError("signed modes must be mutually exclusive")


def test_exact_signed_tensor_legs_equal_separated_scalar_evaluations() -> None:
    state, output, first, _ = _fixture()
    generator = np.random.default_rng(119)
    second = generator.normal(size=(state.size, 2))
    combined = np.asarray(action_bound(
        state,
        mixed_directions=[output[:, :2], second, first],
        exact_signed_tensor_indices=(0, 1),
    ).d[-1], dtype=float)
    separated = np.asarray([
        [
            action_bound(
                state,
                mixed_directions=[output[:, i], second[:, j], first],
                exact_signed_output_index=0,
            ).d[-1]
            for j in range(2)
        ]
        for i in range(2)
    ], dtype=float)
    np.testing.assert_allclose(
        combined, separated, rtol=3.0e-14, atol=1.0e-11,
    )
