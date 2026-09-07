import hashlib
import json

from bhsm.interface.boundary_improved_event_mode_envelopment_charge_map_adjudication import (
    AE4R_CLASS,
    CHG_CLASS,
    DOMH_CLASS,
    ENVH_CLASS,
    EXACT_NEXT_OBJECT,
    MODEE_CLASS,
    REF_CLASS,
    XI_CLASS,
    ae4_impedance_and_crossing_status,
    available_charge_status,
    child_seam_and_increment_status,
    claim_boundary,
    common_domain_status,
    complete_presymplectic_potential_status,
    conservation_and_branching_status,
    differentiability_integrability_status,
    event_and_mode_charge_status,
    exact_next_object,
    generator_adjudication,
    n12_rank_status,
    reference_status,
    registered_action_status,
    retained_outgoing_other_ledger,
    sector_contribution_ledger,
)
from scripts.materialize_boundary_improved_event_mode_envelopment_charge_map_adjudication import (
    TARGET,
    build_payload,
    deterministic_json,
    main,
)


def test_registered_action_is_not_promoted_across_missing_reduction_maps():
    result = registered_action_status()
    assert result["registered_term_count"] == 13
    assert "T8_EH" in result["registered_term_ids"]
    assert "T5_GHY" in result["registered_term_ids"]
    assert not result["single_closed_parent_action"]
    assert not result["reduction_maps_R8_to_5_and_R5_to_4_owned"]
    assert not result["single_full_field_moving_event_child_domain"]


def test_complete_theta_is_withheld_while_sector_ledger_is_complete():
    theta = complete_presymplectic_potential_status()
    rows = sector_contribution_ledger()
    assert theta["complete_Theta_event"] is None
    assert theta["complete_Theta_child"] is None
    assert theta["complete_relative_Theta"] is None
    assert not theta["complete_boundary_presymplectic_potential_derived"]
    assert theta["first_obstruction"] == EXACT_NEXT_OBJECT
    assert len(rows) == 9
    assert all(
        {
            "sector",
            "action_source",
            "theta_contribution",
            "boundary_term",
            "corner_term",
            "owned",
            "common_event_child_domain",
            "charge_assembler_available",
        }
        == set(row)
        for row in rows
    )
    assert all(not row["common_event_child_domain"] for row in rows)
    assert all(not row["charge_assembler_available"] for row in rows)


def test_common_generator_is_XI5_and_charge_stops_at_tangency():
    result = generator_adjudication()
    assert result["classification"] == XI_CLASS == "XI5"
    assert result["common_action_owned_generator"] is None
    assert not result["tangent_to_active_domain"]
    assert result["stop_charge_comparison_here"]
    assert "NOT_A_HAMILTONIAN_SYMMETRY" in result["candidate_retarded_time_flow"]
    assert "NOT_A_SPACETIME_VECTOR_FIELD" in result["candidate_event_mode_generator"]


def test_CHG4_does_not_assign_an_improvement_or_charge():
    result = differentiability_integrability_status()
    assert result["classification"] == CHG_CLASS == "CHG4"
    assert not result["functional_differential_exists_on_current_domain"]
    assert not result["integrability_test_reached"]
    assert result["required_improvement_B_xi"] is None
    assert result["B_xi_is_zero"] is None
    assert result["no_numerical_charge_may_be_assigned"]


def test_REF5_and_MODEE5_preserve_reference_and_projector_blockers():
    reference = reference_status()
    event = event_and_mode_charge_status()
    assert reference["classification"] == REF_CLASS == "REF5"
    assert reference["usable_common_reference"] is None
    assert reference["selected_boundary_ensemble"] is None
    assert event["total_event_charge_H_xi_event"] is None
    assert event["mode_classification"] == MODEE_CLASS == "MODEE5"
    assert event["initiating_mode_projector_P_mode"] is None
    assert event["initiating_mode_charge_H_xi_mode"] is None
    assert not event["frozen_family_projectors_are_P_mode"]
    assert not event["N12_ordered_event_eigenline_is_P_mode"]


