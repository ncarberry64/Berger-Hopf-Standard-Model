"""Assemble inverse-free Weyl enclosures on the extended C2 segment."""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
import sys
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bhsm.interface.aether_forward_boundary_radius import (  # noqa: E402
    boundary_log_radius_jets,
)
from bhsm.interface.aether_forward_c2_volterra_enclosure import (  # noqa: E402
    short_segment_transfer_weyl_enclosure,
)


BASE = ROOT / "artifacts" / "flagship_integration"
RESULT = BASE / "BHSM_N12_C2_OUTER_MARGIN_VOLTERRA_WEYL.json"
EXTENSION = BASE / "BHSM_N12_C2_POLE_FREE_OUTER_MARGIN_EXTENSION.json"
LAUNCH = BASE / "BHSM_N12_C2_REGULARIZED_LAUNCH_SEGMENT.json"
POLE_FREE = BASE / "BHSM_N12_C2_POLE_FREE_REGULARIZED_JACOBI.json"
CANDIDATE = BASE / "BHSM_N12_FINITE_TERMINAL_RESET_STRATUM_CANDIDATE.npz"
PRIOR = BASE / "BHSM_N12_C2_INVERSE_FREE_VOLTERRA_WEYL_SEGMENT.json"
MODULE = ROOT / "src/bhsm/interface/aether_forward_c2_volterra_enclosure.py"
THEORY = ROOT / "theory/n12_c2_outer_margin_volterra_weyl.md"
INPUTS = (EXTENSION, LAUNCH, POLE_FREE, CANDIDATE, PRIOR, MODULE, THEORY)


