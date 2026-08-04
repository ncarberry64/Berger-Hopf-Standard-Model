from __future__ import annotations

from math import pi

import numpy as np

from bhsm.interface.completion.eta_knot_action_completion_v14_0 import (
    ARTIFACT_FILES,
    EXACT_NEXT_OBJECT,
    FLAVOR_UPSTREAM_OBJECT,
    action_ownership_payload,
    bvp_eligibility_payload,
    candidate_action_completion_payload,
    completion_payload,
    family_centrality_witness,
    materialize,
    numerical_reproduction_payload,
    orientation_chirality_flavor_payload,
    orientation_reversal_witness,
)
from bhsm.interface.completion.eta_knot_chiral_color_completion_v13_4 import (
    anomaly_payload,
    eta_wall_data,
    polarization_projectors,
    wall_polarization_payload,
    weyl_determinants,
)
from bhsm.interface.completion.eta_knot_emergent_fermion_v13_3 import (
    allowed_two_j,
    emergent_field_bundle_payload,
    fr_sign,
    native_topological_quantization_payload,
    stabilizer_plane_inertia,
)
from bhsm.interface.completion.eta_knot_projector_connection_v13_5 import (
    image_frame,
    projector_curvature,
    reference_curvature,
    singlet_covariance_witness,
)
from bhsm.interface.completion.eta_static_texture_v13_1 import (
    ode_residual,
    profile_energy_components,
    radial_hessian_eigenvalues,
    solve_profile,
)


def test_static_eta_solution_is_reproduced_and_radially_stable() -> None:
    solution = solve_profile()
    e2, e8 = profile_energy_components(solution)
    assert solution.status == 0
    assert abs(solution.y[0, 0]) < 1.0e-12
    assert abs(solution.y[0, -1] - pi) < 1.0e-12
    assert ode_residual(solution) < 2.0e-5
    assert abs(e8 / e2 - 5.0) < 1.0e-5
    assert np.min(radial_hessian_eigenvalues(solution)) > 0.0


def test_static_solution_is_independent_of_initial_slope() -> None:
    x = np.linspace(-4.0, 3.0, 121)
    profiles = [solve_profile(slope=slope).sol(x)[0] for slope in (1.0, 2.0, 4.0)]
    assert max(np.max(np.abs(a - b)) for a in profiles for b in profiles) < 2.0e-6


def test_fr_quantization_is_discrete_and_odd_degree_is_fermionic() -> None:
    payload = native_topological_quantization_payload()
    assert payload["validation_passed"]
    assert payload["local_density"] is None
    assert fr_sign(1) == -1
    assert fr_sign(2) == 1
    assert allowed_two_j(1, 7) == [1, 3, 5, 7]


def test_eta_knot_replaces_independent_uv_fermion_without_double_counting() -> None:
    payload = emergent_field_bundle_payload()
    assert payload["validation_passed"]
    assert payload["architecture_replacement"]["independent_ultraviolet_Psi"] is False
    assert payload["no_double_counting"]["eta_barPsiPsi_vertex_added"] is False
    assert stabilizer_plane_inertia() > 0.0


def test_wall_orientation_selects_conjugate_rank_three_projectors() -> None:
    u = np.eye(7)[6]
    plus, minus, _ = polarization_projectors(u)
    reversed_plus, _, _ = polarization_projectors(-u)
    assert eta_wall_data()["df_dlogr"] > 0.0
    assert wall_polarization_payload()["validation_passed"]
    assert np.linalg.matrix_rank(plus) == np.linalg.matrix_rank(minus) == 3
    assert np.allclose(reversed_plus, minus, atol=1.0e-13)


def test_weyl_normal_forms_share_the_lorentz_cone_but_do_not_prove_index() -> None:
    p = np.array([2.0, 0.3, -0.4, 0.5])
    left, right = weyl_determinants(p)
    cone = p[0] ** 2 - np.dot(p[1:], p[1:])
    assert abs(left - cone) < 1.0e-12
    assert abs(right - cone) < 1.0e-12
    assert anomaly_payload()["validation_passed"]


def test_projector_curvature_is_nonzero_su3_geometry() -> None:
    payload = reference_curvature()
    assert payload["validation_passed"]
    assert payload["validation"]["restricted_curvature_anti_Hermitian"]
    assert payload["validation"]["restricted_curvature_traceless"]
    assert payload["validation"]["curvature_nonzero"]