def test_available_and_child_seam_charges_are_not_fabricated():
    available = available_charge_status()
    child = child_seam_and_increment_status()
    ledger = retained_outgoing_other_ledger()
    assert available["value"] is None
    assert not available["definition_earned"]
    assert not available["candidate_subtraction_formula_adopted"]
    assert available["blocked_by"] == ["XI5", "CHG4", "REF5", "MODEE5"]
    assert len(ledger) == 5
    assert child["classification"] == ENVH_CLASS == "ENVH5"
    assert child["H_xi_child_plus_seam"] is None
    assert child["Delta_H_xi_child_plus_seam"] is None
    assert child["path_independence"] is None


def test_common_domain_is_DOMH4_not_a_sectorwise_charge_domain():
    result = common_domain_status()
    assert result["classification"] == DOMH_CLASS == "DOMH4"
    assert result["D_H"] is None
    assert result["sectorwise_domains_exist"]
    assert not result["common_generator"]
    assert not result["common_ensemble"]
    assert not result["common_reference"]
    assert "do not host" in result["why_not_DOMH2"]


def test_AE4R5_blocks_ratio_crossing_and_root_search():
    result = ae4_impedance_and_crossing_status()
    assert result["classification"] == AE4R_CLASS == "AE4R5"
    assert not result["historical_E_mode_identified_with_H_xi_mode_avail"]
    assert not result["historical_E_impedance_identified_with_Delta_H_xi_child_plus_seam"]
    assert result["rho_hold_modern_value"] is None
    assert result["first_future_crossing_function"] is None
    assert result["existence"] is None and result["uniqueness"] is None
    assert not result["equality_is_saturation"]
    assert not result["root_search_performed"]


def test_conservation_does_not_force_children_or_change_N12_rank():
    conservation = conservation_and_branching_status()
    rank = n12_rank_status()
    boundary = claim_boundary()
    assert conservation["proposed_child_charge_tests_completed"] == 0
    assert conservation["charge_supported_child_found"] is None
    assert conservation["charge_inadmissible_child_found"] is None
    assert not conservation["multiple_children_forced_by_charge_analysis"]
    assert rank["actual_new_independent_rank"] == 0
    assert rank["residual_before_time_quotient"] == 67
    assert rank["residual_after_time_quotient"] == 66
    assert not boundary["H_XI_MODE_AVAILABLE_DERIVED"]
    assert not boundary["DELTA_H_XI_CHILD_PLUS_SEAM_DERIVED"]
    assert not boundary["RESPONSE_FUNCTION_SELECTED"]
    assert not boundary["FROZEN_PREDICTIONS_CHANGED"]
    assert not boundary["GATE7_PROMOTED"]


def test_exact_next_object_is_the_existing_moving_domain_blocker():
    result = exact_next_object()
    assert result["object"] == EXACT_NEXT_OBJECT
    assert "F_B as an action configuration argument" in result["must_supply"]
    assert "first moving-domain variation" in result["must_supply"][2]
    assert "arbitrary reset graph" in result["not_authorized"]


def test_materialized_artifact_is_valid_and_byte_deterministic():
    first_payload = build_payload()
    second_payload = build_payload()
    assert first_payload["validation_passed"]
    assert all(first_payload["validation"].values())
    assert first_payload["classifications"] == {
        "xi": "XI5",
        "charge": "CHG4",
        "reference": "REF5",
        "mode_energy": "MODEE5",
        "envelopment_charge": "ENVH5",
        "common_domain": "DOMH4",
        "AE4_ratio": "AE4R5",
    }
    assert deterministic_json(first_payload) == deterministic_json(second_payload)
    main()
    first = hashlib.sha256(TARGET.read_bytes()).hexdigest()
    main()
    second = hashlib.sha256(TARGET.read_bytes()).hexdigest()
    assert first == second
    assert json.loads(TARGET.read_text(encoding="utf-8"))["validation_passed"]
