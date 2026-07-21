"""BHSM v6.0.1 B8/S7 physical-domain and action-source closure.

The topology from v6.0 is preserved exactly.  This audit asks the separate
question whether a stored BHSM action selects that topology as the physical
domain.  Mathematical convention checks are never promoted to physical input.
"""

from __future__ import annotations

import json
from math import pi
from pathlib import Path
from typing import Any, Iterable


VERSION = "v6.0.1"
SPRINT = "bhsm-b8-s7-physical-domain-action-source-closure-v6-0-1"
PRIMARY_RESULT = "BHSM_B8_S7_PARENT_ACTION_SOURCE_MISSING"
V6_RESULT = "BHSM_S7_ARCHITECTURE_AMBIGUOUS"

ARTIFACT_FILES = {
    "domain_matrix": "BHSM_b8_s7_physical_domain_candidate_matrix_v6_0_1.json",
    "time_signature": "BHSM_b8_s7_time_signature_ledger_v6_0_1.json",
    "parent_action": "BHSM_b8_s7_parent_action_domain_map_v6_0_1.json",
    "boundary_embedding": "BHSM_b8_s7_boundary_embedding_v6_0_1.json",
    "metric": "BHSM_s7_physical_metric_squashing_ledger_v6_0_1.json",
    "stationarity": "BHSM_s7_metric_stationarity_scale_audit_v6_0_1.json",
    "measure": "BHSM_s7_physical_measure_fiber_volume_v6_0_1.json",
    "bundle_pushforward": "BHSM_s7_bundle_valued_pushforward_v6_0_1.json",
    "collar": "BHSM_s7_physical_collar_matching_v6_0_1.json",
    "physical_boundary": "BHSM_s7_physical_boundary_map_v6_0_1.json",
    "berger_s3": "BHSM_s7_berger_s3_reclassification_v6_0_1.json",
    "scalar_readiness": "BHSM_s7_scalar_localization_readiness_v6_0_1.json",
    "hidden_inputs": "BHSM_b8_s7_hidden_input_audit_v6_0_1.json",
    "report": "BHSM_b8_s7_physical_domain_action_source_closure_report_v6_0_1.json",
}

GUARDS = {
    "empirical_inputs_used": False,
    "measured_scale_or_coupling_used": False,
    "wick_rotation_performed": False,
    "time_silently_introduced": False,
    "s3_relabelled_as_s7": False,
    "riemannian_s4_labelled_observed_spacetime": False,
    "unit_fiber_volume_promoted_to_physical": False,
    "rho_star_promoted_to_physical_length": False,
    "conventional_metric_labelled_action_derived": False,
    "boundary_tension_derived": False,
    "absolute_unit_generated": False,
    "alpha_derived": False,
    "black_hole_recycling_sourced": False,
    "particle_ontology_derived": False,
    "full_bhsm_completion_claimed": False,
    "frozen_predictions_changed": False,
    "official_prediction_logic_changed": False,
    "existing_numerical_predictions_changed": False,
}

OPEN_GATES = (
    "OPEN_MISSING_B8_GEOMETRIC_ACTION",
    "OPEN_MISSING_B8_SIGNATURE_AND_TIME_SELECTION",
    "OPEN_MISSING_ACTION_SELECTED_S7_BOUNDARY_ROLE",
    "OPEN_MISSING_ACTION_SELECTED_S7_METRIC",
    "OPEN_MISSING_S7_SQUASHING_STATIONARITY",
    "OPEN_MISSING_PHYSICAL_FIBER_AND_BASE_SCALES",
    "OPEN_MISSING_B8_S7_VARIATIONAL_BOUNDARY_COMPLETION",
    "OPEN_MISSING_ENERGY_GEOMETRY_ENVELOPMENT_ACTION",
    "OPEN_MISSING_PHYSICAL_S7_COLLAR_EMBEDDING",
    "OPEN_MISSING_COLLAR_SCALE_SOURCE",
    "OPEN_MISSING_BUNDLE_VALUED_PARALLEL_IDENTIFICATION",
    "OPEN_MISSING_S7_TO_PHYSICAL_3_PLUS_1_MAP",
    "OPEN_MISSING_S7_TO_BERGER_S3_REDUCTION_THEOREM",
    "OPEN_MISSING_SCALAR_TOPOGRAPHIC_PHYSICAL_LOCALIZATION_MAP",
    "OPEN_MISSING_ABSOLUTE_UNIT_ANCHOR",
    "FULL_BHSM_NOT_COMPLETE",
)


def _common(artifact: str) -> dict[str, Any]:
    return {
        "artifact": artifact,
        "version": VERSION,
        "sprint": SPRINT,
        "primary_result": PRIMARY_RESULT,
        "preserved_v6_0_result": V6_RESULT,
        "claim_boundary": (
            "v6.0.1 determines the strongest action-supported relationship "
            "among candidate B8/S7 domains, time, signature, collar, measure, "
            "and lower-dimensional geometry. No stored parent action selects "
            "one candidate as the physical BHSM domain."
        ),
        **GUARDS,
    }


def validate_bundle_dimensions(total: int, base: int, fiber: int) -> bool:
    if min(total, base, fiber) < 0:
        raise ValueError("dimensions must be nonnegative")
    return total == base + fiber


