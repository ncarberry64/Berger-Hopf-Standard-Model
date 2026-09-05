from __future__ import annotations

import importlib.util
import json
from pathlib import Path

from bhsm.interface.reset_correspondence_stationarity_adjudication import (
    EXACT_NEXT_OBJECT,
    NEW_PHYSICS_DEFICIT,
    base_map_stationarity_adjudication,
    boundary_restriction_witness,
    claim_boundary,
    corner_and_endpoint_result,
    existing_action_reset_term_inventory,
    formal_F_B_variation,
    formal_L_s_variation,
    generator_charge_and_downstream_status,
    hindsight_ledger,
    hopf_rotor_stationarity_result,
    interface_functional_deficit,
    lagrangian_relation_stationarity_adjudication,
    restricted_action_family,
    seam_transversality_equations,
    stationary_child_set_verdict,
)


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/materialize_reset_correspondence_stationarity_adjudication.py"


def _materializer():
    spec = importlib.util.spec_from_file_location("stationarity_materializer", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_all_existing_action_terms_are_classified_at_the_reset() -> None:
    result = existing_action_reset_term_inventory()
    assert result["all_registered_master_terms_covered"] is True
    assert len(result["master_terms"]) == 13
    assert result["any_term_explicitly_contains_F_B"] is False
    assert result["genuine_reset_seam_terms"]["fermion"] == "S_Sigma_F_AE2=0"
    assert result["genuine_reset_seam_terms"]["nonfermion"] is None
    assert "trace_pullbacks" in result["F_B_dependent_only_after_restriction"]


def test_restricted_action_is_a_memberwise_family_not_one_union_functional() -> None:
    result = restricted_action_family()
    assert result["memberwise_definition"].startswith("S_(F,L)")
    assert result["same_bulk_density_for_every_member"] is True
    assert result["explicit_F_B_dependence"] is False
    assert result["explicit_L_s_dependence"] is False
    assert result["single_functional_on_union_of_domains_exists"] is False
    assert result["partial_derivative_delta_F_S_is_action_defined"] is False
    assert result["partial_derivative_delta_L_S_is_action_defined"] is False


def test_boundary_one_form_derives_momentum_matching_not_graph_selection() -> None:
    result = boundary_restriction_witness()
    assert result["momentum_matching_residual"] < 1.0e-12
    assert result["common_trace_contribution"] == 0.0
    assert result["domain_motion_contribution"] != 0.0
    assert result["decomposition_residual"] < 1.0e-12
    assert result["formal_domain_gradient_nonzero"] is True
    assert result["that_condition_selects_C"] is False


def test_formal_F_variation_is_conditional_transversality_only() -> None:
    result = formal_F_B_variation()
    assert result["map_velocity"].startswith("eta_child")
    assert "J_reset" in result["natural_form"]
    assert result["formal_stationarity_equation"].startswith("J_reset")
    assert result["existing_action_allows_delta_F_as_configuration_variation"] is False
    assert result["attachment_equation_action_owned"] is False
    assert result["F_class"] == "F4"


def test_F4_is_selected_and_no_base_map_route_is_preferred() -> None:
    result = base_map_stationarity_adjudication()
    assert result["F1_unique_modulo_redundancy"] is False
    assert result["F2_structured_residual"] is False
    assert result["F3_equation_with_uncontrolled_freedom"] is False
    assert result["F4_action_blind_to_required_choice"] is True
    assert set(result["base_map_routes"].values()) == {"NOT_SELECTED_OR_ELIMINATED"}
    assert result["identity_selected"] is False
    assert result["minimum_energy_used"] is False


def test_formal_L_variation_does_not_strengthen_self_adjointness_to_selection() -> None:
    result = formal_L_s_variation()
    assert result["bulk_action_contains_lambda_s"] is False
    assert result["lambda_s_is_an_action_configuration_variable"] is False
    assert result["formal_condition_selects_graph"] is False
    assert result["two_fixed_graphs_cancel_field_variations"] is True
    assert result["two_fixed_graphs_maximal_isotropic"] is True
    assert result["graph_jets_and_boundary_potentials_differ"] is True
    assert result["self_adjoint_transfer_spectra_differ"] is True
    assert result["L_class"] == "L4"


def test_L4_is_selected_but_natural_boundary_equations_remain() -> None:
    result = lagrangian_relation_stationarity_adjudication()
    assert result["L1_unique_modulo_redundancy"] is False
    assert result["L2_structured_residual"] is False
    assert result["L3_uncontrolled_family_selected_by_an_equation"] is False
    assert result["L4_no_selection_by_existing_action"] is True
    assert result["natural_boundary_equations_exist_after_L_is_selected"] is True
    assert result["natural_boundary_equations_select_L"] is False


def test_transversality_is_full_sector_but_conditional_on_configuration_graph() -> None:
    result = seam_transversality_equations()
    assert result["generic_momentum_equation"].startswith("C_s(F_B)^STAR")
    assert "Pi_e" in result["metric_geometry"]
    assert "E_child" in result["Maxwell_equation"]
    assert "pi_scalar" in result["scalar_topographic"]
    assert "AE2_Gamma0" in result["fermion"]
    assert result["sectors_combine_into_action_selected_full_field_relation"] is False


def test_existing_corner_and_endpoint_terms_do_not_supply_selector() -> None:
    result = corner_and_endpoint_result()
    assert result["GHY"].startswith("COEFFICIENT_LOCKED")
    assert result["Hayward_selects_matter_or_core_domain"] is False
    assert result["smooth_enclosure_reset_locus"] is False
    assert result["fermion_surface_action"] == "S_Sigma_F_AE2=0"
    assert result["complete_reset_counterterm"] is None
    assert result["standard_zero_parameter_completion_forces_reset_selection"] is False


def test_Hopf_stationarity_is_undefined_without_using_minimum_energy() -> None:
    result = hopf_rotor_stationarity_result()
    assert result["J_total"] == 0.0
    assert result["positive_relative_energy"] is True
    assert result["minimum_energy_selection_invoked"] is False
    assert result["delta_F_S_along_attachment_Hopf_direction_action_defined"] is False
    assert result["stationarity_fixes_relative_Hopf_orientation"] is False
    assert result["stationarity_preserves_or_discretizes_rotor"] is None


def test_stationary_child_is_D4_and_generator_chain_remains_closed() -> None:
    child = stationary_child_set_verdict()
    downstream = generator_charge_and_downstream_status()
    assert child["classification"] == "D4"
    assert child["D1_singleton_physical_child"] is False
    assert child["D2_unique_modulo_proved_redundancy"] is False
    assert child["D3_structured_residual"] is False
    assert child["D4_genuinely_underdetermined"] is True
    assert child["N12_fixed_event_child_relation_dimension"] == 67
    assert downstream["Hamiltonian_generator"] is None
    assert downstream["charge_class"] == "U"
    assert downstream["outcome"] == "D"
    assert downstream["S4"] == "BLOCKED"


def test_new_physics_deficit_is_one_arbitrary_functional_not_a_coefficient() -> None:
    result = interface_functional_deficit()
    claims = claim_boundary()
    ledger = hindsight_ledger()
    assert result["schematic_only_not_implemented"].startswith("S_seam")
    assert result["minimum_derivative_order"].startswith("AT_LEAST_FIRST")
    assert result["unique_zero_new_parameter_term_forced"] is False
    assert result["minimum_independent_choice_count"] == 1
    assert result["minimum_choice_type"] == NEW_PHYSICS_DEFICIT
    assert result["implemented_or_tuned"] is False
    assert claims["F_class"] == "F4" and claims["L_class"] == "L4"
    assert claims["stationary_child_class"] == "D4"
    assert claims["new_interface_functional_implemented"] is False
    assert claims["frozen_predictions_changed"] is False
    assert ledger["EXACT_NEXT_OBJECT"] == EXACT_NEXT_OBJECT


def test_materializer_is_deterministic_validated_and_byte_stable() -> None:
    module = _materializer()
    first = module.build_payload()
    second = module.build_payload()
    assert first["validation_passed"] is True
    assert first["F_class"] == "F4"
    assert first["L_class"] == "L4"
    assert first["stationary_child_class"] == "D4"
    assert first["differentiability_class"] == "G4"
    assert first["charge_class"] == "U"
    assert module.deterministic_json(first) == module.deterministic_json(second)
    path = module.main()
    payload = path.read_bytes()
    module.main()
    assert path.read_bytes() == payload
    assert json.loads(payload)["EXACT_NEXT_OBJECT"] == EXACT_NEXT_OBJECT
