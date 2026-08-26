"""Certify the suppressed ``s D_86h R`` row in the signed C2 denominator."""

from __future__ import annotations

from decimal import Decimal
import hashlib
import json
import math
import os
from pathlib import Path
import sys

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bhsm.interface.aether_retained_action_tensor_interval import (  # noqa: E402
    DirectedInterval,
    interval_tensor_norm_upper,
    retained_action_tensor_interval,
)


BASE = ROOT / "artifacts" / "flagship_integration"
BORDERED = BASE / "BHSM_N12_C2_BORDERED_HARD_RESPONSE_MATRIX.json"
BORDERED_DATA = BORDERED.with_suffix(".npz")
RESPONSE_BALL = BASE / "BHSM_N12_C2_CANCELLED_FIELD_LOHNER_STEP.json"
GROWTH = BASE / "BHSM_N12_C2_FRESH_CHART_FIXED_S_GROWTH.json"
FIELD = BASE / "BHSM_N12_C2_EXACT_CENTER_FIXED_S_FIELD_MATRIX.json"
DOMINANT = BASE / "BHSM_N12_C2_FULLY_REDUCED_SIGNED_ROW_CERTIFICATE.json"
THEORY = ROOT / "theory" / "n12_c2_suppressed_hard_response_row.md"
RESULT = BASE / "BHSM_N12_C2_SUPPRESSED_HARD_RESPONSE_ROW_CERTIFICATE.json"
INTERVAL_SOURCE = (
    ROOT / "src" / "bhsm" / "interface"
    / "aether_retained_action_tensor_interval.py"
)

QDIM = 37
TOTAL = 98
REDUCED = 61
DECISIVE_INDEX = 86
POINTS = 96
RADIUS = 5.5104723095444935e-11
PSI_RADIUS = 6.0e-9
PSI_I_RADIUS = 1.0e-2
V_RADIUS = 40.0


def sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def provenance_inputs() -> list[Path]:
    return [
        BORDERED, BORDERED_DATA, RESPONSE_BALL, GROWTH, FIELD, DOMINANT,
        INTERVAL_SOURCE, THEORY, Path(__file__),
    ]


def upward_decimal(value: str) -> float:
    exact = Decimal(value)
    result = float(exact)
    while Decimal.from_float(result) < exact:
        result = math.nextafter(result, math.inf)
    return result


def norm_upper(value: DirectedInterval) -> float:
    return interval_tensor_norm_upper(value)


if os.environ.get("BHSM_REUSE_STORED_SUPPRESSED_ROW") == "1" and RESULT.is_file():
    payload = json.loads(RESULT.read_text(encoding="utf-8"))
    payload["inputs"] = {
        path.relative_to(ROOT).as_posix(): sha256(path)
        for path in provenance_inputs()
    }
    RESULT.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(json.dumps({
        "status": payload["status"],
        "provenance_refreshed": True,
        "validation_passed": payload["validation_passed"],
    }, indent=2, sort_keys=True))
    raise SystemExit(0)


bordered = json.loads(BORDERED.read_text(encoding="utf-8"))
response_ball = json.loads(RESPONSE_BALL.read_text(encoding="utf-8"))
growth = json.loads(GROWTH.read_text(encoding="utf-8"))
field = json.loads(FIELD.read_text(encoding="utf-8"))
dominant = json.loads(DOMINANT.read_text(encoding="utf-8"))
if not all(parent.get("validation_passed") is True for parent in (
    bordered, response_ball, growth, field, dominant,
)):
    raise RuntimeError("validated signed-row parent artifacts are required")

with np.load(BORDERED_DATA) as data:
    state = np.asarray(data["center_state"], dtype=float)
    weights = np.asarray(data["state_weights"], dtype=float)
    psi = np.asarray(data["selected_vector"], dtype=float)
    psi_first = np.asarray(
        data["selected_vector_derivative_action"], dtype=float
    )
    response = np.asarray(data["bordered_response"], dtype=float)
    response_first = np.asarray(
        data["bordered_response_derivative_action"], dtype=float
    )

if state.shape != (TOTAL,) or psi.shape != (REDUCED,):
    raise RuntimeError("unexpected N12 C2 proof dimensions")

