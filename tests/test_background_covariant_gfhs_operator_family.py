from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pytest

from bhsm.interface.background_covariant_gfhs_operator_family import (
    ACTION_VERSION,
    EXACT_BLOCKER,
    FERMION_DIMENSION,
    GAUGE_DIMENSION,
    GermDirection,
    HS_DIMENSION,
    LocalC2Background,
    SourceClass,
    ae2_to_ae4_transport_diagram,
    background_mixed_derivative_witness,
    child_inheritance_status,
    claim_boundary,
    critical_reductions,
    event_balance_residual,
    full_representation_generators,
    generated_local_c2_action,
    graded_directional_jet,
    hs_incidence_generators,
    local_gfhs_attachment,
    radial_maxwell_boundary_coefficient,
    relative_boundary_graph_nonuniqueness_witness,
    representation_validation,
    source_reconstruction,
    stratified_action_composition,
)
from bhsm.interface.full_field_action_attachment_pre_g7 import (
    BlockStatus,
    FullFieldBackgroundBinder,
    MissingActionSourceError,
    authoritative_field_registry,
)
from scripts.materialize_background_covariant_gfhs_operator_family import (
    TARGET,
    build_payload,
    deterministic_json,
    main,
)


def _basis(size: int, index: int) -> np.ndarray:
    result = np.zeros(size)
    result[index] = 1.0
    return result


def _background() -> LocalC2Background:
    return LocalC2Background(log_radius=0.07, sigma=0.11, omega=0.06)


def test_source_reconstruction_never_promotes_response_to_action():
    rows = source_reconstruction()
    assert {row.classification for row in rows} == set(SourceClass)
    assert not any(
        row.used_in_local_germ and row.classification is SourceClass.DERIVED_RESPONSE
        for row in rows
    )
    open_rows = [row for row in rows if row.classification is SourceClass.OPEN_SOURCE]
    assert len(open_rows) == 1
    assert "relative_boundary_graph" in open_rows[0].object_id


def test_exact_rank16_representation_and_family_lift():
    generators = full_representation_generators()
    assert generators.shape == (12, 48, 48)
    result = representation_validation()
    assert result["all_generators_Hermitian_residual"] < 1.0e-13
    assert result["SU2_commutator_residual"] < 1.0e-13
    assert result["SU3_commutator_residual"] < 1.0e-13
    assert result["family_projector_commutator_residual"] == 0.0
    assert max(result["HS_incidence_hypercharge_covariance_residuals"]) == 0.0
    assert not result["physical_gauge_couplings_inserted"]


def test_hs_incidence_has_all_four_channels_and_no_family_mixing():
    incidence = hs_incidence_generators()
    assert incidence.shape == (4, 48, 48)
    assert [np.linalg.matrix_rank(row) for row in incidence] == [18, 18, 6, 6]
    for row in incidence:
        assert np.allclose(row, row.T)
        assert np.count_nonzero(row[:16, 16:]) == 0


def test_regular_background_validation():
    with pytest.raises(ValueError, match="regular C2 interior"):
        LocalC2Background(0.0, 0.5)
    with pytest.raises(ValueError, match="finite"):
        LocalC2Background(float("nan"), 0.0)
    with pytest.raises(ValueError, match="dimensions 12 and 4"):
        _background().bosonic_state(gauge=np.zeros(11))


def test_radial_maxwell_coefficient_is_generated_and_background_dependent():
    first = float(radial_maxwell_boundary_coefficient(0.0, 0.03))
    second = float(radial_maxwell_boundary_coefficient(0.2, 0.03))
    assert np.isfinite(first) and np.isfinite(second)
    assert first > 0.0 and second > 0.0
    assert first != second


def test_generated_action_has_even_ghost_and_fermion_outputs():
    gauge = np.linspace(-0.04, 0.06, GAUGE_DIMENSION)
    hs = np.asarray((0.03, -0.02, 0.01, 0.04))
    result = generated_local_c2_action(_background(), gauge, hs)
    assert result.even_value > 0.0
    assert result.ghost_operator.shape == (12, 12)
    assert result.fermion_operator.shape == (48, 48)
    assert np.all(np.isfinite(result.ghost_operator))
    assert np.allclose(result.fermion_operator, result.fermion_operator.conj().T)


def test_zero_reference_and_critical_reductions():
    reductions = critical_reductions()
    assert reductions["zero_SM_even_action"] == 0.0
    assert reductions["gauge_only_generated_from_radial_Maxwell_form"]
    assert reductions["fermion_only_matches_internal_Dirac_levels"]
    assert reductions["frozen_family_mode_levels_inserted_as_free_masses"] is False
    assert reductions["HS_only_matches_local_EC_inverse_kernel"]
    assert reductions["fermion_HS_unit_LR_vertices_present"]
    assert not reductions["full_history_seam_reduction_available"]


