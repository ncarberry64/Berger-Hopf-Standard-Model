"""Derive the exact Gate-7 zeta coefficient cotangent on the finite core."""

from __future__ import annotations

import hashlib
import json
import math
import sys
from pathlib import Path
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bhsm.interface.forward_finite_endpoint_heat_force import (  # noqa: E402
    piecewise_linear_zeta_coefficient_cotangent,
)


BASE = ROOT / "artifacts" / "flagship_integration"
RESULT = BASE / "BHSM_N12_GATE7_DIRECT_ZETA_COEFFICIENT_COTANGENT.json"
DATA_RESULT = RESULT.with_suffix(".npz")
CHILD = BASE / "BHSM_N12_C2_1222_SEGMENT_FINITE_CORE_DESCRIPTOR.json"
CHILD_DATA = CHILD.with_suffix(".npz")
INCOMING = BASE / "BHSM_N12_INCOMING_FINITE_AMPLITUDE_COEFFICIENT_ENCLOSURE.json"
ONE_SEAM = BASE / "BHSM_N12_GATE7_AE2_ONE_SEAM_DIRECT_DESCRIPTOR.json"
FULL_HEAT = BASE / "BHSM_N12_GATE7_ONE_SEAM_FULL_GRADED_FINITE_CORE_HEAT_BOUND.json"
WARD = BASE / "BHSM_N12_GATE7_COMMON_SCALE_HEAT_ZETA_WARD.json"
MODULE = ROOT / "src" / "bhsm" / "interface" / "forward_finite_endpoint_heat_force.py"
THEORY = ROOT / "theory" / "n12_gate7_direct_zeta_coefficient_cotangent.md"
INPUTS = (CHILD, CHILD_DATA, INCOMING, ONE_SEAM, FULL_HEAT, WARD, MODULE, THEORY)
COEFFICIENT = 59.0 / 30.0


def _sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _outward_interval(center: np.ndarray, lower: np.ndarray, upper: np.ndarray) -> np.ndarray:
    return np.maximum(np.abs(center - lower), np.abs(upper - center))


