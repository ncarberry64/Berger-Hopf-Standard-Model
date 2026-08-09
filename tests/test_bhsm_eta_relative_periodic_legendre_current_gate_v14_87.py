import numpy as np
import pytest

from bhsm.interface.completion.full_preimage_cap_inertia_operator_v14_84 import EXACT_NEXT_OBJECT
from bhsm.interface.completion.eta_relative_periodic_legendre_current_gate_v14_87 import (
    NEXT_EXECUTABLE_SUBOBJECT,
    canonical_eta_momentum,
    completion_payload,
    deterministic_witness,
    eta_spatial_momentum_current,
    finite_difference_legendre_error,
    legendre_eigenvalues,
    lorentzian_eta_legendre_hessian,
    materialize,
    reflected_odd_coefficients,
    sourced_coexact_shift_coefficients,
)


def test_legendre_matrix_matches_analytic_parallel_and_transverse_spectrum() -> None:
    velocity = np.array([0.2, -0.1, 0.04, 0.03])
    spatial = 1.3 + float(velocity @ velocity)
    matrix = lorentzian_eta_legendre_hessian(velocity, spatial)
    analytic = legendre_eigenvalues(velocity, spatial)
    spectrum = np.linalg.eigvalsh(matrix)
    assert spectrum[0] == pytest.approx(analytic["parallel"])
    assert spectrum[1:] == pytest.approx([analytic["transverse"]] * 3)


def test_positive_degenerate_and_negative_velocity_branches_are_resolved() -> None:
    witness = deterministic_witness()
    assert witness["branches"]["positive"]["analytic_parallel"] > 0.0
    assert witness["branches"]["near_positive"]["analytic_parallel"] > 0.0
    assert witness["branches"]["negative"]["analytic_parallel"] < 0.0
    assert witness["basis_covariance_residual"] < 1e-12
    assert witness["finite_difference_legendre_error"] < 1e-8


def test_legendre_hessian_matches_finite_difference_random_seed() -> None:
    rng = np.random.default_rng(1487001)
    for _ in range(8):
        velocity = rng.normal(scale=0.08, size=5)
        spatial = 1.2 + float(velocity @ velocity)
        assert finite_difference_legendre_error(velocity, spatial) < 1e-8


def test_zero_canonical_momentum_branch_has_zero_eta_spatial_current() -> None:
    velocity = np.zeros(5)
    gradients = np.eye(5)
    assert np.allclose(canonical_eta_momentum(velocity, 1.0), 0.0)
    assert np.allclose(eta_spatial_momentum_current(velocity, gradients), 0.0)


def test_reflection_odd_current_and_round_l2_resolvent() -> None:
    reflection = np.diag([1.0, -1.0, 1.0])
    plus = np.array([0.0, 2.0, 0.0])
    minus = reflection @ np.array([0.0, -2.0, 0.0])
    odd = reflected_odd_coefficients(plus, minus, reflection)
    assert np.allclose(odd, plus)
    assert np.allclose(sourced_coexact_shift_coefficients(odd, radius=2.0), 0.8 * odd)


def test_legendre_gate_fails_closed_outside_retained_x_domain() -> None:
    with pytest.raises(ValueError, match="X>=0"):
        lorentzian_eta_legendre_hessian([2.0, 0.0], 1.0)
    with pytest.raises(ValueError):
        sourced_coexact_shift_coefficients([1.0], gravitational_coupling=0.0)


def test_payload_preserves_completion_and_flavor_boundaries() -> None:
    payload = completion_payload()
    assert payload["validation_passed"] is True
    assert payload["canonical_exact_next_object"] == EXACT_NEXT_OBJECT
    assert payload["next_executable_subobject"] == NEXT_EXECUTABLE_SUBOBJECT
    assert payload["selection_result"]["source_free_periodic_eta_route"] == "CLOSED_ON_ZERO_MOMENTUM_BRANCH"
    assert payload["completion_status"]["eta_cap_kinetic_positivity"].startswith("CONDITIONAL")
    assert payload["completion_status"]["BHSM_complete"] is False
    assert payload["completion_status"]["USB_synchronization_eligible"] is False


def test_materialization_is_deterministic(tmp_path) -> None:
    first = materialize(tmp_path).read_bytes()
    second = materialize(tmp_path).read_bytes()
    assert first == second