def test_graded_fermion_second_derivative_has_ordered_left_sign():
    anti = GermDirection("antifermion", _basis(FERMION_DIMENSION, 0))
    fermion = GermDirection("fermion", _basis(FERMION_DIMENSION, 0))
    forward = graded_directional_jet(_background(), None, None, (anti, fermion))
    reverse = graded_directional_jet(_background(), None, None, (fermion, anti))
    assert forward == -reverse
    assert forward.real > 0.0


def test_graded_ghost_second_derivative_and_gauge_mixed_third_derivative():
    antighost = GermDirection("antighost", _basis(GAUGE_DIMENSION, 1))
    ghost = GermDirection("ghost", _basis(GAUGE_DIMENSION, 2))
    gauge = GermDirection("gauge", _basis(GAUGE_DIMENSION, 3))
    second = graded_directional_jet(_background(), None, None, (antighost, ghost))
    reverse = graded_directional_jet(_background(), None, None, (ghost, antighost))
    third = graded_directional_jet(
        _background(), None, None, (gauge, antighost, ghost)
    )
    assert second == -reverse
    assert np.isfinite(third)


def test_gauge_fermion_and_hs_fermion_vertices_come_from_same_operator():
    anti = GermDirection("antifermion", _basis(FERMION_DIMENSION, 0))
    fermion = GermDirection("fermion", _basis(FERMION_DIMENSION, 0))
    hypercharge = GermDirection("gauge", _basis(GAUGE_DIMENSION, 0))
    assert graded_directional_jet(
        _background(), None, None, (hypercharge, anti, fermion)
    ) == pytest.approx(1.0 / 6.0)

    anti_q = GermDirection("antifermion", _basis(FERMION_DIMENSION, 0))
    fermion_u = GermDirection("fermion", _basis(FERMION_DIMENSION, 8))
    hs_up = GermDirection("HS", _basis(HS_DIMENSION, 0))
    assert graded_directional_jet(
        _background(), None, None, (hs_up, anti_q, fermion_u)
    ) == pytest.approx(1.0)


def test_matrix_free_fourth_derivative_exists_without_dense_tensor():
    gauge = np.linspace(0.01, 0.03, GAUGE_DIMENSION)
    direction = GermDirection("background", np.asarray((1.0, 0.0, 0.0)))
    value = graded_directional_jet(
        _background(), gauge, np.zeros(HS_DIMENSION), (direction,) * 4
    )
    assert np.isfinite(value)


def test_two_backgrounds_and_all_mixed_derivatives_match_direct_differences():
    result = background_mixed_derivative_witness()
    assert result["local_background_dependence_verified"]
    assert result["even_action_values"][0] != result["even_action_values"][1]
    assert result["ghost_operator_difference_norm"] > 0.0
    assert result["fermion_operator_difference_norm"] > 0.0
    assert result["D_geometry_D_gauge_Gamma"] != 0.0
    assert result["D_geometry_D_HS_Gamma"] != 0.0
    assert result["D_geometry_D_antifermion_D_fermion_Gamma"] != 0.0
    assert max(result["direct_difference_residuals"].values()) < 2.0e-8


def test_local_component_attaches_to_pr357_directional_api():
    registry = authoritative_field_registry()
    binding = FullFieldBackgroundBinder(ACTION_VERSION).bind_mathematical(
        np.asarray((_background().log_radius, _background().sigma, _background().omega)),
        background_id="regular-current-c2-germ",
        domain_id="regular-interior-no-global-graph",
        provenance=("local generating germ test",),
    )
    action = local_gfhs_attachment(binding, _background(), registry=registry)
    state = np.zeros(registry.dimension)
    state[registry.block("gauge").start] = 0.2
    assert action.value(state) > 0.0
    anti = registry.embed("antifermion", _basis(FERMION_DIMENSION, 0))
    fermion = registry.embed("fermion", _basis(FERMION_DIMENSION, 0))
    assert action.s2(state, anti, fermion) == -action.s2(state, fermion, anti)
    assert action.block_status[("gauge", "fermion")] is BlockStatus.ACTION_DERIVED
    assert action.block_status[("geometry", "gauge")] is BlockStatus.MISSING_ACTION_SOURCE