def _sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def build_payload() -> dict[str, Any]:
    if not all(path.is_file() for path in INPUTS):
        raise FileNotFoundError("complete extended Weyl inputs required")
    extension, launch, pole_free, prior = (
        _load(path) for path in (EXTENSION, LAUNCH, POLE_FREE, PRIOR)
    )
    if not all(record.get("validation_passed") is True for record in (
        extension, launch, pole_free, prior,
    )):
        raise RuntimeError("validated extended C2 parents required")
    with np.load(CANDIDATE) as data:
        state = np.asarray(data["state"], dtype=float)[:98]
        weights = np.asarray(data["state_weights"], dtype=float)

    segment = extension["extended_segment"]
    improved = extension["improved_launch_ball"]
    x_interval = tuple(float(value) for value in launch["explicit_segment"][
        "log_R4_interval_on_launch_ball"
    ])
    h_interval = tuple(float(value) for value in launch["explicit_segment"][
        "D_tau_log_R4_interval_on_launch_ball"
    ])
    duration = tuple(float(value) for value in segment["proper_time_interval"])
    growth = float(segment["Jacobi_growth_upper"])

    jets = boundary_log_radius_jets(
        12, state[:37], np.zeros(37), np.zeros(37)
    )
    gradient = np.asarray(jets["gradient"], dtype=float)
    gradient_norm = float(np.linalg.norm(gradient / weights[:37]))
    signs_j = (-1.0) ** np.arange(12)
    b_dual = float(np.linalg.norm(signs_j / weights[25:37]))
    gradient_upper = gradient_norm + 2.0 * b_dual**2 * float(
        improved["outer_action_radius"]
    )
    x_parameter = gradient_upper * growth

    signs_k = (-1.0) ** np.arange(1, 13)
    lapse_dual = float(np.linalg.norm(signs_k / weights[74:86]))
    lapse_lower, lapse_upper = (
        float(value) for value in launch["explicit_segment"][
            "lapse_interval_on_launch_ball"
        ]
    )
    Delta_lower = float(improved["Delta_interval"][0])
    Delta_derivative = float(pole_free["bounds"][
        "Delta_action_derivative_upper"
    ])
    lambda_end = float(segment["signed_lambda_end"])
    duration_parameter = (
        0.5 * lambda_end**2
        * (
            lapse_upper * lapse_dual / Delta_lower
            + lapse_upper * Delta_derivative / Delta_lower**2
        ) * growth
    )
    common = {
        "spectral_parameter": -1.0,
        "log_radius_interval": x_interval,
        "proper_log_radius_rate_absolute_upper": max(abs(value) for value in h_interval),
        "proper_duration_interval": duration,
        "log_radius_parameter_upper": x_parameter,
        "proper_duration_parameter_upper": duration_parameter,
    }
    channels = {
        "scalar_c3": short_segment_transfer_weyl_enclosure(
            channel="scalar", unit_channel_value=3.0, **common
        ),
        "product_Dirac_lambda1_5_chirality_plus": short_segment_transfer_weyl_enclosure(
            channel="product_Dirac", unit_channel_value=1.5, chirality=1, **common
        ),
        "product_Dirac_lambda1_5_chirality_minus": short_segment_transfer_weyl_enclosure(
            channel="product_Dirac", unit_channel_value=1.5, chirality=-1, **common
        ),
    }
    prior_margin = min(
        row["chart_margin_lower"]
        for row in prior["channels_at_z_minus_1"].values()
    )
    validation = {
        "extended_actual_C2_segment_consumed": extension["validation_passed"] is True,
        "all_transfer_b_charts_positive": all(
            row["chart_margin_lower"] > 0.0 for row in channels.values()
        ),
        "extended_chart_margin_exceeds_prior_margin": min(
            row["chart_margin_lower"] for row in channels.values()
        ) > prior_margin,
        "moving_duration_and_state_Jacobi_propagated": (
            x_parameter > 0.0 and duration_parameter > 0.0
        ),
        "all_first_Weyl_bounds_finite": all(math.isfinite(
            row["first_parameter_bounds"]["Weyl_parameter_Frobenius_upper"]
        ) for row in channels.values()),
        "no_endpoint_load_or_matrix_inverse": all(
            not row["terminal_load_imposed"]
            and not row["explicit_matrix_inverse_formed"]
            for row in channels.values()
        ),
        "translated_edge_not_promoted_to_physical_endpoint": True,
    }
    passed = all(validation.values())
    return {
        "artifact": "BHSM_N12_C2_OUTER_MARGIN_VOLTERRA_WEYL",
        "status": (
            "EXTENDED_ACTUAL_C2_VOLTERRA_WEYL_AND_FIRST_QUOTIENT_BOUND_CERTIFIED"
            if passed else "C2_OUTER_MARGIN_VOLTERRA_WEYL_NOT_CERTIFIED"
        ),
        "classification": (
            "THE_LONGER_POLE_FREE_C2_SEGMENT_IS_COMPOSED_WITH_THE_EXISTING_"
            "FIXED_CHANNEL_OPERATOR;_DUHAMEL_CONTROL_PRESERVES_THE_FREE_"
            "TWO_BOUNDARY_CALDERON_CHART_AND_PROPAGATES_THE_STATE_AND_"
            "MOVING_DURATION_FIRST_PHYSICAL_QUOTIENT_BOUNDS"
        ),
        "physical_quotient_pullback": {
            "state_Jacobi_growth_upper": growth,
            "log_radius_parameter_upper": x_parameter,
            "proper_duration_parameter_upper": duration_parameter,
        },
        "channels_at_z_minus_1": channels,
        "exact_next_dependency": (
            "TRANSLATE_THE_RETAINED_ACTION_DESCRIPTOR_BALL_TO_THE_CERTIFIED_"
            "PREDICTOR_TUBE_AND_CONTINUE_OR_RECORD_THE_FIRST_CANONICAL_STOP"
        ),
        "claim_boundary": {
            "extended_C2_transfer_segment": "CERTIFIED",
            "complete_M_C2_maximal_response": "OPEN_AFTER_CONTINUATION",
            "physical_encapsulation_endpoint_reached": False,
            "canonical_stop_reached": False,
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
        "chart_margins": {
            key: row["chart_margin_lower"]
            for key, row in payload["channels_at_z_minus_1"].items()
        },
        "validation_passed": payload["validation_passed"],
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
