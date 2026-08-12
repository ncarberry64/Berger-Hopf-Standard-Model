from __future__ import annotations

import json

from bhsm.interface.aether_completion_foundational_obstruction import (
    FULL_BHSM_COMPLETE,
    completion_payload,
    coupled_q_sigma_trajectory,
    foundational_completion_audit,
    materialize,
    nonlinear_nonuniqueness_witness,
    sigma_zero_invariance_theorem,
)


def test_sigma_zero_is_exact_under_full_inertial_hamiltonian() -> None:
    result = coupled_q_sigma_trajectory(
        g=5.0,
        static_sigma_curvature=0.02,
        direct_sigma_quartic=1.0,
        sigma_seed=0.0,
    )
    assert result["solver_success"]
    assert result["maximum_absolute_sigma"] == 0.0
    assert result["final_sigma"] == 0.0
    assert result["sigma_zero_exact_numerically"]
    assert result["energy_drift"] < 5.0e-11


def test_exact_invariance_theorem_survives_q_to_s_transfer() -> None:
    theorem = sigma_zero_invariance_theorem()
    assert theorem["holds_with_q_s_transfer"]
    assert theorem["tachyonic_curvature_creates_nonzero_classical_seed"] is False
    assert theorem["positive_inertial_saturation_creates_nonzero_classical_seed"] is False
    assert theorem["sign_branch_selected"] is False


def test_allowed_response_data_give_inequivalent_nonlinear_trajectories() -> None:
    witness = nonlinear_nonuniqueness_witness()
    assert witness["same_formation_architecture_different_g_changes_amplification"]
    assert witness["same_action_different_unselected_seed_changes_nonlinear_outcome"]
    assert witness["zero_seed_stays_zero"]
    assert witness["controls_are_predictions"] is False


def test_foundational_audit_identifies_minimum_missing_action_data() -> None:
    audit = foundational_completion_audit()
    assert audit["retained_action_is_single_fully_selected_theory"] is False
    assert audit["independent_sigma_response_triples_exist"] == 3
    assert audit["triples_share_sigma_zero_parent_and_first_variation"]
    assert audit["classical_nonzero_seed_or_state_rule_present"] is False
    assert audit["can_be_derived_by_varying_existing_regular_fields"] is False
    assert audit["unique_material_skin_deducible"] is False
    assert audit["unique_child_or_Unique_Actualization_deducible"] is False
    assert audit["foundational_contradiction_to_requested_unconditional_completion"]


def test_completion_fails_closed_without_inventing_selector() -> None:
    payload = completion_payload()
    assert payload["validation_passed"]
    assert payload["FULL_BHSM_COMPLETE"] is False
    assert FULL_BHSM_COMPLETE is False
    assert payload["no_retuning_certificate"]["numeric_response_selector_invented"] is False
    assert "material_skin" in payload["downstream_quantities_not_well_defined"]
    assert "Unique_Actualization" in payload["downstream_quantities_not_well_defined"]


def test_materialization_is_deterministic(tmp_path) -> None:
    path = materialize(tmp_path)
    first = path.read_bytes()
    second = materialize(tmp_path).read_bytes()
    assert first == second
    payload = json.loads(first)
    assert payload["validation_passed"]
