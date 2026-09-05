from __future__ import annotations

import importlib.util
import json
from pathlib import Path

from bhsm.interface.relative_diffeomorphism_generator_charge_adjudication import (
    CHARGE_CLASS,
    DIFFERENTIABILITY_CLASS,
    EXACT_NEXT_OBJECT,
    candidate_relative_generator,
    claim_boundary,
    constraint_noether_ownership,
    decision_power_ledger,
    differentiability_and_charge_verdict,
    hopf_rotor_charge_adjudication,
    infinitesimal_action_and_trace_witness,
    infinitesimal_relative_transformation,
    outcome_and_downstream_status,
    presymplectic_potential_inventory,
    reset_trace_domain_independence_witness,
)


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/materialize_relative_diffeomorphism_generator_charge_adjudication.py"


def _materializer():
    spec = importlib.util.spec_from_file_location("relative_diffeo_materializer", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_complete_relative_presymplectic_potential_is_not_fabricated() -> None:
    result = presymplectic_potential_inventory()
    assert "T8_EH" in result["master_action_terms_traced"]
    assert result["event"]["complete_Theta_event"] is None
    assert result["child"]["complete_Theta_child"] is None
    assert result["complete_relative_Theta"] is None
    assert result["reset_and_seam"]["algebraic_attachment_Theta"] == 0
    assert result["reset_and_seam"]["AE2_spatial_base_pullback_present"] is False
    assert result["reset_and_seam"]["AE4_adds_boundary_counterterm"] is False
    assert result["boundary_polarization"]["complete_reset_ensemble"] is None


def test_infinitesimal_two_sided_action_separates_stabilizer_and_relative() -> None:
    result = infinitesimal_relative_transformation()
    assert result["infinitesimal_attachment"].startswith("delta_F=xi_child")
    assert result["stabilizer_delta_F"] == 0
    assert result["genuine_relative_condition"].endswith("NOT_EQUAL_ZERO")
    assert result["current_AE2_trace_contains_F"] is False
    assert result["current_relative_vector_tangent_to_reset_domain_defined"] is False
    assert result["blocked_by"] == EXACT_NEXT_OBJECT


def test_finite_difference_and_formal_trace_witness_close() -> None:
    result = infinitesimal_action_and_trace_witness()
    assert result["finite_difference_residual"] < 1.0e-9
    assert result["analytic_relative_generator_norm"] > 0.0
    assert result["stabilizer_generator_norm"] < 1.0e-12
    assert result["formal_trace_equivariance_residual"] < 1.0e-12
    assert result["witness_instantiates_current_BHSM_reset_graph"] is False


def test_missing_moving_trace_graph_is_independent_domain_data() -> None:
    result = reset_trace_domain_independence_witness()
    assert result["nonfermion_same_zero_field_graph"] is True
    assert result["nonfermion_different_first_field_jets"] is True
    assert result["both_graphs_maximal_isotropic"] is True
    assert result["both_graphs_cancel_fixed_field_variations"] is True
    assert result["hypothetical_boundary_potentials_differ"] is True
    assert result["moving_gravity_corner_coefficient_locked"] is True
    assert result["moving_gravity_selects_matter_domain"] is False
    assert result["self_adjointness_selects_trace_unitary"] is False
    assert result["inequivalent_conservative_transfer_spectra"] is True
    assert result["seam_embedding_action_owned"] is False
    assert result["seam_embedding_canonical_momentum"] is None


def test_generator_fails_before_charge_or_ensemble_can_be_tested() -> None:
    result = candidate_relative_generator()
    assert result["delta_xi_rel_is_a_vector_field_on_current_reset_domain"] is False
    assert result["Omega_reset_complete"] is False
    assert result["Q_xi_event_assembler"] is None
    assert result["Q_xi_child_assembler"] is None
    assert result["B_xi_relative"] is None
    assert result["Hamiltonian_generator"] is None
    assert result["failure_order"][0] == "F_B_IS_NOT_A_VARIED_CONFIGURATION_ARGUMENT"
    assert result["refined_first_blocker"] == EXACT_NEXT_OBJECT


def test_differentiability_is_G4_and_charge_is_U() -> None:
    result = differentiability_and_charge_verdict()
    assert result["differentiability_class"] == DIFFERENTIABILITY_CLASS == "G4"
    assert result["G1"] is False
    assert result["G2"] is False
    assert result["G3"] is False
    assert result["G4"] is True
    assert result["later_boundary_ensemble_choice_may_be_G3"] is True
    assert result["later_G3_not_reached"] is True
    assert result["event_charge_Q_e"] is None
    assert result["child_charge_Q_c"] is None
    assert result["relative_charge_Q_rel"] is None
    assert result["charge_class"] == CHARGE_CLASS == "U"
    assert result["charge_kernel"] is None


def test_hopf_rotor_is_bulk_energy_not_the_missing_boundary_charge() -> None:
    result = hopf_rotor_charge_adjudication()
    assert result["J_total"] == 0.0
    assert result["positive_energy"] is True
    assert result["is_event_child_attachment_boundary_charge_Q_rel"] is False
    assert "BULK_COLLECTIVE" in result["classification"]
    assert "DOES_NOT_DISTINGUISH" in result["decision_power"]


def test_existing_constraint_algebra_does_not_generate_attachment_motion() -> None:
    result = constraint_noether_ownership()
    assert result["N12_identity_moves_F_B"] is False
    assert result["compact_Hopf_constraint_sets_total_J_zero"] is True
    assert result["compact_Hopf_constraint_kills_relative_rotor"] is False
    assert result["existing_first_class_constraint_generates_relative_attachment"] is False
    assert result["relative_Noether_identity_owned"] is False


def test_outcome_D_is_retained_at_a_sharper_domain_boundary() -> None:
    result = outcome_and_downstream_status()
    assert result["selected_outcome"] == "D"
    assert result["A"] is False and result["B"] is False and result["C"] is False
    assert result["D"] is True
    assert result["D_is_sharper_than_prior"] is True
    assert result["relative_BRST_extension_earned"] is False
    assert result["new_relative_ghost_added"] is False
    assert result["reduced_reset"] is None
    assert result["S1"] == "REFERENCE_SLICE_ONLY"
    assert result["S4"] == "BLOCKED"
    assert result["exact_next_object"] == EXACT_NEXT_OBJECT


def test_decision_power_and_claim_boundaries_are_explicit() -> None:
    rows = decision_power_ledger()
    assert len(rows) == 6
    assert any("FORCES_G4" in row["distinguishes_A_B_C_D"] for row in rows)
    claims = claim_boundary()
    assert claims["formal_infinitesimal_relative_action_derived"] is True
    assert claims["complete_Theta_event_derived"] is False
    assert claims["complete_Theta_child_derived"] is False
    assert claims["differentiable_H_xi_rel_derived"] is False
    assert claims["charge_class"] == "U"
    assert claims["differentiability_class"] == "G4"
    assert claims["relative_BRST_extension_earned"] is False
    assert claims["outcome_D_retained_and_sharpened"] is True
    assert claims["frozen_predictions_changed"] is False
    assert claims["FULL_BHSM_COMPLETE"] is False


def test_materializer_is_deterministic_and_validated() -> None:
    module = _materializer()
    first = module.build_payload()
    second = module.build_payload()
    assert first["validation_passed"] is True
    assert first["charge"]["charge_class"] == "U"
    assert first["differentiability"]["differentiability_class"] == "G4"
    assert first["outcome"]["selected_outcome"] == "D"
    assert first["OPEN"] == [EXACT_NEXT_OBJECT]
    assert first["EXACT_NEXT_OBJECT"] == EXACT_NEXT_OBJECT
    assert first["DECISION_POWER"]
    assert first["REDUNDANT"]
    assert module.deterministic_json(first) == module.deterministic_json(second)


def test_materialized_artifact_is_byte_identical() -> None:
    module = _materializer()
    path = module.main()
    first = path.read_bytes()
    module.main()
    assert path.read_bytes() == first
    assert json.loads(first)["validation_passed"] is True
