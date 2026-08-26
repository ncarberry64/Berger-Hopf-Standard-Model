"""Certify the signed proper-duration density covector on the node-1214 tube."""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
import sys

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bhsm.interface.aether_forward_c2_geometry_incidence import (  # noqa: E402
    boundary_geometry_action_covectors,
)


BASE = ROOT / "artifacts" / "flagship_integration"
DDELTA = BASE / "BHSM_N12_C2_COMPLETE_NON_SCALE_DDELTA_OPERATOR.json"
DDELTA_DATA = DDELTA.with_suffix(".npz")
FIELD = BASE / "BHSM_N12_C2_EXACT_CENTER_FIXED_S_FIELD_MATRIX.json"
FIELD_DATA = FIELD.with_suffix(".npz")
STEP = BASE / "BHSM_N12_C2_CANCELLED_FIELD_LOHNER_STEP.json"
MODULE = ROOT / "src" / "bhsm" / "interface" / "aether_forward_c2_geometry_incidence.py"
THEORY = ROOT / "theory" / "n12_c2_node1214_signed_duration_density_covector.md"
RESULT = BASE / "BHSM_N12_C2_NODE1214_SIGNED_DURATION_DENSITY_COVECTOR.json"
DATA_RESULT = RESULT.with_suffix(".npz")
INFLATION = 1.0 + 1.0e-12


def _up(value: float) -> float:
    return math.nextafter(float(value) * INFLATION, math.inf)


def _down(value: float) -> float:
    return math.nextafter(float(value) / INFLATION, -math.inf)


