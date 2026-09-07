from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pytest

from bhsm.interface.nonfermion_relative_boundary_variation import (
    EXACT_MISSING_DATUM,
    ae4_reset_gluing_status,
    brst_graph_compatibility_witness,
    canonical_boundary_variables,
    cayley_lift,
    claim_boundary,
    event_balance_decomposition,
    full_field_child_inheritance_status,
    gauge_green_form,
    ghost_green_form,
    higher_graph_jet_dependency,
    hs_boundary_variation_witness,
    hs_green_form,
    moving_domain_hessian_witness,
    radial_maxwell_green_identity_witness,
    relative_first_variation_residual,
    two_background_boundary_witness,
    variational_selection_witness,
)
from scripts.materialize_nonfermion_relative_boundary_variation import (
    TARGET,
    build_payload,
    deterministic_json,
    main,
)


def test_retained_radial_maxwell_action_satisfies_green_identity():
    result = radial_maxwell_green_identity_witness()
    assert result["radial_form_assembled_before_DtN_elimination"]
    assert result["green_identity_residual"] < 1.0e-12
    assert not result["stored_response_table_used"]


def test_gauge_green_form_is_anti_hermitian_under_argument_exchange():
    q = np.asarray((1.0 + 0.2j, -0.3))
    p = np.asarray((0.4, 0.1 - 0.5j))
    r = np.asarray((-0.2j, 0.7))
    s = np.asarray((0.6, -0.1 + 0.3j))
    forward = gauge_green_form(q, p, r, s)
    reverse = gauge_green_form(r, s, q, p)
    assert forward == pytest.approx(-reverse.conjugate())


def test_fp_cross_green_form_and_adjoint_graph_cancel():
    qbar = np.asarray((0.3 + 0.1j, -0.2))
    q = np.asarray((0.5, 0.4 - 0.2j))
    theta = np.asarray(((0.7, 0.2j), (-0.2j, 0.4)))
    assert ghost_green_form(qbar, theta.conj().T @ qbar, q, theta @ q) == pytest.approx(0.0)


def test_hs_source_has_no_normal_momentum_or_green_form():
    variables = canonical_boundary_variables()["HS"]
    result = hs_boundary_variation_witness()
    assert not variables["HS_derivative_kinetic_term_present"]
    assert not variables["composite_derivative_kinetic_term_present"]
    assert result["normal_Legendre_rank"] == 0
    assert result["boundary_green_form_value"] == 0.0
    assert hs_green_form(np.ones(4), np.arange(4)) == 0.0
    assert not result["heat_derived_HS_kinetic_response_used_as_action"]
    assert not result["physical_HS_direction_derived"]


def test_cayley_lift_is_unitary_only_for_hermitian_graph_coordinate():
    theta = np.asarray(((0.2, 0.1j), (-0.1j, -0.3)))
    lift = cayley_lift(theta)
    assert np.linalg.norm(lift.conj().T @ lift - np.eye(2)) < 1.0e-12
    with pytest.raises(ValueError, match="Hermitian"):
        cayley_lift(np.asarray(((0.0, 1.0), (0.0, 0.0))))


def test_two_sided_first_variation_cancels_for_a_supplied_graph():
    q = np.asarray((0.2, -0.1, 0.5, 0.3))
    p = np.asarray((0.4, 0.2, -0.3, 0.1))
    dq = np.asarray((-0.2, 0.6, 0.1, -0.4))
    projector = np.diag((1.0, 1.0, 0.0, 0.0))
    assert relative_first_variation_residual(q, p, dq, 0.4 * projector) < 1.0e-12


def test_variation_does_not_reject_either_nonuniqueness_witness():
    result = variational_selection_witness()
    assert result["same_zero_field_graph"]
    assert result["different_first_field_jets"]
    assert result["all_fixed_field_vertical_variations_cancel"]
    assert result["both_graphs_maximal_isotropic"]
    assert result["hypothetical_completions_differ"]
    assert not result["retained_bulk_variation_selects_unique_jet"]
    assert not result["competing_nonuniqueness_witness_rejected"]
    assert result["exact_missing_variational_datum"] == EXACT_MISSING_DATUM
    for row in result["candidate_results"]:
        assert row["Hermiticity_residual"] < 1.0e-12
        assert row["gauge_centrality_residual"] < 1.0e-12
        assert row["projector_preservation_residual"] < 1.0e-12


def test_brst_relates_gauge_ghost_antighost_jets_but_selects_no_value():
    result = brst_graph_compatibility_witness()
    assert result["both_nonuniqueness_witnesses_BRST_compatible"]
    assert not result["independent_antighost_jet_required"]
    assert not result["BRST_selects_common_jet_value"]
    assert not result["spurious_physical_gauge_mode_introduced"]