def induced_signature(bulk: tuple[int, int], normal_sign: int) -> tuple[int, int]:
    """Return (timelike, spacelike) boundary counts for a non-null normal."""
    timelike, spacelike = bulk
    if timelike < 0 or spacelike < 0 or normal_sign not in (-1, 1):
        raise ValueError("invalid signature or normal sign")
    if normal_sign == -1:
        if timelike == 0:
            raise ValueError("no timelike direction available for the normal")
        return timelike - 1, spacelike
    if spacelike == 0:
        raise ValueError("no spacelike direction available for the normal")
    return timelike, spacelike - 1


def pushforward_degree(form_degree: int, fiber_dimension: int) -> int:
    if form_degree < fiber_dimension or min(form_degree, fiber_dimension) < 0:
        raise ValueError("invalid form or fiber degree")
    return form_degree - fiber_dimension


def round_s7_volume(radius: float) -> float:
    if radius <= 0:
        raise ValueError("radius must be positive")
    return pi**4 * radius**7 / 3.0


def quaternionic_s7_volume(horizontal_scale: float, fiber_scale: float) -> float:
    """Standard 3-Sasakian convention: four horizontal and three vertical powers."""
    if horizontal_scale <= 0 or fiber_scale <= 0:
        raise ValueError("scales must be positive")
    return pi**4 * horizontal_scale**4 * fiber_scale**3 / 3.0


def complex_s7_volume(horizontal_scale: float, circle_scale: float) -> float:
    """Standard complex-Hopf convention: six horizontal and one vertical power."""
    if horizontal_scale <= 0 or circle_scale <= 0:
        raise ValueError("scales must be positive")
    return pi**4 * horizontal_scale**6 * circle_scale / 3.0


def nested_s7_volume(s4_scale: float, s2_scale: float, s1_scale: float) -> float:
    """Standard nested convention: S4, twistor S2, and Hopf S1 powers."""
    if min(s4_scale, s2_scale, s1_scale) <= 0:
        raise ValueError("scales must be positive")
    return pi**4 * s4_scale**4 * s2_scale**2 * s1_scale / 3.0


def collar_jacobian(principal_curvatures: Iterable[float], distance: float) -> float:
    """Flat-normal-flow convention J=product(1+u k_i)."""
    value = 1.0
    for curvature in principal_curvatures:
        value *= 1.0 + distance * curvature
    return value


def collar_metric_factors(principal_curvatures: Iterable[float], distance: float) -> list[float]:
    return [(1.0 + distance * curvature) ** 2 for curvature in principal_curvatures]


def physical_collar_distance(rho: float, collar_scale: float | None) -> float:
    if not 0.0 <= rho <= 1.0:
        raise ValueError("normalized collar coordinate must lie in [0,1]")
    if collar_scale is None or collar_scale <= 0:
        raise ValueError("a positive physical collar scale is required")
    return rho * collar_scale


def bundle_pushforward_allowed(kind: str, parallel_identification: bool = False) -> bool:
    direct = {"scalar", "differential_form", "invariant_polynomial", "action_top_form"}
    requires_identification = {"gauge_connection", "spinor", "associated_section", "stress_tensor"}
    if kind in direct:
        return True
    if kind in requires_identification:
        return parallel_identification
    raise ValueError(f"unknown pushforward kind: {kind}")


