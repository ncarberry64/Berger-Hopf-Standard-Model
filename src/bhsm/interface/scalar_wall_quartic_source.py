"""BHSM v6.30.7 scalar-wall quartic normalization and source audit.

The frozen scalar quartic is present in the provisional parent action, but
its field-normalization invariant coefficient is not selected by any licensed
repository mechanism.  This module records that obstruction without changing
the action, choosing a sign, fitting a value, or entering the scale phase.
"""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any


VERSION = "v6.30.7"
SPRINT = "bhsm-scalar-wall-quartic-source-v6-30-7"
SOURCE_MAIN_SHA = "f9b0d4ed11205d6a7d5e5d9f7cbf50bdde8f2715"
PRIMARY_VERDICT = (
    "BHSM_CORE_COMPLETION_BLOCKED_BY_UNSELECTED_SCALAR_QUARTIC_INVARIANT"
)
PARENT_FREEZE_ID = (
    "3131ff26bfa3ee1ec66465a7b714e7bde42718a120141f93e94819561e1227cc"
)
INTRODUCTION_COMMIT = "1a8e2bcad6cb892b75bbf4951a67de76dcebff55"
FREEZE_COMMIT = "c903a2b6788515196225c0634753826d0e7d241d"

G3_LAMBDA = 130.140781376473
G3_GEOMETRY = 2368.23593065773
VE4_LAMBDA = 260.281562752946
VE4_GEOMETRY = 3633.0356624841
G4_LAMBDA = 5.84444718718846
G4_GEOMETRY = 81.5773688846122
K0_REPRESENTATIVE = 6.673443432880105
EXACT_BRANCH_LAMBDA = -18.1974927890349085
STABILITY_THRESHOLD = -13.95809839182684

ARTIFACT_FILES = {
    "normalization": "BHSM_scalar_field_normalization_group_v6_30_7.json",
    "invariant": "BHSM_scalar_quartic_invariant_v6_30_7.json",
    "source": "BHSM_G5_action_source_ledger_v6_30_7.json",
    "selection": "BHSM_G5_candidate_selection_tests_v6_30_7.json",
    "incompatibility": (
        "BHSM_exact_branch_stability_incompatibility_v6_30_7.json"
    ),
    "verdict": "BHSM_scalar_quartic_selection_verdict_v6_30_7.json",
    "stability": (
        "BHSM_unconditional_local_stability_permission_v6_30_7.json"
    ),
    "scale": "BHSM_scale_phase_permission_v6_30_7.json",
    "gate": "BHSM_1_0_gate_update_v6_30_7.json",
}

GUARDS = {
    "measured_input_used": False,
    "fitted_parameter_used": False,
    "empirical_inverse_used": False,
    "branch_restoration_tuning_used": False,
    "stability_tuning_used": False,
    "new_action_term_added": False,
    "new_primitive_added": False,
    "new_scale_added": False,
    "renormalization_condition_selected": False,
    "vacuum_subtracted": False,
    "regulator_changed": False,
    "frozen_prediction_changed": False,
    "official_prediction_logic_changed": False,
    "physical_mass_claimed": False,
    "global_stability_claimed": False,
}


