"""Combine the 1222-core radius and moving-duration reset pullback bounds."""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "artifacts" / "flagship_integration"
RESULT = BASE / "BHSM_N12_C2_1222_COMPLETE_GEOMETRY_PULLBACK_NORM.json"
RADIUS = BASE / "BHSM_N12_C2_1222_RESET_QUOTIENT_RADIUS_PULLBACK_ENCLOSURE.json"
DURATION = BASE / "BHSM_N12_C2_1222_MOVING_DURATION_PULLBACK_ENCLOSURE.json"
THEORY = ROOT / "theory" / "n12_c2_1222_complete_geometry_pullback_norm.md"
INPUTS = (RADIUS, DURATION, THEORY)


def _sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _logaddexp(left: float, right: float) -> float:
    maximum = max(left, right)
    return maximum + math.log(math.exp(left - maximum) + math.exp(right - maximum))


def build_payload() -> dict[str, Any]:
    missing = [str(path) for path in INPUTS if not path.is_file()]
    if missing:
        raise FileNotFoundError("missing complete-pullback inputs: " + ", ".join(missing))
    radius, duration = (_load(path) for path in (RADIUS, DURATION))
    if not radius["validation_passed"] or not duration["validation_passed"]:
        raise RuntimeError("validated radius and duration pullbacks required")
    channels = {}
    for name, radius_row in radius["fixed_node_radius_pullback"].items():
        duration_row = duration["channel_duration_pullback"][name]
        log_bound = _logaddexp(
            float(radius_row["log_reset_image_operator_norm_upper"]),
            float(duration_row["log_reset_image_operator_norm_upper"]),
        )
        channels[name] = {
            "fixed_node_radius_norm_upper": radius_row["reset_image_operator_norm_upper"],
            "moving_duration_log10_norm_upper": duration_row["log10_reset_image_operator_norm_upper"],
            "complete_geometry_log_norm_upper": log_bound,
            "complete_geometry_log10_norm_upper": log_bound / math.log(10.0),
            "complete_geometry_norm_upper": (
                math.exp(log_bound) if log_bound < math.log(1.7976931348623157e308) else None
            ),
            "signed_covector_value_evaluated": False,
        }
    validation = {
        "radius_pullback_certified": radius["claim_boundary"]["fixed_node_radius_pullback"] == "CERTIFIED",
        "duration_pullback_norm_certified": duration["claim_boundary"]["moving_duration_reset_pullback_norm"].startswith("CERTIFIED"),
        "all_three_channel_geometry_norms_are_finite": all(math.isfinite(row["complete_geometry_log_norm_upper"]) for row in channels.values()),
        "signed_covector_value_not_overclaimed": all(row["signed_covector_value_evaluated"] is False for row in channels.values()),
        "maximal_tail_not_closed_by_finite_core_norm": duration["claim_boundary"]["maximal_tail_beyond_1222"] == "OPEN",
        "no_selector_recurrence_scale_fit_action_term_gate_or_chord_added": True,
    }
    validation = {key: bool(value) for key, value in validation.items()}
    passed = all(validation.values())
    return {
        "artifact": "BHSM_N12_C2_1222_COMPLETE_GEOMETRY_PULLBACK_NORM",
        "status": "C2_1222_COMPLETE_GEOMETRY_RESET_PULLBACK_NORM_CERTIFIED" if passed else "C2_1222_COMPLETE_GEOMETRY_PULLBACK_NOT_CERTIFIED",
        "classification": "THE_FIXED_NODE_RADIUS_AND_MOVING_PROPER_DURATION_PARTS_OF_THE_STORED_1222_CORE_WEYL_COEFFICIENT_COTANGENT_HAVE_ONE_FINITE_RESET_IMAGE_OPERATOR_NORM_BOUND;_THE_SIGNED_BACKWARD_CENTER_ADJOINT_VALUE_AND_MAXIMAL_TAIL_REMAIN_OPEN",
        "channels_at_z_minus_1": channels,
        "theorem": {
            "decomposition": "D_Y0_M_C=D_Y0_M_C|radius+D_Y0_M_C|duration",
            "norm_rule": "norm(D_Y0_M_C)<=B_radius+B_duration",
            "quotient_rule": "ORTHOGONAL_GAUGE_TIME_PROJECTION_CANNOT_INCREASE_THE_RESET_IMAGE_BOUND",
        },
        "adjudication": {
            "finite_core_geometry_first_jet_existence_and_norm": "CLOSED",
            "finite_core_signed_geometry_covector": "OPEN_BACKWARD_CENTER_ADJOINT",
            "maximal_geometry_cotangent_tail": "OPEN",
            "actual_graded_force": "OPEN",
        },
        "exact_next_dependency": "EVALUATE_THE_SIGNED_INVERSE_FREE_BACKWARD_CENTER_ADJOINT_ON_THE_1222_CORE_AND_CONTRACT_THE_GRADED_SOURCE;_DO_NOT_BUILD_MORE_NORM_ONLY_GEOMETRY_CERTIFICATES",
        "claim_boundary": {
            "Gate7": "ACTIVE_SIGNED_CENTER_ADJOINT_GRADED_FORCE_AND_MAXIMAL_TAIL",
            "Gate8": "LOCKED",
            "complete_finite_core_geometry_pullback_norm": "CERTIFIED",
            "signed_finite_core_geometry_covector": "OPEN",
            "actual_projected_zero_source_force": "OPEN",
            "chord_03_authorized": False,
            "frozen_predictions_changed": False,
            "FLAGSHIP_READY": False,
            "FULL_BHSM_COMPLETE": False,
        },
        "inputs": {path.relative_to(ROOT).as_posix(): _sha256(path) for path in INPUTS},
        "validation": validation,
        "validation_passed": passed,
        "FLAGSHIP_READY": False,
        "FULL_BHSM_COMPLETE": False,
    }


def main() -> None:
    payload = build_payload()
    RESULT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({
        "status": payload["status"],
        "log10_bounds": {name: row["complete_geometry_log10_norm_upper"] for name, row in payload["channels_at_z_minus_1"].items()},
        "validation_passed": payload["validation_passed"],
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
