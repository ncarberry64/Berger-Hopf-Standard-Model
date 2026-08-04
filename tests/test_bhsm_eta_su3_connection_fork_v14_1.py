from __future__ import annotations

import numpy as np

from bhsm.interface.completion.eta_boundary_dirac_contract_v14_1 import (
    boundary_dirac_contract_payload,
    flavor_independence_payload,
)
from bhsm.interface.completion.eta_color_bundle_matcher_audit_v14_1 import (
    BRANCH_DECISION,
    EXACT_NEXT_OBJECT,
    PROJECTION_PROVENANCE_VERDICT,
    bundle_isomorphism_payload,
    composite_variational_payload,
    matcher_payload,
    parent_architecture_recovery_payload,
    wall_extension_payload,
)
from bhsm.interface.completion.eta_knot_chiral_color_completion_v13_4 import (
    polarization_projectors,
)
from bhsm.interface.completion.eta_knot_projector_connection_v13_5 import (
    image_frame,
    projector_curvature,
    projector_derivative,
)
from bhsm.interface.completion.eta_projector_characteristic_classes_v14_1 import (
    characteristic_class_payload,
    pullback_chern_class,
)
from bhsm.interface.completion.eta_projector_dof_audit_v14_1 import (
    curvature_jacobian_rank,
    curvature_plane_span_rank,
    dof_payload,
    frame_covariance_witness,
    holonomy_algebra_dimension,
    projector_derivative_rank,
    random_unit,
)
from bhsm.interface.completion.eta_projector_principal_symbol_v14_1 import (
    composite_quadratic_symbol,
    independent_yang_mills_symbol,
    principal_symbol_payload,
)
from bhsm.interface.completion.eta_su3_connection_fork_v14_1 import (
    ARTIFACT_FILES,
    completion_payload,
    holonomy_payload,
    materialize,
    scientific_lineage_payload,
)


def test_projector_identities() -> None:
    unit = random_unit(1401)
    plus, minus, q = polarization_projectors(unit)
    assert np.allclose(plus @ plus, plus, atol=1.0e-12)
    assert np.allclose(minus @ minus, minus, atol=1.0e-12)
    assert np.allclose(plus @ minus, 0.0, atol=1.0e-12)
    assert np.allclose(plus + minus, q, atol=1.0e-12)


def test_projector_derivative_identity_and_rank() -> None:
    unit = random_unit(1402)
    tangent = np.eye(7)[0] - unit * unit[0]
    derivative = projector_derivative(unit, tangent)
    plus, _, _ = polarization_projectors(unit)
    assert np.allclose(derivative @ plus + plus @ derivative, derivative, atol=1.0e-12)
    assert projector_derivative_rank(unit) == 6


def test_curvature_is_restricted_anti_hermitian_and_traceless() -> None:
    unit = random_unit(1403)
    frame_tangent = np.linalg.qr(np.eye(7) - np.outer(unit, unit))[0]
    left, right = frame_tangent[:, 0], frame_tangent[:, 1]
    plus, _, _ = polarization_projectors(unit)
    frame = image_frame(plus)
    restricted = frame.conj().T @ projector_curvature(unit, left, right) @ frame
    assert np.allclose(restricted.conj().T, -restricted, atol=1.0e-12)
    assert abs(np.trace(restricted)) < 1.0e-12


def test_local_ranks_are_stable_under_random_frames() -> None:
    payload = dof_payload()
    assert payload["validation_passed"]
    assert payload["dP_rank_per_covector"] == [6, 6, 6, 6]
    assert payload["curvature_plane_span_rank"] == [8, 8, 8, 8]
    assert payload["generic_spacetime_curvature_Jacobian_rank_24_to_48"] == [23, 23, 23, 23]


def test_constant_selector_curvature_jacobian_rank_is_zero() -> None:
    unit = random_unit(1404)
    assert curvature_jacobian_rank(unit, np.zeros((4, 6))) == 0


def test_generic_curvature_does_not_span_arbitrary_spacetime_su3_curvature() -> None:
    unit = random_unit(1405)
    derivatives = np.random.default_rng(1406).normal(size=(4, 6))
    assert curvature_jacobian_rank(unit, derivatives) == 23
    assert 23 < 6 * 8


def test_frame_covariance_is_not_independent_gauge_field_space() -> None:
    payload = frame_covariance_witness()
    assert payload["validation_passed"]
    assert payload["validation"]["frame_change_does_not_change_projector_configuration"]
    assert payload["validation"]["frame_covariance_not_independent_connection_configuration_space"]


def test_composite_quadratic_symbol_vanishes_while_yang_mills_has_rank_24() -> None:
    momentum = np.array([1.0, -0.4, 0.7, 1.2])
    assert np.linalg.matrix_rank(composite_quadratic_symbol(momentum)) == 0
    assert np.linalg.matrix_rank(independent_yang_mills_symbol(momentum)) == 24
    assert principal_symbol_payload()["validation_passed"]


def test_characteristic_class_naturality_forces_c2_zero() -> None:
    payload = characteristic_class_payload()
    assert payload["validation_passed"]
    assert pullback_chern_class("0", 4) == "0"
    assert payload["M4_pullback_classes"]["c2"] == "0"
    assert payload["instanton_number_closed_M4"] == 0


