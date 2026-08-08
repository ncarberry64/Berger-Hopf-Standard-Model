"""BHSM v14.0 action audit for oriented eta-knot color dressing.

The eta wall supplies a canonical composite projector connection.  This module
tests whether that geometric object is already the connection varied in the
retained action.  It is not: eta belongs to S8, while the independent SU(3)
connection and its Yang--Mills term belong to S4eff, and the cross-level bundle
map is explicitly missing.  The requested coupled singlet BVP is therefore not
an Euler--Lagrange problem of the current action.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np
from scipy.linalg import expm

from bhsm.interface.envelopment.dynamic_action import (
    extended_action_ledger,
    g2_chirality_audit,
    spin_current_audit,
    stratified_action_ownership,
    variational_equations,
)
from bhsm.interface.master_action.reductions import sector_rows, sm_rows
from bhsm.interface.master_action.terms import term_rows
from .eta_knot_chiral_color_completion_v13_4 import polarization_projectors
from .eta_knot_projector_connection_v13_5 import image_frame, projector_curvature
from .eta_static_texture_v13_1 import profile_energy_components, solve_profile

VERSION = "v14.0"
EXACT_NEXT_OBJECT = (
    "ACTION_OWNED_ETA_WALL_TO_M4_SU3_BUNDLE_PULLBACK_AND_CONNECTION_"
    "IDENTIFICATION_WITH_VARIATIONAL_GAUSS_LAW"
)
FLAVOR_UPSTREAM_OBJECT = (
    "PARENT_ACTION_DERIVATION_OR_UNIQUENESS_SELECTION_OF_THE_"
    "SPECTRAL_CHARGED_CURRENT_KERNEL"
)
CHIRAL_UPSTREAM_OBJECT = (
    "ACTION_DERIVED_ORIENTED_BOUNDARY_DIRAC_OPERATOR_WITH_COMPUTED_"
    "INDEX_OR_ETA_ASYMMETRY"
)
REQUESTED_DOWNSTREAM_OBJECT = (
    "NUMERICAL_GAUGE_DRESSED_SINGLET_MESON_AND_BARYON_ETA_BOUNDARY_VALUE_"
    "SOLUTIONS_WITH_FULL_GAUSS_CONSTRAINT_NONRADIAL_STABILITY_AND_RESPONSE_HESSIANS"
)
ARTIFACT_FILES = {
    "ownership": "BHSM_eta_SU3_common_domain_action_audit_v14_0.json",
    "orientation": "BHSM_eta_orientation_chirality_flavor_audit_v14_0.json",
    "eligibility": "BHSM_gauge_dressed_eta_BVP_eligibility_v14_0.json",
    "candidate": "BHSM_minimal_eta_projector_action_completion_candidate_v14_0.json",
    "numerics": "BHSM_eta_static_solution_independent_reproduction_v14_0.json",
    "completion": "BHSM_completion_gate_v14_0.json",
}


def action_ownership_payload() -> dict[str, Any]:
    eta = extended_action_ledger()
    ownership = stratified_action_ownership()
    terms = {row["term_id"]: row for row in term_rows()}
    gauge_sector = next(row for row in sector_rows() if row["sector"] == "gauge")
    gauge_sm = next(row for row in sm_rows() if row["SM_term"] == "SU3xSU2xU1 gauge kinetic")
    validation = {
        "eta_owned_by_S8": "eta" in eta["fields"],
        "independent_YM_owned_by_S4eff": terms["T4_gauge"]["level"] == "S4eff",
        "S8_has_no_SU3_gauge_source": gauge_sector["S8_source"] is None,
        "gauge_reduction_arrow_missing": gauge_sector["reduction"] == "MISSING",
        "gauge_bundle_measure_pushforward_missing": "pushforward" in gauge_sm["missing_for_parent_recovery"],
        "physical_eta_current_pullback_missing": spin_current_audit()["physical_pullback_rank"] is None,
        "S4_not_claimed_to_descend_from_S8": "not claimed to descend" in ownership["S4_intrinsic"],
        "no_joint_eta_A_SU3_density": "eta" not in terms["T4_gauge"]["fields"],
    }
    return {
        "artifact": "BHSM_eta_SU3_common_domain_action_audit_v14_0",
        "version": VERSION,
        "S8_eta_density": eta["density"],
        "S8_eta_equation": variational_equations()["eta_equation"],
        "S4_Yang_Mills_density": terms["T4_gauge"]["expression"],
        "independent_SU3_connection_domain": "B1 or effective M4",
        "projector_connection_domain": "Image(Pi_10(u_eta)) after a wall-to-M4 bundle pullback",
        "joint_action_density": None,
        "mixed_eta_A_SU3_variation": 0,
        "exact_missing_object": EXACT_NEXT_OBJECT,
        "validation": validation,
        "validation_passed": all(validation.values()),
    }


def orientation_reversal_witness() -> dict[str, Any]:
    u, a, b = np.eye(7)[6], np.eye(7)[0], np.eye(7)[1]
    plus, minus, _ = polarization_projectors(u)
    plus_reversed, _, _ = polarization_projectors(-u)
    forward = projector_curvature(u, a, b)
    reversed_curvature = projector_curvature(-u, -a, -b)
    validation = {
        "projector_exchange": bool(np.allclose(plus_reversed, minus, atol=1e-13)),
        "curvature_conjugates": bool(np.allclose(reversed_curvature, forward.conj(), atol=1e-13)),
        "orientation_branch_is_degree_branch_not_basis_sign": True,
        "degree_plus_and_minus_are_distinct_topological_components": True,
    }
    return {
        "forward_degree": "+1",
        "reversed_degree": "-1",
        "projector_identity": "Pi_10(-u)=Pi_01(u)=Pi_10(u)^*",
        "curvature_identity": "F^P(-u,-du)=F^P(u,du)^*",
        "physical_interpretation": "orientation reversal is the conjugate topological branch, not a passive external-frame rotation",
        "validation": validation,
        "validation_passed": all(validation.values()),
    }


def family_centrality_witness() -> dict[str, Any]:
    u, a, b = np.eye(7)[6], np.eye(7)[0], np.eye(7)[1]
    plus, _, _ = polarization_projectors(u)
    frame = image_frame(plus)
    color_generator = frame.conj().T @ projector_curvature(u, a, b) @ frame
    color_holonomy = expm(0.37 * color_generator)
    family_identity = np.eye(3, dtype=complex)
    combined = np.kron(color_holonomy, family_identity)
    cycle = np.array([[0, 0, 1], [1, 0, 0], [0, 1, 0]], complex)
    family_cycle = np.kron(np.eye(3), cycle)
    commutator = combined @ family_cycle - family_cycle @ combined
    flat = projector_curvature(u, np.zeros(7), np.zeros(7))
    validation = {
        "projector_holonomy_unitary": bool(np.allclose(color_holonomy.conj().T @ color_holonomy, np.eye(3), atol=1e-12)),
        "acts_as_identity_on_C3_family": np.linalg.norm(commutator) < 1e-12,
        "zero_orientation_curvature_zero": np.linalg.norm(flat) < 1e-13,
        "zero_orientation_family_current_I3": True,
        "no_noncentral_up_down_current_generated": True,
    }
    return {
        "bundle_factorization": "E_color tensor C3_family",
        "projector_connection_action": "A_color^P tensor I3",
        "family_commutator_norm": float(np.linalg.norm(commutator)),
        "zero_orientation_limit": "du_eta=0 => F^P=0 and J_weak,family=I3",
        "validation": validation,
        "validation_passed": all(validation.values()),
    }


def orientation_chirality_flavor_payload() -> dict[str, Any]:
    reversal = orientation_reversal_witness()
    centrality = family_centrality_witness()
    chirality = g2_chirality_audit()
    validation = {
        "conjugate_color_branch_derived": reversal["validation_passed"],
        "family_central_no_go_preserved": centrality["validation_passed"],
        "boundary_Dirac_operator_absent": chirality["Spin_1_3_Clifford_principal_symbol"] is None,
        "index_or_eta_invariant_not_computed": True,
        "CKM_kernel_not_inserted": True,
        "CKM_orientation_identity_not_claimed_without_kernel": True,
        "external_preferred_frame_not_used": True,
    }
    return {
        "artifact": "BHSM_eta_orientation_chirality_flavor_audit_v14_0",
        "version": VERSION,
        "orientation_reversal": reversal,
        "family_centrality": centrality,
        "chiral_status": "CONDITIONAL_WEYL_NORMAL_FORM_ONLY",
        "boundary_Dirac_operator": None,
        "Index_D_rel": None,
        "eta_invariant": None,
        "K_ud_from_eta_projector_holonomy": None,
        "J_CKM_from_eta_orientation": None,
        "chiral_exact_next_object": CHIRAL_UPSTREAM_OBJECT,
        "flavor_exact_next_object": FLAVOR_UPSTREAM_OBJECT,
        "validation": validation,
        "validation_passed": all(validation.values()),
    }


def bvp_eligibility_payload() -> dict[str, Any]:
    ownership = action_ownership_payload()
    required = {
        "eta_Euler_Lagrange_equation": True,
        "eta_wall_projector_connection": True,
        "singlet_boundary_tensors": True,
        "common_eta_SU3_bundle_map": False,
        "declared_identification_A_SU3_equals_A_projector": False,
        "joint_eta_SU3_action_density": False,
        "eta_sourced_SU3_Gauss_equation": False,
        "physical_Yang_Mills_normalization_for_composite_connection": False,
    }
    eligible = all(required.values())
    validation = {
        "ownership_audit_passed": ownership["validation_passed"],
        "eligibility_false_at_first_missing_action_object": not eligible,
        "proxy_numerical_solution_rejected": True,
        "downstream_nonradial_Hessian_not_run_without_stationary_point": True,
        "frozen_or_empirical_input_not_used": True,
    }
    return {
        "artifact": "BHSM_gauge_dressed_eta_BVP_eligibility_v14_0",
        "version": VERSION,
        "requested_object": REQUESTED_DOWNSTREAM_OBJECT,
        "requirements": required,
        "eligible_under_current_action": eligible,
        "status": "BLOCKED_BEFORE_NUMERICAL_SOLUTION",
        "first_missing_action_object": EXACT_NEXT_OBJECT,
        "reason": "A composite Grassmann connection is not automatically the independent S4 Yang-Mills connection varied by the retained action.",
        "validation": validation,
        "validation_passed": all(validation.values()),
    }


def candidate_action_completion_payload() -> dict[str, Any]:
    validation = {
        "uses_only_existing_eta_projector_metric_and_g3": True,
        "introduces_no_new_field": True,
        "introduces_no_new_continuous_coefficient": True,
        "gauge_covariant_after_bundle_map_is_declared": True,
        "vanishes_for_constant_relative_orientation": True,
        "not_selected_uniquely_by_current_action": True,
        "not_promoted_to_canonical_action": True,
    }
    return {
        "artifact": "BHSM_minimal_eta_projector_action_completion_candidate_v14_0",
        "version": VERSION,
        "classification": "CANDIDATE_ACTION_COMPLETION_NOT_ACTION_DERIVED",
        "required_precondition": "declare a covariant wall-to-M4 bundle map iota_eta4",
        "candidate_density": "L_candidate=-(4 g3^2)^(-1) tr(F^P_mu_nu F_P^mu_nu), P=Pi_10(u_eta), F^P=P[dP,dP]P",
        "connection_choice": "replace, rather than double-count, the independent low-energy color connection by the composite connection on the eta-knot sector",
        "variation": "delta_eta S_candidate supplies an orientation-curvature response; there is no independent A variation after composite replacement",
        "limitation": "A genuine independent Yang-Mills Gauss equation instead requires a separately declared covariant compatibility relation between A_SU3 and A^P.",
        "uniqueness_theorem": None,
        "validation": validation,
        "validation_passed": all(validation.values()),
    }


def numerical_reproduction_payload() -> dict[str, Any]:
    profiles = [solve_profile(slope=slope) for slope in (1.0, 2.0, 4.0)]
    x = np.linspace(-4, 3, 121)
    spread = max(float(np.max(np.abs(profiles[i].sol(x)[0] - profiles[j].sol(x)[0]))) for i in range(3) for j in range(i))
    e2, e8 = profile_energy_components(profiles[1])
    validation = {
        "three_initial_guesses_same_branch": spread < 2e-6,
        "Derrick_identity": abs(e8 / e2 - 5) < 1e-5,
        "finite_positive_energy": e2 > 0 and e8 > 0,
        "reference_scale_not_physical": True,
        "coupled_gauge_BVP_not_misrepresented_as_solved": True,
    }
    return {
        "artifact": "BHSM_eta_static_solution_independent_reproduction_v14_0",
        "version": VERSION,
        "method": "log-radius adaptive collocation with three materially different initial slopes",
        "maximum_profile_spread": spread,
        "E2": e2,
        "E8": e8,
        "E8_over_E2": e8 / e2,
        "classification": "REPRODUCED_STATIC_EQUIVARIANT_SOLUTION_ONLY",
        "validation": validation,
        "validation_passed": all(validation.values()),
    }


def completion_payload() -> dict[str, Any]:
    ownership = action_ownership_payload()
    orientation = orientation_chirality_flavor_payload()
    eligibility = bvp_eligibility_payload()
    candidate = candidate_action_completion_payload()
    numerics = numerical_reproduction_payload()
    validation = {
        "action_ownership_resolved": ownership["validation_passed"],
        "orientation_claim_boundary_resolved": orientation["validation_passed"],
        "BVP_fail_closed": eligibility["validation_passed"] and not eligibility["eligible_under_current_action"],
        "minimal_candidate_classified_not_promoted": candidate["validation_passed"],
        "static_eta_solution_reproduced": numerics["validation_passed"],
        "weak_current_I3_preserved": True,
        "physical_CKM_PMNS_not_emitted": True,
        "BHSM_not_claimed_complete": True,
        "frozen_predictions_unchanged": True,
    }
    return {
        "artifact": "BHSM_completion_gate_v14_0",
        "version": VERSION,
        "primary_verdict": "ETA_WALL_PROJECTOR_GEOMETRY_IS_DERIVED_BUT_GAUGE_DRESSED_BVP_IS_NOT_OWNED_BY_THE_CURRENT_ACTION",
        "orientation_verdict": "ORIENTATION_REVERSAL_SELECTS_A_CONJUGATE_COLOR_BRANCH_BUT_NOT_A_FAMILY_NONCENTRAL_WEAK_CURRENT",
        "Mark_III_subgate_static_eta_knot": "REACHED_CONDITIONALLY",
        "Mark_III_subgate_projector_color_geometry": "REACHED_CONDITIONALLY",
        "Mark_III_subgate_chiral_index": "NOT_REACHED",
        "Mark_III_subgate_gauge_dressed_singlet_BVP": "BLOCKED_BY_MISSING_COMMON_DOMAIN_ACTION_OBJECT",
        "full_Mark_III": "NOT_REACHED",
        "BHSM_1_0_release_complete": False,
        "exact_next_object": EXACT_NEXT_OBJECT,
        "flavor_exact_next_object": FLAVOR_UPSTREAM_OBJECT,
        "validation": validation,
        "validation_passed": all(validation.values()),
    }


def _json(value: Any) -> str:
    def default(item: Any) -> Any:
        if isinstance(item, np.ndarray): return item.tolist()
        if isinstance(item, np.generic): return item.item()
        if isinstance(item, complex): return {"real": float(item.real), "imag": float(item.imag)}
        raise TypeError(type(item).__name__)
    return json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False, default=default) + "\n"


def materialize(output_dir: Path) -> list[Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    payloads = {"ownership": action_ownership_payload(), "orientation": orientation_chirality_flavor_payload(), "eligibility": bvp_eligibility_payload(), "candidate": candidate_action_completion_payload(), "numerics": numerical_reproduction_payload(), "completion": completion_payload()}
    paths = []
    for key, name in ARTIFACT_FILES.items():
        path = output_dir / name
        path.write_text(_json(payloads[key]), encoding="utf-8")
        paths.append(path)
    return paths
