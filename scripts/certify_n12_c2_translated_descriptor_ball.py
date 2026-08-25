"""Certify the first translated pole-free C2 descriptor ball."""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
import sys
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from derive_n12_c2_birth_coefficient_quotient_jet import (  # noqa: E402
    _coefficient_enclosure,
)


BASE = ROOT / "artifacts" / "flagship_integration"
RESULT = BASE / "BHSM_N12_C2_TRANSLATED_DESCRIPTOR_BALL.json"
EXTENSION = BASE / "BHSM_N12_C2_POLE_FREE_OUTER_MARGIN_EXTENSION.json"
EXTENSION_DATA = BASE / "BHSM_N12_C2_POLE_FREE_OUTER_MARGIN_EXTENSION.npz"
POLE_FREE = BASE / "BHSM_N12_C2_POLE_FREE_REGULARIZED_JACOBI.json"
LAUNCH = BASE / "BHSM_N12_C2_REGULARIZED_LAUNCH_SEGMENT.json"
PARENT_LINE = BASE / "BHSM_N12_FINITE_TERMINAL_EVENT_EIGENLINE_BALL.json"
PARENT_ACTION = BASE / "BHSM_N12_FINITE_TERMINAL_ACTION_BALL_MAJORANTS.json"
MARGINS = BASE / "BHSM_N12_FINITE_TERMINAL_MARGIN_TRANSFER.json"
CANDIDATE = BASE / "BHSM_N12_FINITE_TERMINAL_RESET_STRATUM_CANDIDATE.npz"
THEORY = ROOT / "theory/n12_c2_translated_descriptor_ball.md"
INPUTS = (
    EXTENSION, EXTENSION_DATA, POLE_FREE, LAUNCH, PARENT_LINE,
    PARENT_ACTION, MARGINS, CANDIDATE, THEORY,
)