def deterministic_json(payload: dict[str, Any]) -> str:
    """Serialize artifacts identically on every supported platform."""

    return json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def scalar_redefinition(
    c: float,
    *,
    z5: float = 1.0,
    a5: float = -1.0,
    g5: float = 1.0,
    kappa1: float = 1.0,
    q: float = 1.0,
    k0: float = K0_REPRESENTATIVE,
) -> dict[str, float]:
    """Return the passive coefficient map for sigma_hat=c*sigma.

    The normalized mode convention uses
    ``u1_hat=sign(c) u1`` and ``q_hat=abs(c) q``.  Holding the orientation of
    ``u1`` fixed instead gives ``q_hat=c q``; both conventions describe the
    same field and canonical quartic.
    """

    if c == 0:
        raise ValueError("a scalar field redefinition requires c != 0")
    c2 = c * c
    c4 = c2 * c2
    sign = math.copysign(1.0, c)
    return {
        "c": c,
        "Z5_hat": z5 / c2,
        "A5_hat": a5 / c2,
        "G5_hat": g5 / c4,
        "kappa1_hat": kappa1,
        "mu_c": -a5 / z5,
        "mu_c_hat": -(a5 / c2) / (z5 / c2),
        "lambda5": kappa1 * g5 / (z5 * z5),
        "lambda5_hat": kappa1 * (g5 / c4) / ((z5 / c2) ** 2),
        "raw_u1_scale": c,
        "normalized_u1_orientation": sign,
        "q_hat_normalized_mode": abs(c) * q,
        "q_hat_fixed_mode_orientation": c * q,
        "raw_KKT_norm": c2,
        "normalized_KKT_norm": 1.0,
        "k0_hat": k0 / c2,
        "phi": math.sqrt(k0) * q,
        "phi_hat_normalized_mode": math.sqrt(k0 / c2) * abs(c) * q,
    }


def lambda5(kappa1: float, g5: float, z5: float) -> float:
    if z5 == 0:
        raise ValueError("Z5 must be nonzero")
    return kappa1 * g5 / (z5 * z5)


def factored_coefficients(
    lambda_5: float, *, z5: float = 1.0, kappa1: float = 1.0
) -> dict[str, float]:
    """Evaluate the v6.30.5 coefficients in invariant factored form."""

    return {
        "g3": (z5 / kappa1)
        * (G3_LAMBDA * lambda_5 + G3_GEOMETRY),
        "Omega3": -(z5 / kappa1)
        * (G3_LAMBDA * lambda_5 + G3_GEOMETRY),
        "VE4": (z5 * z5 / kappa1)
        * (VE4_LAMBDA * lambda_5 + VE4_GEOMETRY),
        "g4_can": (1.0 / kappa1)
        * (G4_LAMBDA * lambda_5 + G4_GEOMETRY),
    }


