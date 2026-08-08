import numpy as np
import pytest

from bhsm.interface.completion.action_selected_charge_current_shape_schur_gate_v14_88 import (
    NEXT_CANONICAL_OBJECT,
    completion_payload,
    deterministic_witness,
    fixed_charge_routhian,
    materialize,
    reflected_relative_vertex,
    round_l2_schur_correction,
    round_representation_kill_screen,
    schur_hessian_correction,
    spin4_tensor_product_doubled,
    zero_background_schur_correction,
    zero_charge_eta_current_shape_vertex,
)


def test_fixed_charge_routhian_selects_velocity_and_zero_charge_is_static() -> None:
    result = fixed_charge_routhian(2.0, 3.0, potential=5.0)
    assert result["angular_velocity"] == pytest.approx(1.5)
    assert result["routhian"] == pytest.approx(-7.25)
    assert result["effective_potential"] == pytest.approx(7.25)
    assert fixed_charge_routhian(2.0, 0.0)["angular_velocity"] == 0.0
    with pytest.raises(ValueError):
        fixed_charge_routhian(0.0, 1.0)


def test_fixed_zero_eta_charge_kills_the_whole_current_shape_map() -> None:
    current, vertex = zero_charge_eta_current_shape_vertex(np.arange(9.0), 8, legendre_margin=0.2)
    assert current.shape == (8,)
    assert vertex.shape == (8, 9)
    assert np.allclose(current, 0.0)
    assert np.allclose(vertex, 0.0)
    with pytest.raises(ValueError, match="positive Legendre cone"):
        zero_charge_eta_current_shape_vertex(np.zeros(9), 8, legendre_margin=0.0)


def test_round_spin4_kill_screen_and_reduced_symmetry_boundary() -> None:
    screen = round_representation_kill_screen()
    assert (3, 1) not in spin4_tensor_product_doubled((2, 0), (2, 2))
    assert screen["round_Spin4_allows_coexact_L2"] is False
    assert screen["diagonal_SO3_allows_L2"] is True
    assert screen["degree_one_reduced_symmetry_status"].startswith("OPEN")


def test_general_schur_hessian_matches_deterministic_finite_difference() -> None:
    witness = deterministic_witness()
    assert witness["general_schur_finite_difference_error"] < 2e-6


def test_zero_background_general_formula_reduces_to_negative_semidefinite_term() -> None:
    rng = np.random.default_rng(1488002)
    m, n = 5, 4
    a = rng.normal(size=(m, m))
    k = a.T @ a + np.eye(m)
    b = rng.normal(size=(m, n))
    c = np.zeros((m, n, n))
    ka = rng.normal(size=(n, m, m))
    ka = 0.5 * (ka + ka.swapaxes(1, 2))
    kab = np.zeros((n, n, m, m))
    exact = schur_hessian_correction(np.zeros(m), k, b, c, ka, kab)
    reduced = zero_background_schur_correction(b, k)
    assert np.allclose(exact, reduced)
    assert np.linalg.eigvalsh(reduced)[-1] <= 1e-12


def test_round_normalization_and_half_factor_are_consistent() -> None:
    b = np.arange(12.0).reshape(3, 4) / 7.0
    direct = zero_background_schur_correction(b, (5.0 / 12.0) * np.eye(3))
    round_result = round_l2_schur_correction(b, radius=2.0, gravitational_coupling=3.0)
    assert np.allclose(direct, round_result)


def test_reflection_relative_vertex_cancels_even_and_doubles_odd_caps() -> None:
    plus = np.arange(12.0).reshape(3, 4)
    rc = np.diag([1.0, -1.0, 1.0])
    rq = np.diag([1.0, -1.0, 1.0, -1.0])
    even_minus = rc @ plus @ rq.T
    odd_minus = -even_minus
    assert np.allclose(reflected_relative_vertex(plus, even_minus, rc, rq), 0.0)
    assert np.allclose(reflected_relative_vertex(plus, odd_minus, rc, rq), 2.0 * plus)


def test_payload_fails_closed_and_preserves_flavor_and_usb_boundaries() -> None:
    payload = completion_payload()
    assert payload["validation_passed"] is True
    assert payload["eta_zero_charge_theorem"]["B_L2"] == "ZERO"
    assert payload["next_canonical_object"] == NEXT_CANONICAL_OBJECT
    assert payload["completion_status"]["FULL_BHSM_COMPLETE"] is False
    assert payload["completion_status"]["PHYSICAL_EXECUTION_BLOCKED"] is True
    assert payload["completion_status"]["USB_SYNCHRONIZATION_ELIGIBLE"] is False
    assert payload["open_flavor_gates"]["charged_current_kernel"]


def test_materialization_is_deterministic(tmp_path) -> None:
    first = materialize(tmp_path).read_bytes()
    second = materialize(tmp_path).read_bytes()
    assert first == second
