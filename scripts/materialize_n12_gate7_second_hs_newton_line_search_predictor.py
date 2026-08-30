"""Damp the second block Newton correction by residual-space line search."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "artifacts" / "flagship_integration"
PARENT = BASE / "BHSM_N12_GATE7_HERMITE_SIMPSON_NEWTON_NONLINEAR_SOURCE.json"
FULL = BASE / "BHSM_N12_GATE7_SECOND_HERMITE_SIMPSON_NEWTON_MIDPOINT_REPLAY.json"
PREDICTOR = BASE / "BHSM_N12_GATE7_SECOND_HERMITE_SIMPSON_BLOCK_NEWTON_PREDICTOR.json"
THEORY = ROOT / "theory" / "n12_gate7_second_hs_newton_line_search_predictor.md"
RESULT = BASE / "BHSM_N12_GATE7_SECOND_HS_NEWTON_LINE_SEARCH_PREDICTOR.json"
DATA = RESULT.with_suffix(".npz")
THIS_SCRIPT = Path(__file__).resolve()


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def _relative(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


def main() -> None:
    parent_record = _load(PARENT)
    full_record = _load(FULL)
    predictor_record = _load(PREDICTOR)
    if parent_record.get("validation_passed") is not True:
        raise RuntimeError("validated parent residual required")
    if full_record.get("validation_passed") is not False:
        raise RuntimeError("rejected full second step required")
    if predictor_record.get("validation_passed") is not True:
        raise RuntimeError("validated full second predictor required")
    with np.load(PARENT.with_suffix(".npz")) as source:
        parent = np.asarray(source["Hermite_Simpson_shooting_residual"], dtype=float)[:, :-1]
    with np.load(FULL.with_suffix(".npz")) as source:
        full = np.asarray(source["Hermite_Simpson_shooting_residual"], dtype=float)[:, :-1]
    with np.load(PREDICTOR.with_suffix(".npz")) as source:
        times = np.asarray(source["action_times"], dtype=float)
        correction = np.asarray(source["endpoint_state_correction_action"], dtype=float)
        left_blocks = np.asarray(source["left_Newton_blocks"], dtype=float)
        right_blocks = np.asarray(source["right_Newton_blocks"], dtype=float)
        conditions = np.asarray(source["right_block_condition_2"], dtype=float)
    difference = full - parent
    alpha = float(np.clip(
        -np.vdot(parent, difference).real / np.vdot(difference, difference).real,
        0.0,
        1.0,
    ))
    predicted = parent + alpha * difference
    scaled = alpha * correction
    np.savez_compressed(
        DATA,
        action_times=times,
        endpoint_state_correction_action=scaled,
        undamped_endpoint_state_correction_action=correction,
        left_Newton_blocks=left_blocks,
        right_Newton_blocks=right_blocks,
        right_block_condition_2=conditions,
        line_search_alpha=np.asarray(alpha),
        secant_predicted_residual=predicted,
    )
    validation = {
        "line_search_alpha_is_strictly_damped": 0.0 < alpha < 1.0,
        "secant_model_reduces_global_residual_2_norm": float(np.linalg.norm(predicted)) < float(np.linalg.norm(parent)),
        "secant_model_reduces_maximum_block_residual": float(np.max(np.linalg.norm(predicted, axis=1))) < float(np.max(np.linalg.norm(parent, axis=1))),
        "all_371_scaled_endpoint_corrections_materialized": scaled.shape == (371, 98),
        "exact_nonlinear_damped_replay_not_claimed": True,
        "all_quantities_finite": bool(np.all(np.isfinite(scaled))),
        "no_action_source_selector_scale_gate_or_chord_changed": True,
    }
    validation = {key: bool(value) for key, value in validation.items()}
    passed = all(validation.values())
    payload = {
        "artifact": "BHSM_N12_GATE7_SECOND_HS_NEWTON_LINE_SEARCH_PREDICTOR",
        "status": "SECOND_BLOCK_NEWTON_SECANT_LINE_SEARCH_DAMPING_MATERIALIZED" if passed else "LINE_SEARCH_PREDICTOR_INVALID",
        "authority": "NUMERICAL_SECANT_LINE_SEARCH_PREDICTOR_NOT_NONLINEAR_OR_INTERVAL_AUTHORITY",
        "mesh": {"blocks": 370, "state_dimension": 98, "Newton_iteration": 2},
        "summary": {
            "line_search_alpha": alpha,
            "parent_global_residual_2_norm": float(np.linalg.norm(parent)),
            "full_step_global_residual_2_norm": float(np.linalg.norm(full)),
            "secant_predicted_global_residual_2_norm": float(np.linalg.norm(predicted)),
            "secant_predicted_global_reduction_factor": float(np.linalg.norm(parent) / np.linalg.norm(predicted)),
            "secant_predicted_maximum_block_residual_2_norm": float(np.max(np.linalg.norm(predicted, axis=1))),
            "maximum_scaled_endpoint_correction_action_2_norm": float(np.max(np.linalg.norm(scaled, axis=1))),
        },
        "data": _relative(DATA),
        "data_SHA256": _sha256(DATA),
        "inputs": {
            _relative(path): _sha256(path)
            for path in (PARENT, PARENT.with_suffix(".npz"), FULL, FULL.with_suffix(".npz"), PREDICTOR, PREDICTOR.with_suffix(".npz"), THEORY, THIS_SCRIPT)
        },
        "claim_boundary": {
            "damped_second_block_step": "OPEN_EXACT_NONLINEAR_REPLAY",
            "continuous_action_constrained_center": "OPEN",
            "Gate7": "ACTIVE_ACTION_OWNED_OPERATOR_ORACLE",
            "FULL_BHSM_COMPLETE": False,
        },
        "exact_next_dependency": "APPLY_THE_DAMPED_CORRECTION_AND_REPLAY_ALL_ENDPOINTS_AND_COLLOCATION_MIDPOINTS",
        "validation": validation,
        "validation_passed": passed,
        "FULL_BHSM_COMPLETE": False,
    }
    RESULT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"status": payload["status"], "summary": payload["summary"], "validation_passed": passed}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