def candidate_selection_tests() -> list[dict[str, Any]]:
    """Audit every licensed candidate without importing a selector."""

    return [
        {
            "mechanism": "exact expansion of an existing frozen potential",
            "result": "TERM_PRESENT_VALUE_NOT_SELECTED",
            "evidence": [
                "artifacts/BHSM_minimal_parent_theory_freeze_v6_0_5.json",
                "artifacts/BHSM_minimal_parent_primitive_count_v6_0_5.json",
            ],
            "reason": (
                "the frozen polynomial contains G0, but the primitive ledger "
                "classifies G0/Zsigma^2 as independently unsourced"
            ),
        },
        {
            "mechanism": "variation of the frozen parent action",
            "result": "NO_SELECTION",
            "evidence": [
                "artifacts/BHSM_minimal_parent_action_equations_stress_v6_0_5.json"
            ],
            "reason": "variation produces G0 sigma^3; it does not determine G0",
        },
        {
            "mechanism": "field or canonical normalization",
            "result": "INVARIANT_EXPOSED_NOT_SELECTED",
            "evidence": [
                "artifacts/BHSM_action_normalization_hidden_input_audit_v6_0_9.json",
                "artifacts/BHSM_fixed_h_canonical_interaction_v6_30_5.json",
            ],
            "reason": "normalization removes redundant powers but leaves lambda5",
        },
        {
            "mechanism": "Z2 symmetry",
            "result": "ALLOWS_QUARTIC_NO_SIGN_OR_MAGNITUDE",
            "evidence": [
                "artifacts/BHSM_minimal_parent_theory_freeze_v6_0_5.json"
            ],
            "reason": "sigma -> -sigma forbids odd terms but permits any G0",
        },
        {
            "mechanism": "regularity and finite action",
            "result": "NO_SELECTION",
            "evidence": [
                "artifacts/BHSM_scalar_wall_action_convention_ledger_v6_1_5.json"
            ],
            "reason": (
                "regular finite profiles exist conditionally over coefficient "
                "domains; regularity supplies no coefficient equation"
            ),
        },
        {
            "mechanism": "cap exchange, two-cap gluing, and matcher consistency",
            "result": "NO_SELECTION",
            "evidence": [
                "artifacts/BHSM_fixed_h_nonlinear_boundary_map_v6_30_2.json",
                "artifacts/BHSM_fixed_h_amplitude_coordinate_v6_30_5.json",
            ],
            "reason": (
                "these conditions fix parity, trace, and reaction data; the "
                "bulk quartic remains an inherited primitive"
            ),
        },
        {
            "mechanism": "wall solution",
            "result": "CONDITIONAL_DOMAIN_ONLY",
            "evidence": [
                "artifacts/BHSM_scalar_wall_integral_identity_v6_1_5.json",
                "artifacts/BHSM_scalar_vacuum_energy_shift_v6_1_5.json",
            ],
            "reason": (
                "A5<0,G5>0 is the stable-wall solution domain, not an "
                "action-derived choice of sign or magnitude"
            ),
        },
        {
            "mechanism": "boundedness of the actual parent potential",
            "result": "CONDITIONAL_REQUIREMENT_NOT_FROZEN_SELECTOR",
            "evidence": [
                "artifacts/BHSM_minimal_parent_nonlinear_sigma_branch_v6_0_5.json",
                "docs/bhsm_minimal_parent_theory_kill_test_v6_0_5.md",
            ],
            "reason": (
                "G0>0 is required if one demands a globally bounded pure "
                "quartic truncation, but the frozen theory did not adopt "
                "global boundedness as a coefficient-selection axiom and "
                "explicitly records all coefficient signs as unselected"
            ),
        },
        {
            "mechanism": "critical-mode condition",
            "result": "FIXES_MU_C_NOT_LAMBDA5",
            "evidence": [
                "artifacts/BHSM_fixed_h_KKT_projectors_v6_30_5.json"
            ],
            "reason": "the linear kernel depends on mu_c=-A5/Z5, not G5",
        },
        {
            "mechanism": "geometric curvature, connection, or singlet spectrum",
            "result": "NO_QUARTIC_SOURCE",
            "evidence": [
                "artifacts/BHSM_parent_scalar_potential_source_map_v6_1.json"
            ],
            "reason": (
                "the source map explicitly finds no direct sigma quartic from "
                "P1 curvature, K_R, or the J=0 spectrum"
            ),
        },
        {
            "mechanism": "heavy-tower elimination",
            "result": "NO_PURE_SINGLET_TREE_SOURCE",
            "evidence": [
                "artifacts/BHSM_parent_scalar_potential_source_map_v6_1.json"
            ],
            "reason": "a local pure singlet polynomial stays in J=0",
        },
        {
            "mechanism": "exact-branch cancellation",
            "result": "REJECTED_FORBIDDEN_TUNING",
            "evidence": [
                "artifacts/BHSM_fixed_h_exact_branch_permission_v6_30_5.json"
            ],
            "reason": (
                "the cancellation is one algebraic locus, is not selected by "
                "the action, and lies in the local-quartic maximum domain"
            ),
        },
        {
            "mechanism": "quantum running or renormalization condition",
            "result": "NOT_RELEVANT_AND_NOT_DERIVED",
            "evidence": [
                "artifacts/BHSM_full_completion_blocker_ledger_v1_8.json"
            ],
            "reason": (
                "the BHSM 1.0 obstruction is already classical; no quantum "
                "action, scheme, or boundary value selects lambda5"
            ),
        },
        {
            "mechanism": "integration constant",
            "result": "NOT_APPLICABLE",
            "evidence": [
                "artifacts/BHSM_minimal_parent_theory_freeze_v6_0_5.json"
            ],
            "reason": "G0 is an action coefficient, not a solved field constant",
        },
    ]


