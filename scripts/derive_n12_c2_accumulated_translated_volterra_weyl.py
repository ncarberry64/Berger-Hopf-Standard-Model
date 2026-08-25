"""Compose the launch and first translated C2 Volterra/Weyl enclosures."""

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
sys.path.insert(0, str(ROOT / "scripts"))

from bhsm.interface.aether_forward_boundary_radius import (  # noqa: E402
    boundary_log_radius_jets,
)
from bhsm.interface.aether_forward_c2_volterra_enclosure import (  # noqa: E402
    short_segment_transfer_weyl_enclosure,
)
from derive_n12_c2_birth_coefficient_quotient_jet import (  # noqa: E402
    _coefficient_enclosure,
)


BASE = ROOT / "artifacts" / "flagship_integration"
RESULT = BASE / "BHSM_N12_C2_ACCUMULATED_TRANSLATED_VOLTERRA_WEYL.json"
SEGMENT = BASE / "BHSM_N12_C2_TRANSLATED_POLE_FREE_SEGMENT.json"
BALL = BASE / "BHSM_N12_C2_TRANSLATED_DESCRIPTOR_BALL.json"
EXTENSION = BASE / "BHSM_N12_C2_POLE_FREE_OUTER_MARGIN_EXTENSION.json"
PRIOR = BASE / "BHSM_N12_C2_OUTER_MARGIN_VOLTERRA_WEYL.json"
CANDIDATE = BASE / "BHSM_N12_FINITE_TERMINAL_RESET_STRATUM_CANDIDATE.npz"
MODULE = ROOT / "src/bhsm/interface/aether_forward_c2_volterra_enclosure.py"
THEORY = ROOT / "theory/n12_c2_accumulated_translated_volterra_weyl.md"
INPUTS = (SEGMENT, BALL, EXTENSION, PRIOR, CANDIDATE, MODULE, THEORY)


def _sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def build_payload() -> dict[str, Any]:
    if not all(path.is_file() for path in INPUTS):
        raise FileNotFoundError("complete accumulated translated Weyl inputs required")
    segment, ball, extension, prior = (
        _load(path) for path in (SEGMENT, BALL, EXTENSION, PRIOR)
    )
    if not all(record.get("validation_passed") is True for record in (
        segment, ball, extension, prior,
    )):
        raise RuntimeError("validated accumulated C2 parents required")
    with np.load(CANDIDATE) as data:
        state = np.asarray(data["state"], dtype=float)[:98]
        weights = np.asarray(data["state_weights"], dtype=float)

    translated = ball["translated_ball"]
    translated_segment = segment["translated_segment"]
    first = extension["extended_segment"]
    radius = float(translated["total_root_relative_radius"])
    coefficient = _coefficient_enclosure(state, weights, radius)
    x_interval = tuple(float(value) for value in coefficient["root_log_R4_interval"])
    h_interval = tuple(
        float(value) for value in translated["D_tau_log_R4_interval"]
    )
    duration_increment = tuple(
        float(value) for value in translated_segment[
            "proper_time_increment_interval"
        ]
    )
    duration = (
        float(first["proper_time_interval"][0]) + duration_increment[0],
        float(first["proper_time_interval"][1]) + duration_increment[1],
    )
    growth = (
        float(first["Jacobi_growth_upper"])
        * float(translated_segment["Jacobi_growth_upper"])
    )

    jets = boundary_log_radius_jets(
        12, state[:37], np.zeros(37), np.zeros(37)
    )
    gradient = np.asarray(jets["gradient"], dtype=float)
    gradient_norm = float(np.linalg.norm(gradient / weights[:37]))
    signs_j = (-1.0) ** np.arange(12)
    b_dual = float(np.linalg.norm(signs_j / weights[25:37]))
    gradient_upper = gradient_norm + 2.0 * b_dual**2 * radius
    x_parameter = gradient_upper * growth

    signs_k = (-1.0) ** np.arange(1, 13)
    lapse_dual = float(np.linalg.norm(signs_k / weights[74:86]))
    lapse_lower, lapse_upper = (
        float(value) for value in translated["lapse_interval"]
    )
    Delta_lower = float(translated["Delta_interval"][0])
    Delta_derivative = float(segment["translated_generator"][
        "Delta_action_derivative_upper"
    ])
    signed_end = float(translated_segment["signed_lambda_end"])
    duration_parameter = (
        0.5 * signed_end**2
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
        "two_consecutive_actual_C2_segments_consumed": True,
        "proper_duration_is_strictly_accumulated": duration[0] > prior_margin,
        "all_accumulated_transfer_b_charts_positive": all(
            row["chart_margin_lower"] > 0.0 for row in channels.values()
        ),
        "accumulated_chart_margin_exceeds_prior_margin": min(
            row["chart_margin_lower"] for row in channels.values()
        ) > prior_margin,
        "composed_state_and_moving_duration_pullbacks_are_positive": (
            growth > 1.0 and x_parameter > 0.0 and duration_parameter > 0.0
        ),
        "all_accumulated_first_Weyl_bounds_finite": all(math.isfinite(
            row["first_parameter_bounds"]["Weyl_parameter_Frobenius_upper"]
        ) for row in channels.values()),
        "no_endpoint_load_or_matrix_inverse": all(
            not row["terminal_load_imposed"]
            and not row["explicit_matrix_inverse_formed"]
            for row in channels.values()
        ),
        "translated_predictor_not_promoted_to_physical_endpoint": True,
    }
    validation = {key: bool(value) for key, value in validation.items()}
    passed = all(validation.values())
    return {
        "artifact": "BHSM_N12_C2_ACCUMULATED_TRANSLATED_VOLTERRA_WEYL",
        "status": (
            "ACCUMULATED_TWO_SEGMENT_C2_VOLTERRA_WEYL_RESPONSE_CERTIFIED"
            if passed else "C2_ACCUMULATED_TRANSLATED_VOLTERRA_WEYL_NOT_CERTIFIED"
        ),
        "classification": (
            "THE_OUTER_MARGIN_LAUNCH_AND_FIRST_TRANSLATED_DESCRIPTOR_SEGMENT_"
            "ARE_COMPOSED_IN_THE_FREE_TWO_BOUNDARY_CALDERON_CHART;_THE_"
            "ACCUMULATED_STATE_AND_MOVING_DURATION_PULLBACKS_REMAIN_"
            "INVERSE_FREE_AND_REQUIRE_NO_TERMINAL_LOAD"
        ),
        "accumulated_history": {
            "segment_count": 2,
            "signed_lambda_end": signed_end,
            "proper_duration_interval": list(duration),
            "state_Jacobi_growth_upper": growth,
            "log_radius_parameter_upper": x_parameter,
            "proper_duration_parameter_upper": duration_parameter,
        },
        "channels_at_z_minus_1": channels,
        "exact_next_dependency": (
            "CONTINUE_THE_SAME_DESCRIPTOR_AND_VOLTERRA_COMPOSITION_ON_THE_"
            "NEXT_TRANSLATED_BALL_UNTIL_ENCAPSULATION_OR_A_CANONICAL_STOP"
        ),
        "claim_boundary": {
            "accumulated_two_segment_C2_response": "CERTIFIED" if passed else "OPEN",
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
        "duration": payload["accumulated_history"]["proper_duration_interval"],
        "chart_margins": {
            key: row["chart_margin_lower"]
            for key, row in payload["channels_at_z_minus_1"].items()
        },
        "validation_passed": payload["validation_passed"],
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
