"""BHSM v14.63 stratified Dirac/zeta microscopic-source exhaustion gate.

This sprint tests the strongest internal zero-input compression candidate left
by v14.62: replace independently owned M8, M5 and intrinsic M4 Wilson data by
one stratified Dirac/spectral functional.

Three mathematically distinct constructions are separated rather than blurred:

1. zeta-regularized induced determinant / one-loop effective action;
2. the local zeta action zeta_P(0) ~ a_d(P) on a d-dimensional stratum;
3. a cutoff spectral action Tr f(P/Lambda^2).

The module is deliberately fail-closed.  It does not select a cutoff profile,
cross-stratum trace normalization, finite Dirac/Yukawa data, renormalization
conditions or physical scale from measured particle data.

No physical predictions are emitted.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
import hashlib
import json
import math
from typing import Any, Iterable, Mapping, Sequence

import numpy as np

VERSION = "v14.63"

PRIMARY_VERDICT = (
    "BHSM_V14_63_THE_FULL_STRATIFIED_DIRAC_ZETA_CANDIDATE_DOES_NOT_YET_CLOSE_"
    "ZERO_INPUT_BHSM_BECAUSE_A_PURE_ZETA_DETERMINANT_FIXES_THE_NONLOCAL_AND_"
    "LOG_ANOMALY_PART_BUT_REQUIRES_LOCAL_RENORMALIZED_COUNTERTERMS_THE_LOCAL_"
    "ZETA_A_D_ACTION_OMITS_THE_RELEVANT_LOWER_HEAT_COEFFICIENTS_NEEDED_FOR_M8_"
    "AND_M5_VOLUME_EINSTEIN_TERMS_AND_A_CUTOFF_SPECTRAL_ACTION_CAN_GENERATE_"
    "THEM_ONLY_AFTER_A_CUTOFF_PROFILE_GLOBAL_CROSS_STRATUM_TRACE_AND_FINITE_"
    "DIRAC_DATA_ARE_DEFINED_SO_THE_CURRENT_ARCHIVE_CONTAINS_NO_DERIVED_SINGLE_"
    "MICROSCOPIC_FUNCTIONAL_THAT_FIXES_ALL_M8_M5_AND_M4_WILSON_FAMILIES"
)

MOMENT_VERDICT = (
    "BHSM_V14_63_FOR_A_GENERIC_CUTOFF_SPECTRAL_ACTION_THE_HEAT_MOMENTS_"
    "REQUIRED_BY_MIXED_8D_5D_4D_STRATA_ARE_FUNCTIONALLY_INDEPENDENT_BEFORE_A_"
    "SPECIFIC_CUTOFF_PROFILE_IS_DECLARED_SO_ONE_COMMON_ACTION_NORMALIZATION_"
    "DOES_NOT_FIX_THEIR_RATIOS"
)

ZETA_VERDICT = (
    "BHSM_V14_63_ZETA_REGULARIZATION_DETERMINES_THE_SPECTRAL_NONLOCAL_PART_AND_"
    "THE_LOG_SCALE_RESPONSE_ONCE_THE_OPERATOR_IS_FIXED_BUT_THE_FINITE_LOCAL_"
    "COUNTERTERM_COEFFICIENTS_ARE_RENORMALIZATION_DATA_AND_CANNOT_BE_READ_OFF_"
    "FROM_THE_DETERMINANT_ALONE"
)

LOCAL_ZETA_VERDICT = (
    "BHSM_V14_63_THE_LOCAL_ZETA_ACTION_ZETA_P_0_EQUALS_THE_DIMENSION_MATCHED_"
    "HEAT_COEFFICIENT_UP_TO_ZERO_MODES_AND_BOUNDARY_DETAILS_AND_THEREFORE_CANNOT_"
    "BY_ITSELF_GENERATE_THE_LOWER_A0_A2_RELEVANT_TERMS_NEEDED_FOR_PARENT_AND_CAP_"
    "VOLUME_AND_EINSTEIN_SECTORS"
)

EXACT_NEXT_OBJECT = (
    "GLOBAL_STRATIFIED_SPECTRAL_TRIPLE_OR_EQUIVALENT_MICROSCOPIC_PRINCIPLE_"
    "THAT_PREDECLARES_THE_CROSS_STRATUM_HILBERT_TRACE_NORMALIZATION_CUTOFF_"
    "PROFILE_OR_RENORMALIZATION_CONDITIONS_AND_FINITE_DIRAC_DATA_BEFORE_ANY_"
    "PHYSICAL_COMPARISON_THEN_REDERIVE_THE_M8_M5_M4_COEFFICIENT_RATIOS_RUN_THE_"
    "GLOBAL_ENVELOPMENT_BVP_BRANCH_EXHAUSTION_GAUGE_REDUCED_HESSIAN_DTN_RELATIVE_"
    "HEAT_KERNEL_AND_ZERO_RETUNING_NEUTRINO_KILL_SCREEN"
)

REQUIRED_MOMENT_ORDERS = (8, 6, 5, 4, 3, 2, 0)


@dataclass(frozen=True)
class CandidateStatus:
    name: str
    can_generate_nonlocal_spectral_response: bool
    can_generate_relevant_volume_EH_terms: bool
    needs_new_profile_or_renormalization_data: bool
    fixes_finite_dirac_yukawa_data: bool
    zero_input_complete_from_current_archive: bool
    note: str


def canonical_json_bytes(payload: Any) -> bytes:
    return json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    ).encode("utf-8")


def sha256_payload(payload: Any) -> str:
    return hashlib.sha256(canonical_json_bytes(payload)).hexdigest()


def exponential_cutoff_moment(order: int, rate: float) -> float:
    """Normalized moment for f(u)=exp(-rate*u).

    For order p>0 use
        F_p = 1/Gamma(p/2) int_0^infty f(u) u^(p/2-1) du = rate^(-p/2).
    For p=0 use F_0=f(0)=1.
    This normalization is sufficient for moment-rank/independence witnesses.
    """
    p = int(order)
    a = float(rate)
    if p < 0:
        raise ValueError("order must be nonnegative")
    if not math.isfinite(a) or a <= 0.0:
        raise ValueError("rate must be positive and finite")
    if p == 0:
        return 1.0
    return a ** (-0.5 * p)


def mixture_moment(order: int, rates: Sequence[float], weights: Sequence[float]) -> float:
    if len(rates) != len(weights) or len(rates) == 0:
        raise ValueError("rates and weights must have equal nonzero length")
    return float(sum(float(w) * exponential_cutoff_moment(order, float(a)) for a, w in zip(rates, weights)))


def moment_matrix(orders: Sequence[int], rates: Sequence[float]) -> np.ndarray:
    return np.asarray(
        [[exponential_cutoff_moment(int(p), float(a)) for a in rates] for p in orders],
        dtype=float,
    )


def matrix_rank_with_tol(matrix: np.ndarray, rtol: float = 1e-12) -> int:
    s = np.linalg.svd(np.asarray(matrix, dtype=float), compute_uv=False)
    if s.size == 0:
        return 0
    tol = float(rtol) * float(s[0])
    return int(np.count_nonzero(s > tol))


def nullspace(matrix: np.ndarray, rtol: float = 1e-12) -> np.ndarray:
    a = np.asarray(matrix, dtype=float)
    u, s, vh = np.linalg.svd(a, full_matrices=True)
    if s.size == 0:
        return np.eye(a.shape[1], dtype=float)
    tol = float(rtol) * float(s[0])
    rank = int(np.count_nonzero(s > tol))
    return vh[rank:].T.copy()


def cutoff_moment_rank_witness() -> dict[str, Any]:
    """Executable witness that generic mixed-dimensional heat moments are independent.

    A seven-exponential basis is used only as a theorem witness.  At a strictly
    positive base weight vector, sufficiently small nullspace perturbations
    remain positive cutoff mixtures.  We preserve F0 and F4 exactly to numeric
    precision while changing F8, proving that even after fixing a common
    normalization and one dimension-four normalization, higher-dimensional
    coefficients are not forced by generic spectral-action kinematics.
    """
    orders = np.asarray(REQUIRED_MOMENT_ORDERS, dtype=int)
    rates = np.asarray((0.55, 0.8, 1.1, 1.6, 2.3, 3.4, 5.2), dtype=float)
    m = moment_matrix(orders, rates)
    rank = matrix_rank_with_tol(m)
    singular = np.linalg.svd(m, compute_uv=False)

    preserve_orders = (0, 4)
    c = moment_matrix(preserve_orders, rates)
    ns = nullspace(c)
    target = moment_matrix((8,), rates).reshape(-1)
    projection = ns @ (ns.T @ target)
    projection_norm = float(np.linalg.norm(projection))
    if projection_norm <= 1e-12:
        raise RuntimeError("unexpected target projection degeneracy")
    direction = projection / projection_norm

    base_weights = np.ones(len(rates), dtype=float)
    max_step = float(np.min(base_weights[np.abs(direction) > 1e-15] / np.abs(direction[np.abs(direction) > 1e-15])))
    epsilon = 0.05 * max_step
    perturbed = base_weights + epsilon * direction
    if np.min(perturbed) <= 0.0:
        raise RuntimeError("positive-cutoff witness lost positivity")

    base = {str(int(p)): mixture_moment(int(p), rates, base_weights) for p in orders}
    alt = {str(int(p)): mixture_moment(int(p), rates, perturbed) for p in orders}
    diffs = {k: alt[k] - base[k] for k in base}

    return {
        "version": VERSION,
        "verdict": MOMENT_VERDICT,
        "moment_orders": [int(x) for x in orders],
        "rates": [float(x) for x in rates],
        "moment_matrix_rank": rank,
        "moment_matrix_dimension": list(m.shape),
        "smallest_singular_value": float(singular[-1]),
        "largest_singular_value": float(singular[0]),
        "preserved_moments": ["F0", "F4"],
        "base_weights": [float(x) for x in base_weights],
        "perturbed_weights": [float(x) for x in perturbed],
        "all_perturbed_weights_positive": bool(np.min(perturbed) > 0.0),
        "base_moments": base,
        "perturbed_moments": alt,
        "moment_differences": diffs,
        "F0_preservation_residual": abs(diffs["0"]),
        "F4_preservation_residual": abs(diffs["4"]),
        "F8_change": diffs["8"],
        "interpretation": (
            "A generic cutoff profile has enough functional freedom to vary the heat moments used by mixed 8D/5D/4D strata. "
            "A specific profile can relate them, but selecting that profile is new microscopic theory data rather than a consequence of the current stratified action."
        ),
        "physical_BHSM_prediction": False,
    }


def zeta_logdet_rescaling_shift(zeta_zero: float, operator_scale: float) -> float:
    """Shift in log det_zeta(alpha P) relative to log det_zeta(P).

    alpha must be positive.  Since zeta_{alpha P}(s)=alpha^{-s} zeta_P(s),
    log det_zeta(alpha P)=log det_zeta(P)+zeta_P(0) log(alpha).
    """
    z0 = float(zeta_zero)
    alpha = float(operator_scale)
    if not math.isfinite(z0):
        raise ValueError("zeta_zero must be finite")
    if not math.isfinite(alpha) or alpha <= 0.0:
        raise ValueError("operator_scale must be positive and finite")
    return z0 * math.log(alpha)


def zeta_renormalization_payload() -> dict[str, Any]:
    examples = []
    for z0, alpha in ((1.5, 4.0), (-2.0, 0.25), (0.0, 9.0)):
        examples.append({
            "zeta_0": z0,
            "operator_scale_alpha": alpha,
            "logdet_shift": zeta_logdet_rescaling_shift(z0, alpha),
        })
    return {
        "version": VERSION,
        "verdict": ZETA_VERDICT,
        "definition": "Gamma_ind=(1/2) STr log_det_zeta(P/mu^2), with statistics/ghost signs fixed once the gauge-fixed operator bundle is fixed",
        "scale_law": "log det_zeta(alpha P)=log det_zeta(P)+zeta_P(0) log(alpha)",
        "examples": examples,
        "nonlocal_finite_spectral_part_fixed_by_operator": True,
        "log_scale_anomaly_fixed_by_zeta_0": True,
        "local_relevant_counterterms_required_in_renormalized_EFT": True,
        "finite_local_counterterm_parts_fixed_by_determinant_alone": False,
        "renormalization_conditions_required": True,
        "physical_parent_child_operator_bundle_required": True,
        "zero_input_all_Wilson_coefficients_derived": False,
    }


def local_zeta_coverage_payload() -> dict[str, Any]:
    rows = [
        {
            "stratum": "M8",
            "dimension": 8,
            "local_zeta_term": "a8(P8) (mod zero-mode/boundary conventions)",
            "needed_relevant_terms": ["Lambda^8 F8 a0 volume/potential", "Lambda^6 F6 a2 Einstein/two-derivative"],
            "needed_terms_generated_by_zeta_0_alone": False,
        },
        {
            "stratum": "M5",
            "dimension": 5,
            "local_zeta_term": "a5(P5) including allowed boundary contributions where present",
            "needed_relevant_terms": ["Lambda^5 F5 a0 volume/potential", "Lambda^3 F3 a2 Einstein/scalar two-derivative"],
            "needed_terms_generated_by_zeta_0_alone": False,
        },
        {
            "stratum": "M4",
            "dimension": 4,
            "local_zeta_term": "a4(P4)",
            "needed_relevant_terms": ["a4 gauge/curvature-squared dimension-four sector"],
            "needed_terms_generated_by_zeta_0_alone": True,
            "warning": "finite Dirac/Yukawa entries remain operator data unless independently derived",
        },
    ]
    return {
        "version": VERSION,
        "verdict": LOCAL_ZETA_VERDICT,
        "rows": rows,
        "local_zeta_can_compress_dimension_four_M4_coefficients": True,
        "local_zeta_generates_M8_M5_relevant_volume_EH_terms": False,
        "absolute_scale_generated": False,
    }


def cutoff_spectral_expansion_payload() -> dict[str, Any]:
    return {
        "version": VERSION,
        "definition": "S_f(P,Lambda)=STr f(P/Lambda^2)",
        "asymptotic_structure": "sum_s sum_k F_(d_s-k) Lambda^(d_s-k) a_k(P_s), plus boundary terms for strata with boundary",
        "required_moment_examples": {
            "M8": ["F8*a0", "F6*a2", "F4*a4", "F2*a6", "F0*a8"],
            "M5": ["F5*a0", "F3*a2", "F1*a4", "boundary half-integer/integer coefficients according to domain"],
            "M4": ["F4*a0", "F2*a2", "F0*a4"],
        },
        "generic_required_moment_orders_tested": list(REQUIRED_MOMENT_ORDERS),
        "specific_profile_would_relate_moments": True,
        "profile_selected_by_current_BHSM_axioms": False,
        "single_common_Lambda_selected_by_current_archive": False,
        "global_cross_stratum_trace_defined_by_current_archive": False,
        "therefore_zero_input_completion": False,
    }


def finite_dirac_data_payload() -> dict[str, Any]:
    return {
        "version": VERSION,
        "canonical_dimension_four_trace_result_retained": {
            "gauge_trace_ratio": "K_Y:K_2:K_3=5/3:1:1",
            "historical_1_2_7_derived": False,
            "xi": 0.0,
        },
        "spectral_action_dependence": {
            "representation_multiplicities": "can fix gauge trace ratios after the representation is declared",
            "finite_Dirac_entries": "enter Higgs/Yukawa invariants such as traces of Y^dagger Y and higher powers",
            "Yukawa_values_derived_by_spectral_trace_alone": False,
            "flavor_mixings_derived_by_spectral_trace_alone": False,
        },
        "authoritative_v7_1_ownership": "intrinsic M4 Standard-Model fields and finite representation/sector data remain independent unless a new microscopic relation is adopted",
        "zero_input_flavor_closed": False,
    }


def global_spectral_triple_requirement_payload() -> dict[str, Any]:
    return {
        "version": VERSION,
        "required_new_foundational_object": "GLOBAL_STRATIFIED_SPECTRAL_TRIPLE_OR_EQUIVALENT_MICROSCOPIC_OPERATOR_MEASURE_PRINCIPLE",
        "must_fix_before_physical_comparison": [
            "Hilbert space / bundle for M8, M5 and M4 sectors",
            "global self-adjoint Dirac-type operator and compatibility/off-diagonal domains",
            "cross-stratum trace normalization and field multiplicities",
            "grading/statistics and complete ghost complex",
            "cutoff profile f and common cutoff/scale rule, OR renormalization conditions replacing a cutoff spectral action",
            "finite Dirac/internal operator data or a theorem deriving them",
            "zero-mode collective-coordinate quotient and determinant phase/eta convention",
        ],
        "may_be_new_theory_definition": True,
        "is_already_derived_in_current_archive": False,
        "cannot_be_selected_using_neutrino_mass_CKM_PMNS_or_coupling_targets": True,
    }


def candidate_statuses() -> tuple[CandidateStatus, ...]:
    return (
        CandidateStatus(
            "PURE_ZETA_INDUCED_DETERMINANT",
            True,
            False,
            True,
            False,
            False,
            "Fixes nonlocal determinant/log anomaly for a fixed operator, but renormalized local Wilson terms have scheme-dependent finite parts.",
        ),
        CandidateStatus(
            "LOCAL_ZETA_A_D",
            False,
            False,
            False,
            False,
            False,
            "Compresses dimension-matched local a_d data, especially M4 a4, but cannot supply M8/M5 lower relevant heat coefficients or absolute scale.",
        ),
        CandidateStatus(
            "CUTOFF_SPECTRAL_ACTION",
            True,
            True,
            True,
            False,
            False,
            "Can generate relevant local terms only after a cutoff profile, cross-stratum trace and finite Dirac data are declared. Those are not selected by the current archive.",
        ),
    )


def micro_source_exhaustion_payload() -> dict[str, Any]:
    return {
        "version": VERSION,
        "primary_verdict": PRIMARY_VERDICT,
        "candidates": [asdict(x) for x in candidate_statuses()],
        "cutoff_moment_rank": cutoff_moment_rank_witness()["moment_matrix_rank"],
        "required_generic_moment_count": len(REQUIRED_MOMENT_ORDERS),
        "pure_zeta_all_local_Wilson_coefficients_derived": False,
        "local_zeta_all_strata_derived": False,
        "cutoff_spectral_action_all_inputs_derived_from_current_axioms": False,
        "single_microscopic_functional_derived_in_current_archive": False,
        "measured_particle_data_used": False,
        "v14_59_global_cap_bypass_retained": True,
        "v14_62_GHY_and_common_normalization_quotient_retained": True,
    }


def next_branch_gate_payload() -> dict[str, Any]:
    return {
        "version": VERSION,
        "branch_A": {
            "name": "FINITE_INPUT_STRATIFIED_EFT",
            "status": "AVAILABLE",
            "rule": "hash-freeze independent Wilson/operator/renormalization data before comparison",
            "zero_input_claim_allowed": False,
        },
        "branch_B": {
            "name": "ZERO_INPUT_MICROSCOPIC_UNIFICATION",
            "status": "OPEN_FOUNDATIONAL_OBJECT_REQUIRED",
            "exact_required_object": global_spectral_triple_requirement_payload()["required_new_foundational_object"],
            "cutoff_profile_or_renormalization_conditions_must_be_predeclared": True,
            "finite_Dirac_data_must_be_derived_or_predeclared": True,
            "postcomparison_selection_forbidden": True,
        },
        "automatic_foundational_choice_made_by_v14_63": False,
        "reason": "Testing the strongest candidate is not authority to add a new microscopic postulate merely because it would force completion.",
    }


def completion_gate_payload() -> dict[str, Any]:
    checks = {
        "v14_59_local_cap_inverse_problem_bypassed": True,
        "global_envelopment_architecture_retained": True,
        "GHY_relative_coefficient_closed": True,
        "common_classical_normalization_quotiented": True,
        "zeta_nonlocal_prefactor_statistics_fixed": True,
        "pure_zeta_local_counterterms_zero_input_fixed": False,
        "local_zeta_generates_M8_M5_relevant_terms": False,
        "cutoff_profile_derived_from_current_axioms": False,
        "global_cross_stratum_trace_derived": False,
        "finite_Dirac_data_derived": False,
        "all_M8_M5_M4_Wilson_families_derived": False,
        "physical_global_parent_child_BVP_completed": False,
        "physical_DtN_relative_heat_kernel_completed": False,
        "zero_retuning_neutrino_kill_screen_executed": False,
    }
    missing = [k for k, v in checks.items() if not v]
    return {
        "version": VERSION,
        "primary_verdict": PRIMARY_VERDICT,
        "checks": checks,
        "missing_checks": missing,
        "full_BHSM_complete": False,
        "mark_III": "NOT_REACHED",
        "frozen_predictions_changed": False,
        "official_prediction_logic_changed": False,
        "physical_prediction_emitted": False,
        "usb_touched": False,
        "exact_next_object": EXACT_NEXT_OBJECT,
    }


def artifact_payloads() -> Mapping[str, dict[str, Any]]:
    return {
        "BHSM_stratified_Dirac_zeta_micro_source_exhaustion_v14_63.json": micro_source_exhaustion_payload(),
        "BHSM_cutoff_moment_rank_witness_v14_63.json": cutoff_moment_rank_witness(),
        "BHSM_zeta_renormalization_ambiguity_v14_63.json": zeta_renormalization_payload(),
        "BHSM_local_zeta_coverage_gate_v14_63.json": local_zeta_coverage_payload(),
        "BHSM_cutoff_spectral_expansion_gate_v14_63.json": cutoff_spectral_expansion_payload(),
        "BHSM_finite_Dirac_data_gate_v14_63.json": finite_dirac_data_payload(),
        "BHSM_global_spectral_triple_requirement_v14_63.json": global_spectral_triple_requirement_payload(),
        "BHSM_next_branch_gate_v14_63.json": next_branch_gate_payload(),
        "BHSM_completion_gate_v14_63.json": completion_gate_payload(),
    }


def materialize(output_dir: str | Path) -> list[Path]:
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    for name, payload in sorted(artifact_payloads().items()):
        path = out / name
        path.write_bytes(canonical_json_bytes(payload) + b"\n")
        written.append(path)
    return written