def _common(artifact: str) -> dict[str, Any]:
    return {
        "artifact": artifact,
        "version": VERSION,
        "sprint": SPRINT,
        "source_main_sha": SOURCE_MAIN_SHA,
        "parent_action_path": (
            "artifacts/BHSM_minimal_parent_theory_freeze_v6_0_5.json"
        ),
        "parent_freeze_id": PARENT_FREEZE_ID,
        "original_introduction": {
            "commit": INTRODUCTION_COMMIT,
            "version": "v6.0.2",
            "classification": (
                "general Taylor coefficient in conditional scalar-potential "
                "architecture; source not derived"
            ),
            "first_frozen_action_commit": FREEZE_COMMIT,
            "first_frozen_action_version": "v6.0.5",
        },
        "exact_term": (
            "-integral sqrt(-G) G0 sigma^4/4 in M8; pushforward gives "
            "-integral N a^4 G5 sigma^4/4 in the M5 radial action"
        ),
        "coefficient_definition": (
            "G5=Vol(S3) G0 on the frozen internal slice; "
            "lambda5=kappa1 G5/Z5^2"
        ),
        "field_normalization": (
            "sigma_hat=c sigma, c!=0; Z5_hat=Z5/c^2, "
            "A5_hat=A5/c^2, G5_hat=G5/c^4"
        ),
        "invariant_combinations": [
            "mu_c=-A5/Z5",
            "lambda5=kappa1 G5/Z5^2",
            "canonical g4=(5.84444718718846 lambda5+81.5773688846122)/kappa1",
        ],
        "candidate_source_tests": (
            "artifacts/BHSM_G5_candidate_selection_tests_v6_30_7.json"
        ),
        "rejected_selection_mechanisms": [
            "stable-wall tuning",
            "exact-branch restoration tuning",
            "observed Higgs self-coupling or mass fitting",
            "vacuum-expectation-value fitting",
            "setting G5 to one by convention",
            "new sigma^4 or sigma^6 term",
            "cutoff or renormalization condition chosen for a target",
            "naturalness",
        ],
        "exact_symbolic_result": {
            "lambda5": "kappa1 G5/Z5^2 is invariant and independent",
            "g3": (
                "(Z5/kappa1)(130.140781376473 lambda5"
                "+2368.23593065773)"
            ),
            "Omega3": "-g3",
            "VE4": (
                "(Z5^2/kappa1)(260.281562752946 lambda5"
                "+3633.0356624841)"
            ),
            "g4_can": (
                "(1/kappa1)(5.84444718718846 lambda5"
                "+81.5773688846122)"
            ),
        },
        "certified_numerical_consequences": {
            "exact_branch_lambda5": EXACT_BRANCH_LAMBDA,
            "stability_threshold_lambda5": STABILITY_THRESHOLD,
            "threshold_minus_branch": (
                STABILITY_THRESHOLD - EXACT_BRANCH_LAMBDA
            ),
            "exact_branch_below_threshold": True,
            "g4_bracket_at_exact_branch": -24.776916660145155,
        },
        "completion_tier_impact": {
            "Tier_A": "BLOCKED_BY_UNSELECTED_DIMENSIONLESS_COEFFICIENT",
            "Tier_B": "NOT_ELIGIBLE_TIER_A_BLOCKED",
            "Tier_C": "NOT_ELIGIBLE_TIER_B_BLOCKED",
        },
        "release_blocking_status": {
            "release_blocking": True,
            "blocker_id": "RB-02_SCALAR_QUARTIC_INVARIANT_SELECTION",
            "affected_headline_artifacts": [
                "artifacts/BHSM_fixed_h_canonical_interaction_v6_30_5.json",
                "artifacts/BHSM_fixed_h_local_stability_v6_30_5.json",
                "artifacts/BHSM_scale_phase_permission_v6_30_5.json",
                "artifacts/BHSM_1_0_completion_gate.json",
            ],
        },
        "frozen_hash_status": "UNCHANGED_VERSION_SCOPED_FILES_ONLY",
        "validated": [
            "lambda5 is invariant under every nonzero constant scalar redefinition",
            "G0 is present in the frozen provisional action as an independent primitive",
            "the v6.30.5 coefficients factor through lambda5",
            "exact-branch cancellation and local quartic stability are incompatible",
        ],
        "invalidated": [
            "G5 can be removed completely by scalar normalization",
            "the stable-wall label selects G5>0",
            "exact-branch cancellation is a licensed coefficient selector",
            "the one-universal-scale allowance can absorb lambda5",
        ],
        "repaired": [
            "the blocker is stated in the invariant lambda5 rather than separate normalization-dependent G5 and Z5",
            "the parent term's presence is separated from derivation of its coefficient",
        ],
        "open": [
            "an action-derived selection rule for lambda5",
            "unconditional local quartic stability",
            "Tier A dimensionless parameter closure",
            "permission to enter the v6.31 scale phase",
        ],
        "primary_verdict": PRIMARY_VERDICT,
        **GUARDS,
    }