def domain_matrix_payload() -> dict[str, Any]:
    candidates = [
        {"id": "A", "domain": "compact Riemannian B8 with boundary S7", "total_dimension": 8, "signature": [0, 8], "time": None, "compact_directions": 8, "noncompact_directions": 0, "total_space": "B8", "base": None, "fiber": None, "boundary": "S7, Euclidean", "collar": "tubular if an embedding metric is supplied", "orientation": "orientation(B8)=outward-normal then orientation(S7)", "causal_interpretation": "none", "action_measure": "dmu_g on B8 and dmu_h on S7", "variational_principle": "Euclidean action plus boundary completion", "v5_compatibility": "no domain identification", "v6_pushforward": "topologically compatible at boundary only", "status": "COHERENT_NOT_ACTION_SELECTED"},
        {"id": "B_s", "domain": "Lorentzian 8D bulk with spacelike S7 boundary", "total_dimension": 8, "signature": [1, 7], "time": "one bulk coordinate normal to boundary", "compact_directions": "seven on boundary", "noncompact_directions": "time or finite time interval", "total_space": "M8", "base": None, "fiber": None, "boundary": "spacelike S7", "collar": "timelike Gaussian normal collar", "orientation": "epsilon_n=-1", "causal_interpretation": "initial/final compact spatial hypersurface", "action_measure": "sqrt(|g|)d8x", "variational_principle": "Lorentzian action with spacelike boundary data", "v5_compatibility": "v5 has no 7D spatial boundary", "v6_pushforward": "spatial fiber integration possible", "status": "COHERENT_NOT_ACTION_SELECTED"},
        {"id": "B_t", "domain": "Lorentzian 8D bulk with timelike seven-boundary", "total_dimension": 8, "signature": [1, 7], "time": "tangent to boundary", "compact_directions": "topology requires a non-round Lorentzian S7 metric if compact", "noncompact_directions": "bulk normal/radial may be noncompact", "total_space": "M8", "base": None, "fiber": None, "boundary": "timelike 7-manifold with S7 topology", "collar": "spacelike Gaussian normal collar", "orientation": "epsilon_n=+1", "causal_interpretation": "worldtube", "action_measure": "sqrt(|g|)d8x", "variational_principle": "Lorentzian action with timelike boundary data", "v5_compatibility": "signature and dimension mismatch unresolved", "v6_pushforward": "round Riemannian Hopf metric not causal", "status": "COHERENT_TOPOLOGY_METRIC_BRANCH_UNSELECTED"},
        {"id": "C", "domain": "Euclidean B8 preparation followed by Lorentzian continuation", "total_dimension": "8 Euclidean then unspecified Lorentzian", "signature": "[0,8] then unselected", "time": "introduced only by a specified continuation", "compact_directions": "Euclidean B8 candidate", "noncompact_directions": "continuation dependent", "total_space": "B8 then M", "base": "continuation dependent", "fiber": "preserve only if continued connection is specified", "boundary": "S7 before continuation", "collar": "Euclidean before continuation", "orientation": "must be analytically continued", "causal_interpretation": "absent until continuation", "action_measure": "Euclidean then continued measure", "variational_principle": "requires continued fields, contours, and boundary conditions", "v5_compatibility": "v5.10 explicitly lacks full continuation", "v6_pushforward": "conditional after continuation", "status": "BLOCKED_NO_CONTINUED_ACTION"},
        {"id": "D", "domain": "canonical spatial B8/S7 with external time", "total_dimension": "9 for R_t x B8; boundary worldvolume dimension 8", "signature": [1, 8], "time": "external Hamiltonian coordinate", "compact_directions": 8, "noncompact_directions": 1, "total_space": "R_t x B8", "base": "time times any reduced base", "fiber": "spatial Hopf fibers", "boundary": "R_t x S7; each S7 slice spacelike", "collar": "spatial normal bundle evolved in time", "orientation": "spatial plus time orientation", "causal_interpretation": "canonical evolution", "action_measure": "dt dmu_B8 with lapse/shift", "variational_principle": "Hamiltonian constraints and boundary terms", "v5_compatibility": "v5.9 is only a reduced collective Hamiltonian", "v6_pushforward": "spatially compatible", "status": "COHERENT_NO_CANONICAL_PARENT_ACTION"},
        {"id": "E", "domain": "independent Lorentzian M3,1 times compact internal K", "total_dimension": {"K=S3": 7, "K=CP3": 10, "K=S7": 11}, "signature": "one timelike direction on M3,1", "time": "one coordinate of M3,1", "compact_directions": "dim K", "noncompact_directions": 4, "total_space": "M3,1 x K", "base": "M3,1 independent of Hopf S4", "fiber": "K or nested fibers inside K", "boundary": "not S7=partial B8 without extra construction", "collar": "existing v5 lower-dimensional interface remains separate", "orientation": "product orientation", "causal_interpretation": "ordinary 3+1 causality with internal compact geometry", "action_measure": "dmu_M3,1 dmu_K", "variational_principle": "Kaluza-Klein-type action required", "v5_compatibility": "closest to v5 distinction between spacetime and internal Berger domains", "v6_pushforward": "compatible as internal reduction if K and action are selected", "status": "STRONG_CONDITIONAL_BRANCH_NO_PARENT_ACTION"},
    ]
    return {**_common("BHSM_b8_s7_physical_domain_candidate_matrix_v6_0_1"), "status": "MULTIPLE_COHERENT_DOMAINS_NONE_ACTION_SELECTED", "selected_branch": None, "candidates": candidates, "incompatible_notation_combined": False}


def time_signature_payload() -> dict[str, Any]:
    return {**_common("BHSM_b8_s7_time_signature_ledger_v6_0_1"), "status": "TIME_AND_SIGNATURE_NOT_SELECTED", "branches": [
        {"branch": "A", "bulk_signature": [0,8], "boundary_signature": [0,7], "epsilon_n": 1, "S7_type": "Euclidean", "time_location": None, "observed_3_plus_1": False, "Hopf_causal_preservation": "not applicable"},
        {"branch": "B_s", "bulk_signature": [1,7], "boundary_signature": [0,7], "epsilon_n": -1, "S7_type": "spacelike", "time_location": "bulk-normal", "observed_3_plus_1": False, "Hopf_causal_preservation": "projection is spatial, not a spacetime derivation"},
        {"branch": "B_t", "bulk_signature": [1,7], "boundary_signature": [1,6], "epsilon_n": 1, "S7_type": "timelike topology with non-round Lorentzian metric", "time_location": "boundary-tangent", "observed_3_plus_1": False, "Hopf_causal_preservation": "standard Riemannian Hopf submersion does not establish it"},
        {"branch": "C", "bulk_signature": [0,8], "boundary_signature": [0,7], "epsilon_n": 1, "S7_type": "Euclidean before continuation", "time_location": "absent until specified continuation", "observed_3_plus_1": False, "Hopf_causal_preservation": "unproved"},
        {"branch": "D", "bulk_signature": [1,8], "boundary_signature": [1,7], "epsilon_n": 1, "S7_type": "spacelike slice inside timelike boundary worldvolume", "time_location": "external canonical coordinate", "observed_3_plus_1": False, "Hopf_causal_preservation": "fiber reduction occurs on spatial slices"},
        {"branch": "E", "bulk_signature": "product Lorentzian M3,1 plus Riemannian K", "boundary_signature": None, "epsilon_n": None, "S7_type": "internal if K=S7", "time_location": "M3,1", "observed_3_plus_1": "assumed parent factor, not derived from Hopf S4", "Hopf_causal_preservation": "causality stays on independent M3,1"},
    ], "stored_action_time": None, "collar_normal_is_time": "branch B_s only; not selected", "wick_rotation_available": False}