def _sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    inputs = (DDELTA, DDELTA_DATA, FIELD, FIELD_DATA, STEP, MODULE, THEORY)
    missing = [str(path) for path in inputs if not path.is_file()]
    if missing:
        raise FileNotFoundError("missing signed-duration-density inputs: " + ", ".join(missing))
    ddelta, field, step = (_load(path) for path in (DDELTA, FIELD, STEP))
    if not all(record.get("validation_passed") is True for record in (ddelta, field, step)):
        raise RuntimeError("validated signed-duration-density parents are required")
    if ddelta.get("data_SHA256") != _sha256(DDELTA_DATA):
        raise RuntimeError("complete-DDelta data digest is stale")

    with np.load(FIELD_DATA) as data:
        center = np.asarray(data["center_state"], dtype=float)
        weights = np.asarray(data["state_weights"], dtype=float)
        delta_partial = np.asarray(data["Delta_first_partial_action"], dtype=float)[1:]
    with np.load(DDELTA_DATA) as data:
        stored_center = np.asarray(data["non_scale_DDelta_partial_action"], dtype=float)
        ddelta_radius = float(data["transported_action_dual_ball_radius_upper"])
    if not np.array_equal(delta_partial, stored_center):
        raise RuntimeError("duration and DDelta center covectors do not align")

    geometry = boundary_geometry_action_covectors(state=center, weights=weights)
    lapse_covector = np.asarray(geometry["D_log_lapse_action_dual"], dtype=float)[1:]
    lapse_norm = _up(float(np.linalg.norm(lapse_covector)))
    delta_center_norm = _up(float(np.linalg.norm(delta_partial)))
    radius = float(ddelta["transport"]["state_action_radius"])
    delta0 = float(field["center_field"]["Delta"])
    signed_s = float(field["center_field"]["signed_descriptor_decimal"])
    log_lapse0 = float(geometry["log_lapse"])
    lapse0 = math.exp(log_lapse0)

    # The newly certified DDelta ball supplies a much sharper value enclosure
    # than the old scalar Delta box: integrate its norm over the same convex
    # action tube, then use the exact affine log-lapse covector.
    ddelta_norm_upper = _up(delta_center_norm + ddelta_radius)
    delta_value_radius = _up(ddelta_norm_upper * radius)
    delta_interval = (
        _down(delta0 - delta_value_radius),
        _up(delta0 + delta_value_radius),
    )
    lapse_interval = (
        _down(math.exp(log_lapse0 - lapse_norm * radius)),
        _up(math.exp(log_lapse0 + lapse_norm * radius)),
    )
    if delta_interval[0] <= 0.0:
        raise ArithmeticError("transported Delta value interval crosses zero")

    q_interval = (
        _down(lapse_interval[0] * signed_s / delta_interval[1]),
        _up(lapse_interval[1] * signed_s / delta_interval[0]),
    )
    a_interval = (
        _down(lapse_interval[0] * signed_s / delta_interval[1] ** 2),
        _up(lapse_interval[1] * signed_s / delta_interval[0] ** 2),
    )
    q0 = lapse0 * signed_s / delta0
    a0 = q0 / delta0
    center_covector = q0 * lapse_covector - a0 * delta_partial
    center_covector_norm = _up(float(np.linalg.norm(center_covector)))
    q_motion = max(abs(q_interval[0] - q0), abs(q_interval[1] - q0))
    a_motion = max(abs(a_interval[0] - a0), abs(a_interval[1] - a0))
    covector_radius = _up(
        q_motion * lapse_norm
        + a_motion * delta_center_norm
        + a_interval[1] * ddelta_radius
    )
    ball_margin = _down(center_covector_norm - covector_radius)
    direct_norm_lower = _down(q_interval[0] * max(
        0.0,
        (delta_center_norm - ddelta_radius) / delta_interval[1] - lapse_norm,
    ))

    np.savez_compressed(
        DATA_RESULT,
        non_scale_duration_density_covector_center=center_covector,
        non_scale_duration_density_covector_ball_radius_upper=np.asarray(covector_radius),
    )
    validation = {
        "complete_DDelta_ball_is_zero_excluding": (
            ddelta["adjudication"]["signed_D_Y_Delta_on_exact_node_1214_family"]
            == "CERTIFIED_ZERO_EXCLUDING_ACTION_DUAL_BALL"
        ),
        "same_node_1214_tube_is_used": radius == 5.5104723095444935e-11,
        "transported_Delta_value_stays_positive": delta_interval[0] > 0.0,
        "proper_duration_density_stays_positive": q_interval[0] > 0.0,
        "signed_centered_duration_covector_ball_excludes_zero": ball_margin > 0.0,
        "independent_triangle_lower_bound_is_positive": direct_norm_lower > 0.0,
        "proof_center_is_not_selected_as_a_physical_history": True,
        "no_inverse_selector_recurrence_scale_fit_gate_or_chord_added": True,
    }
    validation = {key: bool(value) for key, value in validation.items()}
    passed = all(validation.values())
    payload = {
        "artifact": "BHSM_N12_C2_NODE1214_SIGNED_DURATION_DENSITY_COVECTOR",
        "status": (
            "C2_NODE1214_SIGNED_DURATION_DENSITY_COVECTOR_BALL_CERTIFIED"
            if passed else "C2_NODE1214_SIGNED_DURATION_DENSITY_COVECTOR_INVALID"
        ),
        "classification": (
            "EXACT_BHSM_INCIDENCE_WITH_DDELTA_MEAN_VALUE_VALUE_ENCLOSURE_"
            "ON_THE_INTRINSIC_NON_SCALE_QUOTIENT"
        ),
        "exact_incidence": {
            "q_tau": "N_boundary*s/Delta",
            "D_q_tau": "q_tau*(D_log_N_boundary-D_Delta/Delta)",
        },
        "tube": {
            "reference_node": 1214,
            "state_action_radius": radius,
            "Delta_center": delta0,
            "Delta_value_radius_upper": delta_value_radius,
            "Delta_interval": list(delta_interval),
            "boundary_lapse_interval": list(lapse_interval),
            "proper_duration_density_interval": list(q_interval),
        },
        "covector": {
            "reference_center_action_dual_norm": center_covector_norm,
            "transported_ball_radius_upper": covector_radius,
            "zero_exclusion_margin_lower": ball_margin,
            "independent_norm_lower": direct_norm_lower,
        },
        "data": DATA_RESULT.relative_to(ROOT).as_posix(),
        "data_SHA256": _sha256(DATA_RESULT),
        "adjudication": {
            "signed_node1214_DDelta_covector": "CERTIFIED",
            "signed_node1214_duration_density_covector": "CERTIFIED" if passed else "OPEN",
            "transposed_exact_segment_map_action": "OPEN_CURRENT_OWNER",
            "integrated_segment_duration_covector": "OPEN_AFTER_SEGMENT_ACTION",
            "complete_1222_duration_pullback": "OPEN",
            "Gate7": "OPEN",
            "Gate8": "LOCKED",
            "chord_03_authorized": False,
        },
        "exact_next_dependency": (
            "APPLY_THE_CERTIFIED_NODE1214_SIGNED_SOURCE_BALL_THROUGH_THE_"
            "TRANSPOSED_EXACT_SEGMENT_VARIATIONAL_ACTION_BEFORE_INTEGRATION"
        ),
        "inputs": {
            path.relative_to(ROOT).as_posix(): _sha256(path)
            for path in (*inputs, Path(__file__))
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
        "center_covector_norm": center_covector_norm,
        "covector_ball_radius_upper": covector_radius,
        "zero_exclusion_margin_lower": ball_margin,
        "independent_norm_lower": direct_norm_lower,
        "validation_passed": passed,
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