def normalization_payload() -> dict[str, Any]:
    payload = _common("BHSM_scalar_field_normalization_group_v6_30_7")
    payload["normalization_group"] = {
        "group": "R^times acting by sigma_hat=c sigma",
        "coefficient_action": {
            "Z5": "Z5/c^2",
            "A5": "A5/c^2",
            "G5": "G5/c^4",
            "kappa1": "kappa1",
            "mu_c": "mu_c",
            "lambda5": "lambda5",
        },
        "mode_and_amplitude": {
            "raw_mode": "u1_raw_hat=c u1 with KKT norm c^2",
            "normalized_mode": "u1_hat=sign(c)u1",
            "normalized_mode_amplitude": "q_hat=abs(c)q",
            "fixed_orientation_amplitude": "q_hat=cq",
            "normalized_KKT_norm": 1,
        },
        "canonical_map": {
            "k0_hat": "k0/c^2",
            "phi_hat": "sqrt(k0_hat) q_hat=phi in normalized-mode convention",
            "fixed_orientation_note": "phi_hat=sign(c)phi",
        },
        "reduced_force": {
            "coefficient": "g3_hat=g3/c^2",
            "fixed_orientation_function": "g_hat(q_hat)=c g(q)",
            "note": "the projected scalar equation is covariant, not invariant",
        },
        "potential_and_quartic": {
            "VE4_hat": "VE4/c^4",
            "potential_term": (
                "VE4_hat q_hat^4 divided by 4! equals "
                "VE4 q^4 divided by 4!"
            ),
            "g4_can_hat": "g4_can",
        },
    }
    return payload


def invariant_payload() -> dict[str, Any]:
    payload = _common("BHSM_scalar_quartic_invariant_v6_30_7")
    payload["classification"] = {
        "normalization_dependent": [
            "Z5",
            "A5",
            "G5",
            "q",
            "k0",
            "g3",
            "Omega3",
            "VE4",
        ],
        "dimensionless_invariant": ["mu_c", "lambda5"],
        "canonical_but_scale_dependent": [
            "g4_can=(5.84444718718846 lambda5+81.5773688846122)/kappa1"
        ],
        "physical_only_after_scale_closure": [
            "dimensionful canonical interaction strength",
            "particle mass or observable scalar scale",
        ],
    }
    payload["independence"] = {
        "field_redefinition_can_remove_G5_alone": False,
        "one_coefficient_may_be_conventionally_normalized": True,
        "remaining_invariant": "lambda5",
        "lambda5_selected": False,
        "official_dependency": "canonical quartic magnitude and local classification",
    }
    return payload


