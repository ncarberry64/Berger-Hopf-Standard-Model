from __future__ import annotations

import numpy as np
import pytest

from bhsm.interface.gate7_mixed_hermite_simpson_transport import (
    causal_mixed_rhs,
    local_hs_mixed_residual,
    mixed_midpoint_kinematics,
)


def _quadratic_coefficients(
    state: np.ndarray,
    central: np.ndarray,
    transverse: np.ndarray,
    mixed_incidence: np.ndarray,
    linear: np.ndarray,
    hessian: np.ndarray,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    jacobian = linear + np.einsum("oij,j->oi", hessian, state)
    central_first = jacobian @ central
    transverse_first = jacobian @ transverse
    mixed_second = (
        jacobian @ mixed_incidence
        + np.einsum("oij,i,jc->oc", hessian, central, transverse)
    )
    return central_first, transverse_first, mixed_second


def test_mixed_hs_chain_rule_matches_quadratic_polynomial_coefficients() -> None:
    rng = np.random.default_rng(74099)
    ambient = 5
    coordinates = 3
    step = 0.17
    linear = rng.normal(size=(ambient, ambient))
    raw_hessian = rng.normal(size=(ambient, ambient, ambient))
    hessian = (raw_hessian + raw_hessian.swapaxes(1, 2)) / 2
    left_state = rng.normal(size=ambient)
    right_state = rng.normal(size=ambient)
    left_central = rng.normal(size=ambient)
    right_central = rng.normal(size=ambient)
    left_transverse = rng.normal(size=(ambient, coordinates))
    right_transverse = rng.normal(size=(ambient, coordinates))
    zeros = np.zeros((ambient, coordinates))

    left_cf, left_tf, left_mixed = _quadratic_coefficients(
        left_state, left_central, left_transverse, zeros, linear, hessian,
    )
    right_cf, right_tf, right_mixed = _quadratic_coefficients(
        right_state, right_central, right_transverse, zeros, linear, hessian,
    )
    kinematics = mixed_midpoint_kinematics(
        step,
        left_central,
        right_central,
        left_cf,
        right_cf,
        left_transverse,
        right_transverse,
        left_tf,
        right_tf,
        left_mixed,
        right_mixed,
    )
    left_value = linear @ left_state + np.einsum(
        "oij,i,j->o", hessian, left_state, left_state,
    ) / 2
    right_value = linear @ right_state + np.einsum(
        "oij,i,j->o", hessian, right_state, right_state,
    ) / 2
    midpoint_state = (
        (left_state + right_state) / 2
        + step * (left_value - right_value) / 8
    )
    _, _, midpoint_total = _quadratic_coefficients(
        midpoint_state,
        kinematics.central_direction,
        kinematics.transverse_directions,
        kinematics.mixed_second_incidence,
        linear,
        hessian,
    )
    midpoint_jacobian = linear + np.einsum(
        "oij,j->oi", hessian, midpoint_state,
    )
    midpoint_intrinsic = np.einsum(
        "oij,i,jc->oc",
        hessian,
        kinematics.central_direction,
        kinematics.transverse_directions,
    )
    midpoint_incidence = midpoint_jacobian @ kinematics.mixed_second_incidence
    assert np.allclose(midpoint_total, midpoint_intrinsic + midpoint_incidence)
    expected = -step * (
        left_mixed + 4 * midpoint_total + right_mixed
    ) / 6
    actual = local_hs_mixed_residual(
        step,
        left_mixed,
        midpoint_intrinsic,
        midpoint_incidence,
        right_mixed,
    )
    assert np.allclose(actual, expected)


def test_causal_rhs_preserves_signed_matrix_structure_before_solve() -> None:
    rng = np.random.default_rng(74074)
    test = rng.normal(size=(4, 6))
    left = rng.normal(size=(6, 6))
    trial = rng.normal(size=(6, 4))
    previous = rng.normal(size=(4, 3))
    local = rng.normal(size=(6, 3))
    actual = causal_mixed_rhs(test, left, trial, previous, local)
    expected = test @ local + test @ left @ trial @ previous
    assert np.array_equal(actual, expected)


def test_shape_mismatch_fails_closed() -> None:
    with pytest.raises(ValueError):
        mixed_midpoint_kinematics(
            1.0,
            np.zeros(3), np.zeros(4), np.zeros(3), np.zeros(3),
            np.zeros((3, 2)), np.zeros((3, 2)),
            np.zeros((3, 2)), np.zeros((3, 2)),
            np.zeros((3, 2)), np.zeros((3, 2)),
        )
    with pytest.raises(ValueError):
        causal_mixed_rhs(
            np.zeros((4, 6)),
            np.zeros((6, 6)),
            np.zeros((6, 4)),
            np.zeros((4, 3)),
            np.zeros((6, 2)),
        )
