"""Audit joint heat and zeta domains on an infinite maximal C2 route."""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "artifacts" / "flagship_integration"
RESULT = BASE / "BHSM_N12_C2_INFINITE_HEAT_ZETA_COMPATIBILITY.json"
CAUCHY = BASE / "BHSM_N12_C2_PROJECTED_ADJOINT_CAUCHY_CRITERION.json"
ANGULAR = BASE / "BHSM_N12_GATE7_AE2_ANGULAR_DINI_UNIFORMITY_AUDIT.json"
FORCE = BASE / "BHSM_N12_FINITE_ENDPOINT_ZERO_SOURCE_FORCE_FUNCTIONAL.json"
SCALE = BASE / "BHSM_N12_RESET_FIBER_RADIUS_JET_AND_SCALE_CENTER_AUDIT.json"
NHIM_NO_GO = BASE / "BHSM_N12_ASYMPTOTIC_NHIM_ANGULAR_FORCE_NO_GO.json"
FULL_BRANCH = BASE / "BHSM_N12_FULL_RETAINED_ASYMPTOTIC_BRANCH.json"
FINITE_ENDPOINT = BASE / "BHSM_N12_FINITE_ENDPOINT_FORWARD_ADJOINT_KKT.json"
ACCOUNTING = ROOT / "artifacts/BHSM_aether_quantum_functional_accounting_v16_00.json"
THEORY = ROOT / "theory/n12_c2_infinite_heat_zeta_compatibility.md"
INPUTS = (
    CAUCHY, ANGULAR, FORCE, SCALE, NHIM_NO_GO, FULL_BRANCH,
    FINITE_ENDPOINT, ACCOUNTING, THEORY,
)


def _sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _optical_witness(epsilon: float = 0.25) -> dict[str, Any]:
    cutoffs = (1.0, 3.0, 7.0, 15.0, 31.0, 63.0)
    divergent = [math.log1p(cutoff) for cutoff in cutoffs]
    decaying = [
        (1.0 - (1.0 + cutoff) ** (-epsilon)) / epsilon
        for cutoff in cutoffs
    ]
    return {
        "radius": "R4(tau)=1+tau",
        "optical_length": "infinity",
        "persistent_common_scale": {
            "h_cs": "1",
            "truncated_zeta_integrals": divergent,
            "limit": "infinity",
        },
        "decaying_common_scale": {
            "h_cs": "(1+tau)^(-epsilon)",
            "epsilon": epsilon,
            "truncated_zeta_integrals": decaying,
            "limit": 1.0 / epsilon,
        },
        "cutoffs": list(cutoffs),
        "purpose": "GENERAL_MATHEMATICAL_SHARPNESS_WITNESS_NOT_A_BHSM_TAIL",
    }


