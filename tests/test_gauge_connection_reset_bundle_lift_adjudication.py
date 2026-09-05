from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import numpy as np

from bhsm.interface.gauge_connection_reset_bundle_lift_adjudication import (
    EXACT_CLOSED_VERTICAL_DATUM,
    EXACT_ATTACHMENT_QUOTIENT_DATUM,
    EXACT_MISSING_BASE_DATUM,
    EXACT_MISSING_DATUM,
    STATUS,
    attachment_equivalence_adjudication,
    attachment_representative_naturality_witness,
    attachment_symmetry_group,
    canonical_attachment_quotient,
    claim_boundary,
    common_reset_gauge_vertical_one_jet,
    conditional_geometry_checks,
    connection_pullback_residual,
    connection_reset_linearization,
    downstream_status,
    gfhs_naturality,
    induced_connection_transport,
    local_one_jet_nonuniqueness_witness,
    ownership_levels,
    one_jet_component_status,
    requested_object_classification,
    spatial_base_attachment_authority,
    spatial_base_route_audit,
    spatial_correspondence_nonuniqueness_witness,
    source_lineage_ledger,
    weighted_cotangent_momentum_map,
)


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/materialize_gauge_connection_reset_bundle_lift_adjudication.py"


def _materializer():
    spec = importlib.util.spec_from_file_location("gauge_reset_materializer", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_three_ownership_levels_are_not_conflated() -> None:
    levels = ownership_levels()
    assert levels["bundle_isomorphism_class"]["status"] == "EXISTS"
    assert levels["actual_equivariant_bundle_morphism"]["status"] == (
        "EXISTS_ABSTRACTLY_ON_THE_AE2_BOUNDARY_BUNDLE"
    )
    actual = levels["actual_equivariant_bundle_morphism"]
    assert actual["smooth"] is True
    assert actual["principal_bundle_local_representative_evaluable"] is False
    assert actual["local_gauge_transition_g_B_evaluable_in_common_reset_frame"] is True
    assert actual["vertical_first_derivative_dg_B_evaluable_in_common_reset_frame"] is True
    assert actual["base_tangent_DF_B_evaluable"] is False
    assert levels["induced_connection_transport"]["configuration_map"] is None


def test_conditional_connection_law_satisfies_repository_pullback_equation() -> None:
    lift = np.eye(2, dtype=complex)
    tangent = np.asarray(((2.0, 0.0), (0.0, 0.5)))
    event = np.asarray((1.0j * np.eye(2), 2.0j * np.eye(2)))
    derivative = np.asarray((0.25j * lift, -0.5j * lift))
    child = induced_connection_transport(event, tangent, lift, derivative)
    assert connection_pullback_residual(
        event, child, tangent, lift, derivative
    ) < 1.0e-12
    assert np.linalg.norm(child) > 0.0


def test_connection_law_is_affine_and_linearization_excludes_dg_term() -> None:
    root = 1.0 / np.sqrt(2.0)
    lift = root * np.asarray(((1.0, 1.0j), (1.0j, 1.0)), dtype=complex)
    tangent = np.asarray([[2.0]])
    derivative = np.asarray([0.25j * lift])
    zero = np.zeros((1, 2, 2), dtype=complex)
    first = np.asarray([((0.0j, 2.0j), (2.0j, 0.0j))])
    child_zero = induced_connection_transport(zero, tangent, lift, derivative)
    child_first = induced_connection_transport(first, tangent, lift, derivative)
    linearization = connection_reset_linearization(tangent, lift)
    delta = (child_first - child_zero).reshape(-1)
    assert np.allclose(delta, linearization @ first.reshape(-1))
    assert not np.allclose(child_zero, 0.0)


def test_focused_source_lineage_separates_state_and_spatial_maps() -> None:
    rows = source_lineage_ledger()
    assert len(rows) == 17
    assert any("ABSTRACT_ACTUAL_SMOOTH" in row["found"] for row in rows)
    assert any("PARAMETER_SPACE_RANDOM_FRAME" in row["found"] for row in rows)
    assert not any("LOCAL_F_B_DF_B_g_B_dg_B" in row["found"] for row in rows)
    assert all(row["not_found"] for row in rows)


def test_one_jet_split_closes_vertical_gauge_half_only() -> None:
    split = one_jet_component_status()
    assert split["A_base_attachment"]["status"] == "OPEN"
    assert split["A_base_attachment"]["local_spatial_map_F_B"] is None
    assert split["A_base_attachment"]["blocked_by"] == EXACT_MISSING_BASE_DATUM
    assert split["B_vertical_gauge_lift"]["status"] == "CLOSED"
    assert split["B_vertical_gauge_lift"]["object"] == EXACT_CLOSED_VERTICAL_DATUM
    vertical = common_reset_gauge_vertical_one_jet(3, 16)
    assert np.array_equal(vertical["G_R"], np.eye(16))
    assert np.array_equal(vertical["dG_R"], np.zeros((3, 16, 16)))
    assert vertical["full_spin_lift_derivative_claimed_zero"] is False


def test_n12_first_hit_jet_is_not_misidentified_as_spatial_DF_B() -> None:
    base = one_jet_component_status()["A_base_attachment"]
    assert base["N12_first_hit_map"] == "F12:R^196_TO_R^57_ON_CAUCHY_STATE_VARIABLES"
    assert base["N12_moving_endpoint_jet"].startswith("JACOBI_FIELD")
    assert base["implicit_differentiation_for_DF_B"].startswith("INAPPLICABLE")


def test_child_ontology_is_abstract_post_cut_copy_not_same_surface() -> None:
    authority = spatial_base_attachment_authority()
    assert authority["Sigma_child_definition"] == "Sigma_c=S3_times_S3"
    assert authority["child_ontology"].startswith("CASE_4")
    assert authority["event_embedding"] is None
    assert authority["child_embedding"] is None
    assert authority["common_ambient_geometry"] is None
    assert authority["cross_copy_boundary_exchange_selected"] is False
    assert authority["metric_transport_through_firewall"] is False
    assert authority["F_B"] is None
    assert authority["D_F_B"] is None
    assert authority["LOCAL_EVENT_CHILD_BASE_MAP_DERIVED"] is False
    assert authority["GLOBAL_EVENT_CHILD_BASE_MAP_DERIVED"] is False
    assert authority["global_boundary_diffeomorphism_required_now"] is False
    assert authority["exact_next_object"] == EXACT_MISSING_BASE_DATUM


def test_all_four_owned_base_map_constructions_are_exhausted() -> None:
    routes = spatial_base_route_audit()
    assert [row["route"][0] for row in routes] == ["A", "B", "C", "D"]
    assert all(row["status"] == "DOES_NOT_CLOSE" for row in routes)
    assert "EMBEDDINGS" in routes[0]["route"]
    assert "FLOW" in routes[1]["route"]
    assert "NORMAL" in routes[2]["route"]
    assert "IMPLICIT" in routes[3]["route"]


def test_S3_times_S3_retained_data_do_not_select_DF_B() -> None:
    witness = spatial_correspondence_nonuniqueness_witness()
    assert witness["same_marked_group_identity_point"] is True
    assert witness["same_degree"] == 1
    assert witness["same_orientation"] is True
    assert witness["same_volume_jacobian"] is True
    assert witness["both_preserve_product_tangent_metric"] is True
    assert witness["tangent_maps_distinct"] is True
    assert witness["connection_components_can_differ"] is True


def test_common_frame_closes_vertical_ambiguity_but_incidence_not_base_jet() -> None:
    witness = local_one_jet_nonuniqueness_witness()
    assert witness["same_pointwise_gauge_lift"] is True
    assert witness["same_bundle_isomorphism_class"] is True
    assert witness["distinct_children_without_AE2_common_frame_selection"] is True
    assert witness["AE2_common_frame_removes_vertical_ambiguity"] is True
    assert witness["same_base_incidence_point"] is True
    assert witness["distinct_children_from_missing_base_tangent"] is True


def test_reference_identity_recovers_zero_but_does_not_select_nonzero_map() -> None:
    checks = conditional_geometry_checks()
    assert checks["connection_pullback_residual"] < 1.0e-12
    assert checks["nonzero_trace_transported"] is True
    assert checks["affine_term_nonzero"] is True
    assert checks["reference_identity_zero_field_recovery_residual"] == 0.0
    assert checks["not_an_admissible_BHSM_background_evaluation"] is True


def test_weighted_cotangent_rule_preserves_the_exact_pairing() -> None:
    derivative = np.asarray(((2.0, 0.0), (0.0, 0.5)), dtype=complex)
    event_weight = np.diag((3.0, 5.0)).astype(complex)
    child_weight = np.diag((7.0, 11.0)).astype(complex)
    event_momentum = np.asarray((1.0 + 2.0j, -0.5j))
    variation = np.asarray((0.25 - 0.1j, 2.0j))
    child_momentum = weighted_cotangent_momentum_map(
        event_momentum, derivative, event_weight, child_weight
    )
    event_pairing = np.vdot(event_momentum, event_weight @ variation)
    child_pairing = np.vdot(
        child_momentum, child_weight @ (derivative @ variation)
    )
    assert abs(event_pairing - child_pairing) < 1.0e-12


def test_downstream_chain_fails_closed_at_the_local_one_jet() -> None:
    result = downstream_status()
    assert result["R_A"] is None
    assert result["D_R_A_at_zero"] is None
    assert result["D_R_A_at_two_admissible_backgrounds"] is None
    assert result["Maxwell_conormal_cotangent_lift"] is None
    assert result["gauge_symplectic_reset"] is None
    assert result["S_RESET_GFHS"] is None
    assert result["D3_Theta"] is None
    assert result["HS_normal_Legendre_rank"] == 0
    assert result["pi_H"] == 0.0
    assert result["blocked_by"] == EXACT_MISSING_DATUM


def test_every_requested_object_has_a_separate_authority_status() -> None:
    result = requested_object_classification()
    assert set(result) == {
        "F_B",
        "F_B_equivalence_class",
        "D_F_B",
        "U_R",
        "d_U_R",
        "R_A",
        "cotangent_lift",
        "symplectic_reset",
        "S_RESET_GFHS",
        "graph_jets",
        "global_S1_S4",
    }
    assert "REPRESENTATIVE_ABSENT" in result["F_B"]
    assert result["F_B_equivalence_class"].startswith("NOT_DEFINED")
    assert "ABSENT" in result["D_F_B"]
    assert "GAUGE_FACTOR_IS_I" in result["U_R"]
    assert "dG_R_EQUALS_ZERO" in result["d_U_R"]
    assert result["R_A"].startswith("CONDITIONAL_FOR_A_REPRESENTATIVE")


def test_claim_boundary_preserves_physical_and_gate7_flags() -> None:
    claims = claim_boundary()
    assert claims["status"] == STATUS
    assert claims["bundle_isomorphism_class_exists"] is True
    assert claims["abstract_AE2_equivariant_boundary_lift_exists"] is True
    assert claims["common_reset_frame_gauge_vertical_one_jet_derived"] is True
    assert claims["common_reset_frame_G_R_is_identity"] is True
    assert claims["common_reset_frame_dG_R_is_zero"] is True
    assert claims["action_owned_local_spatial_base_map_F_B_exists"] is False
    assert claims["levelwise_diffeomorphism_covariance_exists"] is True
    assert claims["cross_level_diffeomorphism_intertwiner_proved"] is False
    assert claims["action_owned_relative_event_child_diffeomorphism_group_exists"] is False
    assert claims["attachment_representative_independence_proved"] is False
    assert claims["attachment_representative_dependence_proved"] is False
    assert claims["identity_representative_is_admissible_gauge_fixing"] is False
    assert claims["evaluable_principal_bundle_lift_local_one_jet_exists"] is False
    assert claims["connection_transport_derived"] is False
    assert claims["constant_v15_57_reused"] is False
    assert claims["family_spectrum_rebuilt"] is False
    assert claims["empirical_coefficients_used"] is False
    assert claims["FULL_FIELD_ACTION_ATTACHMENT_READY_FOR_GATE7_BACKGROUND"] is False
    assert claims["FULL_BHSM_COMPLETE"] is False
    assert claims["exact_missing_datum"] == EXACT_ATTACHMENT_QUOTIENT_DATUM


def test_maximal_proved_group_is_not_silently_enlarged_to_full_diff() -> None:
    group = attachment_symmetry_group()
    assert group["levelwise_action_covariance"]["S8"] == "YES"
    assert group["levelwise_action_covariance"]["S5_relative"] == (
        "YES_BEFORE_ADM_GAUGE_FIX"
    )
    assert group["levelwise_action_covariance"]["S4_effective"] == "YES"
    assert group["levelwise_action_covariance"]["cross_level"] == "UNPROVED"
    assert group["full_Diff_Sigma_admissible"] is False
    assert group["proved_nontrivial_relative_attachment_group"] is None
    assert group["candidate_Ad_family_is_action_owned_relative_gauge"] is False
    assert group["blocked_by"] == EXACT_ATTACHMENT_QUOTIENT_DATUM


def test_id_and_Ad_witness_preserve_tensorial_action_objects() -> None:
    witness = attachment_representative_naturality_witness()
    assert witness["representatives"] == ["F_0=id_times_id", "F_a=Ad_a_times_id"]
    assert witness["metric_invariance_residual"] < 1.0e-12
    assert witness["measure_jacobian_residual"] < 1.0e-12
    assert witness["orientation_preserved"] is True
    assert witness["connection_pullback_residual"] < 1.0e-12
    assert witness["curvature_pullback_residual"] < 1.0e-12
    assert witness["Maxwell_quadratic_residual"] < 1.0e-12
    assert witness["Maxwell_canonical_alpha_residual"] < 1.0e-12
    assert witness["Maxwell_canonical_omega_residual"] < 1.0e-12
    assert witness["combined_tensorial_GFHS_value_residual"] < 1.0e-12


def test_fermion_brst_hs_and_frozen_fibers_are_natural_in_witness() -> None:
    witness = attachment_representative_naturality_witness()
    assert witness["fermion_Dirac_unitary_residual"] < 1.0e-12
    assert witness["fermion_Dirac_eigenvalue_residual"] < 1.0e-12
    assert witness["fermion_Dirac_singular_value_residual"] < 1.0e-12
    assert witness["spatial_spin_lift_commutes_with_U_R_tensor_I3_residual"] < 1.0e-12
    assert max(witness["BRST_nilpotency_residuals"]) < 1.0e-12
    assert witness["BRST_rank_invariant"] is True
    assert witness["ghost_bilinear_residual"] < 1.0e-12
    assert witness["HS_algebraic_value_residual"] == 0.0
    assert witness["representation_projector_ranks_unchanged"] is True


def test_levelwise_gfhs_naturality_does_not_claim_reset_naturality() -> None:
    result = gfhs_naturality()
    for sector in ("Maxwell", "ghost", "fermion", "HS", "gauge_fermion", "fermion_HS"):
        assert result[sector]["current_C2_relative_reset_test"] == "NOT_EVALUABLE"
    combined = result["combined_germ"]
    assert combined["formal_levelwise_identity"].startswith("Gamma_GFHS")
    assert combined["full_BHSM_reset_natural"] is None


def test_canonical_form_requires_moment_map_reduction_not_naive_quotient() -> None:
    result = canonical_attachment_quotient()
    assert result["alpha_invariant_under_cotangent_lift"] is True
    assert result["alpha_horizontal_on_full_phase_space"] is False
    assert result["alpha_basic_on_full_phase_space"] is False
    assert result["omega_invariant_under_cotangent_lift"] is True
    assert result["constraints_descend"] is None
    assert result["quotient_phase_space"] is None
    assert result["reduced_reset_canonical"] is None
    assert result["blocked_by"] == EXACT_ATTACHMENT_QUOTIENT_DATUM


def test_no_physical_outcome_or_identity_gauge_is_overclaimed() -> None:
    result = attachment_equivalence_adjudication()
    assert result["outcome_A_pure_redundancy"]["proved"] is False
    assert result["outcome_B_partial_redundancy"]["proved"] is False
    assert result["outcome_C_physical_nonuniqueness"]["proved"] is False
    assert result["formal_id_Ad_witness_equivalent_after_simultaneous_pullback"] is True
    assert result["formal_witness_sufficient_to_close_physical_equivalence"] is False
    assert result["representative_independence"] is None
    assert result["identity_representative_allowed"] is False
    assert result["residual_physical_attachment_datum"] is None
    assert result["full_field_reset_can_proceed_without_new_physical_law"] is False
    assert result["exact_next_object"] == EXACT_ATTACHMENT_QUOTIENT_DATUM


def test_materialized_hindsight_payload_is_deterministic() -> None:
    module = _materializer()
    first = module.build_payload()
    second = module.build_payload()
    assert first["VALIDATED"]
    assert first["INVALIDATED"]
    assert first["OPEN"] == [EXACT_ATTACHMENT_QUOTIENT_DATUM]
    assert first["EXACT_NEXT_OBJECT"] == EXACT_ATTACHMENT_QUOTIENT_DATUM
    assert {
        "attachment_symmetry_group",
        "allowed_representatives",
        "nonuniqueness_witness",
        "GFHS_naturality",
        "Maxwell_naturality",
        "fermion_naturality",
        "BRST_naturality",
        "canonical_form_naturality",
        "physical_observable_invariance",
        "quotient_phase_space",
        "representative_independence",
        "identity_representative_allowed",
        "residual_physical_attachment_datum",
        "reset_generator_status",
        "graph_jet_status",
        "global_S1_S4_status",
        "validated",
        "invalidated",
        "open",
        "exact_next_object",
    }.issubset(first)
    assert first["one_jet_component_split"]["B_vertical_gauge_lift"]["status"] == "CLOSED"
    assert first["child_ontology"].startswith("CASE_4")
    assert first["Sigma_event_definition"]
    assert first["Sigma_child_definition"] == "Sigma_c=S3_times_S3"
    assert first["event_embedding"] is None
    assert first["child_embedding"] is None
    assert first["flow_if_any"]["spatial_event_child_flow"] is None
    assert first["F_B"] is None
    assert first["D_F_B"] is None
    assert first["connection_reset"] is None
    assert first["Maxwell_cotangent_lift"] is None
    assert first["global_S1"] == "REFERENCE_SLICE_ONLY"
    assert first["global_S4"] == "BLOCKED"
    assert first["attachment_symmetry_group"]["full_Diff_Sigma_admissible"] is False
    assert first["representative_independence"] is None
    assert first["identity_representative_allowed"] is False
    assert first["residual_physical_attachment_datum"] is None
    assert first["quotient_phase_space"]["quotient_phase_space"] is None
    assert first["validated"] == first["VALIDATED"]
    assert first["invalidated"] == first["INVALIDATED"]
    assert first["open"] == first["OPEN"]
    assert first["ownership_levels"]["induced_connection_transport"]["status"] == (
        "CONDITIONAL_FORMULA_ONLY_NOT_ACTION_OWNED_EVALUABLE_MAP"
    )
    assert first["validation_passed"] is True
    assert module.deterministic_json(first) == module.deterministic_json(second)


def test_materializer_is_byte_identical() -> None:
    module = _materializer()
    path = module.main()
    first = path.read_bytes()
    module.main()
    assert path.read_bytes() == first
    assert json.loads(first)["validation_passed"] is True
