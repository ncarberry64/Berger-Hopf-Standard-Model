"""Build a local trust-region fraction from the exact damped residual sample."""

from __future__ import annotations
import hashlib
import json
from pathlib import Path
import numpy as np
ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "artifacts" / "flagship_integration"
PARENT = BASE / "BHSM_N12_GATE7_HERMITE_SIMPSON_NEWTON_NONLINEAR_SOURCE.json"
SAMPLE = BASE / "BHSM_N12_GATE7_DAMPED_SECOND_HS_NEWTON_MIDPOINT_REPLAY.json"
FULL = BASE / "BHSM_N12_GATE7_SECOND_HERMITE_SIMPSON_BLOCK_NEWTON_PREDICTOR.json"
LINE = BASE / "BHSM_N12_GATE7_SECOND_HS_NEWTON_LINE_SEARCH_PREDICTOR.json"
THEORY = ROOT / "theory" / "n12_gate7_second_hs_newton_local_trust_predictor.md"
RESULT = BASE / "BHSM_N12_GATE7_SECOND_HS_NEWTON_LOCAL_TRUST_PREDICTOR.json"
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
    if _load(PARENT).get("validation_passed") is not True or _load(SAMPLE).get("validation_passed") is not False:
        raise RuntimeError("validated parent and rejected exact damped sample required")
    with np.load(PARENT.with_suffix(".npz")) as z:
        parent = np.asarray(z["Hermite_Simpson_shooting_residual"], dtype=float)[:, :-1]
    with np.load(SAMPLE.with_suffix(".npz")) as z:
        sampled = np.asarray(z["Hermite_Simpson_shooting_residual"], dtype=float)[:, :-1]
    with np.load(FULL.with_suffix(".npz")) as z:
        times = np.asarray(z["action_times"], dtype=float)
        full_correction = np.asarray(z["endpoint_state_correction_action"], dtype=float)
    sampled_alpha = float(_load(LINE)["summary"]["line_search_alpha"])
    derivative = (sampled - parent) / sampled_alpha
    alpha = float(np.clip(-np.vdot(parent, derivative).real / np.vdot(derivative, derivative).real, 0.0, sampled_alpha))
    predicted = parent + alpha * derivative
    correction = alpha * full_correction
    np.savez_compressed(DATA, action_times=times, endpoint_state_correction_action=correction,
                        undamped_endpoint_state_correction_action=full_correction,
                        line_search_alpha=np.asarray(alpha), local_secant_derivative=derivative,
                        local_secant_predicted_residual=predicted)
    validation = {
        "local_trust_alpha_is_inside_sampled_radius": 0.0 < alpha < sampled_alpha,
        "local_secant_direction_is_descent": float(np.vdot(parent, derivative).real) < 0.0,
        "local_secant_predicts_global_reduction": float(np.linalg.norm(predicted)) < float(np.linalg.norm(parent)),
        "all_371_scaled_corrections_materialized": correction.shape == (371, 98),
        "exact_trust_step_replay_not_claimed": True,
        "all_quantities_finite": bool(np.all(np.isfinite(correction))),
    }
    validation = {k: bool(v) for k, v in validation.items()}
    passed = all(validation.values())
    payload = {
        "artifact": "BHSM_N12_GATE7_SECOND_HS_NEWTON_LOCAL_TRUST_PREDICTOR",
        "status": "LOCAL_EXACT_SECANT_TRUST_FRACTION_MATERIALIZED" if passed else "LOCAL_TRUST_PREDICTOR_INVALID",
        "authority": "NUMERICAL_LOCAL_SECANT_TRUST_PREDICTOR_NOT_NONLINEAR_OR_INTERVAL_AUTHORITY",
        "summary": {"sampled_alpha": sampled_alpha, "local_trust_alpha": alpha,
                    "directional_inner_product": float(np.vdot(parent, derivative).real),
                    "predicted_global_residual_2_norm": float(np.linalg.norm(predicted)),
                    "predicted_maximum_block_residual_2_norm": float(np.max(np.linalg.norm(predicted, axis=1))),
                    "maximum_scaled_endpoint_correction_action_2_norm": float(np.max(np.linalg.norm(correction, axis=1)))},
        "data": _relative(DATA), "data_SHA256": _sha256(DATA),
        "inputs": {_relative(p): _sha256(p) for p in (PARENT, PARENT.with_suffix(".npz"), SAMPLE, SAMPLE.with_suffix(".npz"), FULL, FULL.with_suffix(".npz"), LINE, THEORY, THIS_SCRIPT)},
        "claim_boundary": {"local_trust_step": "OPEN_EXACT_REPLAY", "continuous_action_constrained_center": "OPEN", "Gate7": "ACTIVE_ACTION_OWNED_OPERATOR_ORACLE", "FULL_BHSM_COMPLETE": False},
        "exact_next_dependency": "APPLY_AND_EXACTLY_REPLAY_THE_LOCAL_TRUST_FRACTION",
        "validation": validation, "validation_passed": passed, "FULL_BHSM_COMPLETE": False,
    }
    RESULT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"status": payload["status"], "summary": payload["summary"], "validation_passed": passed}, indent=2, sort_keys=True))


if __name__ == "__main__": main()