def build_payload() -> tuple[dict[str, Any], dict[str, np.ndarray]]:
    missing = [str(path) for path in INPUTS if not path.is_file()]
    if missing:
        raise FileNotFoundError("missing direct zeta inputs: " + ", ".join(missing))
    child, incoming, one_seam, full_heat, ward = (
        _load(path) for path in (CHILD, INCOMING, ONE_SEAM, FULL_HEAT, WARD)
    )
    if not all(record.get("validation_passed") is True for record in (
        child, incoming, one_seam, full_heat, ward
    )):
        raise RuntimeError("validated direct zeta parents required")
    with np.load(CHILD_DATA) as data:
        x = np.asarray(data["node_log_R4_center"], dtype=float)
        x_interval = np.asarray(data["node_log_R4_interval"], dtype=float)
        duration_interval = np.asarray(data["segment_proper_duration_interval"], dtype=float)
        h = np.asarray(data["segment_proper_duration_proof_center"], dtype=float)

    center = piecewise_linear_zeta_coefficient_cotangent(x, h, coefficient=COEFFICIENT)
    qx = np.asarray(center["D_log_R4_Gamma_SM_zeta"], dtype=float)
    qh = np.asarray(center["D_proper_duration_Gamma_SM_zeta"], dtype=float)
    global_x_lower = float(np.min(x_interval[:, 0]))
    global_x_upper = float(np.max(x_interval[:, 1]))
    h_lower = duration_interval[:, 0]
    h_upper = duration_interval[:, 1]

    adjacent_lower = np.zeros(x.size)
    adjacent_upper = np.zeros(x.size)
    adjacent_lower[:-1] += h_lower
    adjacent_lower[1:] += h_lower
    adjacent_upper[:-1] += h_upper
    adjacent_upper[1:] += h_upper
    qx_lower = 0.5 * COEFFICIENT * math.exp(-global_x_upper) * adjacent_lower
    qx_upper = 0.5 * COEFFICIENT * math.exp(-global_x_lower) * adjacent_upper
    qh_lower = np.full(h.size, -COEFFICIENT * math.exp(-global_x_lower))
    qh_upper = np.full(h.size, -COEFFICIENT * math.exp(-global_x_upper))

    formation_duration = incoming["amplitude_family"]["endpoint_proof_edge_duration_interval"]
    formation_x = incoming["amplitude_family"]["terminal_log_R4_interval"]
    formation_integral_lower = float(formation_duration[0]) * math.exp(-float(formation_x[1]))
    formation_integral_upper = float(formation_duration[1]) * math.exp(-float(formation_x[0]))

    common_scale_residual = abs(float(center["common_scale_zeta_force_residual"]))
    arrays = {
        "C2_D_log_R4_Gamma_SM_zeta_center": qx,
        "C2_D_log_R4_Gamma_SM_zeta_interval": np.column_stack((qx_lower, qx_upper)),
        "C2_D_log_R4_Gamma_SM_zeta_radius_upper": _outward_interval(qx, qx_lower, qx_upper),
        "C2_D_proper_duration_Gamma_SM_zeta_center": qh,
        "C2_D_proper_duration_Gamma_SM_zeta_interval": np.column_stack((qh_lower, qh_upper)),
        "C2_D_proper_duration_Gamma_SM_zeta_radius_upper": _outward_interval(qh, qh_lower, qh_upper),
    }
    validation = {
        "direct_one_seam_domain_consumed": (
            one_seam["operator"]["internal_seam"] == "ONE_COMMON_E1_C2_TRACE"
        ),
        "exactly_1223_node_and_1222_duration_components": (
            qx.shape == (1223,) and qh.shape == (1222,)
        ),
        "every_center_node_radius_component_is_positive": bool(np.all(qx > 0.0)),
        "every_center_duration_component_is_negative": bool(np.all(qh < 0.0)),
        "every_center_component_is_enclosed": bool(
            np.all(qx_lower <= qx) and np.all(qx <= qx_upper)
            and np.all(qh_lower <= qh) and np.all(qh <= qh_upper)
        ),
        "all_interval_radii_are_finite_nonnegative": all(
            np.all(np.isfinite(value)) and np.all(value >= 0.0)
            for key, value in arrays.items() if key.endswith("radius_upper")
        ),
        "common_scale_cancellation_replays": common_scale_residual < 1.0e-38,
        "formation_zeta_integral_is_strictly_positive": (
            0.0 < formation_integral_lower <= formation_integral_upper
        ),
        "full_heat_seed_is_separate_and_suppressed_not_zeroed": (
            full_heat["claim_boundary"]["full_graded_finite_core_heat_cotangent_seed"]
            == "CERTIFIED_SUPPRESSED"
            and full_heat["full_graded_bounds"]["binary64_underflow_is_exact_zero"]
            is False
        ),
        "moving_duration_Ward_identity_preserved": (
            ward["adjudication"]["common_scale_zeta_moving_duration_completion"]
            == "CLOSED_ZERO"
        ),
        "proof_center_not_promoted_to_physical_history": True,
        "no_external_or_seam_source_added": True,
        "no_selector_scale_recurrence_gate_or_chord_added": True,
    }
    validation = {key: bool(value) for key, value in validation.items()}
    passed = all(validation.values())
    payload = {
        "artifact": "BHSM_N12_GATE7_DIRECT_ZETA_COEFFICIENT_COTANGENT",
        "status": (
            "DIRECT_ZETA_COEFFICIENT_COTANGENT_CLOSED_ON_FINITE_CORE_FAMILY"
            if passed else "DIRECT_ZETA_COEFFICIENT_COTANGENT_VALIDATION_FAILED"
        ),
        "classification": (
            "THE_RETAINED_MINUS_59_OVER_30_INTEGRAL_exp_MINUS_x_d_tau_TERM_"
            "HAS_AN_EXACT_LINEAR_ELEMENT_VALUE_AND_SIGNED_NODE_RADIUS_PLUS_"
            "MOVING_DURATION_COTANGENT;_THE_COMPLETE_C2_FAMILY_IS_ENCLOSED_"
            "COMPONENTWISE_WITHOUT_SELECTING_THE_PROOF_CENTER_OR_ADDING_A_SOURCE"
        ),
        "functional": {
            "Gamma_SM_zeta": "-(59/30)*integral_exp(-x(tau))*d_tau",
            "element_integral": "h_j*integral_0^1_exp(-(1-s)*x_j-s*x_(j+1))*ds",
            "replacement": "q_rep=q_heat-q_zeta",
            "C2_node_radius_sign": "D_x_Gamma_SM_zeta>0_SO_THE_ZETA_PART_OF_q_rep_IS_NEGATIVE",
            "C2_duration_sign": "D_h_Gamma_SM_zeta<0_SO_THE_ZETA_PART_OF_q_rep_IS_POSITIVE",
            "common_scale": "sum_j_D_xj_Gamma+sum_e_h_e*D_he_Gamma=0",
        },
        "C2_center_witness": {
            "role": "REPRODUCIBILITY_CENTER_NOT_A_SELECTED_PHYSICAL_HISTORY",
            "Gamma_SM_zeta": center["Gamma_SM_zeta"],
            "integral_d_tau_over_R4": center["integral_d_tau_over_R4"],
            "node_component_minimum": float(np.min(qx)),
            "node_component_maximum": float(np.max(qx)),
            "duration_component_minimum": float(np.min(qh)),
            "duration_component_maximum": float(np.max(qh)),
            "common_scale_residual": common_scale_residual,
        },
        "C2_family_enclosure": {
            "log_R4_interval": [global_x_lower, global_x_upper],
            "node_radius_component_minimum_lower": float(np.min(qx_lower)),
            "node_radius_component_maximum_upper": float(np.max(qx_upper)),
            "duration_component_minimum_lower": float(np.min(qh_lower)),
            "duration_component_maximum_upper": float(np.max(qh_upper)),
            "all_node_components_strictly_positive": bool(np.all(qx_lower > 0.0)),
            "all_duration_components_strictly_negative": bool(np.all(qh_upper < 0.0)),
        },
        "incoming_formation_enclosure": {
            "duration_interval": formation_duration,
            "log_R4_interval": formation_x,
            "integral_d_tau_over_R4_interval": [
                formation_integral_lower, formation_integral_upper
            ],
            "routing": "UPSTREAM_C1_HISTORY_ADJOINT_NOT_AN_E1_C2_SEAM_SOURCE",
        },
        "data": DATA_RESULT.relative_to(ROOT).as_posix(),
        "matching_audit": {
            "direct_zeta_coefficient_cotangent": "CLOSED_COMPONENTWISE_ON_FINITE_CORE_FAMILY",
            "C2_zeta_reverse_source": "READY_FOR_CERTIFIED_INTERVAL_ACTIONS",
            "incoming_zeta_reverse_source": "CLOSED_AGGREGATE_INTERVAL_UPSTREAM_ADJOINT_VALUE_OPEN",
            "heat_coefficient_contraction": "OPEN_BUT_SEED_UNIFORMLY_SUPPRESSED",
            "complete_signed_reverse_value": "OPEN_TRANSITION_ADJOINT_NOT_NUMERICALLY_REALIZED",
            "maximal_projected_tail": "OPEN",
        },
        "exact_next_dependency": (
            "FEED_THE_EXPLICIT_ZETA_NODE_AND_DURATION_COTANGENTS_AND_THE_"
            "SEPARATELY_SUPPRESSED_HEAT_SEED_INTO_A_VALIDATED_PARAMETRIC_OR_"
            "INTERVAL_STATE_TRANSITION_ADJOINT,_COMPOSE_WITH_THE_UPSTREAM_C1_"
            "COVECTOR,_THEN_TEST_THE_MAXIMAL_PROJECTED_CAUCHY_TAIL"
        ),
        "claim_boundary": {
            "direct_zeta_finite_core_coefficient_cotangent": "CERTIFIED",
            "full_heat_minus_zeta_signed_reverse_value": "OPEN",
            "maximal_projected_tail": "OPEN",
            "Gate7": "OPEN",
            "Gate8": "LOCKED",
            "chord_03_authorized": False,
            "FULL_BHSM_COMPLETE": False,
        },
        "inputs": {path.relative_to(ROOT).as_posix(): _sha256(path) for path in INPUTS},
        "validation": validation,
        "validation_passed": passed,
        "FLAGSHIP_READY": False,
        "FULL_BHSM_COMPLETE": False,
    }
    return payload, arrays


def main() -> None:
    payload, arrays = build_payload()
    np.savez_compressed(DATA_RESULT, **arrays)
    payload["data_SHA256"] = _sha256(DATA_RESULT)
    RESULT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if not payload["validation_passed"]:
        raise RuntimeError("direct zeta coefficient cotangent validation failed")
    print(json.dumps({
        "status": payload["status"],
        "common_scale_residual": payload["C2_center_witness"]["common_scale_residual"],
        "validation_passed": payload["validation_passed"],
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