def parent_action_payload() -> dict[str, Any]:
    rows = [
        {"term": "v5.4 unified candidate", "formula": "integral_Sigma[L_geom+sum L_gauge+L_fermion+L_topographic+L_charged+L_neutral+L_scale]dmu_Sigma,rho", "source": "artifacts/BHSM_unified_dynamical_action_candidate_v5_4.json", "domain": "relative Berger Sigma_rho, coordinate dimension 3", "measure": "sqrt(det h_rho)d3x", "signature": None, "fields": "delta h,A_i,Psi,Phi,J_ch,N,rho", "coefficient": "symbolic kappa/zeta/g", "coefficient_dimension": "ell_BH powers in normalized table", "classification": "reduced symbolic boundary action", "lives_on_B8": False, "lives_on_S7": False},
        {"term": "v5.6 T bulk", "formula": "integral_B[1/2 z_T|grad T|2+U_T]dV", "source": "artifacts/BHSM_scalar_topographic_action_source_v5_6.json", "domain": "unspecified spacetime B", "measure": "dV", "signature": None, "fields": "T", "coefficient": "z_T and symbolic potential", "coefficient_dimension": "dimensionless before ell_star", "classification": "symbolic fundamental candidate on unresolved B", "lives_on_B8": False, "lives_on_S7": False},
        {"term": "v5.6 Phi internal", "formula": "integral_Bint[1/2 z_Phi|D_B Phi|2+U_Phi]dmu_B", "source": "artifacts/BHSM_scalar_topographic_action_source_v5_6.json", "domain": "internal Berger/topographic Bint", "measure": "dmu_B", "signature": "Riemannian implicit", "fields": "Phi", "coefficient": "z_Phi and symbolic potential", "coefficient_dimension": "dimensionless before ell_star", "classification": "symbolic internal candidate", "lives_on_B8": False, "lives_on_S7": False},
        {"term": "v5.6/v5.12 boundary", "formula": "integral_Sigma[U_boundary+c_KK+c_K2K2+c_STr(S2)]dmu_h", "source": "artifacts/BHSM_primordial_boundary_collar_action_source_v5_12.json", "domain": "symbolic Sigma; evaluated v5.7 cell is lower-dimensional", "measure": "dmu_h", "signature": None, "fields": "T,Phi,h,K,S", "coefficient": "unsourced symbolic", "coefficient_dimension": "[A]L powers in symbolic d_Sigma", "classification": "boundary candidate", "lives_on_B8": False, "lives_on_S7": "not selected"},
        {"term": "v5.6/v5.12 collar", "formula": "integral_Sigma integral_0^rho_star J B_collar d rho dmu_h", "source": "artifacts/BHSM_primordial_boundary_collar_action_source_v5_12.json", "domain": "symbolic collar over Sigma", "measure": "J dmu_h d rho", "signature": None, "fields": "T,Phi,h,K,S,J", "coefficient": "B_collar symbolic", "coefficient_dimension": "depends on physical versus normalized rho", "classification": "conditional collar candidate", "lives_on_B8": False, "lives_on_S7": "not selected"},
        {"term": "v5.7 reduced cell", "formula": "V_red=-sigma_scale^2+2sigma_scale^4", "source": "artifacts/BHSM_scalar_topographic_evaluated_vacuum_functional_v5_7.json", "domain": "one-dimensional normalized mode after lower-dimensional integrations", "measure": "normalized", "signature": "not spacetime", "fields": "sigma_scale", "coefficient": "normalized 1,3,8 data", "coefficient_dimension": "dimensionless", "classification": "reduced", "lives_on_B8": False, "lives_on_S7": False},
        {"term": "v5.9 pilot wave", "formula": "reduced canonical Hamiltonian", "source": "artifacts/BHSM_pilot_wave_canonical_hamiltonian_v5_9.json", "domain": "collective configuration space", "measure": "configuration metric", "signature": "positive definite reduced metric", "fields": "collective coordinates", "coefficient": "conditional", "coefficient_dimension": "normalized", "classification": "reduced dynamics", "lives_on_B8": False, "lives_on_S7": False},
        {"term": "v5.10 determinant", "formula": "1/2 log[(4+8sigma^2)/(mu^2L^2)]", "source": "artifacts/BHSM_quantum_effective_action_casimir_backreaction_report_v5_10.json", "domain": "one integrated homogeneous fluctuation", "measure": "finite mode", "signature": "full continuation absent", "fields": "delta_perp", "coefficient": "one-mode determinant", "coefficient_dimension": "mu remains explicit", "classification": "reduced quantum diagnostic", "lives_on_B8": False, "lives_on_S7": False},
        {"term": "v5.11 Hessian", "formula": "36-block quadratic operator ledger", "source": "artifacts/BHSM_full_geometric_gauge_fixed_hessian_report_v5_11.json", "domain": "v5 configuration space", "measure": "inherits unresolved v5 domains", "signature": "domain open", "fields": "geometry/gauge/ghost/fermion/scalar sectors", "coefficient": "partial", "coefficient_dimension": "symbolic", "classification": "second variation, not parent action", "lives_on_B8": False, "lives_on_S7": False},
        {"term": "v5.12 recycling", "formula": "-Z_F/(2d_B!) integral_B sqrt|G| F_[d_B]^2", "source": "artifacts/BHSM_spacetime_recycling_candidate_action_v5_12.json", "domain": "general symbolic d_B", "measure": "sqrt|G|d^d_Bx", "signature": "Lorentzian candidate", "fields": "candidate top form", "coefficient": "Z_F unsourced", "coefficient_dimension": "[A]L^(2-d_B)[C]^-2", "classification": "candidate not adopted as BHSM action", "lives_on_B8": "only by unsupported choice d_B=8", "lives_on_S7": False},
        {"term": "v6.0 fibration", "formula": "fiber pushforward theorem", "source": "artifacts/BHSM_s7_fiber_pushforward_theorem_v6_0.json", "domain": "mathematical bundles", "measure": "must be supplied", "signature": None, "fields": "forms", "coefficient": None, "coefficient_dimension": None, "classification": "topological/differential theorem", "lives_on_B8": False, "lives_on_S7": "topology only"},
    ]
    assembly = {key: None for key in ("S_B8_geometry", "S_S7_boundary", "S_fibration", "S_collar", "S_scalar_topographic", "S_gauge", "S_fermion", "S_recycling")}
    return {**_common("BHSM_b8_s7_parent_action_domain_map_v6_0_1"), "status": PRIMARY_RESULT, "terms": rows, "attempted_parent_action": assembly, "B8_action_exists": False, "S7_action_selected": False, "term_migration_used": False, "relational_physicality_candidate": {"hypothesis":"a spacetime region becomes physically distinguished when an action-derived energy distribution encloses or constrains it and produces a nonzero boundary/junction differential","required_equations":["bulk metric equation relating geometry to a conserved stress tensor","boundary or junction equation relating normal stress to extrinsic geometry","constraint equation selecting admissible bounded data","energy-transfer/conservation law across the interface"],"minimum_observables":["inside/outside stress difference","induced metric and shape response","causal time evolution or canonical constraint flow"],"status":"CONDITIONAL_PRINCIPLE_NOT_DERIVED_FROM_STORED_BHSM_ACTION","not_equivalent_to":"topology, coordinate boundary, or nonzero normalized vacuum value alone"}, "first_missing_object": "a dimensionally and variationally complete B8 geometric action with signature, conserved energy stress, and S7 boundary completion"}


