"""BHSM v14.62 coefficient-provenance quotient and zero-input exhaustion gate.

This module distinguishes four things that were intentionally conflated in the
v14.61 fail-closed ledger:

1. true Wilson/action inputs;
2. variational-completion coefficients fixed relative to an owned bulk term;
3. dynamical variables selected by the Euler-Lagrange/Floquet problem;
4. functional-determinant prefactors fixed by field statistics once the
   gauge-fixed operator content is specified.

The purpose is not to manufacture missing constants.  It is to remove false
"coefficient" blockers and then state exactly which independent action data
remain irreducible under the current stratified BHSM axioms.

Authoritative v7.1 ownership preserved by this package:
- M8 and M5 kinetic terms are independently typed Wilson data off shell;
- the intrinsic M4 Standard-Model action is boundary-localized fundamental data;
- GHY is the variational completion of its owned Einstein-Hilbert bulk term;
- no M4 term is relabeled as an M8 prediction.

No measured particle data are used anywhere in this module.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
import hashlib
import json
import math
from typing import Any, Mapping, Sequence

import numpy as np

VERSION = "v14.62"

PRIMARY_VERDICT = (
    "BHSM_V14_62_THE_V14_61_COEFFICIENT_LEDGER_REDUCES_AFTER_QUOTIENTING_"
    "COMMON_CLASSICAL_NORMALIZATION_FIXING_THE_GHY_RELATIVE_COEFFICIENT_"
    "RECLASSIFYING_THE_RELATIVE_DETERMINANT_PREFACTOR_AS_STATISTICS_DERIVED_"
    "AND_TREATING_RH_AND_TRANSVERSE_SHAPE_AMPLITUDES_AS_DYNAMICAL_VARIABLES_"
    "BUT_THE_AUTHORITATIVE_STRATIFIED_ACTION_STILL_CONTAINS_INDEPENDENT_M8_M5_"
    "AND_INTRINSIC_M4_WILSON_DATA_SO_ZERO_INPUT_PHYSICAL_COMPLETION_CANNOT_BE_"
    "DERIVED_FROM_THE_CURRENT_AXIOMS_WITHOUT_A_NEW_MICROSCOPIC_RELATION"
)

GHY_VERDICT = (
    "BHSM_V14_62_IN_THE_DIRICHLET_METRIC_CONVENTION_S_EH_EQUALS_C_R_INT_R_"
    "THE_REQUIRED_GHY_VARIATIONAL_COMPLETION_IS_S_GHY_EQUALS_2_C_R_INT_K_"
    "UP_TO_THE_ORIENTATION_SIGN_SO_GHY_IS_NOT_AN_INDEPENDENT_WILSON_COEFFICIENT"
)

DETERMINANT_VERDICT = (
    "BHSM_V14_62_ONCE_THE_GAUGE_FIXED_FIELD_CONTENT_DOMAIN_AND_MEASURE_"
    "CONVENTION_ARE_FIXED_THE_GAUSSIAN_LOG_DETERMINANT_PREFACTORS_ARE_FIXED_BY_"
    "STATISTICS_WHILE_THE_RENORMALIZED_RELATIVE_SPECTRAL_VALUE_STILL_REQUIRES_"
    "THE_PHYSICAL_PARENT_CHILD_OPERATORS_AND_LOCAL_COUNTERTERM_SCHEME"
)

ZERO_INPUT_VERDICT = (
    "BHSM_V14_62_GLOBAL_ENVELOPMENT_CAN_SELECT_FIELDS_SEAMS_CAPS_AND_RELATIONAL_"
    "MODULI_FOR_GIVEN_ACTION_DATA_BUT_IT_DOES_NOT_DERIVE_INDEPENDENT_WILSON_"
    "RATIOS_THAT_THE_CURRENT_STRATIFIED_ACTION_DECLARED_AS_SEPARATE_INPUTS"
)

EXACT_NEXT_OBJECT = (
    "MICROSCOPIC_SOURCE_CHOICE_GATE_EITHER_FREEZE_THE_FINITE_INPUT_STRATIFIED_"
    "EFT_WILSON_DATA_BEFORE_ANY_PHYSICAL_COMPARISON_OR_ADD_AND_DERIVE_A_SINGLE_"
    "MICROSCOPIC_FUNCTIONAL_RELATING_M8_M5_AND_M4_COEFFICIENTS_WITH_THE_"
    "STRONGEST_EXISTING_CANDIDATE_BEING_A_FULL_STRATIFIED_DIRAC_ZETA_INDUCED_"
    "ACTION_THEN_RUN_THE_GLOBAL_PARENT_CHILD_BVP_BRANCH_EXHAUSTION_DTN_RELATIVE_"
    "HEAT_KERNEL_AND_ZERO_RETUNING_NEUTRINO_GATE"
)


@dataclass(frozen=True)
class ProvenanceEntry:
    name: str
    v14_61_label: str
    v14_62_class: str
    status: str
    true_wilson_input: bool
    physical_ready: bool
    note: str


def canonical_json_bytes(payload: Any) -> bytes:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False).encode("utf-8")


def sha256_payload(payload: Any) -> str:
    return hashlib.sha256(canonical_json_bytes(payload)).hexdigest()


def ghy_required_coefficient(eh_coefficient: float) -> float:
    """Required GHY coefficient in S_EH=c_R int sqrt(g) R convention.

    With outward-normal orientation encoded in K, the relative magnitude is 2.
    Flipping the normal flips K rather than introducing a new Wilson parameter.
    """
    c = float(eh_coefficient)
    if not math.isfinite(c):
        raise ValueError("eh_coefficient must be finite")
    return 2.0 * c


def ghy_boundary_derivative_residual(eh_coefficient: float, ghy_coefficient: float) -> float:
    """Coefficient of the uncancelled normal-derivative boundary variation.

    The convention is chosen so cancellation is equivalent to c_GHY=2 c_EH.
    """
    return 2.0 * float(eh_coefficient) - float(ghy_coefficient)


def determinant_prefactor_ledger() -> dict[str, Any]:
    """Gaussian one-loop prefactors before local renormalization counterterms."""
    rows = [
        {
            "field": "real_boson",
            "quadratic_form": "(1/2) phi P phi",
            "effective_action_logdet": "+(1/2) log det' P",
            "positive_operator_prefactor": 0.5,
            "statistics": "commuting",
        },
        {
            "field": "complex_boson",
            "quadratic_form": "phi^* P phi",
            "effective_action_logdet": "+ log det' P",
            "positive_operator_prefactor": 1.0,
            "statistics": "commuting",
        },
        {
            "field": "dirac_fermion",
            "quadratic_form": "bar(psi) D psi",
            "effective_action_logdet": "- log det D = -(1/2) log det(D^dagger D) + phase",
            "positive_operator_prefactor": -0.5,
            "statistics": "Grassmann",
        },
        {
            "field": "complex_FP_ghost",
            "quadratic_form": "bar(c) M_FP c",
            "effective_action_logdet": "- log det' M_FP",
            "positive_operator_prefactor": -1.0,
            "statistics": "Grassmann",
        },
    ]
    return {
        "version": VERSION,
        "rows": rows,
        "prefactors_are_tunable_Wilson_coefficients": False,
        "operator_spectrum_required_for_numeric_value": True,
        "gauge_zero_mode_projector_required": True,
        "local_counterterm_scheme_still_required": True,
        "determinant_phase_or_eta_invariant_may_be_required": True,
    }


def provenance_quotient_ledger() -> tuple[ProvenanceEntry, ...]:
    return (
        ProvenanceEntry(
            "M8_volume_and_parent_potential_data", "A8 normalization open",
            "INDEPENDENT_PARENT_WILSON_FAMILY", "OPEN", True, False,
            "Vacuum/cosmological and parent-potential coefficients are not related to the M5/M4 coefficients by the current stratified action.",
        ),
        ProvenanceEntry(
            "M8_two_derivative_geometry_eta", "A6 normalization/background open",
            "INDEPENDENT_PARENT_WILSON_FAMILY", "OPEN", True, False,
            "The parent Einstein/carrier/eta sector remains independently normalized under the current action ownership.",
        ),
        ProvenanceEntry(
            "M5_cap_Einstein_scalar_data", "A3 physical normalization open",
            "INDEPENDENT_CAP_WILSON_FAMILY_WITH_FIXED_GHY_COMPLETION", "OPEN", True, False,
            "The cap Wilson data remain independent, but the GHY coefficient is fixed relative to the owned cap Einstein coefficient and is not an extra parameter.",
        ),
        ProvenanceEntry(
            "M4_intrinsic_local_action", "A0 complete normalized attachment open",
            "INDEPENDENT_INTRINSIC_M4_WILSON_FAMILY", "OPEN", True, False,
            "Gauge, Yukawa/Dirac, Higgs/scalar and current normalizations are intrinsic M4 data in the authoritative stratified action unless a new microscopic relation is adopted.",
        ),
        ProvenanceEntry(
            "relative_nonlocal_spectral", "Z full parent-child coefficient open",
            "STATISTICS_FIXED_PREFACTOR_NUMERIC_FUNCTIONAL_OPEN", "PARTIAL", False, False,
            "The Gaussian determinant coefficient is fixed by field statistics; the physical relative value is still unevaluated until the complete gauge-fixed parent/child operators and renormalization prescription exist.",
        ),
        ProvenanceEntry(
            "Berger_connection_curvature_endomorphism", "xi=0",
            "FOUNDATIONAL_CONNECTION_LOCK", "CLOSED", False, True,
            "The extra scalar curvature endomorphism branch remains locked to xi=0.",
        ),
        ProvenanceEntry(
            "three_transverse_shape_channels", "q_Lr amplitudes/phases open",
            "DYNAMICAL_ORBIT_VARIABLES_NOT_WILSON_INPUTS", "SOLVER_OPEN", False, False,
            "The channel basis is action-owned; amplitudes/phases are to be selected by the periodic global BVP/Floquet orbit, not inserted as Wilson coefficients.",
        ),
        ProvenanceEntry(
            "cosmological_parent_anchor", "R_H coupled value open",
            "DYNAMICAL_BACKGROUND_MODULUS_OR_EFFECTIVE_EXTERNAL_ANCHOR", "SOLVER_OPEN", False, False,
            "R_H is a solution variable on the zero-input coupled cosmology branch, or a frozen external anchor on the explicitly finite-input effective branch; it is not a local action coefficient.",
        ),
        ProvenanceEntry(
            "common_positive_classical_action_scale", "not separated in v14.61",
            "CONVENTIONAL_CLASSICAL_NORMALIZATION", "QUOTIENTED", False, True,
            "A common positive multiplier leaves the classical Euler-Lagrange zero set unchanged. Relative quantum/local weights must still be kept consistent.",
        ),
    )


def coefficient_quotient_payload() -> dict[str, Any]:
    ledger = provenance_quotient_ledger()
    true_inputs = [x.name for x in ledger if x.true_wilson_input]
    false_blockers = [x.name for x in ledger if not x.true_wilson_input and not x.physical_ready]
    ready = [x.name for x in ledger if x.physical_ready]
    return {
        "version": VERSION,
        "primary_verdict": PRIMARY_VERDICT,
        "true_independent_Wilson_families": true_inputs,
        "reclassified_non_Wilson_open_objects": false_blockers,
        "already_closed_or_quotiented": ready,
        "ledger": [asdict(x) for x in ledger],
        "measured_particle_data_used": False,
        "historical_1_2_7_used_as_constraint": False,
    }


def toy_stationary_point(c8: float, c5: float, c4: float) -> float:
    """Convex theorem witness for coefficient-ratio dependence.

    S(u)=1/2 c8 (u-1)^2 + 1/2 c5 (u+1)^2 + 1/2 c4 (u-2)^2.
    Coefficients are positive stratum weights.  A common rescaling cancels,
    but changing ratios changes the globally minimized u.
    """
    cs = np.asarray([c8, c5, c4], dtype=float)
    if cs.shape != (3,) or not np.all(np.isfinite(cs)) or np.any(cs <= 0):
        raise ValueError("all toy coefficients must be positive finite numbers")
    targets = np.asarray([1.0, -1.0, 2.0], dtype=float)
    return float(cs @ targets / np.sum(cs))


def common_normalization_invariance_payload() -> dict[str, Any]:
    base = (1.3, 0.8, 2.1)
    factor = 7.25
    u0 = toy_stationary_point(*base)
    u1 = toy_stationary_point(*(factor*x for x in base))
    altered = (1.3, 1.7, 2.1)
    ua = toy_stationary_point(*altered)
    return {
        "version": VERSION,
        "toy_model": "S=1/2 c8(u-1)^2+1/2 c5(u+1)^2+1/2 c4(u-2)^2",
        "base_coefficients": list(base),
        "common_rescaling_factor": factor,
        "base_stationary_point": u0,
        "rescaled_stationary_point": u1,
        "common_rescaling_difference": abs(u1-u0),
        "altered_ratio_coefficients": list(altered),
        "altered_ratio_stationary_point": ua,
        "ratio_change_effect": abs(ua-u0),
        "theorem_witness": "common normalization is redundant for the classical stationary set, independent coefficient ratios are not",
        "physical_BHSM_solution": False,
    }


def ghy_payload() -> dict[str, Any]:
    witnesses = []
    for c in (0.125, 1.0, 3.75):
        g = ghy_required_coefficient(c)
        witnesses.append({
            "c_EH": c,
            "required_c_GHY": g,
            "boundary_derivative_residual": ghy_boundary_derivative_residual(c, g),
        })
    return {
        "version": VERSION,
        "verdict": GHY_VERDICT,
        "convention": "S_EH=c_R integral_M sqrt(g) R; S_GHY=c_K integral_boundary sqrt(h) K",
        "required_relation": "c_K=2 c_R (orientation sign carried by outward normal/K)",
        "witnesses": witnesses,
        "GHY_is_independent_Wilson_input": False,
        "cap_Einstein_coefficient_is_derived": False,
    }


def dynamic_vs_wilson_payload() -> dict[str, Any]:
    return {
        "version": VERSION,
        "dynamical_variables": {
            "R_H": "varied cosmological/background modulus on the zero-input branch; frozen external anchor only on an explicitly finite-input branch",
            "x=log(R_child/R_parent)": "global nesting coordinate varied in the envelopment Euler-Lagrange system",
            "q_Lr(tau)": "moving-seam shape-harmonic coordinates selected by the periodic BVP/Floquet solution",
            "seam_X": "variational output of the global parent-child solution",
        },
        "not_allowed_as_post_comparison_fit_parameters": ["R_H", "x", "q_Lr(tau)", "seam_X"],
        "true_Wilson_families": coefficient_quotient_payload()["true_independent_Wilson_families"],
    }


def spectral_candidate_payload() -> dict[str, Any]:
    """Status of the strongest already-tested internal input-compression branch."""
    return {
        "version": VERSION,
        "branch": "CANONICAL_ZETA_LOCAL_A4_FOUNDATIONAL_DECLARATION",
        "adopted_into_authoritative_stratified_action": False,
        "derived_from_current_M8_to_M5_to_M4_correspondence": False,
        "dimension_four_common_normalization_can_be_fixed_by_declaration": True,
        "minimal_gravitational_ray": "(c_R2,c_Ricci2)=s(-2/3,2) modulo Euler density when xi=0",
        "xi": 0.0,
        "canonical_gauge_trace_ratio": "K_Y:K_2:K_3=5/3:1:1",
        "historical_1_2_7_derived": False,
        "absolute_scale_derived": False,
        "M8_parent_Wilson_family_derived": False,
        "M5_cap_Wilson_family_derived": False,
        "zero_input_completion_from_this_branch": False,
        "interpretation": "This branch is a possible new microscopic postulate/input-compression rule, not a theorem of the current stratified action.",
    }


def zero_input_no_go_payload() -> dict[str, Any]:
    toy = common_normalization_invariance_payload()
    true_inputs = coefficient_quotient_payload()["true_independent_Wilson_families"]
    checks = {
        "global_envelopment_varies_fields_not_Wilson_coefficients": True,
        "common_classical_normalization_quotiented": True,
        "relative_stratum_weight_changes_stationary_solution": toy["ratio_change_effect"] > 1e-6,
        "GHY_relative_coefficient_fixed": True,
        "determinant_statistics_prefactor_fixed": True,
        "q_Lr_reclassified_as_dynamical": True,
        "R_H_reclassified_as_dynamical_or_explicit_anchor": True,
        "independent_Wilson_families_remain": len(true_inputs) > 0,
        "current_action_contains_relation_deriving_all_remaining_Wilson_families": False,
    }
    return {
        "version": VERSION,
        "verdict": ZERO_INPUT_VERDICT,
        "checks": checks,
        "remaining_true_Wilson_families": true_inputs,
        "zero_input_completion_derivable_from_current_axioms": False,
        "global_envelopment_cap_selection_invalidated": False,
        "meaning": "The obstruction is coefficient provenance, not local cap reconstruction. A new microscopic coefficient relation would be new theory and must be stated before comparison.",
    }


def finite_input_branch_payload() -> dict[str, Any]:
    return {
        "version": VERSION,
        "branch": "FINITE_INPUT_STRATIFIED_EFT",
        "internally_well_typed_action_architecture": True,
        "can_run_global_BVP_after_inputs_and_operators_are_frozen": True,
        "zero_input_prediction_of_Standard_Model_parameters": False,
        "allowed_workflow": [
            "declare every independent Wilson datum and renormalization prescription before comparison",
            "hash-freeze the complete parameter/operator manifest",
            "solve the global parent-child BVP and branch search",
            "derive DtN/relative determinant and Floquet observables",
            "compare only after freeze",
            "treat any later parameter change as a new model version",
        ],
        "not_allowed": "using neutrino, mass, CKM/PMNS or coupling targets to choose unfrozen Wilson ratios while claiming zero-retuning derivation",
    }


def microscopic_choice_gate_payload() -> dict[str, Any]:
    return {
        "version": VERSION,
        "gate": "MICROSCOPIC_SOURCE_CHOICE_REQUIRED",
        "option_A": finite_input_branch_payload(),
        "option_B": {
            "branch": "ZERO_INPUT_MICROSCOPIC_UNIFICATION",
            "requirement": "derive a single microscopic functional or symmetry that relates the independently typed M8, M5 and intrinsic M4 Wilson data",
            "must_be_declared_before_physical_comparison": True,
            "must_reproduce_variational_GHY_relation": True,
            "must_preserve_xi_zero_connection_lock": True,
            "must_generate_complete_gauge_fixed_bosonic_fermionic_ghost_operators": True,
            "strongest_existing_candidate": spectral_candidate_payload(),
        },
        "automatic_choice_made_by_v14_62": False,
        "reason": "Choosing a new microscopic source is a theory-definition decision, not a coefficient derivation already contained in the present action.",
    }


def completion_gate_payload() -> dict[str, Any]:
    no_go = zero_input_no_go_payload()
    checks = {
        "v14_59_local_cap_inverse_problem_bypassed": True,
        "global_envelopment_architecture_retained": True,
        "GHY_variational_coefficient_closed_relative_to_EH": True,
        "common_classical_normalization_quotiented": True,
        "relative_determinant_prefactor_classified": True,
        "shape_channels_classified_as_dynamical": True,
        "R_H_classified_as_dynamical_or_explicit_anchor": True,
        "remaining_true_Wilson_families_identified": True,
        "all_remaining_Wilson_families_derived_from_current_axioms": False,
        "complete_physical_parent_child_operator_bundle": False,
        "physical_global_BVP_branch_exhaustion": False,
        "physical_DtN_relative_heat_kernel": False,
        "zero_retuning_neutrino_kill_screen_executed": False,
    }
    missing = [k for k,v in checks.items() if not v]
    return {
        "version": VERSION,
        "primary_verdict": PRIMARY_VERDICT,
        "checks": checks,
        "missing_checks": missing,
        "zero_input_no_go": no_go,
        "full_BHSM_complete": False,
        "mark_III": "NOT_REACHED",
        "physical_prediction_emitted": False,
        "frozen_predictions_changed": False,
        "official_prediction_logic_changed": False,
        "usb_touched": False,
        "exact_next_object": EXACT_NEXT_OBJECT,
    }


def artifact_payloads() -> Mapping[str, Any]:
    payloads = {
        "BHSM_coefficient_provenance_quotient_v14_62.json": coefficient_quotient_payload(),
        "BHSM_GHY_variational_completion_v14_62.json": ghy_payload(),
        "BHSM_determinant_prefactor_ledger_v14_62.json": determinant_prefactor_ledger(),
        "BHSM_dynamic_vs_Wilson_classification_v14_62.json": dynamic_vs_wilson_payload(),
        "BHSM_common_normalization_ratio_witness_v14_62.json": common_normalization_invariance_payload(),
        "BHSM_spectral_micro_source_candidate_v14_62.json": spectral_candidate_payload(),
        "BHSM_zero_input_no_go_v14_62.json": zero_input_no_go_payload(),
        "BHSM_microscopic_source_choice_gate_v14_62.json": microscopic_choice_gate_payload(),
        "BHSM_completion_gate_v14_62.json": completion_gate_payload(),
    }
    return payloads


def materialize(output_dir: str) -> list[str]:
    from pathlib import Path
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    written = []
    for name, payload in artifact_payloads().items():
        path = out / name
        path.write_bytes(canonical_json_bytes(payload) + b"\n")
        written.append(str(path))
    return written