def source_payload() -> dict[str, Any]:
    payload = _common("BHSM_G5_action_source_ledger_v6_30_7")
    payload["provenance"] = {
        "architecture_entry": {
            "commit": INTRODUCTION_COMMIT,
            "artifact": (
                "artifacts/BHSM_energy_geometry_physicality_"
                "order_parameter_action_v6_0_2.json"
            ),
            "term": "U_sigma=A(C_EG)sigma^2/2+G(C_EG)sigma^4/4+O(sigma^6)",
            "status": "ARCHITECTURE_IDENTIFIED_SOURCE_NOT_DERIVED",
        },
        "frozen_parent_entry": {
            "commit": FREEZE_COMMIT,
            "artifact": (
                "artifacts/BHSM_minimal_parent_theory_freeze_v6_0_5.json"
            ),
            "term": "-G0 sigma^4/4",
            "status": "PROVISIONAL_ACTION_PRIMITIVE_FROZEN_NOT_DERIVED",
            "scalar_normalization_fixed": False,
        },
        "pushforward": {
            "artifact": (
                "artifacts/BHSM_scalar_wall_action_convention_"
                "ledger_v6_1_5.json"
            ),
            "map": "[Z5,A5,G5]=Vol(S3)[Zsigma,A0,G0]",
            "status": "CONDITIONAL_GEOMETRIC_PUSHFORWARD",
        },
        "supposed_parent_primitive": (
            "the independent scalar potential Taylor coefficient G(C_EG), "
            "later frozen as G0; no C_EG formula or geometric value was derived"
        ),
        "bulk_or_boundary_normalization_fixes_coefficient": False,
        "symmetry_fixes_sign_or_magnitude": False,
        "cap_gluing_fixes_coefficient": False,
        "two_cap_action_fixes_coefficient": False,
        "matcher_fixes_coefficient": False,
        "wall_solution_fixes_coefficient": False,
        "regularity_fixes_coefficient": False,
        "boundedness_status": (
            "conditional G0>0 requirement for a globally bounded pure "
            "quartic truncation; not an adopted frozen selector"
        ),
        "critical_mode_fixes": "mu_c only",
        "related_to_mu_c": False,
        "related_to_Z5_or_kappa1": (
            "only through the invariant lambda5 after normalization"
        ),
        "integration_constant": False,
        "independent_wilson_coefficient": True,
        "quantum_running_needed_for_classical_gate": False,
        "official_prediction_dependence": (
            "magnitude changes g3, VE4, and canonical g4; inequality changes "
            "the local minimum/maximum classification"
        ),
        "missing_parent_term": False,
        "missing_geometric_derivation_of_value": True,
    }
    return payload


def selection_payload() -> dict[str, Any]:
    payload = _common("BHSM_G5_candidate_selection_tests_v6_30_7")
    payload["tests"] = candidate_selection_tests()
    payload["summary"] = {
        "tested": len(payload["tests"]),
        "unique_value_selected": False,
        "sign_selected": False,
        "inequality_selected": False,
        "coefficient_redundant": False,
        "parent_term_absent": False,
        "classification": "OUTCOME_D",
    }
    return payload


def incompatibility_payload() -> dict[str, Any]:
    payload = _common(
        "BHSM_exact_branch_stability_incompatibility_v6_30_7"
    )
    payload["comparison"] = {
        "exact_branch_condition": (
            "lambda5=-2368.23593065773/130.140781376473"
        ),
        "exact_branch_certified_value": EXACT_BRANCH_LAMBDA,
        "quartic_minimum_condition": (
            "lambda5>-81.5773688846122/5.84444718718846"
        ),
        "stability_threshold_certified_value": STABILITY_THRESHOLD,
        "strict_inequality": (
            "lambda5_exact_branch < lambda5_stability_threshold"
        ),
        "certified_gap": STABILITY_THRESHOLD - EXACT_BRANCH_LAMBDA,
        "g4_bracket_at_branch": -24.776916660145155,
        "same_selected_value_can_restore_branch_and_be_minimum": False,
        "exact_branch_required_for_isolated_critical_configuration": False,
        "release_object": "reduced effective family through fourth order",
        "higher_order_at_cancellation": "POST_BHSM_1_0_RESEARCH_BACKLOG",
    }
    return payload


