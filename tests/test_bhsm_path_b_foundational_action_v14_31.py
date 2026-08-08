from __future__ import annotations

from pathlib import Path

import numpy as np

from bhsm.interface.completion.path_b_foundational_action_v14_31 import (
    BVP_NEXT_OBJECT,
    action_current,
    connection_fork_payload,
    covariant_derivative,
    eta_density,
    finite_difference_current_error,
    foundational_action_payload,
    foundational_bundle_payload,
    kinetic_invariant,
    mixed_variation_witness,
    no_new_vector_hessian_payload,
)
from bhsm.interface.completion.path_b_completion_gate_v14_31 import (
    all_payloads,
    completion_payload,
    materialization_hashes,
)
from bhsm.interface.confinement.path_b_bvp_eligibility_v14_31 import (
    bvp_eligibility_payload,
)
from bhsm.interface.master_action.path_b_master_action_v14_31 import (
    master_action_payload,
)


def test_01_foundational_bundle_uses_physical_color_cocycle():
    payload = foundational_bundle_payload()
    assert payload["validation_passed"]
    assert payload["classification"] == "EXPLICIT_FOUNDATIONAL_BHSM_POSTULATE"
    assert "P_color" in payload["parent_bundle"]


def test_02_connection_fork_rejects_independent_coset_vectors():
    payload = connection_fork_payload()
    assert payload["validation_passed"]
    rejected = [row for row in payload["fork"] if row.get("status") == "REJECTED_BY_NO_NEW_VECTOR_GATE"]
    assert len(rejected) == 1
    assert "six additional" in rejected[0]["result"]


def test_03_path_b_selects_composite_connection():
    payload = connection_fork_payload()
    selected = [row for row in payload["fork"] if row.get("status") == "SELECTED"]
    assert len(selected) == 1
    assert "Theta_eta" in selected[0]["connection"]


def test_04_covariant_derivative_reduces_at_zero_connection():
    eta = np.asarray([0.2, 0.1j, -0.4], complex)
    partial = np.asarray([[0.1j, 0.2, -0.3j]], complex)
    assert np.allclose(covariant_derivative(eta, partial, np.zeros((1, 8))), partial)


def test_05_current_is_negative_connection_variation():
    eta = np.asarray([0.2 + 0.1j, -0.4j, 0.7], complex)
    partial = np.asarray([[0.1, 0.2j, -0.2]], complex)
    gauge = np.zeros((1, 8))
    assert finite_difference_current_error(eta, partial, gauge) < 5e-6


def test_06_action_current_is_nonzero_away_from_selector():
    eta = np.asarray([0.2, 0.0, 0.0], complex)
    derivative = np.asarray([[0.2j, 0.0, 0.0]], complex)
    assert np.linalg.norm(action_current(eta, derivative)) > 0


def test_07_selector_current_is_zero():
    eta = np.zeros(3, complex)
    derivative = np.zeros((1, 3), complex)
    assert np.allclose(action_current(eta, derivative), 0)


def test_08_mixed_variation_is_generically_nonzero():
    assert mixed_variation_witness() > 1e-6


def test_09_no_new_vector_hessian():
    payload = no_new_vector_hessian_payload()
    assert payload["validation_passed"]
    assert payload["additional_vector_pole_count"] == 0
    assert payload["quadratic_blocks"]["H_thetatheta"] is None


def test_10_eta_density_has_retained_p2_p8_form():
    x = 0.7
    assert np.isclose(eta_density(x), -(0.5 * x + 0.125 * x**4))
    assert kinetic_invariant(np.asarray([[1.0, 0.0, 0.0]], complex)) == 2.0


def test_11_foundational_action_gate_passes():
    payload = foundational_action_payload()
    assert payload["validation_passed"]
    assert payload["M8_status"].startswith("OPEN_UV")
    assert payload["new_continuous_parameters"] == []


def test_12_master_action_replaces_duplicate_eta_copy():
    payload = master_action_payload()
    assert payload["validation_passed"]
    assert payload["action_ownership_gate"] == "PASSED_BY_EXPLICIT_FOUNDATIONAL_POSTULATE"
    assert "do not add a second" in payload["replacement_rule"]


def test_13_bvp_is_eligible_but_not_solved():
    payload = bvp_eligibility_payload()
    assert payload["validation_passed"]
    assert payload["eligible"] is True
    assert payload["status"] == "ELIGIBLE_NOT_SOLVED"
    assert payload["exact_next_object"] == BVP_NEXT_OBJECT


def test_14_completion_gate_does_not_claim_full_bhsm():
    payload = completion_payload()
    assert payload["validation_passed"]
    assert payload["BHSM_complete"] is False
    assert payload["action_ownership_gate"].startswith("PASSED")
    assert payload["confinement_gate"] == "OPEN"
    assert all(value is None for value in payload["forbidden_outputs"].values())


def test_15_materialization_is_deterministic(tmp_path: Path):
    first = materialization_hashes(tmp_path / "first")
    second = materialization_hashes(tmp_path / "second")
    assert first == second
    assert "BHSM_completion_gate_v14_31.json" in first


def test_16_required_artifacts_are_present():
    names = all_payloads()
    for required in (
        "BHSM_Path_B_foundational_G2_color_bundle_v14_31.json",
        "BHSM_Path_B_G2_connection_fork_v14_31.json",
        "BHSM_Path_B_no_new_vector_Hessian_v14_31.json",
        "BHSM_Path_B_foundational_color_eta_action_v14_31.json",
        "BHSM_Path_B_master_action_v14_31.json",
        "BHSM_Path_B_nonAbelian_BVP_eligibility_v14_31.json",
        "BHSM_completion_gate_v14_31.json",
    ):
        assert required in names