def boundary_embedding_payload() -> dict[str, Any]:
    return {**_common("BHSM_b8_s7_boundary_embedding_v6_0_1"), "status": "STANDARD_CONDITIONAL_GEOMETRY_BHSM_EMBEDDING_OPEN", "candidate_relation": "partial B8=S7 only in branches A or a compact-ball specialization; not selected", "definitions": {"induced_metric": "h=i^*g_B8", "normal": "g(n,n)=epsilon_n", "second_fundamental_form": "K_AB=1/2 L_n h_AB in the declared convention", "shape_operator": "S^A_B=h^AC K_CB", "mean_curvature": "K=Tr_h S", "collar_map": "X(Y,u)=exp_Y(u n)", "jacobian": "J=sqrt(|det h_u|/|det h_0|)"}, "dimension_check": {"dim_B8":8,"dim_boundary":7,"S_matrix_shape":"7x7"}, "v5_formula_reuse": "abstract tensor identities are dimension-independent; v5 evaluated 3x3 Berger data and coefficients are not S7 data", "orientation_selected": False, "embedding_selected": False}


def metric_payload() -> dict[str, Any]:
    metrics = [
        {"name":"round_S7","ansatz":"g=L^2 g_round,unit","scales":{"L":"positive"},"connections":"standard Hopf connections","volume":"pi^4 L^7/3","scalar_curvature":"42/L^2","Einstein":"Ric=6g/L^2","isometry":"SO(8)","quaternionic_compatible":True,"complex_compatible":True,"action_selected":False},
        {"name":"quaternionic_canonical_variation","ansatz":"g=L_H^2 g_horizontal,S4+L_Q^2 sum_i eta_i^2","scales":{"horizontal":"L_H","Sp1_fiber":"L_Q"},"connections":"three 3-Sasakian Sp(1) connection forms eta_i","volume":"pi^4 L_H^4 L_Q^3/3 in the standard convention","scalar_curvature":"O'Neill expression R_H/L_H^2+R_V/L_Q^2-(L_Q^2/(4L_H^4))|F_Q|^2; constants depend on declared normalization","Einstein":"round ratio 1; standard 3-Sasakian convention also admits Jensen ratio L_Q^2/L_H^2=1/5","isometry":"SO(8) round; generically Sp(2)xSp(1)","quaternionic_compatible":True,"complex_compatible":"only with additional U(1) choice","action_selected":False},
        {"name":"complex_U1_variation","ansatz":"g=L_C^2 p_C^*g_FS+L_1^2 eta^2","scales":{"CP3_horizontal":"L_C","U1_fiber":"L_1"},"connections":"eta=-i z^dagger dz","volume":"pi^4 L_C^6 L_1/3 in the standard convention","scalar_curvature":"O'Neill expression with U(1) curvature; normalization dependent away from round","Einstein":"round ratio L_1=L_C; generic deformation is not Einstein","isometry":"SO(8) round; generically U(4)","quaternionic_compatible":"not as a uniform Sp(1) fiber unless extra equalities hold","complex_compatible":True,"action_selected":False},
        {"name":"nested_independent_scales","ansatz":"g=L_4^2 g_S4+L_2^2 g_twistor,S2,cov+L_1^2 eta^2 with connection cross terms fixed by horizontal lift","scales":{"S4":"L_4","S2":"L_2","S1":"L_1"},"connections":"Sp(1) connection reduced by U(1) subset","volume":"pi^4 L_4^4 L_2^2 L_1/3 in the compatible standard convention","scalar_curvature":"requires both curvature normalizations and O'Neill tensors","Einstein":"not established generically","isometry":"intersection generically Sp(2)xU(1); enhancement at special equal scales","quaternionic_compatible":"when S2 and S1 combine to the declared Sp(1) fiber metric","complex_compatible":True,"action_selected":False},
    ]
    return {**_common("BHSM_s7_physical_metric_squashing_ledger_v6_0_1"), "status":"METRIC_FAMILY_TOPOLOGICALLY_PERMITTED_DYNAMICALLY_UNSELECTED", "metrics":metrics, "single_Berger_parameter_controls_all_fibers":False, "selected_metric":None}


