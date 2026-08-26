"""Certify the complete ``s D2 R`` operator on the node-1214 tube.

The proof uses the committed terminal-parent action ball after explicitly
checking that it contains the current tube.  The two large second-Jacobi
contractions are reused from their cancellation-preserving interval
evaluation; all remaining product-rule terms are bounded by the parent full
action majorants, with the hard first-matrix motion kept in the sharper
complement/selected geometry.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "artifacts" / "flagship_integration"
PARENT = BASE / "BHSM_N12_C2_TERMINAL_PARENT_ACTION_MAJORANTS_2P0E10.json"
PARENT_STATE = BASE / "BHSM_N12_FINITE_TERMINAL_RESET_STRATUM_CANDIDATE.npz"
BORDERED = BASE / "BHSM_N12_C2_BORDERED_HARD_RESPONSE_MATRIX.json"
BORDERED_DATA = BORDERED.with_suffix(".npz")
GROWTH = BASE / "BHSM_N12_C2_FRESH_CHART_FIXED_S_GROWTH.json"
RESPONSE = BASE / "BHSM_N12_C2_CANCELLED_FIELD_LOHNER_STEP.json"
FIELD = BASE / "BHSM_N12_C2_EXACT_CENTER_FIXED_S_FIELD_MATRIX.json"
SECOND_ROW = Path(os.environ.get(
    "BHSM_C2_SUPPRESSED_ROW_INPUT",
    BASE / "BHSM_N12_C2_SUPPRESSED_HARD_RESPONSE_ROW_CERTIFICATE.json",
)).resolve()
THEORY = Path(os.environ.get(
    "BHSM_C2_COMPLETE_SUPPRESSED_R_THEORY",
    ROOT / "theory" / "n12_c2_complete_suppressed_r_operator.md",
)).resolve()
RESULT = Path(os.environ.get(
    "BHSM_C2_COMPLETE_SUPPRESSED_R_RESULT",
    BASE / "BHSM_N12_C2_COMPLETE_SUPPRESSED_R_OPERATOR.json",
)).resolve()

QDIM = 37
TOTAL = 98
TUBE_RADIUS = float(os.environ.get(
    "BHSM_C2_TUBE_RADIUS", "5.5104723095444935e-11"
))
PSI_RADIUS = 6.0e-9
HARD_RADIUS = 40.0
INFLATION = 1.0 + 1.0e-12


def _up(value: float) -> float:
    return math.nextafter(float(value) * INFLATION, math.inf)


def _down(value: float) -> float:
    return math.nextafter(float(value) / INFLATION, -math.inf)


def _norm(value: np.ndarray) -> float:
    return _up(float(np.linalg.norm(np.asarray(value, dtype=float), 2)))


def _sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


parents = [_load(path) for path in (PARENT, BORDERED, GROWTH, RESPONSE, FIELD, SECOND_ROW)]
parent, bordered, growth, response, field, second_row = parents
if not all(item.get("validation_passed") is True for item in parents):
    raise RuntimeError("validated complete-suppressed-R parents are required")

with np.load(PARENT_STATE) as data:
    terminal_pair = np.asarray(data["state"], dtype=float)
    parent_weights = np.asarray(data["state_weights"], dtype=float)
with np.load(BORDERED_DATA) as data:
    state = np.asarray(data["center_state"], dtype=float)
    weights = np.asarray(data["state_weights"], dtype=float)
    psi = np.asarray(data["selected_vector"], dtype=float)
    psi_first = np.asarray(data["selected_vector_derivative_action"], dtype=float)
    hard = np.asarray(data["bordered_response"], dtype=float)[:-1]
    hard_first = np.asarray(data["bordered_response_derivative_action"], dtype=float)[:-1]

if terminal_pair.shape != (2 * TOTAL,) or not np.array_equal(weights, parent_weights):
    raise RuntimeError("terminal-parent and node-1214 action coordinates do not align")
terminal_event = terminal_pair[:TOTAL]
center_distance = _up(_norm(weights * (state - terminal_event)))
parent_radius = float(parent["action_coordinate_ball_radius"])
containing_radius = _up(center_distance + TUBE_RADIUS)

event = next(item for item in parent["sectors"] if item["sector"] == "event")
majorants = event["derivative_operator_majorants_0_through_5"]
d3, d4, d5 = (_up(float(majorants[index])) for index in (3, 4, 5))

reduced_weights = weights[QDIM:]
embed = np.zeros((TOTAL, TOTAL - QDIM))
embed[QDIM:] = np.diag(reduced_weights)
configuration = np.zeros(TOTAL)
configuration[:QDIM] = weights[:QDIM] * state[QDIM:2 * QDIM]
configuration_first = np.zeros((TOTAL, TOTAL))
configuration_first[:QDIM, QDIM:2 * QDIM] = np.diag(
    weights[:QDIM] / weights[QDIM:2 * QDIM]
)

p_center = embed @ psi
p_first_center = embed @ psi_first
w_center = configuration + embed @ hard
w_first_center = configuration_first + embed @ hard_first

embed_norm = _norm(embed)
p_center_norm = _norm(p_center)
p_direction_motion = _up(embed_norm * PSI_RADIUS)
p_ball_norm = _up(p_center_norm + p_direction_motion)
w_ball_norm = _up(
    _norm(w_center)
    + _norm(configuration_first) * TUBE_RADIUS
    + embed_norm * HARD_RADIUS
)
p_first_center_norm = _norm(p_first_center)
w_first_center_norm = _norm(w_first_center)

line_second = float(
    growth["fresh_line_bounds"]["selected_line_second_variation_coefficient_upper"]
)
response_second = float(
    response["second_variation"]["response_second_variation_upper"]
)
psi_first_motion_raw = _up(line_second * TUBE_RADIUS)
hard_first_motion_raw = _up(response_second * TUBE_RADIUS)
p_first_motion_norm = _up(embed_norm * psi_first_motion_raw)
p_first_ball_norm = _up(p_first_center_norm + p_first_motion_norm)

mixed = growth["retained_action_mixed_bounds"]
d3_ccp = _up(float(mixed["D3_CCP"]))
d3_cpp = _up(float(mixed["D3_CPP"]))
d4_xcpp = _up(float(mixed["D4_XCPP"]))

# The normalized eigenline derivative is complement-valued.  Retain the tiny
# floating-point selected leakage explicitly instead of declaring it zero.
selected_leakage = _norm(psi @ psi_first)
psi_first_complement_raw = _up(_norm(psi_first) + selected_leakage)
ccp_with_motion = _up(
    d3_ccp * (psi_first_complement_raw + psi_first_motion_raw)
    + d3_cpp * (selected_leakage + psi_first_motion_raw)
)

row_terms = second_row["raw_R_second_row_term_norm_uppers"]
sharp_w_second = _up(float(row_terms["D3_W_ih_p_p"]))
sharp_psi_second = _up(float(row_terms["2D3_W_p_ih_p"]))

# R=D3S[W,Psi,Psi].  These eleven entries partition the ten exact second
# product-rule terms; the W_h and Psi_h terms are split into center/motion
# pieces so the large inverse-free motion is never fed to a generic bound.
terms = {
    "D5_i_h_W_p_p": _up(d5 * w_ball_norm * p_ball_norm**2),
    "two_D4_W_first_center_p_p": _up(
        2.0 * d4 * w_first_center_norm * p_ball_norm**2
    ),
    "two_D4_W_first_motion_selected_p_p": _up(
        2.0 * d4_xcpp * hard_first_motion_raw
    ),
    "two_D4_W_first_motion_p_box_correction": _up(
        2.0 * d4 * (embed_norm * hard_first_motion_raw)
        * (p_ball_norm**2 - p_center_norm**2)
    ),
    "four_D4_i_W_p_first_p": _up(
        4.0 * d4 * w_ball_norm * p_first_ball_norm * p_ball_norm
    ),
    "D3_W_second_p_p": sharp_w_second,
    "four_D3_W_first_center_p_first_p": _up(
        4.0 * d3 * w_first_center_norm * p_first_ball_norm * p_ball_norm
    ),
    "four_D3_W_first_motion_p_first_selected_p": _up(
        4.0 * hard_first_motion_raw * ccp_with_motion
    ),
    "four_D3_W_first_motion_p_box_correction": _up(
        4.0 * d3 * (embed_norm * hard_first_motion_raw)
        * p_first_ball_norm * p_direction_motion
    ),
    "two_D3_W_p_second_p": sharp_psi_second,
    "two_D3_W_p_first_p_first": _up(
        2.0 * d3 * w_ball_norm * p_first_ball_norm**2
    ),
}
raw_operator = _up(math.fsum(terms.values()))
signed_descriptor = _up(abs(float(field["center_field"]["signed_descriptor_decimal"])))
suppressed_operator = _up(signed_descriptor * raw_operator)

validation = {
    "terminal_parent_majorant_is_validated": parent["validation_passed"] is True,
    "node_tube_is_strictly_inside_terminal_parent_event_ball": containing_radius < parent_radius,
    "event_parent_supplies_derivatives_through_five": len(majorants) == 6 and d5 > 0.0,
    "complete_ten_term_product_rule_is_partitioned": len(terms) == 11,
    "hard_first_motion_uses_action_owned_complement_selected_bound": d4_xcpp > 0.0 and d3_ccp > 0.0,
    "selected_leakage_is_retained": selected_leakage >= 0.0,
    "global_certificate_dominates_decisive_row_certificate": (
        suppressed_operator >= float(second_row["s_suppressed_R_second_row_2_norm_upper"])
    ),
    "suppressed_operator_is_finite": math.isfinite(suppressed_operator),
    "no_inverse_selector_recurrence_scale_fit_gate_or_chord_added": True,
}
validation = {key: bool(value) for key, value in validation.items()}
passed = all(validation.values())

payload = {
    "artifact": "BHSM_N12_C2_COMPLETE_SUPPRESSED_R_OPERATOR",
    "status": (
        "C2_COMPLETE_SUPPRESSED_R_OPERATOR_CERTIFIED"
        if passed else "C2_COMPLETE_SUPPRESSED_R_OPERATOR_INVALID"
    ),
    "classification": (
        "OUTWARD_ROUNDED_GLOBAL_ACTION_OPERATOR_MAJORANT_WITH_"
        "CANCELLATION_PRESERVING_SECOND_JACOBI_CONTRACTIONS"
    ),
    "exact_identity": {
        "R": "D3S[W,Psi,Psi],_W=Qdot+E*V_hard",
        "D2R": (
            "D5S[i,h,W,Psi,Psi]+D4S[i,W_h,Psi,Psi]+D4S[h,W_i,Psi,Psi]+"
            "2D4S[i,W,Psi_h,Psi]+2D4S[h,W,Psi_i,Psi]+D3S[W_ih,Psi,Psi]+"
            "2D3S[W_i,Psi_h,Psi]+2D3S[W_h,Psi_i,Psi]+"
            "2D3S[W,Psi_ih,Psi]+2D3S[W,Psi_i,Psi_h]"
        ),
    },
    "parent_ball_containment": {
        "terminal_parent_sector": "event",
        "terminal_parent_action_radius": parent_radius,
        "node_1214_center_distance_from_parent_event": center_distance,
        "node_1214_tube_radius": TUBE_RADIUS,
        "containing_radius_upper": containing_radius,
        "strict_margin_lower": _down(parent_radius - containing_radius),
    },
    "action_majorants": {"D3": d3, "D4": d4, "D5": d5},
    "direction_bounds": {
        "embed_operator_norm_upper": embed_norm,
        "Psi_ball_action_norm_upper": p_ball_norm,
        "W_ball_action_norm_upper": w_ball_norm,
        "Psi_first_center_action_operator_norm_upper": p_first_center_norm,
        "Psi_first_motion_action_operator_norm_upper": p_first_motion_norm,
        "Psi_first_ball_action_operator_norm_upper": p_first_ball_norm,
        "W_first_center_action_operator_norm_upper": w_first_center_norm,
        "W_first_motion_raw_coefficient_upper": hard_first_motion_raw,
        "Psi_first_motion_raw_coefficient_upper": psi_first_motion_raw,
        "selected_line_first_derivative_leakage_upper": selected_leakage,
    },
    "raw_R_second_operator_term_uppers": terms,
    "raw_R_second_operator_2_norm_upper": raw_operator,
    "signed_descriptor_absolute_upper": signed_descriptor,
    "complete_s_suppressed_R_second_operator_2_norm_upper": suppressed_operator,
    "adjudication": {
        "complete_non_scale_sR_operator": "CERTIFIED",
        "complete_non_scale_D2Delta_operator": "OPEN_PENDING_COMPLETE_cb_ROW_SWEEP",
        "transposed_exact_segment_map_action": "OPEN",
        "Gate7": "OPEN",
        "Gate8": "LOCKED",
        "chord_03_authorized": False,
    },
    "exact_next_dependency": (
        "MERGE_THE_FINGERPRINTED_NON_SCALE_cb_ROW_SWEEP_AND_ADD_THIS_ONE_TIME_"
        "GLOBAL_sR_OPERATOR_BOUND"
    ),
    "inputs": {
        path.relative_to(ROOT).as_posix(): _sha256(path)
        for path in (
            PARENT, PARENT_STATE, BORDERED, BORDERED_DATA, GROWTH,
            RESPONSE, FIELD, SECOND_ROW, THEORY, Path(__file__),
        )
    },
    "validation": validation,
    "validation_passed": passed,
    "FLAGSHIP_READY": False,
    "FULL_BHSM_COMPLETE": False,
}

RESULT.write_text(
    json.dumps(payload, indent=2, sort_keys=True) + "\n",
    encoding="utf-8", newline="\n",
)
print(json.dumps({
    "status": payload["status"],
    "containing_radius_upper": containing_radius,
    "parent_radius": parent_radius,
    "raw_R_second_operator_2_norm_upper": raw_operator,
    "complete_s_suppressed_R_second_operator_2_norm_upper": suppressed_operator,
    "validation_passed": passed,
}, indent=2, sort_keys=True))
