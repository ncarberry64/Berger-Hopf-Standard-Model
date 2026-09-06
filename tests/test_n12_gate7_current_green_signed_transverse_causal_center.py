from __future__ import annotations

import importlib.util
from pathlib import Path

import numpy as np
import pytest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / (
    "scripts/certify_n12_gate7_current_green_signed_transverse_causal_center.py"
)


def _module():
    spec = importlib.util.spec_from_file_location("signed_causal_center", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_signed_output_and_input_maps_are_composed_before_norms() -> None:
    module = _module()
    rng = np.random.default_rng(1729)
    tensor = rng.normal(size=(5, 4, 4))
    tensor = 0.5 * (tensor + tensor.transpose(0, 2, 1))
    output_map = rng.normal(size=(3, 5))
    input_map = rng.normal(size=(4, 6))
    transformed = module._transformed(output_map, tensor, input_map)
    expected = np.empty((3, 6, 6))
    for left in range(6):
        for right in range(6):
            expected[:, left, right] = output_map @ np.einsum(
                "oab,a,b->o", tensor, input_map[:, left], input_map[:, right],
            )
    assert np.allclose(transformed, expected, rtol=2.0e-14, atol=2.0e-14)


def test_local_pair_covariances_retain_left_cross_right_evaluations() -> None:
    module = _module()
    rng = np.random.default_rng(1733)
    local = rng.normal(size=(module.COORDINATES, 2 * module.COORDINATES,
                             2 * module.COORDINATES))
    local = 0.5 * (local + local.transpose(0, 2, 1))
    covariances = module._covariance_blocks(local)
    left = local[:, :module.COORDINATES, :module.COORDINATES]
    cross = 2.0 * local[:, :module.COORDINATES, module.COORDINATES:]
    right = local[:, module.COORDINATES:, module.COORDINATES:]
    for covariance, block in zip(
        covariances, (left, cross, right), strict=True,
    ):
        flat = block.reshape((module.COORDINATES, -1))
        assert np.allclose(covariance, flat @ flat.T, rtol=2.0e-14, atol=2.0e-10)


def test_adjacent_diagonal_sources_are_combined_before_the_causal_norm() -> None:
    module = _module()
    rng = np.random.default_rng(1741)
    vectors = rng.normal(size=(2, 3, module.COORDINATES))
    local_covariances = np.einsum(
        "ipa,ipb->ipab", vectors, vectors, optimize=True,
    )
    adjacent = np.zeros((2, module.COORDINATES, module.COORDINATES))
    adjacent[1] = np.outer(vectors[0, 2], vectors[1, 0])
    maps = np.stack((
        np.eye(module.COORDINATES),
        np.eye(module.COORDINATES) + 1.0e-3 * rng.normal(
            size=(module.COORDINATES, module.COORDINATES)
        ),
    ))
    axes = rng.normal(size=(3, module.COORDINATES))
    axes /= np.linalg.norm(axes, axis=1)[:, None]
    longitudinal, transverse = module._causal_bounds(
        local_covariances, adjacent, maps, axes,
    )

    diagonal_node1_at_node2 = maps[1] @ vectors[0, 2] + vectors[1, 0]
    expected = [
        diagonal_node1_at_node2,
        vectors[1, 2],
        maps[1] @ vectors[0, 1],
        vectors[1, 1],
    ]
    axis = axes[2]
    expected_l = sum(abs(float(axis @ value)) for value in expected)
    expected_t = sum(float(np.linalg.norm(value - axis * (axis @ value)))
                     for value in expected)
    assert np.isclose(longitudinal[2], expected_l, rtol=2.0e-14)
    assert np.isclose(transverse[2], expected_t, rtol=2.0e-14)


def test_endpoint_transverse_hs_hessian_includes_induced_midpoint_axis_terms() -> None:
    """Compare the assembled chain rule with an independent polynomial derivative."""
    import sympy as sp

    module = _module()
    left_parameter, right_parameter = sp.symbols("left right")
    step = sp.Rational(1, 2)

    def rate(value):
        x, y = value
        return sp.Matrix([y**2 / 2, x * y + x**2 / 2])

    # Each endpoint perturbation has zero first (longitudinal) coordinate.
    left = sp.Matrix([1, 2 + left_parameter])
    right = sp.Matrix([3, 4 + right_parameter])
    midpoint = (left + right) / 2 + step * (rate(left) - rate(right)) / 8
    expression = step * (rate(left) + 4 * rate(midpoint) + rate(right)) / 6
    variables = (left_parameter, right_parameter)
    origin = {left_parameter: 0, right_parameter: 0}
    expected = np.asarray([
        sp.hessian(value, variables).subs(origin).tolist() for value in expression
    ], dtype=float)
    augmented = np.asarray(midpoint.jacobian(variables).subs(origin), dtype=float)
    midpoint_value = midpoint.subs(origin)
    x, y = sp.symbols("x y")
    hessian = np.asarray([
        sp.hessian(value, (x, y)).tolist() for value in rate((x, y))
    ], dtype=float)
    derivative = np.asarray(
        rate((x, y)).jacobian((x, y)).subs(dict(zip((x, y), midpoint_value))),
        dtype=float,
    )
    axis = np.array([1.0, 0.0])
    basis = np.array([[0.0], [1.0]])
    geometry = module._split_midpoint_map(np.eye(2), augmented)
    intrinsic = module._complete_midpoint_pullback(
        np.eye(2), hessian[:, 1:, 1:], basis, axis, geometry,
        hessian[:, 0, 0], hessian[:, 0, 1:],
    )
    # Endpoint Hessians and the second variation of the midpoint incidence.
    assembled = 2 * float(step) * intrinsic / 3
    endpoint_second = hessian[:, 1, 1]
    assembled[:, 0, 0] += (
        float(step) * endpoint_second / 6
        + float(step)**2 * derivative @ endpoint_second / 12
    )
    assembled[:, 1, 1] += (
        float(step) * endpoint_second / 6
        - float(step)**2 * derivative @ endpoint_second / 12
    )
    assert np.any(axis @ augmented != 0.0)
    assert np.allclose(assembled, expected, rtol=0.0, atol=2.0e-16)
    old_tt_only = module._transformed(
        np.eye(2), hessian[:, 1:, 1:], basis.T @ augmented,
    )
    assert not np.allclose(old_tt_only, intrinsic)


def test_directional_conversion_retains_scalar_scale_and_mixed_basis_coordinates() -> None:
    module = _module()
    frame = np.eye(3)
    axis = np.array([1.0, 0.0, 0.0])
    # Deliberately swapped and signed; the first source columns are not this basis.
    basis = np.array([[0.0, 0.0], [0.0, -1.0], [1.0, 0.0]])
    hessian = np.array([
        [[2.0, 3.0, -1.0], [3.0, 5.0, 4.0], [-1.0, 4.0, 7.0]],
        [[-3.0, 1.0, 2.0], [1.0, 6.0, -5.0], [2.0, -5.0, 8.0]],
    ])
    direction = 4.0 * axis
    mixed_directions = np.array([[1.0, -2.0, 3.0],
                                 [2.0, 0.0, -1.0],
                                 [0.0, 4.0, 2.0]])
    scalar = np.einsum("oab,a,b->o", hessian, direction, direction)
    mixed_source = np.einsum("oab,a,bj->oj", hessian, direction, mixed_directions)
    central, mixed = module._tangent_blocks_from_directional_data(
        frame, axis, basis, direction, scalar, mixed_directions, mixed_source,
    )
    assert np.allclose(central, hessian[:, 0, 0], atol=1.0e-14)
    assert np.allclose(mixed, hessian[:, 0] @ basis, atol=1.0e-14)
    coordinate = np.array([[1.0, -2.0, 3.0, 0.0],
                           [4.0, 1.0, 0.0, -1.0],
                           [-1.0, 2.0, 1.0, 3.0]])
    transverse_tensor = np.einsum("oab,ai,bj->oij", hessian, basis, basis)
    actual = module._signed_tangent_pullback(
        np.eye(2), transverse_tensor, basis, axis, coordinate, central, mixed,
    )
    expected = np.einsum("oab,ai,bj->oij", hessian, coordinate, coordinate)
    assert np.allclose(actual, expected, rtol=2.0e-14, atol=2.0e-14)


def test_nonzero_normal_map_blocks_even_when_all_tangent_hessian_terms_vanish() -> None:
    module = _module()
    frame = np.array([[1.0, 0.0], [0.0, 1.0], [0.0, 0.0]])
    augmented = np.array([[0.0, 0.0], [1.0, 2.0], [0.25, -0.5]])
    midpoint = module._split_midpoint_map(frame, augmented)
    basis = np.array([[0.0], [1.0]])
    axis = np.array([1.0, 0.0])
    with pytest.raises(module.MidpointChainRuleIncomplete, match="midpoint input normal"):
        module._complete_midpoint_pullback(
            np.eye(1), np.zeros((1, 1, 1)), basis, axis, midpoint,
            np.zeros(1), np.zeros((1, 1)),
        )
    # f(z)=z_normal^2 has no tangent Hessian but a nonzero full pullback.
    correction = 2.0 * np.einsum("i,j->ij", augmented[2], augmented[2])[None]
    restored = module._complete_midpoint_pullback(
        np.eye(1), np.zeros((1, 1, 1)), basis, axis, midpoint,
        np.zeros(1), np.zeros((1, 1)), normal_hessian_correction=correction,
    )
    assert np.array_equal(restored, correction)


def test_full_normal_correction_retains_both_tangent_normal_legs() -> None:
    module = _module()
    frame = np.array([[1.0, 0.0], [0.0, 1.0], [0.0, 0.0]])
    augmented = np.array([[1.0, 2.0], [3.0, -1.0], [0.5, -0.25]])
    hessian = np.array([[[2.0, 3.0, -4.0], [3.0, 5.0, 7.0], [-4.0, 7.0, 11.0]]])
    midpoint = module._split_midpoint_map(frame, augmented)
    tangent = frame @ midpoint.coordinate
    normal = midpoint.normal
    correction = (
        np.einsum("oab,ai,bj->oij", hessian, tangent, normal)
        + np.einsum("oab,ai,bj->oij", hessian, normal, tangent)
        + np.einsum("oab,ai,bj->oij", hessian, normal, normal)
    )
    actual = module._complete_midpoint_pullback(
        np.eye(1), hessian[:, 1:2, 1:2], np.array([[0.0], [1.0]]),
        np.array([1.0, 0.0]), midpoint, hessian[:, 0, 0], hessian[:, 0, 1:2],
        normal_hessian_correction=correction,
    )
    assert np.allclose(actual, np.einsum("oab,ai,bj->oij", hessian, augmented, augmented))


@pytest.mark.parametrize("source", ["central", "mixed"])
def test_normal_contaminated_source_cannot_be_relabelled_as_tangent_data(source) -> None:
    module = _module()
    frame = np.array([[1.0, 0.0], [0.0, 1.0], [0.0, 0.0]])
    central_direction = np.array([2.0, 0.0, 0.0])
    mixed_directions = frame.copy()
    if source == "central":
        central_direction[2] = 1.0e-20
    else:
        mixed_directions[2, 1] = 1.0e-20
    with pytest.raises(module.MidpointChainRuleIncomplete, match=f"{source}-direction normal"):
        module._tangent_blocks_from_directional_data(
            frame, np.array([1.0, 0.0]), np.array([[0.0], [1.0]]),
            central_direction, np.zeros(1), mixed_directions, np.zeros((1, 2)),
        )


def test_rank_deficient_mixed_source_does_not_determine_missing_axis_tensor() -> None:
    module = _module()
    with pytest.raises(module.MidpointChainRuleIncomplete, match="does not span"):
        module._tangent_blocks_from_directional_data(
            np.eye(3), np.array([1.0, 0.0, 0.0]), np.eye(3)[:, 1:],
            np.array([2.0, 0.0, 0.0]), np.zeros(1),
            np.array([[1.0, 2.0], [0.0, 0.0], [0.0, 0.0]]), np.zeros((1, 2)),
        )


def test_incomplete_chain_rule_cannot_emit_a_positive_screen_or_center_authority() -> None:
    module = _module()
    payload = module._incomplete_payload("unresolved normal", ())
    assert payload["screen"] is None
    assert payload["coefficients"] is None
    assert payload["validation_passed"] is False
    assert payload["claim_boundary"]["SIGNED_CAUSAL_TRANSVERSE_CENTER_OPERATOR_DERIVED"] is False
    assert payload["claim_boundary"]["GATE7_CLOSED"] is False
