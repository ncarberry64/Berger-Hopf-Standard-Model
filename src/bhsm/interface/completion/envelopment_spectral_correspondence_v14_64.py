"""BHSM v14.64 envelopment spectral-correspondence gate.

This sprint tests whether the existing global envelopment geometry can supply
what v14.63 identified as the missing microscopic operator/measure principle.

The result is deliberately fail-closed:
* the envelopment incidence graph and geometric L2 measures do canonically
  constrain the cross-stratum architecture;
* edge-restricted Connes-distance matching can fix incidence magnitudes from
  geometric envelopment lengths;
* one gauge-invariant loop phase remains on the two-cap diamond incidence graph;
* the naive direct-sum L2 spectral triple fails in the continuum because the
  bulk-to-boundary trace map is unbounded on L2;
* a heat-semigroup microscopic branch uniquely fixes the cutoff profile to an
  exponential once that branch is adopted, but adopting "the heat trace is the
  microscopic action" is a new foundational axiom, not a theorem of the
  current BHSM archive.

No physical particle prediction is emitted.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
import hashlib
import json
import math
from typing import Any, Mapping, Sequence

import numpy as np

VERSION = "v14.64"

PRIMARY_VERDICT = (
    "BHSM_V14_64_GLOBAL_ENVELOPMENT_CAN_CANONICALLY_FIX_THE_STRATUM_INCIDENCE_"
    "GRAPH_GEOMETRIC_L2_MEASURES_AND_EDGE_MAGNITUDES_AFTER_DISTANCE_MATCHING_"
    "BUT_THE_NAIVE_DIRECT_SUM_L2_SPECTRAL_TRIPLE_IS_NOT_A_VALID_CONTINUUM_"
    "REALIZATION_BECAUSE_BULK_TO_BOUNDARY_TRACE_MAPS_ARE_UNBOUNDED_ON_L2_AND_"
    "THE_TWO_CAP_DIAMOND_RETAINS_ONE_GAUGE_INVARIANT_LOOP_HOLONOMY_SO_THE_"
    "CORRECT_MICROSCOPIC_OBJECT_IS_A_RELATIVE_BOUNDARY_OR_UNBOUNDED_"
    "CORRESPONDENCE_OPERATOR_WITH_AN_ACTION_DERIVED_DOMAIN"
)

HEAT_BRANCH_VERDICT = (
    "BHSM_V14_64_IF_THE_MICROSCOPIC_FUNCTIONAL_IS_PREDECLARED_TO_BE_THE_TRACE_"
    "OF_THE_CANONICAL_HEAT_SEMIGROUP_THEN_STRONG_CONTINUOUS_SEMIGROUP_"
    "COMPOSITION_AND_GENERATOR_NORMALIZATION_FIX_THE_PROFILE_TO_EXP_MINUS_TP_"
    "AND_REMOVE_THE_V14_63_GENERIC_CUTOFF_PROFILE_AMBIGUITY_BUT_THIS_HEAT_TRACE_"
    "ACTION_POSTULATE_IS_NOT_DERIVED_BY_THE_CURRENT_ARCHIVE"
)

TRACE_VERDICT = (
    "BHSM_V14_64_THE_COMPATIBILITY_TRACE_FROM_A_BULK_L2_SPACE_TO_A_BOUNDARY_L2_"
    "SPACE_IS_UNBOUNDED_SO_A_FINITE_INCIDENCE_MATRIX_CANNOT_BE_PROMOTED_"
    "UNCHANGED_TO_AN_ORDINARY_CONTINUUM_DIRECT_SUM_SPECTRAL_TRIPLE"
)

HOLONOMY_VERDICT = (
    "BHSM_V14_64_THE_TWO_CAP_ENVELOPMENT_INCIDENCE_GRAPH_HAS_CYCLE_RANK_ONE_SO_"
    "VERTEX_REPHASING_REMOVES_THREE_EDGE_PHASES_BUT_LEAVES_ONE_GAUGE_INVARIANT_"
    "DIAMOND_HOLONOMY_WHICH_MUST_BE_FIXED_BY_CONNECTION_OR_ORIENTATION_DATA_"
    "RATHER_THAN_BY_FLAVOR_TARGETS"
)

EXACT_NEXT_OBJECT = (
    "ACTION_DERIVED_RELATIVE_BOUNDARY_SPECTRAL_CORRESPONDENCE_OR_UNBOUNDED_KK_"
    "CYCLE_FOR_M8_TO_M5_PLUS_MINUS_TO_M4_WITH_CALDERON_OR_BOUNDARY_TRIPLE_"
    "DOMAIN_GEOMETRIC_EDGE_LENGTHS_GAUGE_GHOST_COMPLETION_AND_PREDECLARED_HEAT_"
    "SEMIGROUP_OR_OTHER_MICROSCOPIC_FUNCTIONAL_THEN_DERIVE_THE_FULL_HEAT_"
    "COEFFICIENTS_FINITE_FERMION_OPERATOR_GLOBAL_ENVELOPMENT_STATIONARY_BRANCH_"
    "DTN_RELATIVE_HEAT_KERNEL_AND_ZERO_RETUNING_NEUTRINO_KILL_SCREEN"
)

VERTICES = ("M8", "M5_plus", "M5_minus", "M4")
EDGES = (
    ("M8", "M5_plus", "e_8p"),
    ("M8", "M5_minus", "e_8m"),
    ("M5_plus", "M4", "e_p4"),
    ("M5_minus", "M4", "e_m4"),
)


def canonical_json_bytes(payload: Any) -> bytes:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False).encode("utf-8")


def sha256_payload(payload: Any) -> str:
    return hashlib.sha256(canonical_json_bytes(payload)).hexdigest()


def cycle_rank(vertex_count: int, edge_count: int, connected_components: int = 1) -> int:
    v, e, c = int(vertex_count), int(edge_count), int(connected_components)
    if v <= 0 or e < 0 or c <= 0 or c > v:
        raise ValueError("invalid graph counts")
    return e - v + c


def edge_weight_from_length(length: float) -> float:
    """Edge-restricted two-point Connes calibration |D_ij|=1/ell_ij."""
    ell = float(length)
    if not math.isfinite(ell) or ell <= 0.0:
        raise ValueError("length must be positive and finite")
    return 1.0 / ell


def _edge_index() -> dict[str, tuple[int, int]]:
    idx = {v: i for i, v in enumerate(VERTICES)}
    return {name: (idx[a], idx[b]) for a, b, name in EDGES}


def incidence_dirac(lengths: Mapping[str, float], phases: Mapping[str, float] | None = None) -> np.ndarray:
    """Hermitian reduced incidence Dirac on the two-cap diamond.

    This is a finite theorem witness only.  It is not the continuum spectral
    correspondence because the continuum trace maps are not bounded on L2.
    """
    phases = {} if phases is None else dict(phases)
    d = np.zeros((len(VERTICES), len(VERTICES)), dtype=complex)
    for name, (i, j) in _edge_index().items():
        w = edge_weight_from_length(lengths[name])
        phi = float(phases.get(name, 0.0))
        if not math.isfinite(phi):
            raise ValueError("phase must be finite")
        z = w * np.exp(1j * phi)
        d[i, j] = z
        d[j, i] = np.conjugate(z)
    return d


def vertex_gauge_transform(d: np.ndarray, vertex_phases: Sequence[float]) -> np.ndarray:
    a = np.asarray(d, dtype=complex)
    if a.shape != (len(VERTICES), len(VERTICES)):
        raise ValueError("wrong matrix shape")
    if len(vertex_phases) != len(VERTICES):
        raise ValueError("wrong number of vertex phases")
    u = np.diag(np.exp(1j * np.asarray(vertex_phases, dtype=float)))
    return u @ a @ np.conjugate(u.T)


def diamond_holonomy(phases: Mapping[str, float]) -> float:
    """Gauge-invariant oriented loop phase modulo 2*pi.

    Loop orientation: M8 -> M5+ -> M4 -> M5- -> M8.
    """
    raw = float(phases.get("e_8p", 0.0)) + float(phases.get("e_p4", 0.0)) - float(phases.get("e_m4", 0.0)) - float(phases.get("e_8m", 0.0))
    return math.atan2(math.sin(raw), math.cos(raw))


def phases_from_matrix(d: np.ndarray) -> dict[str, float]:
    a = np.asarray(d, dtype=complex)
    out = {}
    for name, (i, j) in _edge_index().items():
        out[name] = float(np.angle(a[i, j]))
    return out


def gauge_holonomy_witness() -> dict[str, Any]:
    lengths = {"e_8p": 2.0, "e_8m": 2.4, "e_p4": 0.75, "e_m4": 0.9}
    phases = {"e_8p": 0.21, "e_8m": -0.37, "e_p4": 0.44, "e_m4": 0.13}
    d = incidence_dirac(lengths, phases)
    theta = (0.31, -0.27, 0.52, -0.11)
    dg = vertex_gauge_transform(d, theta)
    h0 = diamond_holonomy(phases)
    h1 = diamond_holonomy(phases_from_matrix(dg))
    ev0 = np.linalg.eigvalsh(d)
    ev1 = np.linalg.eigvalsh(dg)
    return {
        "version": VERSION,
        "verdict": HOLONOMY_VERDICT,
        "vertices": list(VERTICES),
        "edges": [list(e) for e in EDGES],
        "connected_components": 1,
        "cycle_rank": cycle_rank(len(VERTICES), len(EDGES), 1),
        "edge_lengths_diagnostic": lengths,
        "edge_weights_inverse_length_diagnostic": {k: edge_weight_from_length(v) for k, v in lengths.items()},
        "initial_phases": phases,
        "vertex_gauge_phases": list(theta),
        "holonomy_before": h0,
        "holonomy_after": h1,
        "holonomy_invariance_residual": abs(math.atan2(math.sin(h1-h0), math.cos(h1-h0))),
        "spectrum_invariance_residual": float(np.max(np.abs(ev0-ev1))),
        "interpretation": "The diamond has E-V+1=1 independent cycle phase. Local vertex phase conventions cannot remove it.",
        "physical_BHSM_prediction": False,
    }


def normalized_boundary_layer(n: int, x: np.ndarray | float) -> np.ndarray:
    """L2-normalized exp(-n x) boundary layer on [0,1]."""
    k = int(n)
    if k <= 0:
        raise ValueError("n must be positive")
    norm = math.sqrt(2.0 * k / (1.0 - math.exp(-2.0 * k)))
    return norm * np.exp(-k * np.asarray(x, dtype=float))


def boundary_trace_amplitude(n: int) -> float:
    return float(normalized_boundary_layer(n, 0.0))


def boundary_layer_l2_norm_exact(n: int) -> float:
    # By construction on [0,1].
    if int(n) <= 0:
        raise ValueError("n must be positive")
    return 1.0


def trace_map_obstruction_payload() -> dict[str, Any]:
    ns = (1, 2, 4, 8, 16, 32, 64, 128, 256)
    amps = [boundary_trace_amplitude(n) for n in ns]
    ratios = [amps[i+1]/amps[i] for i in range(len(amps)-1)]
    return {
        "version": VERSION,
        "verdict": TRACE_VERDICT,
        "witness_family": "u_n(x)=sqrt(2n/(1-exp(-2n))) exp(-n x) on [0,1]",
        "L2_norm_each": 1.0,
        "n_values": list(ns),
        "boundary_values_u_n_0": amps,
        "last_boundary_value": amps[-1],
        "asymptotic_boundary_growth": "sqrt(2n)",
        "successive_growth_ratios": ratios,
        "trace_L2_to_boundary_bounded": False,
        "trace_Hs_to_boundary_bounded_only_above_threshold": "yes; standard trace regularity requires positive Sobolev control (e.g. s>1/2 in the scalar codimension-one model)",
        "naive_finite_incidence_matrix_is_exact_continuum_operator": False,
        "required_replacement": "relative/boundary spectral triple, boundary triple, Calderon realization, Wentzell-type dynamic boundary operator, or unbounded KK correspondence with explicit domain",
        "physical_BHSM_prediction": False,
    }


def heat_multiplier(t: float, u: float) -> float:
    tt, uu = float(t), float(u)
    if not math.isfinite(tt) or tt < 0.0:
        raise ValueError("t must be nonnegative and finite")
    if not math.isfinite(uu) or uu < 0.0:
        raise ValueError("u must be nonnegative and finite")
    return math.exp(-tt * uu)


def heat_semigroup_residual(t: float, s: float, u: float) -> float:
    return abs(heat_multiplier(t+s, u) - heat_multiplier(t, u)*heat_multiplier(s, u))


def exponential_heat_moment(order: int, rate: float = 1.0) -> float:
    p = int(order)
    a = float(rate)
    if p < 0:
        raise ValueError("order must be nonnegative")
    if not math.isfinite(a) or a <= 0.0:
        raise ValueError("rate must be positive and finite")
    if p == 0:
        return 1.0
    return a ** (-0.5*p)


def heat_semigroup_profile_payload() -> dict[str, Any]:
    checks = []
    for t, s, u in ((0.1,0.2,3.0),(0.7,1.3,0.4),(2.0,4.0,1.1)):
        checks.append({"t":t,"s":s,"u":u,"residual":heat_semigroup_residual(t,s,u)})
    orders = (8,6,5,4,3,2,0)
    return {
        "version": VERSION,
        "verdict": HEAT_BRANCH_VERDICT,
        "candidate_microscopic_branch": "Gamma_heat(t)=STr exp(-t P)",
        "scalar_multiplier": "f_t(u)=exp(-t u)",
        "uniqueness_conditions": [
            "f_0(u)=1",
            "f_{t+s}(u)=f_t(u) f_s(u)",
            "strong/pointwise continuity in t",
            "generator normalization d/dt f_t(u)|_{t=0}=-u",
        ],
        "semigroup_checks": checks,
        "normalized_moments_at_rate_1": {f"F{p}": exponential_heat_moment(p,1.0) for p in orders},
        "v14_63_generic_profile_ambiguity_removed_if_branch_adopted": True,
        "branch_derived_by_existing_BHSM_action": False,
        "new_foundational_axiom_required": True,
        "can_be_selected_after_particle_comparison": False,
        "physical_BHSM_prediction": False,
    }


def geometric_trace_payload() -> dict[str, Any]:
    return {
        "version": VERSION,
        "geometric_incidence": {
            "M8_to_M5": "quaternionic Hopf correspondence already declared in v7.1",
            "M5_caps": 2,
            "M5_to_M4": "two caps share the M4 equator",
            "incidence_graph": "diamond",
        },
        "hilbert_space_candidate": "H8 direct_sum H5_plus direct_sum H5_minus direct_sum H4",
        "measure_rule": "use the geometric L2 measures already carried by each stratum; no fitted cross-stratum trace weights",
        "canonical_unweighted_direct_sum_trace_available": True,
        "arbitrary_weighted_trace_needed": False,
        "caveat": "This fixes trace multiplicity only after the direct-sum correspondence is adopted. It does not cure the unbounded continuum trace/restriction map or define its self-adjoint domain.",
        "physical_BHSM_prediction": False,
    }


def incidence_distance_payload() -> dict[str, Any]:
    diagnostic_lengths = {"e_8p": 3.0, "e_8m": 3.0, "e_p4": 0.5, "e_m4": 0.5}
    return {
        "version": VERSION,
        "rule": "on each isolated two-point incidence edge, require Connes distance to equal the corresponding action-selected geometric envelopment/collar length",
        "edge_magnitude_rule": "|D_ij|=1/ell_ij",
        "diagnostic_lengths": diagnostic_lengths,
        "diagnostic_weights": {k: edge_weight_from_length(v) for k,v in diagnostic_lengths.items()},
        "edge_magnitudes_fixed_once_geometric_lengths_are_action_selected": True,
        "edge_phases_fully_fixed": False,
        "global_full_Connes_distance_claimed": False,
        "note": "This is an edge-restricted calibration contract, not a proof that the full continuum diamond Connes metric equals the classical stratified distance.",
        "physical_BHSM_prediction": False,
    }


def finite_fermion_operator_payload() -> dict[str, Any]:
    return {
        "version": VERSION,
        "reclassification": "finite Dirac/Yukawa numbers should be outputs of the action-derived stationary background, not independently tuned matrices, on the zero-input branch",
        "action_derivative_contract": {
            "fermion_bilinear_operator": "D_eff = delta^2 Gamma / (delta barPsi delta Psi) evaluated at Phi_star",
            "charged_current_vertex": "Gamma_plus = delta^3 Gamma / (delta W_plus delta barPsi_u delta Psi_d) evaluated at Phi_star",
            "moving_seam_shape_vertex": "Gamma_plus_X = delta^4 Gamma / (delta q_Lr delta W_plus delta barPsi_u delta Psi_d) evaluated at Phi_star",
        },
        "static_Yukawa_matrix_may_be_inserted_from_data": False,
        "current_archive_has_complete_microscopic_Gamma_for_these_derivatives": False,
        "therefore_zero_input_flavor_closed": False,
        "pair_wake_dynamic_flavor_program_retained": True,
        "physical_BHSM_prediction": False,
    }


def candidate_status_payload() -> dict[str, Any]:
    return {
        "version": VERSION,
        "primary_verdict": PRIMARY_VERDICT,
        "validated": [
            "The v7.1 envelopment architecture fixes a two-cap diamond incidence pattern.",
            "The connected diamond has one independent cycle phase.",
            "Edge-restricted Connes calibration fixes incidence magnitudes once physical edge lengths are action-selected.",
            "The naive bulk-L2 to boundary-L2 trace map is unbounded in the continuum.",
            "A strongly continuous normalized diffusion semigroup has exponential scalar spectral multiplier.",
            "Adopting the heat-semigroup action would collapse the generic cutoff-profile freedom identified in v14.63.",
        ],
        "invalidated": [
            "A finite diamond incidence matrix by itself is already the exact continuum stratified spectral triple.",
            "Vertex rephasings remove every phase of the two-cap incidence graph.",
            "Global envelopment geometry alone already proves that the heat trace is the microscopic action.",
        ],
        "reclassified": [
            "The missing global spectral triple is better formulated as a relative/boundary spectral correspondence with an explicit domain.",
            "Cross-stratum trace weights need not be arbitrary if the geometric direct-sum Hilbert trace is adopted.",
            "The cutoff-profile ambiguity can be reduced to one explicit foundational choice: whether the microscopic functional is the canonical heat trace (or another predeclared alternative).",
            "Finite Yukawa/mixing data should be stationary-background derivative outputs on the zero-input branch.",
        ],
        "open": [
            "construct the self-adjoint relative/boundary operator and its Calderon or boundary-triple domain",
            "derive or predeclare the unique microscopic functional before comparison",
            "fix the one loop holonomy from action-owned connection/orientation data",
            "compute full M8/M5/M4 heat coefficients including boundaries/ghosts/zero modes",
            "solve the global stationary background and derive the effective fermion/current operators",
            "run the frozen no-retuning neutrino and downstream particle kill screens",
        ],
    }


def next_branch_gate_payload() -> dict[str, Any]:
    return {
        "version": VERSION,
        "exact_next_object": EXACT_NEXT_OBJECT,
        "branch_A": {
            "name": "HEAT_SEMIGROUP_MICROSCOPIC_BRANCH",
            "status": "AVAILABLE_AS_PREDECLARED_FOUNDATIONAL_CANDIDATE",
            "profile": "exp(-t P)",
            "benefit": "removes generic cutoff moment-profile ambiguity",
            "not_yet_authoritative": True,
        },
        "branch_B": {
            "name": "PURE_RELATIVE_ZETA_BRANCH",
            "status": "AVAILABLE_BUT_LOCAL_RELEVANT_COUNTERTERMS_REMAIN_OPEN",
        },
        "mandatory_common_step": "construct the continuum relative/boundary spectral correspondence and self-adjoint domain before either branch can emit physics",
        "automatic_foundational_choice_made_by_v14_64": False,
        "postcomparison_branch_selection_forbidden": True,
    }


def completion_gate_payload() -> dict[str, Any]:
    return {
        "version": VERSION,
        "primary_verdict": PRIMARY_VERDICT,
        "full_BHSM_complete": False,
        "mark_III": "NOT_REACHED",
        "frozen_predictions_changed": False,
        "official_prediction_logic_changed": False,
        "physical_prediction_emitted": False,
        "usb_touched": False,
        "v14_59_cap_inverse_problem_architecturally_bypassed": True,
        "v14_60_global_envelopment_selection_retained": True,
        "v14_63_cutoff_profile_independence_result_retained": True,
        "v14_64_envelopment_incidence_architecture_derived": True,
        "naive_continuum_direct_sum_spectral_triple_closed": False,
        "heat_semigroup_branch_authoritatively_adopted": False,
        "missing_checks": [
            "self-adjoint continuum relative/boundary spectral correspondence",
            "complete action-derived domain and Calderon/boundary projector",
            "one loop holonomy derived from action-owned connection/orientation data",
            "microscopic functional selected before physical comparison",
            "complete ghost and zero-mode quotient",
            "full mixed-dimensional heat coefficients",
            "global cosmological-parent/particle-child stationary solution",
            "effective fermion/current operator derived on that solution",
            "branch exhaustion and gauge-reduced Hessian",
            "DtN and relative heat kernel physical bundle",
            "zero-retuning neutrino kill screen",
            "downstream physical masses/mixing/couplings only after all gates pass",
        ],
        "exact_next_object": EXACT_NEXT_OBJECT,
    }


def master_payload() -> dict[str, Any]:
    return {
        "version": VERSION,
        "title": "BHSM envelopment spectral correspondence",
        "primary_verdict": PRIMARY_VERDICT,
        "heat_branch_verdict": HEAT_BRANCH_VERDICT,
        "trace_verdict": TRACE_VERDICT,
        "holonomy_verdict": HOLONOMY_VERDICT,
        "incidence": incidence_distance_payload(),
        "holonomy": gauge_holonomy_witness(),
        "trace_map": trace_map_obstruction_payload(),
        "heat_semigroup": heat_semigroup_profile_payload(),
        "geometric_trace": geometric_trace_payload(),
        "finite_fermion": finite_fermion_operator_payload(),
        "status": candidate_status_payload(),
        "exact_next_object": EXACT_NEXT_OBJECT,
        "physical_BHSM_prediction": False,
    }


def artifact_payloads() -> dict[str, dict[str, Any]]:
    return {
        "BHSM_envelopment_spectral_correspondence_v14_64.json": master_payload(),
        "BHSM_envelopment_incidence_distance_gate_v14_64.json": incidence_distance_payload(),
        "BHSM_diamond_holonomy_gate_v14_64.json": gauge_holonomy_witness(),
        "BHSM_trace_map_obstruction_v14_64.json": trace_map_obstruction_payload(),
        "BHSM_heat_semigroup_profile_gate_v14_64.json": heat_semigroup_profile_payload(),
        "BHSM_geometric_cross_stratum_trace_gate_v14_64.json": geometric_trace_payload(),
        "BHSM_finite_fermion_operator_reclassification_v14_64.json": finite_fermion_operator_payload(),
        "BHSM_next_branch_gate_v14_64.json": next_branch_gate_payload(),
        "BHSM_completion_gate_v14_64.json": completion_gate_payload(),
    }


def materialize(directory: str | Path) -> list[Path]:
    root = Path(directory)
    root.mkdir(parents=True, exist_ok=True)
    written = []
    for name, payload in sorted(artifact_payloads().items()):
        path = root / name
        path.write_bytes(canonical_json_bytes(payload) + b"\n")
        written.append(path)
    return written