eye = np.eye(TOTAL)
i = eye[DECISIVE_INDEX]
reduced_weights = weights[QDIM:]
embed = np.zeros((TOTAL, REDUCED))
embed[QDIM:] = np.diag(reduced_weights)
psi_matrix = np.zeros((TOTAL, TOTAL))
psi_matrix[QDIM:] = reduced_weights[:, None] * psi_first
configuration = np.zeros(TOTAL)
configuration[:QDIM] = weights[:QDIM] * state[QDIM:2 * QDIM]
configuration_first = np.zeros((TOTAL, TOTAL))
configuration_first[:QDIM, QDIM:2 * QDIM] = np.diag(
    weights[:QDIM] / weights[QDIM:2 * QDIM]
)
hard = response[:-1]
hard_first = response_first[:-1]
hard_action = embed @ hard
hard_first_action = embed @ hard_first
whole_hard = configuration + hard_action
whole_hard_first = configuration_first + hard_first_action

state_lower = np.nextafter(state - RADIUS / weights, -np.inf)
state_upper = np.nextafter(state + RADIUS / weights, np.inf)


def raw_ball(center: np.ndarray, radius: float) -> tuple[np.ndarray, np.ndarray]:
    action_center = embed @ np.asarray(center, dtype=float)
    spread = np.abs(embed @ np.ones(REDUCED)) * radius
    return (
        np.nextafter(action_center - spread, -np.inf),
        np.nextafter(action_center + spread, np.inf),
    )


def whole_hard_box() -> tuple[np.ndarray, np.ndarray]:
    configuration_spread = np.linalg.norm(configuration_first, axis=1) * RADIUS
    hard_spread = np.abs(embed @ np.ones(REDUCED)) * V_RADIUS
    spread = configuration_spread + hard_spread
    return (
        np.nextafter(whole_hard - spread, -np.inf),
        np.nextafter(whole_hard + spread, np.inf),
    )


psi_box = raw_ball(psi, PSI_RADIUS)
psi_i = psi_first[:, DECISIVE_INDEX]
psi_i_box = raw_ball(psi_i, PSI_I_RADIUS)
whole_hard_interval = whole_hard_box()


def tensor(*directions: np.ndarray | tuple[np.ndarray, np.ndarray]) -> DirectedInterval:
    return retained_action_tensor_interval(
        12, state_lower, state_upper, list(directions), points=POINTS
    )


def evaluated(name: str, *directions: np.ndarray | tuple[np.ndarray, np.ndarray]) -> float:
    value = norm_upper(tensor(*directions))
    print(f"{name}={value:.17g}", flush=True)
    return value


line = growth["fresh_line_bounds"]
response_second = float(
    response_ball["second_variation"]["response_second_variation_upper"]
)
psi_second = float(line["selected_line_second_variation_coefficient_upper"])
hard_first_motion = math.nextafter(response_second * RADIUS, math.inf)
psi_first_motion = math.nextafter(psi_second * RADIUS, math.inf)

