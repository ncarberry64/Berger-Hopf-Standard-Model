from __future__ import annotations

import json

import numpy as np
import pytest

from bhsm.interface.reset_boundary_generating_functional_adjudication import (
    EXACT_MISSING_DATUM,
    STATUS,
    actual_reset_map_ledger,
    boundary_phase_space_contract,
    brst_reset_compatibility,
    canonical_one_form_matrix,
    canonical_one_form_pullback_residual,
    canonical_symplectic_matrix,
    canonicality_adjudication,
    child_inheritance_status,
    claim_boundary,
    event_balance_status,
    exactness_adjudication,
    graph_and_global_derivative_status,
    hs_reset_adjudication,
    reference_canonicality_witness,
    source_search_ledger,
    symplectic_pullback_residual,
    unitary_cotangent_lift,
)
from scripts.materialize_reset_boundary_generating_functional_adjudication import (
    TARGET,
    build_payload,
    deterministic_json,
    main,
)


def test_canonical_boundary_pair_and_one_form_have_full_rank():
    alpha = canonical_one_form_matrix(3)
    omega = canonical_symplectic_matrix(3)
    assert alpha.shape == (6, 6)
    assert omega.shape == (6, 6)
    assert np.linalg.matrix_rank(omega) == 6
    assert np.linalg.norm(omega + omega.conj().T) == 0.0


def test_boundary_phase_space_reduces_null_and_brst_directions():
    phase = boundary_phase_space_contract()
    assert phase["gauge"]["finite_witness_rank"] == 4
    assert phase["fermion"]["finite_witness_rank"] == 2
    assert phase["HS"]["finite_witness_rank"] == 0
    assert not phase["HS"]["forced_canonical_partner_added"]
    assert phase["ghost_antighost"]["independent_reset_coefficient"] is False
    assert phase["reduced_phase_space"]["algebraic_trace_outside_symplectic_quotient"] == "HS"


def test_unitary_trace_map_has_exact_symplectic_cotangent_lift():
    root = 1.0 / np.sqrt(2.0)
    unitary = root * np.asarray(((1.0, 1.0j), (1.0j, 1.0)))
    reset = unitary_cotangent_lift(unitary)
    omega = canonical_symplectic_matrix(2)
    alpha = canonical_one_form_matrix(2)
    assert symplectic_pullback_residual(reset, omega) < 1.0e-12
    assert canonical_one_form_pullback_residual(reset, alpha) < 1.0e-12
    with pytest.raises(ValueError, match="unitary"):
        unitary_cotangent_lift(np.asarray(((1.0, 1.0), (0.0, 1.0))))


def test_existing_source_search_finds_no_nonzero_connection_trace_map():
    rows = source_search_ledger()
    assert len(rows) == 9
    assert not any(row.get("nonzero_gauge_connection_trace_map", False) for row in rows)
    constant = next(row for row in rows if "V15_57" in row["source"])
    zero = next(row for row in rows if "V17_97" in row["source"])
    bundle = next(row for row in rows if "V15_53" in row["source"])
    n12 = next(row for row in rows if "N12_FULL_RESET" in row["source"])
    assert not constant["usable"]
    assert "D_R=0" in constant["reason"]
    assert not zero["evidence"]
    assert bundle["evidence"] is False
    assert "NO_GFHS" in n12["reason"]


def test_actual_reset_map_ledger_stops_at_first_gauge_component():
    result = actual_reset_map_ledger()
    assert result["geometry_background"]["status"] == "DEFINED"
    assert result["gauge"]["status"] == "MISSING"
    assert result["ghost"]["status"] == "BRST_INDUCED"
    assert result["antighost"]["status"] == "ADJOINT_INDUCED"
    assert result["fermion"]["status"] == "DEFINED"
    assert result["HS"]["status"] == "STRUCTURAL_ZERO"
    assert not result["complete_on_reduced_GFHS_boundary_phase_space"]
    assert result["first_missing_component"] == EXACT_MISSING_DATUM


def test_reference_maps_are_exact_but_constant_reconstruction_is_not_symplectic():
    result = reference_canonicality_witness()
    assert result["zero_field_gauge_identity"]["symplectic_residual"] == 0.0
    assert result["zero_field_gauge_identity"]["canonical_one_form_residual"] == 0.0
    assert result["AE2_fermion_cotangent_lift"]["symplectic_residual"] == 0.0
    constant = result["v15_57_constant_reconstruction"]
    assert constant["symplectic_residual"] == constant["expected_residual"]
    assert constant["symplectic_residual"] > 0.0
    assert not constant["may_be_used_as_nonzero_GFHS_reset"]


def test_full_canonicality_is_incomplete_not_falsely_non_symplectic():
    result = canonicality_adjudication()
    assert result["classification"] == STATUS
    assert result["Delta_omega_full"] is None
    assert not result["full_canonicality_testable"]
    assert result["reset_is_incompletely_defined"]
    assert not result["reset_is_exact_symplectic"]
    assert not result["reset_is_symplectic_but_nonexact"]
    assert not result["reset_is_proven_nonsymplectic"]
    assert result["first_undefined_map_component"] == EXACT_MISSING_DATUM


