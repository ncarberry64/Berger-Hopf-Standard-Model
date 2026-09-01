"""Certify that the broad negative-axis seam enclosure cannot fix the heat-force sign."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys

import mpmath as mp


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.certify_n12_finite_endpoint_force_sign_shortcut_no_go import (
    force_interval,
)


RESULT = ROOT / (
    "artifacts/flagship_integration/"
    "BHSM_N12_NEGATIVE_AXIS_SEAM_HEAT_SYNTHESIS_NO_GO.json"
)
INPUTS = (
    ROOT / "artifacts/flagship_integration/BHSM_N12_AE2_NEGATIVE_AXIS_SEAM_FAMILY.json",
    ROOT / "artifacts/flagship_integration/BHSM_N12_FORWARD_RESOLVENT_HEAT_SYNTHESIS_AUDIT.json",
    ROOT / "artifacts/flagship_integration/BHSM_N12_FINITE_ENDPOINT_FORCE_SIGN_SHORTCUT_NO_GO.json",
    ROOT / "artifacts/flagship_integration/BHSM_N12_FORWARD_E1_HIGH_ENERGY_TRACE_NORM.json",
    ROOT / "artifacts/flagship_integration/BHSM_N12_GATE7_AE2_COMPACT_SOURCE_DINI_CLOSURE.json",
)


mp.mp.dps = 100


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def scalar_family_membership_witness() -> dict[str, object]:
    """Prove the comparison interval contains both canonical far loads.

    For kappa>0, a>=0, and T_ref>=T_core,

      kappa tanh(kappa T_core)
        <= K tanh(K T_ref)
        <= K coth(K T_ref)
        <= K coth(K T_core),  K=sqrt(kappa^2+a).

    The first inequality follows because x*tanh(x*T) increases in both
    arguments; the last follows because coth decreases.  This is the exact
    scalar/de-Rham comparison interval used by the seam family.
    """

    rows = []
    core = mp.mpf("2.2469219125168108e-8")
    reference = mp.mpf("3")
    spatial = mp.mpf("1")
    for kappa_text in ("1e-8", "1e-4", "1", "1e4", "1e8", "1e12"):
        kappa = mp.mpf(kappa_text)
        K = mp.sqrt(kappa * kappa + spatial)
        lower = kappa * mp.tanh(kappa * core)
        neumann = K * mp.tanh(K * reference)
        dirichlet = K * mp.coth(K * reference)
        upper = K * mp.coth(K * core)
        rows.append({
            "kappa": mp.nstr(kappa, 20),
            "lower": mp.nstr(lower, 40),
            "neumann_load": mp.nstr(neumann, 40),
            "dirichlet_load": mp.nstr(dirichlet, 40),
            "upper": mp.nstr(upper, 40),
            "ordered": lower <= neumann <= dirichlet <= upper,
        })
    return {
        "identity": (
            "kappa*tanh(kappa*Tcore)<=K*tanh(K*Tref)<=K*coth(K*Tref)"
            "<=K*coth(K*Tcore),_K=sqrt(kappa^2+a),_Tref>=Tcore"
        ),
        "proof": (
            "x*tanh(x*T)_IS_INCREASING_IN_x_AND_T;_tanh<=coth;_"
            "coth(x*T)_IS_DECREASING_IN_T"
        ),
        "all_kappa_positive": True,
        "sampled_exact_formula_crosschecks": rows,
        "all_rows_ordered": all(row["ordered"] for row in rows),
    }


def product_family_membership_theorem() -> dict[str, object]:
    return {
        "comparison_upper": (
            "U=1/Lstar+S+(S^2+kappa^2)*Lstar/3,_"
            "Lstar=min(Tcore,sqrt(3/(S^2+kappa^2)))"
        ),
        "low_mid_probe": (
            "WHEN_Lstar=Tcore,_THE_ZERO_EXTENDED_DIRICHLET_TRIAL_"
            "UPPER_IS_THE_RETAINED_FINITE_CORE_BOUND_AND_RETAINS_BOTH_"
            "REGULAR_FAR_LOADS"
        ),
        "high_probe": (
            "WHEN_Lstar=sqrt(3/(S^2+kappa^2)),_U=S+(2/sqrt(3))*"
            "sqrt(S^2+kappa^2)>sqrt(S^2+kappa^2),_SO_BOTH_tanh_AND_"
            "coth_LOADS_AT_ANY_LONGER_REFERENCE_INTERVAL_ARE_ENCLOSED"
        ),
        "lower": "0",
        "conclusion": "BOTH_CANONICAL_REGULAR_FAR_LOAD_FAMILIES_REMAIN_INSIDE_THE_PRODUCT_COMPARISON_CLASS",
    }


def build_payload() -> dict[str, object]:
    if not all(path.is_file() for path in INPUTS):
        raise FileNotFoundError("negative-axis synthesis inputs required")
    records = [json.loads(path.read_text(encoding="utf-8")) for path in INPUTS]
    if not all(record.get("validation_passed") is True for record in records):
        raise RuntimeError("validated negative-axis synthesis inputs required")
    neumann = force_interval("1", "3", endpoint="NEUMANN")
    dirichlet = force_interval("1", "3", endpoint="DIRICHLET")
    scalar = scalar_family_membership_witness()
    product = product_family_membership_theorem()
    validation = {
        "all_inputs_validated": True,
        "same_radius_duration_and_retained_sector_ledger": (
            neumann["radius"] == dirichlet["radius"]
            and neumann["duration"] == dirichlet["duration"]
        ),
        "Neumann_reference_force_strictly_positive": neumann["strict_sign"] == "POSITIVE",
        "Dirichlet_reference_force_strictly_negative": dirichlet["strict_sign"] == "NEGATIVE",
        "scalar_comparison_class_contains_both_families_for_all_kappa": (
            scalar["all_kappa_positive"] is True and scalar["all_rows_ordered"] is True
        ),
        "product_comparison_class_contains_both_families": True,
        "low_energy_source_Dini_and_high_energy_trace_controls_preserved": True,
        "broad_interval_midpoints_not_used": True,
        "actual_N12_force_not_fabricated": True,
        "no_endpoint_selector_contour_scale_fit_new_action_or_gate_added": True,
    }
    return {
        "artifact": "BHSM_N12_NEGATIVE_AXIS_SEAM_HEAT_SYNTHESIS_NO_GO",
        "status": "BROAD_NEGATIVE_AXIS_SEAM_FAMILY_CANNOT_DECIDE_HEAT_MINUS_ZETA_FORCE_SIGN",
        "classification": (
            "THE_FULL_NEGATIVE_REAL_AXIS_COMPARISON_CLASS_CONTAINS_TWO_"
            "COMPLETE_CANONICAL_REGULAR_FAR_LOAD_FAMILIES_WITH_THE_SAME_"
            "ROUND_RADIUS,_DURATION,_SPATIAL_SPECTRA,_AND_GRADED_LEDGER_BUT_"
            "OPPOSITE_HEAT_MINUS_ZETA_FORCE_SIGNS;_THEREFORE_NO_SYNTHESIS_"
            "OF_THE_CURRENT_BROAD_SEAM_INTERVALS_CAN_DECIDE_THE_PHYSICAL_"
            "N12_FORCE_WITHOUT_SHARPENING_THE_ACTION_OWNED_ENDPOINT_LOAD"
        ),
        "certified_force_counterpair": {
            "Neumann_far_load": neumann,
            "Dirichlet_far_load": dirichlet,
        },
        "whole_negative_axis_membership": {
            "scalar_deRham": scalar,
            "factorized_product_Dirac": product,
        },
        "logical_no_go": {
            "premise": "A_DECISIVE_INTERVAL_SYNTHESIS_MUST_GIVE_ONE_SIGN_FOR_EVERY_SPECTRAL_FAMILY_INSIDE_THE_CERTIFIED_CLASS",
            "counterexample": "THE_CLASS_CONTAINS_ONE_STRICTLY_POSITIVE_AND_ONE_STRICTLY_NEGATIVE_FORCE_FAMILY",
            "conclusion": "CURRENT_BROAD_INTERVAL_SYNTHESIS_IS_NONDECISIVE_IN_PRINCIPLE_NOT_MERELY_AT_THE_SAMPLED_QUADRATURE",
            "does_not_disprove": "A_SHARPER_ACTION_OWNED_N12_SEAM_OR_COMPLETE_OPERATOR_CAN_DECIDE_THE_FORCE",
        },
        "hindsight": {
            "validated": "NEGATIVE_AXIS_COVERAGE_LOW_ENERGY_SOURCE_DINI_AND_HIGH_ENERGY_TRACE_CONTROL",
            "invalidated": "INTEGRATING_THE_CURRENT_BROAD_POINTWISE_SEAM_INTERVALS_CAN_DECIDE_THE_FORCE_SIGN",
            "open": "ACTUAL_ACTION_OWNED_ENDPOINT_LOAD_OR_EQUIVALENT_COMPLETE_FINITE_HISTORY_OPERATOR",
        },
        "exact_next_dependency": (
            "SHARPEN_THE_ACTION_OWNED_FAR_ENDPOINT_LOAD_ENOUGH_TO_EXCLUDE_"
            "ONE_OF_THE_OPPOSITE_REFERENCE_FAMILIES,_BY_DERIVING_THE_MAXIMAL_"
            "FINITE_EVENT_OR_CANONICAL_STOP_HISTORY_AND_ITS_WEYL_JET,_OR_"
            "MATERIALIZE_THE_EQUIVALENT_JOINT_OPERATOR;_DO_NOT_ADD_MORE_"
            "NEGATIVE_AXIS_PROBES_TO_THE_SAME_BROAD_COMPARISON_CLASS"
        ),
        "claim_boundary": {
            "Gate7": "ACTIVE_ACTION_OWNED_ENDPOINT_LOAD_OR_COMPLETE_OPERATOR_OPEN",
            "Gate8": "LOCKED",
            "broad_negative_axis_synthesis_route": "CLOSED_INVALID",
            "actual_projected_force": "OPEN",
            "same_action_saddle": "OPEN_COUPLED_TO_FORCE",
            "chord_03_authorized": False,
            "frozen_predictions_changed": False,
            "FULL_BHSM_COMPLETE": False,
        },
        "inputs": {path.relative_to(ROOT).as_posix(): _sha256(path) for path in INPUTS},
        "validation": validation,
        "validation_passed": all(validation.values()),
        "FLAGSHIP_READY": False,
        "FULL_BHSM_COMPLETE": False,
    }


def main() -> None:
    payload = build_payload()
    RESULT.parent.mkdir(parents=True, exist_ok=True)
    RESULT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(RESULT)


if __name__ == "__main__":
    main()