def stationarity_payload() -> dict[str, Any]:
    return {**_common("BHSM_s7_metric_stationarity_scale_audit_v6_0_1"), "status":"STATIONARITY_UNAVAILABLE_PARENT_ACTION_MISSING", "coordinates":["L","L_H","L_Q","L_C","L_4","L_2","L_1","ell_c","squashing parameters"], "reduced_parent_action":None, "first_variations":None, "reduced_hessian":None, "negative_directions":None, "flat_directions":"not classifiable as dynamical flat directions because no reduced parent action exists", "topological_moduli":"all positive metric scales remain conventional family parameters", "scale_covariance":"uniform rescaling sends dmu_S7 to lambda^7 dmu_S7 and curvature to lambda^-2 curvature; this is not scale generation", "metric_normalization_source":None, "stationary_branch":None}


def measure_payload() -> dict[str, Any]:
    rows = [
        {"space":"S7","dimension":7,"standard_round_measure":"dmu_S7","standard_volume":"pi^4 L^7/3","physical_dimension":"L^7"},
        {"space":"S4","dimension":4,"standard_Hopf_base":"radius L/2","standard_volume":"pi^2 L^4/6","physical_dimension":"L^4"},
        {"space":"CP3","dimension":6,"standard_FS_volume":"pi^3 L^6/6","physical_dimension":"L^6"},
        {"space":"S3","dimension":3,"standard_Hopf_fiber_volume":"2pi^2 L^3","physical_dimension":"L^3"},
        {"space":"S2","dimension":2,"standard_twistor_fiber":"radius L/2, area pi L^2","physical_dimension":"L^2"},
        {"space":"S1","dimension":1,"standard_Hopf_fiber_length":"2pi L","physical_dimension":"L"},
    ]
    return {**_common("BHSM_s7_physical_measure_fiber_volume_v6_0_1"), "status":"STANDARD_MEASURE_FACTORIZATIONS_DERIVED_PHYSICAL_MEASURE_UNSELECTED", "rows":rows, "standard_checks":["Vol(S7)=Vol(S4_radius_half)Vol(S3)=pi^4L^7/3","Vol(S7)=Vol(CP3)Vol(S1)=pi^4L^7/3","Vol(CP3)=Area(S2_radius_half)Vol(S4_radius_half)=pi^3L^6/6"], "deformed_volume_rules":{"quaternionic":"pi^4 L_H^4 L_Q^3/3","complex":"pi^4 L_C^6 L_1/3","nested":"pi^4 L_4^4 L_2^2 L_1/3"}, "candidate_measure_types":{"raw_Riemannian":"valid after metric selection","Haar":"valid for group fibers with scale","normalized_Haar_probability":"not selected by action","action_weighted":"requires parent integrand","bundle_trace":"requires representation pairing","collar_warped":"J or warp factor after embedding"}, "physical_measure":None}


def bundle_pushforward_payload() -> dict[str, Any]:
    rows = [
        {"object":"scalar fields","direct":True,"output":"fiber-integrated scalar density/function","requirements":"integrability and physical fiber measure"},
        {"object":"differential forms","direct":True,"output":"degree k-r form","requirements":"orientation, compact fiber, boundary correction"},
        {"object":"gauge connection","direct":False,"output":"no canonical direct integral because connections form an affine space","requirements":"horizontal connection, invariant zero mode or holonomy/Wilson construction"},
        {"object":"gauge curvature/invariant polynomial","direct":"trace polynomial yes; raw adjoint form only after identification","output":"base form","requirements":"associated-bundle trace and representation normalization"},
        {"object":"spinors","direct":False,"output":"base spinor mode","requirements":"spin structure, vertical Dirac mode, horizontal lift, spin connection, holonomy projection"},
        {"object":"associated-bundle section","direct":False,"output":"invariant/covariantly averaged section","requirements":"connection, parallel transport, representation pairing"},
        {"object":"stress tensor","direct":False,"output":"horizontal effective stress tensor","requirements":"horizontal projector, frame transport, fiber density and possible vertical pressure terms"},
        {"object":"action density/top form","direct":True,"output":"base top form","requirements":"actual metric/action measure; boundary Stokes term when present"},
    ]
    return {**_common("BHSM_s7_bundle_valued_pushforward_v6_0_1"), "status":"OBJECTWISE_PUSHFORWARD_RULES_DERIVED_PHYSICAL_CONNECTION_OPEN", "rows":rows, "parallel_identification":{"connection":None,"horizontal_lift":None,"holonomy":"topological candidates only","trace_normalization":None,"fiber_transport":None}, "nested_scalar_form_composition":"preserved from v6.0 under compatible orientation and Fubini hypotheses"}