def test_projector_curvature_vanishes_when_orientation_does_not_vary() -> None:
    u = np.eye(7)[6]
    plus, _, _ = polarization_projectors(u)
    frame = image_frame(plus)
    curvature = projector_curvature(u, np.zeros(7), np.eye(7)[0])
    assert np.allclose(curvature, 0.0, atol=1.0e-13)
    assert frame.shape == (7, 3)


def test_mesons_and_baryons_close_covariantly() -> None:
    payload = singlet_covariance_witness()
    assert payload["validation_passed"]
    assert payload["validation"]["meson_finite_transport_invariant"]
    assert payload["validation"]["baryon_finite_transport_invariant"]
    assert payload["validation"]["baryon_infinitesimal_connection_cancels"]


def test_orientation_reversal_is_conjugate_topological_branch() -> None:
    payload = orientation_reversal_witness()
    assert payload["validation_passed"]
    assert payload["validation"]["projector_exchange"]
    assert payload["validation"]["curvature_conjugates"]
    assert payload["validation"]["degree_plus_and_minus_are_distinct_topological_components"]


def test_color_holonomy_remains_family_central_and_zero_limit_is_i3() -> None:
    payload = family_centrality_witness()
    assert payload["validation_passed"]
    assert payload["family_commutator_norm"] < 1.0e-12
    assert payload["validation"]["zero_orientation_family_current_I3"]
    assert payload["validation"]["no_noncentral_up_down_current_generated"]


def test_current_action_has_no_common_eta_su3_variation() -> None:
    payload = action_ownership_payload()
    assert payload["validation_passed"]
    assert payload["joint_action_density"] is None
    assert payload["mixed_eta_A_SU3_variation"] == 0
    assert payload["exact_missing_object"] == EXACT_NEXT_OBJECT


def test_gauge_dressed_bvp_fails_closed_before_numerical_solution() -> None:
    payload = bvp_eligibility_payload()
    assert payload["validation_passed"]
    assert payload["eligible_under_current_action"] is False
    assert payload["status"] == "BLOCKED_BEFORE_NUMERICAL_SOLUTION"
    assert payload["first_missing_action_object"] == EXACT_NEXT_OBJECT


def test_minimal_completion_is_candidate_not_canonical_action() -> None:
    payload = candidate_action_completion_payload()
    assert payload["validation_passed"]
    assert payload["classification"] == "CANDIDATE_ACTION_COMPLETION_NOT_ACTION_DERIVED"
    assert payload["uniqueness_theorem"] is None


def test_chirality_and_flavor_claim_boundaries_are_explicit() -> None:
    payload = orientation_chirality_flavor_payload()
    assert payload["validation_passed"]
    assert payload["boundary_Dirac_operator"] is None
    assert payload["Index_D_rel"] is None
    assert payload["K_ud_from_eta_projector_holonomy"] is None
    assert payload["J_CKM_from_eta_orientation"] is None
    assert payload["flavor_exact_next_object"] == FLAVOR_UPSTREAM_OBJECT


def test_static_numerical_reproduction_does_not_claim_coupled_bvp() -> None:
    payload = numerical_reproduction_payload()
    assert payload["validation_passed"]
    assert payload["classification"] == "REPRODUCED_STATIC_EQUIVARIANT_SOLUTION_ONLY"
    assert abs(payload["E8_over_E2"] - 5.0) < 1.0e-5


def test_v14_completion_advances_geometry_without_overclaim() -> None:
    payload = completion_payload()
    assert payload["validation_passed"]
    assert payload["Mark_III_subgate_projector_color_geometry"] == "REACHED_CONDITIONALLY"
    assert payload["Mark_III_subgate_chiral_index"] == "NOT_REACHED"
    assert payload["Mark_III_subgate_gauge_dressed_singlet_BVP"].startswith("BLOCKED")
    assert payload["BHSM_1_0_release_complete"] is False


def test_materialization_is_deterministic(tmp_path) -> None:
    first = {path.name: path.read_bytes() for path in materialize(tmp_path)}
    second = {path.name: path.read_bytes() for path in materialize(tmp_path)}
    assert first == second
    assert set(first) == set(ARTIFACT_FILES.values())