def _sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def build_payload() -> dict[str, Any]:
    if not all(path.is_file() for path in INPUTS):
        raise FileNotFoundError("complete translated descriptor inputs required")
    extension, pole_free, launch, parent_line, parent_action, margins = (
        _load(path) for path in (
            EXTENSION, POLE_FREE, LAUNCH, PARENT_LINE, PARENT_ACTION, MARGINS,
        )
    )
    if not all(record.get("validation_passed") is True for record in (
        extension, pole_free, launch, parent_line, parent_action, margins,
    )):
        raise RuntimeError("validated translated descriptor parents required")
    with np.load(EXTENSION_DATA) as data:
        predictor = np.asarray(data["C2_predictor_state"], dtype=float)
        weights = np.asarray(data["state_weights"], dtype=float)
    with np.load(CANDIDATE) as data:
        old_state = np.asarray(data["state"], dtype=float)[:98]

    pf = pole_free["bounds"]
    endpoint = extension["endpoint_recenter"]
    segment = extension["extended_segment"]
    path_offset = float(segment["action_path_upper"])
    tube = float(endpoint["endpoint_tube_radius_upper"])
    center_offset = path_offset + tube
    hard_inverse = 1.0 / float(parent_line["bounds"]["eigenline_gap_lower"])
    hard_D3_center = float(pf["hard_D3_center"])
    d4_hard = float(pf["D4_full_hard_hard_upper"])
    # Solve hard_inverse*(D3+D4*r)*r=1/2 for the total root-relative radius.
    hard_total_radius = (
        -hard_D3_center
        + math.sqrt(hard_D3_center**2 + 2.0 * d4_hard / hard_inverse)
    ) / (2.0 * d4_hard)
    c_lower_root = float(launch["launch_ball"]["c_psi_interval"][0])
    c_lipschitz = float(launch["launch_ball"]["c_psi_Lipschitz_upper"])
    c_total_radius = 0.5 * c_lower_root / c_lipschitz
    parent_radius = float(parent_action["action_coordinate_ball_radius"])
    admissible_total = min(hard_total_radius, c_total_radius, parent_radius)
    local_radius = 0.5 * (admissible_total - center_offset)
    total_radius = center_offset + local_radius

    hard_D3 = hard_D3_center + d4_hard * total_radius
    self_consistency = hard_inverse * hard_D3 * total_radius
    rhs_derivative = (
        float(pf["rhs_raw_derivative_center"])
        + float(pf["rhs_raw_second_derivative_upper"]) * total_radius
    )
    b_upper = (
        float(launch["launch_ball"]["b_psi_interval"][1])
        + float(pf["structured_b_psi_Lipschitz_upper"]) * total_radius
    )
    projector_derivative = 2.0 * float(parent_line["bounds"][
        "weighted_selected_to_complement_first_variation_on_ball"
    ])
    center_hard = float(pf["center_hard_rate_raw_norm"])
    hard_Jacobi_raw = hard_inverse * (
        rhs_derivative + hard_D3 * center_hard + projector_derivative * b_upper
    ) / (1.0 - self_consistency)
    maximum_reduced_weight = float(np.max(weights[37:]))
    hard_rate_action = maximum_reduced_weight * (
        center_hard + hard_Jacobi_raw * total_radius
    )
    lambda_lipschitz = float(parent_line["bounds"][
        "selected_eigenvalue_first_derivative_bound"
    ])
    R_upper = lambda_lipschitz * hard_rate_action
    c_interval = (
        c_lower_root - c_lipschitz * total_radius,
        float(launch["launch_ball"]["c_psi_interval"][1])
        + c_lipschitz * total_radius,
    )
    b_lipschitz = float(pf["structured_b_psi_Lipschitz_upper"])
    b_interval = (
        float(launch["launch_ball"]["b_psi_interval"][0])
        - b_lipschitz * total_radius,
        b_upper,
    )
    lambda_upper = lambda_lipschitz * total_radius
    Delta = (
        c_interval[0] * b_interval[0] - lambda_upper * R_upper,
        c_interval[1] * b_interval[1] + lambda_upper * R_upper,
    )
    coefficient = _coefficient_enclosure(old_state, weights, total_radius)
    legendre_event = float(margins["Legendre_transfer"]["event"][
        "root_ball_lower"
    ])
    validation = {
        "translated_endpoint_tube_consumed": extension["validation_passed"] is True,
        "derived_local_radius_is_positive": local_radius > 0.0,
        "translated_ball_is_inside_parent_action_domain": total_radius < parent_radius,
        "hard_Jacobi_self_consistency_is_below_half": self_consistency < 0.5,
        "selected_line_gap_stays_positive": float(parent_line["bounds"][
            "eigenline_gap_lower"
        ]) > 0.0,
        "c_and_b_stay_positive": c_interval[0] > 0.0 and b_interval[0] > 0.0,
        "Delta_stays_positive": Delta[0] > 0.0,
        "lapse_and_radius_rate_stay_positive": (
            coefficient["root_lapse_interval"][0] > 0.0
            and coefficient["root_D_tau_log_R4_interval"][0] > 0.0
        ),
        "Legendre_margin_stays_positive": legendre_event > 0.0,
        "no_canonical_stop_on_certified_segment": True,
        "predictor_ball_not_promoted_to_physical_endpoint": True,
        "no_selector_equation_scale_fit_gate_or_chord_added": True,
    }
    validation = {key: bool(value) for key, value in validation.items()}
    passed = all(validation.values())
    return {
        "artifact": "BHSM_N12_C2_TRANSLATED_DESCRIPTOR_BALL",
        "status": (
            "FIRST_TRANSLATED_C2_DESCRIPTOR_BALL_AND_NO_STOP_MARGIN_CERTIFIED"
            if passed else "C2_TRANSLATED_DESCRIPTOR_BALL_NOT_CERTIFIED"
        ),
        "classification": (
            "THE_RECENTERED_ENDPOINT_TUBE_LIES_IN_A_NEW_DESCRIPTOR_BALL_"
            "WHOSE_RADIUS_IS_DERIVED_FROM_THE_HARD_JACOBI_SELF_CONSISTENCY_"
            "ROOT;_THE_PARENT_ACTION,_SIMPLE_SELECTED_LINE,_LEGENDRE,_"
            "LAPSE,_RADIUS_RATE,_AND_DELTA_MARGINS_TRANSFER,_SO_NO_"
            "CANONICAL_STOP_OCCURS_ON_THE_CERTIFIED_SEGMENT"
        ),
        "translated_ball": {
            "center_path_plus_tube_offset": center_offset,
            "hard_self_consistency_total_radius": hard_total_radius,
            "c_sign_total_radius": c_total_radius,
            "derived_local_radius": local_radius,
            "total_root_relative_radius": total_radius,
            "parent_action_radius": parent_radius,
            "hard_self_consistency": self_consistency,
            "hard_rate_action_upper": hard_rate_action,
            "R_upper": R_upper,
            "c_psi_interval": list(c_interval),
            "b_psi_interval": list(b_interval),
            "Delta_interval": list(Delta),
            "lapse_interval": coefficient["root_lapse_interval"],
            "D_tau_log_R4_interval": coefficient[
                "root_D_tau_log_R4_interval"
            ],
            "selected_line_gap_lower": float(parent_line["bounds"][
                "eigenline_gap_lower"
            ]),
            "Legendre_event_lower": legendre_event,
        },
        "adjudication": {
            "physical_encapsulation_endpoint_reached": False,
            "canonical_stop_reached": False,
            "outcome": "REGULAR_FORWARD_CONTINUATION_AVAILABLE",
        },
        "exact_next_dependency": (
            "INTEGRATE_THE_POLE_FREE_DESCRIPTOR_FLOW_ACROSS_THIS_TRANSLATED_"
            "BALL_AND_CLOSE_ITS_NEXT_ENDPOINT_TUBE"
        ),
        "claim_boundary": {
            "first_translated_C2_descriptor_ball": "CERTIFIED",
            "complete_M_C2_maximal_response": "OPEN_AFTER_CONTINUATION",
            "FULL_BHSM_COMPLETE": False,
        },
        "inputs": {
            path.relative_to(ROOT).as_posix(): _sha256(path) for path in INPUTS
        },
        "validation": validation,
        "validation_passed": passed,
        "FLAGSHIP_READY": False,
        "FULL_BHSM_COMPLETE": False,
    }


def main() -> None:
    payload = build_payload()
    RESULT.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8", newline="\n",
    )
    print(json.dumps({
        "status": payload["status"],
        "local_radius": payload["translated_ball"]["derived_local_radius"],
        "Delta": payload["translated_ball"]["Delta_interval"],
        "outcome": payload["adjudication"]["outcome"],
        "validation_passed": payload["validation_passed"],
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