def verdict_payload() -> dict[str, Any]:
    payload = _common("BHSM_scalar_quartic_selection_verdict_v6_30_7")
    payload["outcome"] = {
        "classification": "D",
        "verdict": PRIMARY_VERDICT,
        "why_not_A": "no licensed mechanism selects lambda5",
        "why_not_B": "conditional wall/boundedness domains are not action selectors",
        "why_not_C": "lambda5 and canonical g4 remain invariant",
        "why_not_E": "the term is explicitly present in the frozen parent action",
        "why_not_F": "the action does not select the cancellation locus",
    }
    return payload


def stability_payload() -> dict[str, Any]:
    payload = _common(
        "BHSM_unconditional_local_stability_permission_v6_30_7"
    )
    payload["permission"] = {
        "unconditional_local_stability_permitted": False,
        "conditional_minimum": "lambda5>-13.95809839182684",
        "conditional_maximum": "lambda5<-13.95809839182684",
        "quartic_flat_threshold": "lambda5=-13.95809839182684",
        "stable_wall_domain_result": (
            "G5>0,Z5>0,kappa1>0 implies lambda5>0 and hence a strict "
            "local quartic minimum, conditional on that domain"
        ),
        "global_stability_claimed": False,
        "physical_mass_claimed": False,
        "result": "BHSM_UNCONDITIONAL_LOCAL_STABILITY_NOT_PERMITTED",
    }
    return payload


def scale_payload() -> dict[str, Any]:
    payload = _common("BHSM_scale_phase_permission_v6_30_7")
    payload["scale"] = {
        "v6_31_permitted": False,
        "dimensionless_structure_closed": False,
        "unselected_dimensionless_coefficient": "lambda5",
        "one_universal_scale_allowance_applies": False,
        "independent_dimensionful_normalization_derived": False,
        "stop_reason": (
            "Tier A remains blocked by lambda5; a dimensionless coefficient "
            "cannot be hidden in one universal dimensionful calibration"
        ),
        "result": (
            "BHSM_SCALE_BRIDGE_PHASE_NOT_PERMITTED_WITH_UNSELECTED_"
            "SCALAR_QUARTIC_INVARIANT"
        ),
    }
    return payload


def gate_payload() -> dict[str, Any]:
    payload = _common("BHSM_1_0_gate_update_v6_30_7")
    payload["gate_update"] = {
        "completion_contract": "artifacts/BHSM_1_0_completion_gate.json",
        "blocker": "RB-02",
        "previous_wording": "Scalar quartic invariant selection",
        "scientific_resolution": (
            "normalization redundancy removed; one genuine invariant "
            "dimensionless coefficient lambda5 remains unselected"
        ),
        "blocker_status": "OPEN_EXACT_UPSTREAM_SCIENTIFIC_BLOCKER",
        "gate_1_parent_action": (
            "term present, coefficient provenance/value unselected"
        ),
        "gate_4_dimensionless": "BLOCKED",
        "tier_A": "BLOCKED",
        "tier_B": "NOT_ELIGIBLE",
        "tier_C": "NOT_ELIGIBLE",
        "next_phase": None,
        "campaign_stop_rule": (
            "required dimensionless coefficient remains unselected"
        ),
        "campaign_may_continue_to_independent_downstream_work": False,
        "reason": (
            "the explicit campaign stop condition is reached before scale or "
            "downstream benchmark work"
        ),
    }
    return payload


def materialized_payloads() -> dict[str, dict[str, Any]]:
    return {
        "normalization": normalization_payload(),
        "invariant": invariant_payload(),
        "source": source_payload(),
        "selection": selection_payload(),
        "incompatibility": incompatibility_payload(),
        "verdict": verdict_payload(),
        "stability": stability_payload(),
        "scale": scale_payload(),
        "gate": gate_payload(),
    }


def materialize(root: Path) -> list[Path]:
    artifact_dir = root / "artifacts"
    artifact_dir.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    for key, payload in materialized_payloads().items():
        path = artifact_dir / ARTIFACT_FILES[key]
        path.write_text(deterministic_json(payload), encoding="utf-8", newline="\n")
        written.append(path)
    return written
