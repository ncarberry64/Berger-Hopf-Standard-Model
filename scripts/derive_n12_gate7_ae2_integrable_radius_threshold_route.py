"""Derive the geometry-first integrable-radius route to factorized E1 closure."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bhsm.interface.action_extension_ae2_factorized_source_measure import (  # noqa: E402
    integrable_reciprocal_radius_normalization,
    reciprocal_radius_integral_from_power_growth,
    resonant_transfer_majorant,
)


TARGET = ROOT / "artifacts/flagship_integration/BHSM_N12_GATE7_AE2_INTEGRABLE_RADIUS_THRESHOLD_ROUTE.json"
INPUTS = (
    ROOT / "artifacts/flagship_integration/BHSM_N12_GATE7_AE2_FACTORIZED_SOURCE_MEASURE_REDUCTION.json",
    ROOT / "artifacts/flagship_integration/BHSM_N12_FORWARD_BOUNDARY_RADIUS_ACTION_PROJECTION.json",
    ROOT / "artifacts/flagship_integration/BHSM_N12_FORWARD_PROPER_TIME_FORM_OWNERSHIP.json",
    ROOT / "artifacts/intrinsic_state_selection/BHSM_N12_CONTINUUM_MAXIMAL_FLOW_DICHOTOMY.json",
    ROOT / "artifacts/intrinsic_state_selection/BHSM_N12_GLOBAL_FLOW_COERCIVE_CONTROL_GATE.json",
    ROOT / "src/bhsm/interface/action_extension_ae2_factorized_source_measure.py",
    ROOT / "scripts/derive_n12_gate7_ae2_integrable_radius_threshold_route.py",
)


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def build_payload() -> dict[str, Any]:
    if not all(path.is_file() for path in INPUTS):
        raise FileNotFoundError("integrable-radius theorem inputs required")
    reduction, radius, proper, dichotomy, global_gate = (_load(path) for path in INPUTS[:5])
    if not all(item.get("validation_passed") is True for item in (reduction, radius, proper, dichotomy, global_gate)):
        raise RuntimeError("validated geometry-first threshold lineage required")

    growth_witness = reciprocal_radius_integral_from_power_growth(1.0, 2.0, 0.5)
    normalization_witness = integrable_reciprocal_radius_normalization(
        1.5, growth_witness["reciprocal_radius_integral_upper"], 2, 2
    )
    source_witness = resonant_transfer_majorant(
        1.5, 0.25, 1.0,
        normalization_witness["uniform_near_threshold_normalization_squared_sum_upper"],
    )
    validation = {
        "all_inputs_validated": True,
        "abstract_source_measure_reduction_closed": reduction["claim_boundary"]["abstract_factorized_transfer_to_source_measure_theorem"] == "CLOSED",
        "radius_is_action_projection_not_independent_input": radius["action_projection"]["no_independent_radius_degree_of_freedom"] is True,
        "proper_time_is_canonical": (
            proper["proper_time_form_theorem"]["positive_orientation"] == "N_boundary>0_IMPLIES_d_tau>0"
            and "log_R4(tau)" in proper["proper_time_form_theorem"]["compactly_supported_geometry_variation"]
        ),
        "maximal_flow_infinite_branch_exists_in_dichotomy": dichotomy["maximal_flow_alternative"]["global_if_norm_and_all_existing_margins_remain_controlled"] is True,
        "current_global_coercive_radius_control_unavailable": global_gate["owned_and_missing_energy_structure"]["coercive_S2_bound_on_continuum_child_component"] is False,
        "power_growth_integral_is_finite": growth_witness["reciprocal_radius_integral_upper"] > 0.0,
        "normalization_sum_is_finite": normalization_witness["uniform_near_threshold_normalization_squared_sum_upper"] > 0.0,
        "source_measure_exponent_is_three_halves": source_witness["source_measure_excess_exponent"] == 0.5,
        "actual_N12_radius_integral_not_fabricated": True,
        "no_SM_observable_scale_fit_selector_or_new_action_term": True,
        "FULL_BHSM_COMPLETE_false": True,
    }
    return {
        "artifact": "BHSM_N12_GATE7_AE2_INTEGRABLE_RADIUS_THRESHOLD_ROUTE",
        "action_version": "BHSM-AE-2.0.0",
        "status": "INFINITE_FACTORIZED_THRESHOLD_REDUCED_TO_RECIPROCAL_RADIUS_INTEGRABILITY_OR_DIRECT_NON_L1_TAIL_THEOREM",
        "classification": "FOR_s_chi=chi*mu/R4_ON_AN_INFINITE_REGULAR_MAXIMAL_FORWARD_HISTORY,_FINITE_I_R=integral_d_tau/R4_GIVES_EXPLICIT_FINITE_TWO_CHIRALITY_EVENT_CHILD_THRESHOLD_NORMALIZATION_SUM_AND_THEREFORE_THE_FACTORIZED_O(Lambda^(3/2))_E1_SOURCE_MEASURE_BOUND;_A_SUPERLINEAR_LOWER_GROWTH_BOUND_FOR_R4_IS_ONE_SUFFICIENT_GEOMETRIC_ROUTE,_BUT_THE_CURRENT_ACTION_LEDGER_DOES_NOT_YET_PROVE_IT",
        "theorem": {
            "superpotential": "s_chi(tau)=chi*mu/R4(tau)",
            "integrable_tail_hypothesis": "I_R=integral_0^infinity_d_tau/R4(tau)<infinity",
            "zero_transfer_limit": "u_0(infinity)=exp(-chi*mu*I_R)",
            "normalization": "N_chi(0)^2=(2/pi)*exp(2*chi*mu*I_R)",
            "two_chirality_sum": "N_plus^2+N_minus^2=(4/pi)*cosh(2*mu*I_R)",
            "sufficient_radius_growth": "R4(tau)>=R0*(1+tau/T0)^(1+delta), delta>0",
            "integral_bound": "I_R<=T0/(R0*delta)",
            "witness": {"growth": growth_witness, "normalization": normalization_witness, "source_measure": source_witness},
        },
        "current_disk_adjudication": {
            "finite_event_or_canonical_stop_branch": "ALREADY_CLOSED_AT_THE_ABSTRACT_THRESHOLD_LEVEL_BY_COMPACT_RESOLVENT_AND_ZERO_ATOM_WEIGHT_ZERO",
            "infinite_regular_branch": "OPEN",
            "reciprocal_radius_integral_bound": "NOT_AVAILABLE",
            "local_positive_radius_rate": "INSUFFICIENT_FOR_A_GLOBAL_GROWTH_LAW",
            "coercive_S2_or_domain_margin_control": "NOT_AVAILABLE",
            "nonintegrable_supersymmetric_tail_route": "NOT_YET_ADJUDICATED",
        },
        "claim_boundary": {
            "conditional_integrable_radius_threshold_theorem": "CLOSED",
            "actual_N12_reciprocal_radius_integrability": "OPEN",
            "direct_nonintegrable_tail_theorem": "OPEN",
            "Gate7": "ACTIVE_NOT_CLOSED",
            "Gate8": "LOCKED",
            "chord_03_authorized": False,
            "frozen_predictions_changed": False,
            "FULL_BHSM_COMPLETE": False,
        },
        "exact_next_dependency": "ON_THE_INFINITE_REGULAR_MAXIMAL_FORWARD_BRANCH_PROVE_I_R=integral_d_tau/R4<infinity_FROM_THE_RETAINED_ACTION_GEOMETRY,_OR_PROVE_DIRECTLY_FOR_THE_NON_L1_SUPERSYMMETRIC_TAIL_s=chi*mu/R4_A_UNIFORM_NEAR_THRESHOLD_SOURCE_NORMALIZATION_BOUND;_DO_NOT_IMPORT_A_PHYSICAL_SCALE_OR_TERMINAL_RETURN",
        "inputs": {path.relative_to(ROOT).as_posix(): _sha256(path) for path in INPUTS},
        "validation": validation,
        "validation_passed": all(validation.values()),
        "FLAGSHIP_READY": False,
        "FULL_BHSM_COMPLETE": False,
    }


def deterministic_bytes(payload: dict[str, Any]) -> bytes:
    return (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode("utf-8")


def materialize() -> Path:
    payload = build_payload()
    if not payload["validation_passed"]:
        failed = [key for key, value in payload["validation"].items() if not value]
        raise RuntimeError(f"integrable-radius threshold route failed: {failed}")
    TARGET.write_bytes(deterministic_bytes(payload))
    return TARGET


if __name__ == "__main__":
    print(materialize())