def test_exactness_stops_before_closedness_and_cohomology():
    result = exactness_adjudication()
    assert result["beta_zero_field_gauge"] == 0.0
    assert result["S_RESET_GFHS_zero_field_normalization"] == 0.0
    assert result["beta_nonzero_GFHS"] is None
    assert result["d_beta_nonzero_GFHS"] is None
    assert result["cohomology_class_nonzero_GFHS"] is None
    assert not result["domain_simple_connectivity_assumed"]
    assert not result["S_RESET_GFHS_derived"]


def test_brst_maps_are_induced_but_uninstantiable_without_gauge_map():
    result = brst_reset_compatibility()
    assert result["reference_common_frame_BRST_intertwining_residual"] == 0.0
    assert not result["independent_ghost_coefficient_added"]
    assert not result["independent_antighost_coefficient_added"]
    assert not result["nonzero_BRST_reset_instantiable"]
    assert result["blocked_by"] == EXACT_MISSING_DATUM


def test_hs_nullity_does_not_manufacture_or_select_boundary_dynamics():
    result = hs_reset_adjudication()
    assert result["normal_Legendre_rank"] == 0
    assert result["pi_H"] == 0.0
    assert not result["independent_HS_symplectic_coordinate"]
    assert not result["bare_HS_boundary_kinetic_term_added"]
    assert result["independent_HS_term_in_S_RESET_GFHS"] == 0.0
    assert result["mixed_HS_dependence_of_S_RESET_GFHS"] is None
    assert not result["HS_graph_derivatives_may_be_declared_structural_zero"]


def test_graph_equations_jets_and_global_s1_s4_fail_closed():
    result = graph_and_global_derivative_status()
    assert result["generating_equations"] is None
    assert result["Theta_GFHS"] is None
    assert result["D_Theta_at_zero"] is None
    assert result["D2_Theta_at_zero"] is None
    assert result["D3_Theta_at_zero"] is None
    assert not result["old_Theta0_Theta1_witnesses_uniquely_discriminated"]
    assert result["S1_global"] == "REFERENCE_SLICE_ONLY"
    assert result["S2_global"] == "BLOCKED"
    assert result["S3_global"] == "BLOCKED"
    assert result["S4_global"] == "BLOCKED"
    assert not result["reset_derivatives_added_without_generator"]


def test_event_balance_exposes_the_unavailable_canonical_reset_term():
    result = event_balance_status()
    assert result["bulk"] == 0.0
    assert result["history_seam"] == 0.0
    assert result["canonical_reset"] is None
    assert result["event_child"] is None
    assert result["constraint_BRST"] is None
    assert result["total"] is None
    assert not result["global_residual_evaluable"]
    assert result["nonclosing_contribution"] == EXACT_MISSING_DATUM
    assert not result["empirical_repair_added"]


def test_child_inheritance_reuses_fermions_without_full_promotion():
    result = child_inheritance_status()
    assert result["geometry"] == "DEFINED"
    assert result["fermion"] == "DEFINED_AE2_U_R_TENSOR_I3"
    assert result["gauge"] == "MISSING_NONZERO_TRACE_MAP"
    assert not result["nine_frozen_family_mode_fibers_rebuilt"]
    assert not result["full_field_child_inheritance_promoted"]


def test_claim_boundary_names_one_datum_and_preserves_gate7_flags():
    claims = claim_boundary()
    assert claims["reset_classification"] == "INCOMPLETELY_DEFINED"
    assert claims["reference_gauge_and_fermion_maps_exact_symplectic"]
    assert not claims["full_GFHS_reset_symplecticity_proved"]
    assert not claims["full_GFHS_reset_nonsymplecticity_proved"]
    assert not claims["S_RESET_GFHS_derived"]
    assert claims["exact_missing_datum"] == EXACT_MISSING_DATUM
    assert not claims["BACKGROUND_COVARIANT_STRATIFIED_GFHS_OPERATOR_FAMILY_DERIVED"]
    assert not claims["FULL_FIELD_ACTION_ATTACHMENT_READY_FOR_GATE7_BACKGROUND"]
    assert not claims["physical_background_bound"]
    assert not claims["physical_HS_direction_derived"]
    assert not claims["physical_yukawas_derived"]
    assert not claims["physical_spectrum_derived"]
    assert not claims["FULL_BHSM_COMPLETE"]
    assert not claims["empirical_inputs_used"]


def test_authority_payload_is_complete_deterministic_and_has_one_open_object():
    payload = build_payload()
    assert payload["reset_classification"] == "INCOMPLETELY_DEFINED"
    assert payload["OPEN"] == [EXACT_MISSING_DATUM]
    assert payload["EXACT_NEXT_OBJECT"] == EXACT_MISSING_DATUM
    assert not payload["S_RESET_GFHS"]["derived"]
    assert payload["empirical_inputs"] == []
    assert payload["validation_passed"]
    assert deterministic_json(payload) == deterministic_json(build_payload())


def test_materialized_authority_is_byte_identical():
    path = main()
    assert path == TARGET
    first = path.read_bytes()
    main()
    assert path.read_bytes() == first
    assert json.loads(first)["validation_passed"]
