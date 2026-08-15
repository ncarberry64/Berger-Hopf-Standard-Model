from __future__ import annotations

import json

import numpy as np
import pytest

from bhsm.interface.aether_moving_formed_symplectic_v15_25 import (
    FULL_BHSM_COMPLETE,
    completion_payload,
    critical_moving_l2_coefficients,
    leading_whitened_qs_gram,
    local_shape_legendre_and_symplectic_certificate,
    materialize,
    raw_cross_transfer_audit,
    reduced_shape_kinetics,
    sigma_cross_kinetic_parity,
)


def test_exact_constraint_coefficients_and_slaving_identity() -> None:
    result = critical_moving_l2_coefficients()
    radius = (343.0 / 5.0) ** (1.0 / 6.0)
    assert np.isclose(result["A"], -21.0)
    assert np.isclose(result["B"], -96.0 / radius**2)
    assert np.isclose(result["C2"], -49.0 / (9.0 * radius**4))
    assert np.isclose(result["D1"], 343.0 / (9.0 * radius**2))
    assert np.isclose(result["slaving_coefficient_c"], 343.0 / 1728.0)
    assert np.isclose(result["D1_plus_2cB"], 0.0, atol=1e-13)
    assert np.isclose(result["normal_shift_reduction_coefficient"], 20736.0 / 49.0)


def test_forced_tangent_cancels_shift_source_exactly() -> None:
    q, q_dot = 0.13, -0.27
    c = 343.0 / 1728.0
    result = reduced_shape_kinetics(q=q, q_dot=q_dot, a_dot=2 * c * q * q_dot)
    assert np.isclose(result["s_dot"], 0.0, atol=1e-14)
    assert np.isclose(result["constraint_shift_b"], 0.0, atol=1e-12)
    assert np.isclose(result["positive_normal_shift_kinetic"], 0.0, atol=1e-14)
    assert result["on_forced_tangent"]
    assert not result["singular_shift_excited"]


def test_normal_deviation_has_positive_stiff_kinetic() -> None:
    q, q_dot = 0.13, -0.27
    c = 343.0 / 1728.0
    result = reduced_shape_kinetics(
        q=q, q_dot=q_dot, a_dot=2 * c * q * q_dot + 0.02
    )
    assert np.isclose(result["s_dot"], 0.02)
    assert result["positive_normal_shift_kinetic"] > 0.0
    assert result["singular_shift_excited"]


def test_round_limit_is_not_used_as_formed_chart() -> None:
    with pytest.raises(ValueError):
        reduced_shape_kinetics(q=0.0, q_dot=0.2, a_dot=0.0)
    with pytest.raises(ValueError):
        local_shape_legendre_and_symplectic_certificate(0.0)


def test_local_shape_legendre_and_symplectic_pair() -> None:
    result = local_shape_legendre_and_symplectic_certificate(0.14)
    assert result["G_ss"] > 0.0
    assert result["positive_shape_Legendre_direction"]
    assert result["shape_symplectic_rank"] == 2
    assert result["canonical_pair_exists_locally"]
    assert result["full_q_sigma_s_symplectic_rank"] is None


def test_sigma_cross_terms_vanish_only_on_symmetric_branch() -> None:
    result = sigma_cross_kinetic_parity()
    assert result["G_qsigma_at_sigma_zero"] == 0.0
    assert result["G_ssigma_at_sigma_zero"] == 0.0
    assert result["G_asigma_at_sigma_zero"] == 0.0
    assert result["localized_sigma_profile_can_change_this_after_sigma_nonzero"]


def test_raw_normal_momentum_is_not_whitened_transfer() -> None:
    result = raw_cross_transfer_audit(0.14, 0.2)
    assert result["raw_p_s_nonzero"]
    assert result["physical_whitened_transfer_proved"] is False


def test_leading_whitened_qs_gram_is_positive_and_noncentral() -> None:
    result = leading_whitened_qs_gram(0.14)
    gram = np.asarray(result["Gram"])
    assert np.allclose(gram, gram.T)
    assert result["positive_definite"]
    assert result["determinant"] > 0.0
    assert result["whitened_cross_correlation"] < 0.0
    assert result["whitened_transfer_nonzero"]
    assert result["phase_two_form_rank"] == 4
    assert result["sigma_zero_extension_rank"] == 6


def test_whitened_cross_has_exact_small_q_coefficient_and_orientation() -> None:
    coefficient = -2401.0 * np.sqrt(210.0) / 311040.0
    small = leading_whitened_qs_gram(1.0e-4, zeta=1.0)
    reversed_result = leading_whitened_qs_gram(1.0e-4, zeta=-1.0)
    balanced = leading_whitened_qs_gram(0.14, zeta=0.0)
    assert np.isclose(
        small["whitened_cross_correlation"] / 1.0e-8,
        coefficient,
        rtol=2e-8,
    )
    assert np.isclose(
        reversed_result["whitened_cross_correlation"],
        -small["whitened_cross_correlation"],
    )
    assert balanced["whitened_cross_correlation"] == 0.0
    assert balanced["whitened_transfer_nonzero"] is False


def test_completion_stays_on_complete_moving_gram_gate() -> None:
    payload = completion_payload()
    assert payload["validation_passed"]
    assert payload["FULL_BHSM_COMPLETE"] is False
    assert FULL_BHSM_COMPLETE is False
    assert payload["full_physical_Gram_operator"] is None
    assert payload["physical_whitened_q_to_s_transfer"][
        "derived_to_leading_small_q_order"
    ]
    assert payload["physical_whitened_q_to_s_transfer"]["full_nonlinear_value"] is None
    assert len(payload["Hindsight_20_20"]["OPEN"]) == 1


def test_materialization_is_deterministic(tmp_path) -> None:
    path = materialize(tmp_path)
    first = path.read_bytes()
    second = materialize(tmp_path).read_bytes()
    assert first == second
    payload = json.loads(first)
    assert payload["validation_passed"]
