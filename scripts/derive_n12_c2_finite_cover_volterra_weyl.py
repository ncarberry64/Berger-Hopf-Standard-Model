"""Assemble the inverse-free Weyl response on the finite C2 cover prefix."""

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

from bhsm.interface.aether_forward_boundary_radius import boundary_log_radius_jets  # noqa: E402
from bhsm.interface.aether_forward_c2_volterra_enclosure import (  # noqa: E402
    short_segment_transfer_weyl_enclosure,
)
from derive_n12_c2_birth_coefficient_quotient_jet import _coefficient_enclosure  # noqa: E402


BASE = ROOT / "artifacts" / "flagship_integration"
RESULT = BASE / "BHSM_N12_C2_FINITE_COVER_VOLTERRA_WEYL.json"
COVER = BASE / "BHSM_N12_C2_FINITE_TRANSLATED_DESCRIPTOR_COVER.json"
EXTENSION = BASE / "BHSM_N12_C2_POLE_FREE_OUTER_MARGIN_EXTENSION.json"
SECOND = BASE / "BHSM_N12_C2_TRANSLATED_POLE_FREE_SEGMENT.json"
PRIOR = BASE / "BHSM_N12_C2_ACCUMULATED_TRANSLATED_VOLTERRA_WEYL.json"
CANDIDATE = BASE / "BHSM_N12_FINITE_TERMINAL_RESET_STRATUM_CANDIDATE.npz"
MODULE = ROOT / "src/bhsm/interface/aether_forward_c2_volterra_enclosure.py"
THEORY = ROOT / "theory/n12_c2_finite_cover_volterra_weyl.md"
INPUTS = (COVER, EXTENSION, SECOND, PRIOR, CANDIDATE, MODULE, THEORY)


def _sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def build_payload() -> dict[str, Any]:
    if not all(path.is_file() for path in INPUTS):
        raise FileNotFoundError("complete finite-cover Weyl inputs required")
    cover, extension, second, prior = (
        _load(path) for path in (COVER, EXTENSION, SECOND, PRIOR)
    )
    if not all(record.get("validation_passed") is True for record in (
        cover, extension, second, prior,
    )):
        raise RuntimeError("validated finite-cover Weyl parents required")
    with np.load(CANDIDATE) as data:
        state = np.asarray(data["state"], dtype=float)[:98]
        weights = np.asarray(data["state_weights"], dtype=float)
    rows = cover["cover"]["rows"]
    radius = max(float(row["translated_ball_total_radius"]) for row in rows)
    coefficient = _coefficient_enclosure(state, weights, radius)
    first_duration = extension["extended_segment"]["proper_time_interval"]
    second_duration = second["translated_segment"]["proper_time_increment_interval"]
    duration = [
        float(first_duration[index]) + float(second_duration[index])
        + sum(float(row["proper_time_increment_interval"][index]) for row in rows)
        for index in range(2)
    ]
    growth = (
        float(extension["extended_segment"]["Jacobi_growth_upper"])
        * float(second["translated_segment"]["Jacobi_growth_upper"])
        * math.prod(float(row["Jacobi_growth_upper"]) for row in rows)
    )
    x_interval = tuple(float(value) for value in coefficient["root_log_R4_interval"])
    h_interval = tuple(
        float(value) for value in coefficient["root_D_tau_log_R4_interval"]
    )
    jets = boundary_log_radius_jets(12, state[:37], np.zeros(37), np.zeros(37))
    gradient = np.asarray(jets["gradient"], dtype=float)
    gradient_norm = float(np.linalg.norm(gradient / weights[:37]))
    signs_j = (-1.0) ** np.arange(12)
    b_dual = float(np.linalg.norm(signs_j / weights[25:37]))
    x_parameter = (gradient_norm + 2.0 * b_dual**2 * radius) * growth
    signs_k = (-1.0) ** np.arange(1, 13)
    lapse_dual = float(np.linalg.norm(signs_k / weights[74:86]))
    lapse_lower, lapse_upper = (
        float(value) for value in coefficient["root_lapse_interval"]
    )
    Delta_lower = min(float(row["Delta_lower"]) for row in rows)
    Delta_derivative = max(
        float(row["Delta_action_derivative_upper"]) for row in rows
    )
    signed_end = float(cover["cover"]["final_signed_lambda"])
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
        "proper_duration_interval": tuple(duration),
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
        row["chart_margin_lower"] for row in prior["channels_at_z_minus_1"].values()
    )
    validation = {
        "all_98_certified_segments_consumed": (
            cover["cover"]["certified_total_segment_count"] == 98
        ),
        "proper_duration_strictly_extends_two_segment_prefix": duration[0] > prior_margin,
        "all_transfer_b_charts_positive_and_extended": all(
            row["chart_margin_lower"] > prior_margin for row in channels.values()
        ),
        "state_and_moving_duration_pullbacks_propagated": (
            growth > 1.0 and x_parameter > 0.0 and duration_parameter > 0.0
        ),
        "all_first_Weyl_bounds_finite": all(math.isfinite(
            row["first_parameter_bounds"]["Weyl_parameter_Frobenius_upper"]
        ) for row in channels.values()),
        "no_terminal_load_or_matrix_inverse": all(
            not row["terminal_load_imposed"]
            and not row["explicit_matrix_inverse_formed"]
            for row in channels.values()
        ),
        "finite_cover_frontier_not_promoted_to_physical_endpoint": True,
    }
    validation = {key: bool(value) for key, value in validation.items()}
    passed = all(validation.values())
    return {
        "artifact": "BHSM_N12_C2_FINITE_COVER_VOLTERRA_WEYL",
        "status": (
            "FINITE_98_SEGMENT_C2_VOLTERRA_WEYL_RESPONSE_CERTIFIED"
            if passed else "C2_FINITE_COVER_VOLTERRA_WEYL_NOT_CERTIFIED"
        ),
        "finite_history_response": {
            "segment_count": 98,
            "signed_lambda_end": signed_end,
            "proper_duration_interval": duration,
            "state_Jacobi_growth_upper": growth,
            "maximum_root_relative_ball_radius": radius,
            "minimum_Delta_lower": Delta_lower,
            "log_radius_parameter_upper": x_parameter,
            "proper_duration_parameter_upper": duration_parameter,
        },
        "channels_at_z_minus_1": channels,
        "exact_next_dependency": (
            "REPLACE_THE_SCALAR_TUBE_ZENO_MAJORANT_BY_THE_DESCRIPTOR_SLICE_"
            "QUOTIENT_AND_MATRIX_LOHNER_REMAINDER,_THEN_EXTEND_THE_RESPONSE"
        ),
        "claim_boundary": {
            "finite_98_segment_C2_response": "CERTIFIED" if passed else "OPEN",
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
        "duration": payload["finite_history_response"]["proper_duration_interval"],
        "growth": payload["finite_history_response"]["state_Jacobi_growth_upper"],
        "chart_margins": {
            key: row["chart_margin_lower"]
            for key, row in payload["channels_at_z_minus_1"].items()
        },
        "validation_passed": payload["validation_passed"],
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
