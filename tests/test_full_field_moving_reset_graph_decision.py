from __future__ import annotations

import importlib.util
import json
from pathlib import Path

from bhsm.interface.full_field_moving_reset_graph_decision import (
    EXACT_NEXT_OBJECT,
    claim_boundary,
    conditional_full_field_reset_graph,
    existing_reset_contract_inventory,
    field_by_field_attachment_rules,
    first_moving_domain_variation,
    hopf_rotor_adversarial_result,
    outcome_and_hindsight,
    reconstruction_determinism_audit,
    relative_tangent_and_generator_verdict,
    second_order_and_downstream_status,
    transport_and_tangent_witness,
    uniqueness_and_ambiguity_verdict,
)


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/materialize_full_field_moving_reset_graph_decision.py"


def _materializer():
    spec = importlib.util.spec_from_file_location("moving_reset_materializer", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_reset_contract_inventory_separates_owned_conditional_and_missing_data() -> None:
    result = existing_reset_contract_inventory()
    assert result["inventory_complete"] is True
    assert len(result["rows"]) == 29
    assert "F_B" in result["categories"]["lacking_attachment_law"]
    assert "AE2_internal_spin_gauge_lift_U_R" in result["categories"]["mathematically_defined_map"]
    assert "curvature" in result["categories"]["automatic_by_naturality_once_F_B_and_lift_are_supplied"]


def test_field_rules_use_one_base_map_and_correct_geometric_lifts() -> None:
    result = field_by_field_attachment_rules()
    assert result["convention"].startswith("F_B:Sigma_event")
    assert "dU+" in result["gauge_connection"]
    assert "Kosmann" not in result["spinor"]  # finite rule uses the lift itself
    assert "COTANGENT" in result["canonical_pair"]
    assert result["rule_status"].startswith("CONDITIONAL")


def test_maximal_conditional_family_is_constructed_without_selecting_a_member() -> None:
    result = conditional_full_field_reset_graph()
    assert result["maximal_authorized_family_constructed"] is True
    assert result["single_graph_constructed"] is False
    assert "L_s(F_B)" in result["transported_relation"]
    assert "Graph(U_R)" in result["AE2_fixed_component"]
    assert "F_B" in result["unselected_components"]


def test_first_moving_domain_variation_is_explicit_for_all_geometric_types() -> None:
    result = first_moving_domain_variation()
    assert result["map_velocity"].startswith("eta_child")
    assert "mathfrak_L" in result["natural_pullback"]
    assert "D_F C_s" in result["D_R"]
    assert "F_B^*(delta A_c+L_eta A_c)" in result["connection_D_R"]
    assert "Kosmann" in result["geometric_derivatives"]["spinor"]
    assert result["first_variation_derived_for_entire_conditional_family"] is True
    assert result["first_variation_action_owned"] is False


def test_numerical_moving_pullback_and_cotangent_witnesses_close() -> None:
    result = transport_and_tangent_witness()
    assert result["moving_tensor_pullback_residual"] < 1.0e-8
    assert result["cotangent_symplectic_residual"] < 1.0e-12
    assert result["equivariant_graph_residual"] < 1.0e-12
    assert result["linearized_tangent_residual"] < 1.0e-8
    assert result["relative_attachment_variation_norm"] > 0.0
    assert result["witness_is_conditional_not_action_owned"] is True


def test_Norman_semantics_do_not_promote_missing_master_map_or_local_chart() -> None:
    result = reconstruction_determinism_audit()
    assert result["typed_parent_to_updated_parent"] is True
    assert result["typed_cycle_is_physical_operator"] is False
    assert result["master_self_reconstruction_map_exists"] is False
    assert result["repository_Fix_P_s_singleton_found"] is False
    assert result["repository_D_P_s_zero_applicable_to_full_field_reset"] is False
    assert "NOT_A_GLOBAL" in result["N3_local_child_chart"]["scope"]
    assert result["N12_event_child_relation"]["fixed_event_child_fiber_dimension"] == 67


def test_uniqueness_attempt_selects_R4_only_after_physical_witness() -> None:
    result = uniqueness_and_ambiguity_verdict()
    assert result["R1_unique"] is False
    assert result["R2_representation_only"] is False
    assert result["R3_finite_or_small_physical_family"] is False
    assert result["R4_uncontrolled_functional_choice"] is True
    assert result["same_topology_orientation_metric_volume_distinct_DF"] is True
    assert result["physical_transfer_spectra_differ"] is True
    assert result["boundary_potentials_differ"] is True
    assert result["minimum_new_physical_choice"] == EXACT_NEXT_OBJECT


def test_Norman_candidate_classification_rejects_arbitrary_child_data() -> None:
    result = uniqueness_and_ambiguity_verdict()["Norman_semantics_consistency"]
    assert result["natural_diagonal_graph"].startswith("CONSISTENT")
    assert result["simultaneous_coordinate_frame_basis_relabeling"].startswith("REPRESENTATIONALLY_EQUIVALENT")
    assert result["arbitrary_independent_child_boundary_data"].startswith("INCONSISTENT")
    assert "FALSE" in result["physical_equivalence_of_distinct_surviving_members"]


def test_conditional_tangency_does_not_change_active_generator_charge_verdict() -> None:
    result = relative_tangent_and_generator_verdict()
    assert result["conditional_family_equivariant"] is True
    assert result["relative_vector_tangent_to_each_supplied_equivariant_graph"] is True
    assert result["relative_vector_tangent_to_active_BHSM_reset_domain"] is False
    assert result["Hamiltonian_generator"] is None
    assert result["event_charge_Q_e"] is None
    assert result["child_charge_Q_c"] is None
    assert result["relative_charge_Q_rel"] is None
    assert result["differentiability_class"] == "G4"
    assert result["charge_class"] == "U"


def test_hopf_rotor_breaks_blanket_quotient_and_downstream_stays_closed() -> None:
    hopf = hopf_rotor_adversarial_result()
    downstream = second_order_and_downstream_status()
    assert hopf["J_total"] == 0.0
    assert hopf["relative_energy_positive"] is True
    assert hopf["blanket_Hopf_quotient_rejected"] is True
    assert downstream["second_variation_required_now"] is False
    assert downstream["reduced_reset"] is None
    assert downstream["S4"] == "BLOCKED"


def test_hindsight_and_claim_boundaries_are_fail_closed() -> None:
    result = outcome_and_hindsight()
    claims = claim_boundary()
    assert result["outcome"] == "D"
    assert result["A"] is False and result["B"] is False and result["C"] is False
    assert result["D"] is True
    assert result["OPEN"] == [EXACT_NEXT_OBJECT]
    assert claims["R_class"] == "R4"
    assert claims["new_physical_postulate_inserted"] is False
    assert claims["unique_physical_child_from_complete_parent_and_event_derived"] is False
    assert claims["frozen_predictions_changed"] is False
    assert claims["FULL_BHSM_COMPLETE"] is False


def test_materializer_is_deterministic_validated_and_byte_stable() -> None:
    module = _materializer()
    first = module.build_payload()
    second = module.build_payload()
    assert first["validation_passed"] is True
    assert first["R_class"] == "R4"
    assert first["differentiability_class"] == "G4"
    assert first["charge_class"] == "U"
    assert first["outcome"] == "D"
    assert module.deterministic_json(first) == module.deterministic_json(second)
    path = module.main()
    payload = path.read_bytes()
    module.main()
    assert path.read_bytes() == payload
    assert json.loads(payload)["EXACT_NEXT_OBJECT"] == EXACT_NEXT_OBJECT