def test_moving_domain_hessian_confirms_rather_than_resolves_nonuniqueness():
    result = moving_domain_hessian_witness()
    assert result["both_moving_domain_Hessians_internally_consistent"]
    assert result["Hessians_distinct"]
    assert not result["retained_action_contains_either_hypothetical_completion"]
    assert not result["second_variation_selects_unique_jet"]
    assert result["geometry_nonfermion_boundary_mixed_block"] is None
    assert result["nonfermion_nonfermion_boundary_mixed_block"] is None


def test_two_background_bulk_dependence_does_not_select_graph():
    result = two_background_boundary_witness()
    assert result["bulk_background_dependence_nontrivial"]
    assert result["both_graph_candidates_admissible_at_both_backgrounds"]
    assert not result["background_dependence_selects_graph_jet"]


def test_higher_graph_jets_are_required_for_global_s3_and_s4():
    result = higher_graph_jet_dependency()
    assert result["S1_global"]["available"]
    assert not result["S2_global"]["available"]
    assert not result["S3_global"]["available"]
    assert not result["S4_global"]["available"]
    assert "SQUARED" in result["S3_global"]["required_graph_data"]
    assert "CUBED" in result["S4_global"]["required_graph_data"]
    assert not result["first_jet_alone_completes_global_S1_through_S4"]
    assert not result["affine_graph_truncation_action_derived"]


def test_ae4_gluing_and_child_inheritance_fail_closed_without_rebuilding():
    gluing = ae4_reset_gluing_status()
    inheritance = full_field_child_inheritance_status()
    assert gluing["zero_field_trace_match_reused"]
    assert not gluing["fermion_AE2_transport_changed"]
    assert not gluing["nine_frozen_family_mode_fibers_rebuilt"]
    assert not gluing["nonfermion_first_order_reset_gluing"]
    assert inheritance["fermion_child_relation_reused"]
    assert inheritance["family_projectors_reused"]
    assert not inheritance["nonzero_first_order_nonfermion_inheritance_unique"]


def test_event_balance_is_decomposed_without_empirical_repair():
    result = event_balance_decomposition()
    assert result["bulk"]["residual"] == 0.0
    assert result["history_seam"]["residual"] == 0.0
    assert result["boundary_reset"]["residual"] is None
    assert result["event_child"]["residual"] is None
    assert result["total"] is None
    assert not result["physical_event_balance_evaluable"]
    assert not result["empirical_counterterm_inserted"]
    assert result["exact_owning_term"] == EXACT_MISSING_DATUM


def test_claim_boundary_preserves_all_pre_gate7_false_flags():
    claims = claim_boundary()
    assert not claims["retained_bulk_variation_uniquely_determines_D_PhiSM_Theta"]
    assert claims["gauge_boundary_green_form_derived"]
    assert claims["ghost_boundary_green_form_derived"]
    assert claims["HS_boundary_green_form_identically_zero"]
    assert not claims["global_stratified_GFHS_operator_family_derived"]
    assert not claims["FULL_FIELD_ACTION_ATTACHMENT_READY_FOR_GATE7_BACKGROUND"]
    assert not claims["physical_background_bound"]
    assert not claims["physical_HS_direction_derived"]
    assert not claims["physical_yukawas_derived"]
    assert not claims["physical_spectrum_derived"]
    assert not claims["FULL_BHSM_COMPLETE"]
    assert not claims["empirical_inputs_used"]


def test_authority_payload_has_required_fields_and_one_exact_open_datum():
    payload = build_payload()
    required = {
        "Theta_GFHS_zero_field",
        "D_Phi_Theta_GFHS_at_zero",
        "jet_source",
        "boundary_green_form",
        "variational_selection",
        "brst_compatibility",
        "ae4_reset_gluing",
        "child_inheritance",
        "event_balance",
        "higher_graph_jets_required",
        "S1_global",
        "S2_global",
        "S3_global",
        "S4_global",
        "empirical_inputs",
        "validated",
        "invalidated",
        "open",
        "exact_next_calculation",
    }
    assert required <= payload.keys()
    assert payload["open"] == [EXACT_MISSING_DATUM]
    assert payload["validation_passed"]
    assert payload["empirical_inputs"] == []
    assert not payload["FULL_BHSM_COMPLETE"]
    assert deterministic_json(payload) == deterministic_json(build_payload())


def test_materialized_authority_is_byte_identical():
    path = main()
    assert path == TARGET
    first = path.read_bytes()
    main()
    assert path.read_bytes() == first
    assert json.loads(first)["validation_passed"]