def test_nonzero_local_curvature_does_not_imply_nonzero_instanton_sector() -> None:
    payload = characteristic_class_payload()
    assert payload["validation"]["local_curvature_need_not_vanish"]
    assert payload["verdict"] == "THE_ETA_PROJECTOR_CONNECTION_CANNOT_SPAN_GENERAL_NONZERO_INSTANTON_SU3_SECTORS"


def test_holonomy_closure_reaches_su3_but_is_not_equivalence() -> None:
    unit = random_unit(1407)
    assert curvature_plane_span_rank(unit) == 8
    assert holonomy_algebra_dimension(unit) == 8
    payload = holonomy_payload()
    assert payload["validation_passed"]
    assert payload["validation"]["full_holonomy_not_field_space_equivalence"]


def test_constant_selector_has_flat_spacetime_holonomy() -> None:
    payload = holonomy_payload()
    assert payload["constant_selector_dimension"] == 0


def test_orientation_reversal_conjugates_projectors_and_curvature() -> None:
    unit = np.eye(7)[6]
    left, right = np.eye(7)[0], np.eye(7)[1]
    plus, minus, _ = polarization_projectors(unit)
    reversed_plus, _, _ = polarization_projectors(-unit)
    forward = projector_curvature(unit, left, right)
    reversed_curvature = projector_curvature(-unit, -left, -right)
    assert np.allclose(reversed_plus, minus, atol=1.0e-13)
    assert np.allclose(reversed_curvature, forward.conj(), atol=1.0e-13)


def test_bundle_isomorphism_is_not_implied_by_rank_and_group() -> None:
    payload = bundle_isomorphism_payload()
    assert payload["validation_passed"]
    assert payload["candidate_isomorphism_status"] == "NOT_DECLARED_OR_ACTION_SELECTED"
    assert payload["validation"]["canonical_Phi_absent"]


def test_v7_parent_architecture_is_recovered_without_promoting_eta_projection() -> None:
    payload = parent_architecture_recovery_payload()
    assert payload["validation_passed"]
    assert payload["primary_classification"] == BRANCH_DECISION
    assert payload["projection_provenance_verdict"] == PROJECTION_PROVENANCE_VERDICT
    rows = {row["object"]: row for row in payload["object_audit"]}
    assert rows["P_parent"]["status"].startswith("CONDITIONAL")
    assert rows["eta-dependent reduction"]["status"] == "MISSING"
    assert rows["independent Gauss equation"]["status"].endswith("ETA_UNSOURCED")


def test_wall_extension_singularity_and_nonuniqueness_are_detected() -> None:
    payload = wall_extension_payload()
    assert payload["validation_passed"]
    assert payload["canonical_extension"] is None
    assert payload["validation"]["normalization_singularity_detected"]


def test_composite_variation_is_not_an_independent_gauss_law() -> None:
    payload = composite_variational_payload()
    assert payload["validation_passed"]
    assert payload["Gauss_identity"].startswith("only Image(P) frame covariance")
    assert payload["validation"]["independent_SU3_Gauss_law_absent"]


def test_retained_action_has_no_eta_color_matcher() -> None:
    payload = matcher_payload()
    assert payload["validation_passed"]
    assert payload["retained_matcher"] is None
    assert payload["eta_sourced_independent_Gauss_law"] is None
    assert payload["branch_decision"] == BRANCH_DECISION
    assert payload["projection_provenance_verdict"] == PROJECTION_PROVENANCE_VERDICT
    assert payload["exact_next_object"] == EXACT_NEXT_OBJECT


def test_boundary_dirac_contract_does_not_emit_index() -> None:
    payload = boundary_dirac_contract_payload()
    assert payload["validation_passed"]
    assert payload["Index_D_rel"] is None
    assert payload["eta_D_boundary"] is None
    assert payload["validation"]["Lorentzian_operator_not_called_elliptic"]


def test_family_centrality_and_weak_current_no_go_are_preserved() -> None:
    payload = flavor_independence_payload()
    assert payload["validation_passed"]
    assert payload["charged_current"] == "J_+^family=I3"
    assert payload["K_ud"] is None


def test_lineage_keeps_diagnostic_candidates_unpromoted() -> None:
    payload = scientific_lineage_payload()
    assert payload["validation_passed"]
    classes = {row["classification"] for row in payload["rows"]}
    assert "SUPERSEDED_INVALIDATED" in classes
    assert "DIAGNOSTIC_ACTION_CANDIDATE" in classes


def test_completion_gate_fails_closed_at_exact_action_object() -> None:
    payload = completion_payload()
    assert payload["validation_passed"]
    assert payload["branch_decision"] == BRANCH_DECISION
    assert payload["Mark_III"].startswith("BLOCKED")
    assert payload["BHSM_physical_completion"] is False
    assert payload["exact_next_object"] == EXACT_NEXT_OBJECT


def test_materialization_is_deterministic(tmp_path) -> None:
    first = {path.name: path.read_bytes() for path in materialize(tmp_path)}
    second = {path.name: path.read_bytes() for path in materialize(tmp_path)}
    assert first == second
    assert set(first) == set(ARTIFACT_FILES.values())