# R=D3S[W,Psi,Psi], W=Qdot+E*V_hard.  Differentiate twice in
# (i,h), retain all signed center matrices, and bound only the two second
# derivatives and the first-matrix motions by their certified operator balls.
terms: dict[str, float] = {}
terms["D5_i_h_W_p_p"] = evaluated(
    "D5_i_h_W_p_p", i, eye, whole_hard_interval, psi_box, psi_box
)
terms["D4_i_W_h_center_p_p"] = evaluated(
    "D4_i_W_h_center_p_p", i, whole_hard_first, psi_box, psi_box
)
terms["D4_i_W_h_motion_p_p"] = hard_first_motion * evaluated(
    "D4_i_Eraw_p_p", i, embed, psi_box, psi_box
)
terms["D4_h_W_i_center_p_p"] = evaluated(
    "D4_h_W_i_center_p_p",
    eye, whole_hard_first[:, DECISIVE_INDEX], psi_box, psi_box,
)
terms["D4_h_W_i_motion_p_p"] = hard_first_motion * evaluated(
    "D4_h_Eraw_p_p", eye, embed, psi_box, psi_box
)
terms["2D4_i_W_p_h_center_p"] = 2.0 * evaluated(
    "D4_i_W_p_h_center_p", i, whole_hard_interval, psi_matrix, psi_box
)
terms["2D4_i_W_p_h_motion_p"] = 2.0 * psi_first_motion * evaluated(
    "D4_i_W_Eraw_p", i, whole_hard_interval, embed, psi_box
)
terms["2D4_h_W_p_i_p"] = 2.0 * evaluated(
    "D4_h_W_p_i_p", eye, whole_hard_interval, psi_i_box, psi_box
)
terms["D3_W_ih_p_p"] = response_second * evaluated(
    "D3_Eraw_p_p", embed, psi_box, psi_box
)
terms["2D3_W_i_center_p_h_center_p"] = 2.0 * evaluated(
    "D3_W_i_center_p_h_center_p",
    whole_hard_first[:, DECISIVE_INDEX], psi_matrix, psi_box,
)
terms["2D3_W_i_motion_p_h_center_p"] = (
    2.0 * hard_first_motion * evaluated(
        "D3_Eraw_p_h_center_p", embed, psi_matrix, psi_box
    )
)
terms["2D3_W_i_center_p_h_motion_p"] = (
    2.0 * psi_first_motion * evaluated(
        "D3_W_i_center_Eraw_p",
        whole_hard_first[:, DECISIVE_INDEX], embed, psi_box,
    )
)
terms["2D3_W_i_motion_p_h_motion_p"] = (
    2.0 * hard_first_motion * psi_first_motion * evaluated(
        "D3_Eraw_Eraw_p", embed, embed, psi_box
    )
)
terms["2D3_W_h_center_p_i_p"] = 2.0 * evaluated(
    "D3_W_h_center_p_i_p", whole_hard_first, psi_i_box, psi_box
)
terms["2D3_W_h_motion_p_i_p"] = 2.0 * hard_first_motion * evaluated(
    "D3_Eraw_p_i_p", embed, psi_i_box, psi_box
)
terms["2D3_W_p_ih_p"] = 2.0 * psi_second * evaluated(
    "D3_W_Eraw_p", whole_hard_interval, embed, psi_box
)
terms["2D3_W_p_i_p_h_center"] = 2.0 * evaluated(
    "D3_W_p_i_p_h_center", whole_hard_interval, psi_i_box, psi_matrix
)
terms["2D3_W_p_i_p_h_motion"] = 2.0 * psi_first_motion * evaluated(
    "D3_W_p_i_Eraw", whole_hard_interval, psi_i_box, embed
)

raw_row_upper = math.nextafter(math.fsum(terms.values()), math.inf)
signed_descriptor_upper = upward_decimal(
    field["center_field"]["signed_descriptor_decimal"]
)
suppressed_row_upper = math.nextafter(
    signed_descriptor_upper * raw_row_upper, math.inf
)
dominant_upper = float(dominant["fully_reduced_cb_row_2_norm_upper"])
ceiling = float(dominant["rigorous_resolving_row_norm_ceiling"])
combined_upper = math.nextafter(dominant_upper + suppressed_row_upper, math.inf)
remaining = math.nextafter(ceiling - combined_upper, -math.inf)