def test_local_attachment_rejects_geometry_and_numeric_odd_backgrounds():
    registry = authoritative_field_registry()
    binding = FullFieldBackgroundBinder(ACTION_VERSION).bind_mathematical(
        np.zeros(3),
        background_id="germ",
        domain_id="local",
        provenance=("test",),
    )
    action = local_gfhs_attachment(binding, _background(), registry=registry)
    state = np.zeros(registry.dimension)
    state[registry.block("geometry").start] = 0.1
    with pytest.raises(MissingActionSourceError):
        action.value(state)
    state[:] = 0.0
    state[registry.block("ghost").start] = 1.0
    with pytest.raises(ValueError, match="numeric odd backgrounds"):
        action.value(state)


def test_ae2_to_ae4_diagram_locates_first_noncommuting_term():
    diagram = ae2_to_ae4_transport_diagram()
    assert diagram["fermion_family_intertwining_residual"] == 0.0
    assert diagram["fermion_action_transport_commutes"]
    assert not diagram["nine_frozen_family_mode_fibers_rebuilt"]
    assert diagram["nonfermion_zero_field_match_available"]
    assert not diagram["nonfermion_first_field_jet_available"]
    assert "D_PhiSM_THETA_GFHS" in diagram["first_exact_noncommuting_term"]
    assert not diagram["AE2_to_AE4_compatible"]


def test_boundary_graph_nonuniqueness_is_exact_and_irreducible():
    witness = relative_boundary_graph_nonuniqueness_witness()
    assert witness["both_Hermitian"]
    assert witness["both_gauge_central_in_witness"]
    assert witness["both_projector_preserving"]
    assert witness["reference_graph_operator_difference_norm"] == 0.0
    assert witness["first_field_jet_difference_norm"] > 0.0
    assert witness["reference_actions"] == [0.0, 0.0]
    assert witness["same_zero_field_match"]
    assert witness["different_nonzero_field_actions"]
    assert witness["missing_source"] == EXACT_BLOCKER


def test_child_inheritance_reuses_fibers_but_fails_closed_on_domain():
    result = child_inheritance_status()
    assert result["fermion_family_intertwining_residual"] == 0.0
    assert result["projectors"] == "UNCHANGED_AND_INTERTWINED"
    assert not result["executable_full_field_inheritance_map"]
    assert "THETA_GFHS" in result["action_domain_metadata"]


def test_event_balance_separates_identity_from_physical_residual():
    result = event_balance_residual()
    assert result["algebraic_event_canonical_flux_balance_norm"] < 1.0e-12
    assert abs(result["algebraic_noether_flux_residual"]) < 1.0e-12
    assert result["physical_event_balance_residual"] is None
    assert not result["physical_residual_evaluable"]
    assert not result["physical_event_promotion"]


def test_stratified_composition_invents_no_seam_or_child_term():
    result = stratified_action_composition()
    assert set(result["strata"]) == {
        "bulk", "history", "seam", "junction", "event_child", "boundary"
    }
    assert "EXACTLY_ZERO" in result["strata"]["seam"]["status"]
    assert "EXACTLY_ZERO" in result["strata"]["junction"]["status"]
    assert not result["invented_seam_or_child_term"]


def test_claim_boundary_preserves_gate7_and_physical_flags():
    claims = claim_boundary()
    assert claims["local_current_C2_generating_germ_exists"]
    assert not claims["generating_family_exists"]
    assert not claims["arbitrary_global_BHSM_background_accepted"]
    assert not claims["physical_background_bound"]
    assert not claims["physical_HS_direction_derived"]
    assert not claims["physical_yukawas_derived"]
    assert not claims["physical_spectrum_derived"]
    assert not claims["FULL_FIELD_ACTION_ATTACHMENT_READY_FOR_GATE7_BACKGROUND"]
    assert not claims["FULL_BHSM_COMPLETE"]
    assert not claims["empirical_inputs_used"]
    assert claims["exact_blocker"] == EXACT_BLOCKER


def test_authority_artifact_is_valid_deterministic_and_names_one_blocker(tmp_path: Path):
    payload = build_payload()
    assert payload["validation_passed"]
    assert payload["open_blockers"] == [EXACT_BLOCKER]
    assert payload["Noether_Hamiltonian_balance_status"]["physical_event_balance_residual"] is None
    assert payload["empirical_inputs_used"] == []
    assert not payload["FULL_BHSM_COMPLETE"]
    first = deterministic_json(payload)
    second = deterministic_json(build_payload())
    assert first == second
    assert json.loads(first)["status"].startswith("GFHS_OPERATOR_FAMILY_PARTIALLY_DERIVED")


def test_materialized_authority_matches_builder():
    path = main()
    assert path == TARGET
    first = path.read_bytes()
    main()
    assert path.read_bytes() == first
    assert json.loads(first)["validation_passed"]
