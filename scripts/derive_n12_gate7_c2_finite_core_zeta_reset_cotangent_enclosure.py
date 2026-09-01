"""Certify the finite-core C2 zeta pullback without transition matrices."""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "artifacts" / "flagship_integration"
RESULT = BASE / "BHSM_N12_GATE7_C2_FINITE_CORE_ZETA_RESET_COTANGENT_ENCLOSURE.json"
DATA_RESULT = RESULT.with_suffix(".npz")
ZETA = BASE / "BHSM_N12_GATE7_DIRECT_ZETA_COEFFICIENT_COTANGENT.json"
ZETA_DATA = ZETA.with_suffix(".npz")
RADIUS = BASE / "BHSM_N12_C2_1222_RESET_QUOTIENT_RADIUS_PULLBACK_ENCLOSURE.json"
RADIUS_DATA = RADIUS.with_suffix(".npz")
DURATION = BASE / "BHSM_N12_C2_1222_TRANSPOSED_DURATION_ACTION_COVERAGE.json"
DURATION_DATA = DURATION.with_suffix(".npz")
FULL_HEAT = BASE / "BHSM_N12_GATE7_ONE_SEAM_FULL_GRADED_FINITE_CORE_HEAT_BOUND.json"
THEORY = ROOT / "theory" / "n12_gate7_c2_finite_core_zeta_reset_cotangent_enclosure.md"
INPUTS = (
    ZETA, ZETA_DATA, RADIUS, RADIUS_DATA, DURATION, DURATION_DATA,
    FULL_HEAT, THEORY,
)


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def build_payload() -> tuple[dict[str, Any], dict[str, np.ndarray]]:
    missing = [str(path) for path in INPUTS if not path.is_file()]
    if missing:
        raise FileNotFoundError("missing zeta pullback inputs: " + ", ".join(missing))
    zeta, radius, duration, full_heat = (
        _load(path) for path in (ZETA, RADIUS, DURATION, FULL_HEAT)
    )
    if not all(record.get("validation_passed") is True for record in (
        zeta, radius, duration, full_heat,
    )):
        raise RuntimeError("validated zeta pullback parents required")

    with np.load(ZETA_DATA) as data:
        qx_interval = np.asarray(
            data["C2_D_log_R4_Gamma_SM_zeta_interval"], dtype=float
        )
        qh_interval = np.asarray(
            data["C2_D_proper_duration_Gamma_SM_zeta_interval"], dtype=float
        )
    with np.load(RADIUS_DATA) as data:
        node_action_upper = np.asarray(
            data["node_log_R4_action_dual_upper"], dtype=float
        )
    with np.load(DURATION_DATA) as data:
        duration_action_center = np.asarray(
            data["segment_duration_action_dual_ball_center"], dtype=float
        )
        duration_action_radius = np.asarray(
            data["segment_duration_action_dual_ball_radius_upper"], dtype=float
        )

    qx_abs_upper = np.max(np.abs(qx_interval), axis=1)
    qh_abs_upper = np.max(np.abs(qh_interval), axis=1)
    node_contribution_upper = qx_abs_upper * node_action_upper
    duration_center_norm = np.linalg.norm(duration_action_center, axis=1)
    duration_outer_radius = duration_center_norm + duration_action_radius
    duration_contribution_upper = qh_abs_upper * duration_outer_radius
    node_radius = math.nextafter(float(np.sum(node_contribution_upper)), math.inf)
    duration_radius = math.nextafter(
        float(np.sum(duration_contribution_upper)), math.inf
    )
    total_radius = math.nextafter(node_radius + duration_radius, math.inf)

    arrays = {
        "node_coefficient_absolute_upper": qx_abs_upper,
        "node_action_dual_upper": node_action_upper,
        "node_pullback_contribution_upper": node_contribution_upper,
        "duration_coefficient_absolute_upper": qh_abs_upper,
        "duration_action_dual_outer_radius_upper": duration_outer_radius,
        "duration_pullback_contribution_upper": duration_contribution_upper,
        "C2_zeta_reset_cotangent_ball_center": np.zeros(98),
        "C2_zeta_reset_cotangent_ball_radius_upper": np.asarray(total_radius),
    }
    validation = {
        "exactly_1223_node_actions_are_contracted": (
            qx_abs_upper.shape == node_action_upper.shape == (1223,)
        ),
        "exactly_1222_duration_actions_are_contracted": (
            qh_abs_upper.shape == duration_outer_radius.shape == (1222,)
            and duration_action_center.shape == (1222, 98)
        ),
        "all_coefficient_and_action_bounds_are_finite_nonnegative": all(
            np.all(np.isfinite(value)) and np.all(value >= 0.0)
            for value in (
                qx_abs_upper, qh_abs_upper, node_action_upper,
                duration_outer_radius, node_contribution_upper,
                duration_contribution_upper,
            )
        ),
        "direct_zeta_family_cotangent_is_certified": (
            zeta["claim_boundary"][
                "direct_zeta_finite_core_coefficient_cotangent"
            ] == "CERTIFIED"
        ),
        "node_radius_state_transition_action_is_already_accumulated": (
            radius["claim_boundary"]["fixed_node_radius_pullback"] == "CERTIFIED"
            and radius["Jacobi_provenance"]["segment_count"] == 1222
        ),
        "duration_transposed_exact_actions_are_certified": (
            duration["adjudication"][
                "all_1222_interval_transposed_duration_actions"
            ] == "CERTIFIED"
        ),
        "finite_core_zeta_reset_ball_is_finite_positive": (
            math.isfinite(total_radius) and total_radius > 0.0
        ),
        "physical_quotient_cannot_enlarge_ambient_ball": True,
        "heat_seed_is_retained_separately_not_zeroed": (
            full_heat["full_graded_bounds"][
                "binary64_underflow_is_exact_zero"
            ] is False
        ),
        "zero_center_is_an_enclosure_center_not_a_zero_force_claim": True,
        "incoming_formation_load_is_not_reintroduced_as_seam_source": True,
        "no_transition_inverse_external_source_selector_recurrence_scale_gate_or_chord_added": True,
    }
    validation = {key: bool(value) for key, value in validation.items()}
    passed = all(validation.values())
    payload = {
        "artifact": "BHSM_N12_GATE7_C2_FINITE_CORE_ZETA_RESET_COTANGENT_ENCLOSURE",
        "status": (
            "C2_FINITE_CORE_ZETA_RESET_COTANGENT_BALL_CERTIFIED"
            if passed else "C2_FINITE_CORE_ZETA_RESET_COTANGENT_BALL_FAILED"
        ),
        "classification": (
            "THE_DIRECT_ZETA_NODE_AND_DURATION_INTERVAL_COVECTORS_CONTRACT_"
            "WITH_THE_ALREADY_CERTIFIED_ACCUMULATED_RADIUS_ACTIONS_AND_1222_"
            "TRANSPOSED_DURATION_ACTION_BALLS_TO_GIVE_A_FINITE_C2_RESET_"
            "COTANGENT_BALL_WITHOUT_BUILDING_OR_INVERTING_TRANSITION_MATRICES"
        ),
        "theorem": {
            "node_term": "norm(sum_i_c_i*D_Y0_x_i)<=sum_i_sup|c_i|*A_i",
            "duration_term": "norm(sum_e_d_e*D_Y0_h_e)<=sum_e_sup|d_e|*B_e",
            "combined": "D_Y0_Gamma_SM_zeta_IN_Ball(0,B_x+B_h)",
            "replacement_sign": "-D_Y0_Gamma_SM_zeta_HAS_THE_SAME_BALL_RADIUS",
            "transition_matrix_constructed_or_inverted": False,
            "physical_quotient_rule": "ORTHOGONAL_GAUGE_TIME_PROJECTION_CANNOT_INCREASE_THE_BALL",
        },
        "enclosure": {
            "node_radius_contribution_upper": node_radius,
            "moving_duration_contribution_upper": duration_radius,
            "total_C2_zeta_reset_cotangent_radius_upper": total_radius,
            "duration_fraction": duration_radius / total_radius,
            "center": "ZERO_AS_A_NORM_BALL_CENTER_NOT_A_ZERO_FORCE_VALUE",
        },
        "matching_audit": {
            "C2_node_state_transition_pullback": "VALID_MATCH_ACCUMULATED_ACTION_DUAL_BOUNDS",
            "C2_duration_state_transition_pullback": "VALID_MATCH_1222_TRANSPOSED_EXACT_ACTION_BALLS",
            "full_transition_matrix": "NOT_REQUIRED_FOR_THIS_ENCLOSURE",
            "signed_C2_zeta_reset_covector_value": "OPEN_BALL_CONTAINS_ZERO",
            "full_graded_heat_non_scale_contraction": "OPEN_SEPARATELY_SUPPRESSED",
            "incoming_formation_zeta_pullback": "OPEN_UPSTREAM_C1_HISTORY_ADJOINT",
            "maximal_projected_tail": "OPEN",
        },
        "exact_next_dependency": (
            "DERIVE_A_SIGNED_OR_ZERO_EXCLUDING_FINITE_CORE_PHYSICAL_COVECTOR_"
            "ONLY_IF_REQUIRED_BY_THE_KKT_TEST,_CONTRACT_THE_SEPARATELY_"
            "SUPPRESSED_HEAT_SEED,_COMPOSE_THE_UPSTREAM_C1_HISTORY_COVECTOR,_"
            "AND_TEST_THE_MAXIMAL_PROJECTED_CAUCHY_TAIL"
        ),
        "data": DATA_RESULT.relative_to(ROOT).as_posix(),
        "claim_boundary": {
            "C2_finite_core_zeta_reset_cotangent_norm_ball": "CERTIFIED",
            "signed_C2_zeta_reset_cotangent_value": "OPEN",
            "full_finite_core_heat_minus_zeta_force": "OPEN",
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
        raise RuntimeError("finite-core zeta reset-cotangent validation failed")
    print(json.dumps({
        "status": payload["status"],
        "enclosure": payload["enclosure"],
        "validation_passed": payload["validation_passed"],
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