def collar_payload() -> dict[str, Any]:
    return {**_common("BHSM_s7_physical_collar_matching_v6_0_1"), "status":"CONDITIONAL_TUBULAR_COLLAR_FORMULA_EMBEDDING_AND_SCALE_OPEN", "candidate_type":"normal tubular neighborhood inside B8 only if branches A/B/D and an embedding are selected", "embedding":"X:S7x[0,rho_star]->B8, X(Y,rho)=exp_Y(ell_c rho n)", "physical_coordinate":"u=ell_c rho", "ell_c":None, "rho_star":{"stored":1.0,"dimension":"dimensionless","physical_thickness":None}, "induced_metric":"h_rho=X_rho^*g_B8; in flat principal frame h_ii(rho)=(1+ell_c rho k_i)^2h_ii(0)", "jacobian":"J=sqrt(|det h_rho|/|det h_0|); flat principal-frame J=product_i(1+ell_c rho k_i)", "endpoint":"X(S7,1) not physically located until ell_c and injectivity radius are supplied", "normal_orientation":"n reversal sends k_i and signed u convention together; must be fixed once", "field_matching":{"scalar":"trace/normal derivative conditions open","gauge":"pullback connection and normal flux conditions open","spin":"spin structure and boundary projector open"}, "pushforward_compatibility":"fiber reduction must commute with collar restriction only after horizontal distribution and endpoint data are compatible", "existing_v5_collar":"same abstract determinant identity, but v5 uses a three-dimensional boundary and supplies no S7 embedding"}


def physical_boundary_payload() -> dict[str, Any]:
    rows = [
        {"map":"S7->S4 as spacetime","dimension":4,"signature":"Riemannian from stored Hopf metric","locality":"bundle projection","causal":"absent","status":"REJECTED_AS_OBSERVED_SPACETIME_WITHOUT_LORENTZIAN_ACTION"},
        {"map":"S7->CP3 then further 3+1 reduction","dimension":"6 then 4","signature":"Riemannian then unspecified","locality":"second map absent","causal":"unproved","status":"BLOCKED_MISSING_SECOND_REDUCTION"},
        {"map":"M3,1 x S7 -> M3,1","dimension":4,"signature":"Lorentzian assumed on independent factor","locality":"standard internal reduction candidate","causal":"preserved on M3,1","status":"STRONG_CONDITIONAL_BRANCH_PARENT_ACTION_MISSING"},
        {"map":"S7 to canonical spatial S3 by slicing/projection","dimension":3,"signature":"spatial","locality":"map absent","causal":"requires external time","status":"BLOCKED_MISSING_REDUCTION_THEOREM"},
    ]
    return {**_common("BHSM_s7_physical_boundary_map_v6_0_1"), "status":"PHYSICAL_BOUNDARY_MAP_NOT_CLOSED", "candidates":rows, "relational_physicality_gate":{"energy_envelops_or_constrains_region":"candidate interpretation","physical_test":"solve sourced bulk constraints and boundary/junction equations and obtain a nonzero, conserved interface differential","current_result":"not evaluable because parent geometry-stress action and energy-transfer law are absent"}, "selected_map":None, "lower_dimensional_fields_produced":False, "lower_dimensional_action_produced":False}


def berger_s3_payload() -> dict[str, Any]:
    return {**_common("BHSM_s7_berger_s3_reclassification_v6_0_1"), "status":"MULTIPLE_S3_EMBEDDING_OR_REDUCTION_ROLES_UNRESOLVED", "candidate_classifications":[
        {"role":"quaternionic Hopf S3 fiber","map":"one fiber p_H^-1(x)","metric_relation":"restriction can be round or Berger only after a vertical metric is selected","action_relation":"fiber action/zero-mode reduction absent","status":"TOPOLOGICALLY_AVAILABLE_CONDITIONALLY"},
        {"role":"homogeneous truncation of an internal compact sector","map":"retain invariant S3 modes","metric_relation":"requires explicit embedding/horizontal split","action_relation":"requires consistent truncation theorem","status":"CONDITIONAL"},
        {"role":"independent internal S3 in M3,1xS3","map":"not a subspace of S7","metric_relation":"existing explicit Berger metric applies directly","action_relation":"closest to v5 internal/spacetime split but parent product action absent","status":"STRONG_CONDITIONAL_BRANCH"},
        {"role":"effective physical boundary","map":None,"metric_relation":"v5 three-coordinate metric","action_relation":"v5 reduced boundary action only","status":"NOT_PROMOTED_TO_S7_BOUNDARY"},
    ], "selected_classification":None, "metric_pullback_proved":False, "volume_relation_proved":"standard round fiber convention only", "curvature_relation_proved":False, "mode_label_map_proved":False, "action_reduction_proved":False, "retained_results":"all correct S3 coordinate, Hodge, measure, and reduced-mode calculations retain their stated lower-dimensional/conditional domains", "invalidated_interpretation":"the existing Berger S3 is not the physical S7 boundary and is not uniquely the S3 Hopf fiber"}