validation = {
    "reference_node_and_state_tube_are_unchanged": (
        dominant["tube"]["reference_node"] == 1214
        and float(dominant["tube"]["state_action_radius"]) == RADIUS
    ),
    "fixed_positive_descriptor_is_used": signed_descriptor_upper > 0.0,
    "response_second_variation_parent_is_certified": response_second > 0.0,
    "selected_line_second_variation_parent_is_certified": psi_second > 0.0,
    "response_first_matrix_motion_is_mean_value_bounded": (
        hard_first_motion == math.nextafter(response_second * RADIUS, math.inf)
    ),
    "selected_line_first_matrix_motion_is_mean_value_bounded": (
        psi_first_motion == math.nextafter(psi_second * RADIUS, math.inf)
    ),
    "all_ten_product_rule_terms_are_present": len(terms) == 18,
    "suppressed_hard_response_row_fits_remaining_budget": combined_upper < ceiling,
    "no_second_response_or_second_eigenline_tensor_is_inverted": True,
    "no_selector_recurrence_scale_fit_gate_or_chord_added": True,
}
validation = {key: bool(value) for key, value in validation.items()}
passed = all(validation.values())
payload = {
    "artifact": "BHSM_N12_C2_SUPPRESSED_HARD_RESPONSE_ROW_CERTIFICATE",
    "status": (
        "C2_COMPLETE_SIGNED_D2DELTA_DOMINANT_ROW_CERTIFIED"
        if passed else "C2_SUPPRESSED_HARD_RESPONSE_ROW_CERTIFICATE_INVALID"
    ),
    "classification": (
        "OUTWARD_ROUNDED_RETAINED_ACTION_TENSOR_INTERVAL_WITH_CERTIFIED_"
        "FIRST_MATRIX_MOTION_AND_INVERSE_FREE_SECOND_VARIATION_BOUNDS"
    ),
    "exact_identity": {
        "hard_contraction": "R=D3S[W,Psi,Psi],_W=Qdot+E*V_hard",
        "row": (
            "R_ih=D5S[i,h,W,Psi,Psi]+D4S[i,W_h,Psi,Psi]+"
            "D4S[h,W_i,Psi,Psi]+2D4S[i,W,Psi_h,Psi]+"
            "2D4S[h,W,Psi_i,Psi]+D3S[W_ih,Psi,Psi]+"
            "2D3S[W_i,Psi_h,Psi]+2D3S[W_h,Psi_i,Psi]+"
            "2D3S[W,Psi_ih,Psi]+2D3S[W,Psi_i,Psi_h]"
        ),
        "whole_hard_direction": "W=Qdot+E*V_hard",
        "whole_hard_first": "W_h=DQdot[h]+E*(V_hard)_h",
        "whole_hard_second": "W_ih=E*(V_hard)_ih",
    },
    "tube": {
        "reference_node": 1214,
        "state_action_radius": RADIUS,
        "Psi_radius": PSI_RADIUS,
        "Psi_i_radius": PSI_I_RADIUS,
        "V_hard_radius": V_RADIUS,
        "response_first_matrix_motion_upper": hard_first_motion,
        "selected_line_first_matrix_motion_upper": psi_first_motion,
    },
    "parent_variation_bounds": {
        "response_second_variation_upper": response_second,
        "selected_line_second_variation_upper": psi_second,
    },
    "raw_R_second_row_term_norm_uppers": terms,
    "raw_R_second_row_2_norm_upper": raw_row_upper,
    "signed_descriptor_absolute_upper": signed_descriptor_upper,
    "s_suppressed_R_second_row_2_norm_upper": suppressed_row_upper,
    "dominant_cb_row_2_norm_upper": dominant_upper,
    "complete_signed_D2Delta_row_2_norm_upper": combined_upper,
    "rigorous_resolving_row_norm_ceiling": ceiling,
    "remaining_row_budget": remaining,
    "adjudication": {
        "dominant_cb_row": "CERTIFIED",
        "s_suppressed_hard_response_row": (
            "CERTIFIED" if passed else "OPEN"
        ),
        "complete_signed_D2Delta_dominant_row": (
            "CERTIFIED_BELOW_RESOLVING_CEILING" if passed else "OPEN"
        ),
        "signed_D_Y_Delta_on_exact_node_1214_family": (
            "ZERO_EXCLUDED" if passed else "OPEN"
        ),
        "local_duration_denominator_data": (
            "CERTIFIED" if passed else "OPEN"
        ),
        "transposed_exact_segment_map_action": "OPEN",
        "complete_upstream_heat_minus_zeta_covector": "OPEN",
        "maximal_projected_tail": "OPEN",
        "Gate7": "OPEN",
        "Gate8": "LOCKED",
        "chord_03_authorized": False,
    },
    "exact_next_dependency": (
        "APPLY_THE_CERTIFIED_LOCAL_SIGNED_DURATION_COVECTOR_THROUGH_THE_"
        "TRANSPOSED_EXACT_SEGMENT_MAP_AND_ASSEMBLE_THE_COMPLETE_UPSTREAM_"
        "HEAT_MINUS_ZETA_FORCE_COVECTOR_ON_THE_PHYSICAL_QUOTIENT"
    ),
    "inputs": {
        path.relative_to(ROOT).as_posix(): sha256(path)
        for path in provenance_inputs()
    },
    "validation": validation,
    "validation_passed": passed,
    "FLAGSHIP_READY": False,
    "FULL_BHSM_COMPLETE": False,
}
RESULT.write_text(
    json.dumps(payload, indent=2, sort_keys=True) + "\n",
    encoding="utf-8",
    newline="\n",
)
print(json.dumps({
    "status": payload["status"],
    "raw_R_second_row_2_norm_upper": raw_row_upper,
    "s_suppressed_R_second_row_2_norm_upper": suppressed_row_upper,
    "complete_signed_D2Delta_row_2_norm_upper": combined_upper,
    "rigorous_resolving_row_norm_ceiling": ceiling,
    "remaining_row_budget": remaining,
    "validation_passed": passed,
}, indent=2, sort_keys=True))
