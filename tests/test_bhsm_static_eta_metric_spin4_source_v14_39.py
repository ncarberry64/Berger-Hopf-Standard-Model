from __future__ import annotations

import numpy as np

from bhsm.interface.completion.static_eta_metric_spin4_completion_gate_v14_39 import (
    all_payloads,
    completion_payload,
    materialization_hashes,
)
from bhsm.interface.completion.static_eta_metric_spin4_source_v14_39 import (
    F_prime,
    finite_difference_mixed_derivative,
    metric_eta_mixed_bilinear,
    mixed_variation_payload,
    phase_metric_mixed_bilinear,
    phase_variation_gradient,
    route_eligibility_payload,
    scalar_momentum_density,
    static_coexact_source,
    static_shift_phase_block,
    static_source_payload,
)


def _sample() -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    rng = np.random.default_rng(14039)
    raw = rng.normal(size=(4, 4))
    g_inverse = raw @ raw.T + 3.0 * np.eye(4)
    gamma_raw = rng.normal(size=(4, 4))
    gamma = 0.5 * (gamma_raw + gamma_raw.T)
    gradient = rng.normal(size=(4, 5))
    variation = rng.normal(size=(4, 5))
    return g_inverse, gamma, gradient, variation


def test_exact_metric_eta_mixed_formula_matches_finite_difference() -> None:
    g_inverse, gamma, gradient, variation = _sample()
    exact = metric_eta_mixed_bilinear(g_inverse, gamma, gradient, variation)
    finite = finite_difference_mixed_derivative(g_inverse, gamma, gradient, variation)
    assert abs(exact - finite) / max(1.0, abs(exact), abs(finite)) < 2.0e-6


def test_phase_specialization_matches_general_formula() -> None:
    rng = np.random.default_rng(3914)
    raw = rng.normal(size=(3, 3))
    g_inverse = raw @ raw.T + 2.0 * np.eye(3)
    gamma_raw = rng.normal(size=(3, 3))
    gamma = 0.5 * (gamma_raw + gamma_raw.T)
    eta = rng.normal(size=6)
    eta /= np.linalg.norm(eta)
    gradient = rng.normal(size=(3, 6))
    raw_T = rng.normal(size=(6, 6))
    generator = raw_T - raw_T.T
    phase = 0.37
    dphi = rng.normal(size=3)
    variation = phase_variation_gradient(eta, gradient, generator, phase, dphi)
    general = metric_eta_mixed_bilinear(g_inverse, gamma, gradient, variation)
    specialized = phase_metric_mixed_bilinear(
        g_inverse,
        gamma,
        eta,
        gradient,
        generator,
        dphi,
    )
    assert np.isclose(general, specialized, rtol=1.0e-11, atol=1.0e-11)


def test_static_shift_block_is_zero_but_dynamic_term_can_exist() -> None:
    beta = np.asarray([0.3, -0.2, 0.7])
    current = np.asarray([0.4, 0.5, -0.1])
    assert static_shift_phase_block(beta, current, 0.0, F_prime(2.0)) == 0.0
    assert abs(static_shift_phase_block(beta, current, 0.6, F_prime(2.0))) > 0.0


def test_static_eta_and_zero_electric_field_have_zero_momentum_source() -> None:
    rng = np.random.default_rng(1439)
    gradient = rng.normal(size=(6, 7))
    temporal = np.zeros(7)
    scalar = scalar_momentum_density(temporal, gradient, 1.3)
    total = static_coexact_source(temporal, gradient, np.zeros(6), 1.3)
    assert np.array_equal(scalar, np.zeros(6))
    assert np.array_equal(total, np.zeros(6))


def test_payloads_validate_and_fail_closed() -> None:
    assert mixed_variation_payload()["validation_passed"]
    assert static_source_payload()["validation_passed"]
    assert route_eligibility_payload()["validation_passed"]
    gate = completion_payload()
    assert gate["validation_passed"]
    assert gate["static_ADM_momentum_source_gate"] == "FAILED_ZERO"
    assert gate["Spin4_L2_L3_activation_gate"] == "OFF_ON_STATIC_BRANCH"
    assert gate["nonhomogeneous_spatial_metric_gate"] == "OPEN_GAUGE_FIXED_COMPACT_CAP_OPERATOR"
    assert gate["BHSM_complete"] is False


def test_no_physical_outputs_are_promoted() -> None:
    gate = completion_payload()
    assert gate["physical_CKM_CP_mass_scale"] == "WITHHELD"
    assert gate["validation"]["frozen_predictions_unchanged"]


def test_deterministic_materialization(tmp_path) -> None:
    first = materialization_hashes(tmp_path / "first")
    second = materialization_hashes(tmp_path / "second")
    assert first == second
    assert len(first) == len(all_payloads()) == 4