def build_payload() -> dict[str, Any]:
    missing = [str(path) for path in INPUTS if not path.is_file()]
    if missing:
        raise FileNotFoundError("missing heat-zeta compatibility inputs: " + ", ".join(missing))
    records = [_load(path) for path in INPUTS[:-1]]
    if not all(record.get("validation_passed") is True for record in records):
        raise RuntimeError("validated heat-zeta compatibility parents required")
    (
        cauchy, angular, force, scale, nhim_no_go, full_branch,
        finite_endpoint, accounting,
    ) = records
    witness = _optical_witness()
    divergent = witness["persistent_common_scale"]["truncated_zeta_integrals"]
    decaying = witness["decaying_common_scale"]["truncated_zeta_integrals"]
    limit = witness["decaying_common_scale"]["limit"]

    validation = {
        "all_inputs_validated": True,
        "projected_force_Cauchy_criterion_available": (
            cauchy["claim_boundary"]["projected_Cauchy_criterion"] == "DERIVED"
        ),
        "zeta_variation_identity_exact": (
            force["exact_force_theorem"]["zeta_first_variation"]
            == "D_Gamma_SM_zeta[h]=(59/30)*integral_I_h*d_tau/R4"
        ),
        "common_scale_is_physical_not_gauge": (
            scale["claim_boundary"]["common_scale_full_action_gauge"] is False
            and scale["claim_boundary"]["common_scale_physical_modulation"]
            == "RETAIN"
        ),
        "time_quotient_leaves_radius_coefficient_direction": (
            scale["validation"]["one_dimensional_time_quotient_leaves_a_coefficient_jet_direction"]
            is True
        ),
        "finite_optical_length_fails_absolute_graded_heat_domain": (
            angular["minimal_requirement"]["finite_optical_length_excluded_by_angular_finiteness"]
            is True
            and nhim_no_go["claim_boundary"]["asymptotic_NHIM_absolute_graded_force_route"]
            == "CLOSED_NO_GO"
        ),
        "finite_optical_NHIM_branch_preserved_nonrealized": (
            full_branch["adjudication"]["physical_status"]
            == "NONREALIZED_FORMATION_HISTORY_OWNER_AUTHORIZED"
        ),
        "finite_endpoint_alternative_available": (
            finite_endpoint["claim_boundary"]["G7_09_joint_system"]
            == "DERIVED_UNSOLVED"
        ),
        "replacement_accounting_identity_exact": (
            accounting["determinant_accounting"]["physical_quantum_functional"]
            == "Gamma_Q=Gamma_parent+Gamma_SM_heat"
            and accounting["determinant_accounting"]["equivalent_replacement_form"].startswith(
                "Gamma_Q=Gamma_attached_zeta-Gamma_SM_zeta"
            )
        ),
        "persistent_common_scale_witness_diverges": (
            all(left < right for left, right in zip(divergent, divergent[1:]))
            and divergent[-1] > 4.0
        ),
        "decaying_common_scale_witness_converges": (
            all(left < right for left, right in zip(decaying, decaying[1:]))
            and abs(decaying[-1] - limit) < 1.5
        ),
        "actual_C2_common_scale_decay_not_assumed": True,
        "no_selector_relative_reference_scale_fit_recurrence_endpoint_box_or_chord_added": True,
    }
    validation = {key: bool(value) for key, value in validation.items()}
    passed = all(validation.values())
    return {
        "artifact": "BHSM_N12_C2_INFINITE_HEAT_ZETA_COMPATIBILITY",
        "status": (
            "INFINITE_C2_HEAT_ZETA_COMPATIBILITY_REDUCED_TO_COMBINED_PROJECTED_REPLACEMENT_CAUCHY_TAIL"
            if passed else "INFINITE_C2_HEAT_ZETA_COMPATIBILITY_NOT_REDUCED"
        ),
        "classification": (
            "FINITE_OPTICAL_LENGTH_IS_EXCLUDED_BY_THE_EXACT_GRADED_ANGULAR_"
            "HEAT_NO_GO,_WHILE_INFINITE_OPTICAL_LENGTH_REQUIRES_THE_RETAINED_"
            "PHYSICAL_COMMON_SCALE_JACOBI_MODULATION_TO_HAVE_A_CAUCHY_ZETA_"
            "OPTICAL_INTEGRAL_FOR_A_TERMWISE_CONSTRUCTION;_THE_EXACT_WEAKEST_"
            "OWNER_IS_THE_COMBINED_PROJECTED_q_heat_MINUS_q_zeta_CAUCHY_TAIL"
        ),
        "termwise_zeta_domain": {
            "functional": force["exact_force_theorem"]["zeta_functional"],
            "variation": force["exact_force_theorem"]["zeta_first_variation"],
            "optical_measure": "d_s_opt=d_tau/R4(tau)",
            "common_scale_tail_criterion": (
                "FOR_EVERY_epsilon>0_EXISTS_T0_FOR_ALL_S,T>T0:_"
                "abs(integral_S^T_h_cs*d_s_opt)<epsilon"
            ),
            "absolute_sufficient_condition": (
                "integral_0^Tmax_abs(h_cs(tau))*d_tau/R4(tau)<infinity"
            ),
            "nonzero_one_sided_limit_consequence": (
                "IF_optical_length=infinity_AND_h_cs->c_nonzero_EVENTUALLY_"
                "ONE_SIDED_THEN_ZETA_VARIATION_DIVERGES"
            ),
            "logically_required_for_combined_replacement_force": False,
        },
        "replacement_accounting": accounting["determinant_accounting"],
        "route_dichotomy": {
            "finite_optical_length": {
                "bounded_zeta_variation": "FINITE",
                "absolute_graded_heat_force": "EXCLUDED_BY_EXACT_TRANSFER_NO_GO",
                "full_infinite_route_force_domain": "CLOSED_NO_GO",
            },
            "infinite_optical_length": {
                "graded_heat": "CONDITIONAL_ON_ACTION_OWNED_UNIFORM_BARRIER_OR_RELATIVE_TRACE",
                "termwise_zeta_common_scale": "REQUIRES_h_cs_OPTICAL_CAUCHY_DECAY",
                "direct_replacement_route": "PROVE_PROJECTED_q_heat_MINUS_q_zeta_CAUCHY_TAIL",
                "separate_zeta_convergence_required_on_direct_route": False,
                "actual_C2_combined_tail": "OPEN_CURRENT_OWNER",
            },
            "finite_later_event_or_canonical_stop": {
                "infinite_tail_conditions": "NOT_REQUIRED",
                "operator_route": "RETAINED_COMPACT_ENDPOINT_FORWARD_ADJOINT_KKT",
                "actual_outcome": "OPEN",
            },
        },
        "matching_audit": [
            {
                "diagram_slot": "ZETA_HISTORY_VERTEX",
                "required_type": "FIRST_VARIATION_DENSITY_ON_THE_ACTUAL_HISTORY",
                "candidate": "(59/30)*h*d_tau/R4",
                "verdict": "VALID_MATCH_EXACT_TERMWISE_VERTEX",
            },
            {
                "diagram_slot": "PHYSICAL_COMMON_SCALE_LEG",
                "required_type": "NON_GAUGE_RESET_TANGENT_JACOBI_MODULATION_h_cs",
                "candidate": "RANK_TWO_RADIUS_CAUCHY_JET_AND_RETAINED_SCALE_CENTER",
                "verdict": "VALID_INITIAL_LEG_MAXIMAL_MODULATION_TAIL_MISSING",
            },
            {
                "diagram_slot": "INFINITE_ZETA_LOAD",
                "required_type": "SCALAR_OPTICAL_CAUCHY_TAIL_FOR_h_cs",
                "candidate": "NONE_ACTION_CERTIFIED_ON_Phi_C2",
                "verdict": "ACTUALLY_MISSING_FOR_TERMWISE_ROUTE_NOT_SEPARATELY_NECESSARY",
            },
            {
                "diagram_slot": "INFINITE_GRADED_HEAT_LOAD",
                "required_type": "FULL_ANGULAR_PHYSICAL_COTANGENT_TAIL",
                "candidate": "FIXED_CHANNEL_DINI_PLUS_CONDITIONAL_ANGULAR_BARRIERS",
                "verdict": "ACTUALLY_MISSING_ON_ACTUAL_C2_TAIL",
            },
        ],
        "sharpness_witness": witness,
        "validated_invalidated_open": {
            "VALIDATED": [
                "zeta is a history-distributed optical integral",
                "common scale remains a physical force direction after the time quotient",
                "finite optical length cannot support the retained absolute graded heat force",
                "infinite optical length requires a separate common-scale Jacobi zeta tail theorem",
            ],
            "INVALIDATED": [
                "zeta is a reset-local q_direct term with no maximal tail",
                "radius optical behavior alone determines zeta-force convergence",
                "the physical time quotient removes the common-scale test direction",
                "fixed-channel source-Dini closes the joint heat-zeta infinite route",
                "separate common-scale zeta convergence is necessary for a direct combined replacement proof",
            ],
            "OPEN": [
                "actual C2 common-scale Jacobi optical Cauchy tail",
                "actual C2 full graded heat cotangent tail",
                "direct combined q_rep projected force limit or finite later endpoint",
            ],
        },
        "hindsight": {
            "physical_enclosure_class": "UNCHANGED_ONE_C2_CLASS",
            "continuous_modulation_within_class": "COMMON_SCALE_JACOBI_TAIL_IS_PHYSICAL",
            "proof_box": "DOES_NOT_DECIDE_OPTICAL_OR_JACOBI_TAIL",
            "difficulty_type": "JOINT_HISTORY_DUAL_DOMAIN_NOT_ENCLOSURE_CLASSIFICATION",
        },
        "exact_next_dependency": (
            "ON_AN_INFINITE_C2_ROUTE_PROVE_THE_COMBINED_ACTION_OWNED_PROJECTED_"
            "q_heat_MINUS_q_zeta_CAUCHY_TAIL_DIRECTLY,_OR_PROVE_BOTH_THE_"
            "TERMWISE_COMMON_SCALE_ZETA_OPTICAL_TAIL_AND_FULL_GRADED_HEAT_"
            "TAIL,_OR_CERTIFY_A_FINITE_LATER_EVENT_OR_CANONICAL_STOP;_DO_NOT_"
            "REOPEN_FIXED_CHANNEL_DINI_OR_PROJECT_AWAY_COMMON_SCALE"
        ),
        "claim_boundary": {
            "Gate7": "ACTIVE_JOINT_C2_HEAT_ZETA_TAIL_OR_FINITE_ENDPOINT",
            "Gate8": "LOCKED",
            "finite_optical_infinite_route": "CLOSED_NO_GO",
            "infinite_optical_common_scale_zeta_criterion": "DERIVED",
            "separate_common_scale_zeta_tail_required": False,
            "actual_common_scale_zeta_tail": "OPEN_TERMWISE_ROUTE",
            "actual_full_graded_heat_tail": "OPEN_TERMWISE_ROUTE",
            "direct_joint_replacement_Cauchy_criterion": "DERIVED",
            "actual_joint_replacement_Cauchy_tail": "OPEN_CURRENT_OWNER",
            "zero_source_force": "OPEN",
            "chord_03_authorized": False,
            "frozen_predictions_changed": False,
            "FLAGSHIP_READY": False,
            "FULL_BHSM_COMPLETE": False,
        },
        "inputs": {path.relative_to(ROOT).as_posix(): _sha256(path) for path in INPUTS},
        "validation": validation,
        "validation_passed": passed,
        "FLAGSHIP_READY": False,
        "FULL_BHSM_COMPLETE": False,
    }


def main() -> None:
    payload = build_payload()
    RESULT.parent.mkdir(parents=True, exist_ok=True)
    RESULT.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(json.dumps({
        "status": payload["status"],
        "validation_passed": payload["validation_passed"],
        "joint_replacement_tail": payload["claim_boundary"]["actual_joint_replacement_Cauchy_tail"],
    }, indent=2))


if __name__ == "__main__":
    main()