def scalar_readiness_payload() -> dict[str, Any]:
    inputs = {"parent_domain":None,"physical_measure":None,"time_treatment":None,"S7_metric":None,"fiber_measures":"standard conditional formulas only","collar_embedding":None,"bundle_valued_pushforward":"rules known, physical connection absent","T_location":"v5 unspecified spacetime/collar support","Phi_location":"v5 internal Berger/topographic support","physical_action_location":None,"coefficient_dimension_ledger":"v5 normalized/symbolic only"}
    return {**_common("BHSM_s7_scalar_localization_readiness_v6_0_1"), "status":"SCALAR_LOCALIZATION_BLOCKED_PARENT_ACTION_ABSENT", "readiness":"blocked because the parent action is absent", "unique":False, "finite_conditional_branches":False, "inputs":inputs, "v6_1_may_proceed":False, "reason":"localizing T and Phi before selecting their parent domain, signature, measure, and action would move terms between domains by hand"}


def hidden_inputs_payload() -> dict[str, Any]:
    names = ["overall radius","quaternionic fiber radius","U1 fiber radius","twistor S2 radius","squashing","collar thickness","orientation","metric normalization","signature","time coordinate","B8 action coefficient","boundary completion coefficient","normalized Haar choice","volume convention","Wick-rotation contour/scale","connection normalization","representation trace"]
    return {**_common("BHSM_b8_s7_hidden_input_audit_v6_0_1"), "status":"ALL_PHYSICAL_NORMALIZATION_CHOICES_EXPOSED_UNSELECTED", "inputs":[{"input":name,"action_derived":False,"physical_value":None,"may_be_used_as_convention_check":True} for name in names], "hidden_inputs_promoted":False}


def report_payload() -> dict[str, Any]:
    return {**_common("BHSM_b8_s7_physical_domain_action_source_closure_report_v6_0_1"), "status":PRIMARY_RESULT, "central_answer":"The v6.0 nested S7 topology is exact, but no stored BHSM term is a foundational B8 action or an action-selected S7 boundary action. Several Euclidean, Lorentzian, canonical, and product-domain branches are mathematically coherent; none supplies the missing action, signature, time, metric stationarity, physical collar scale, or 3+1 map. Energy-driven spacetime enclosure is retained as a conditional physicality criterion requiring sourced bulk constraints and boundary/junction equations.", "physical_domain_candidates":["A","B_s","B_t","C","D","E"], "selected_branch":None, "rejected_branches":["S7->Riemannian S4 as observed Lorentzian spacetime","unwritten Wick rotation"], "conditional_branches":["A","B_s","B_t","D","E"], "derived":["complete candidate-domain and induced-signature matrix","source-traced proof that v5.4-v6.0 contains no B8 parent action","dimension-correct conditional B8/S7 boundary and collar formulas","round and nested S7 metric/volume families as convention-controlled mathematics","objectwise bundle-pushforward admissibility rules","explicit preservation and reclassification boundary for Berger S3"], "derived_conditionally":["standard Hopf volume factorizations","tubular collar metric and Jacobian after embedding/scale selection","bundle-valued reductions after physical connection and invariant pairing","internal-space product branch after a Kaluza-Klein parent action","energy-geometry enclosure as a physicality test after a conserved stress source and junction law are derived"], "invalidated":["moving v5 terms onto B8 or S7 to close dimensions","calling Riemannian S4 observed spacetime","using rho_star=1 as a thickness","using unit fiber volume as an absolute unit","calling topological metric families stationary solutions","uniquely identifying legacy Berger S3 with the S7 Hopf fiber","treating energy enclosure language alone as an equation of motion"], "still_requiring_new_mathematics":list(OPEN_GATES), "scalar_localization_readiness":"BLOCKED_PARENT_ACTION_ABSENT", "completion_gate_status":"V6_0_1_STOP_PARENT_ACTION_SOURCE_MISSING", "recommended_next_branch":"bhsm-b8-geometric-action-construction-v6-0-2"}


def build_artifact_payloads(repo_root: Path | None = None) -> dict[str, dict[str, Any]]:
    _ = repo_root
    return {"domain_matrix":domain_matrix_payload(),"time_signature":time_signature_payload(),"parent_action":parent_action_payload(),"boundary_embedding":boundary_embedding_payload(),"metric":metric_payload(),"stationarity":stationarity_payload(),"measure":measure_payload(),"bundle_pushforward":bundle_pushforward_payload(),"collar":collar_payload(),"physical_boundary":physical_boundary_payload(),"berger_s3":berger_s3_payload(),"scalar_readiness":scalar_readiness_payload(),"hidden_inputs":hidden_inputs_payload(),"report":report_payload()}


def deterministic_json(payload: dict[str, Any]) -> str:
    return json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def materialize_artifacts(root: Path) -> list[Path]:
    target = root / "artifacts"
    target.mkdir(parents=True, exist_ok=True)
    payloads = build_artifact_payloads(root)
    written = []
    for key, name in ARTIFACT_FILES.items():
        path = target / name
        path.write_text(deterministic_json(payloads[key]), encoding="utf-8")
        written.append(path)
    return written


def b8_s7_status_report(repo_root: Path | None = None) -> dict[str, Any]:
    _ = repo_root
    report = report_payload()
    report["artifacts"] = {key:f"artifacts/{name}" for key,name in ARTIFACT_FILES.items()}
    return report


def b8_s7_status_to_markdown(report: dict[str, Any]) -> str:
    return "\n".join(["# BHSM v6.0.1 B8/S7 Physical Domain and Action-Source Closure","",f"Primary result: `{report['primary_result']}`.","",report["central_answer"],"","Selected branch: none.","",f"Scalar-localization readiness: `{report['scalar_localization_readiness']}`.","","## Open gates","",*[f"- `{gate}`" for gate in report["still_requiring_new_mathematics"]]])+"\n"
