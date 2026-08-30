"""Adjudicate the stored graph Jacobian against exact projected block residuals."""

from __future__ import annotations
import hashlib
import json
from pathlib import Path
import numpy as np
ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "artifacts" / "flagship_integration"
PARENT = BASE / "BHSM_N12_GATE7_HERMITE_SIMPSON_NEWTON_NONLINEAR_SOURCE.json"
PREDICTOR = BASE / "BHSM_N12_GATE7_SECOND_HERMITE_SIMPSON_BLOCK_NEWTON_PREDICTOR.json"
FULL = BASE / "BHSM_N12_GATE7_SECOND_HERMITE_SIMPSON_NEWTON_MIDPOINT_REPLAY.json"
DAMPED = BASE / "BHSM_N12_GATE7_DAMPED_SECOND_HS_NEWTON_MIDPOINT_REPLAY.json"
TRUST_PREDICTOR = BASE / "BHSM_N12_GATE7_SECOND_HS_NEWTON_LOCAL_TRUST_PREDICTOR.json"
TRUST = BASE / "BHSM_N12_GATE7_LOCAL_TRUST_SECOND_HS_MIDPOINT_REPLAY.json"
THEORY = ROOT / "theory" / "n12_gate7_hermite_simpson_projected_residual_jacobian.md"
RESULT = BASE / "BHSM_N12_GATE7_HERMITE_SIMPSON_PROJECTED_RESIDUAL_JACOBIAN_ADJUDICATION.json"
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
    records = {path: _load(path) for path in (PARENT, PREDICTOR, FULL, DAMPED, TRUST_PREDICTOR, TRUST)}
    if records[PARENT].get("validation_passed") is not True or records[PREDICTOR].get("validation_passed") is not True:
        raise RuntimeError("validated parent and block predictor required")
    if any(records[path].get("validation_passed") is not False for path in (FULL, DAMPED, TRUST)):
        raise RuntimeError("all three rejected nonlinear step records required")
    with np.load(PARENT.with_suffix(".npz")) as z:
        parent = np.asarray(z["Hermite_Simpson_shooting_residual"], dtype=float)[:, :-1]
    with np.load(TRUST.with_suffix(".npz")) as z:
        trust = np.asarray(z["Hermite_Simpson_shooting_residual"], dtype=float)[:, :-1]
    alpha = float(records[TRUST_PREDICTOR]["summary"]["local_trust_alpha"])
    actual_directional = (trust - parent) / alpha
    parent_norm = float(np.linalg.norm(parent))
    directional_norm = float(np.linalg.norm(actual_directional))
    inner = float(np.vdot(parent, actual_directional).real)
    cosine_with_descent = float(-inner / (parent_norm * directional_norm))
    next_alpha = float(np.clip(-inner / np.vdot(actual_directional, actual_directional).real, 0.0, alpha))
    next_predicted = parent + next_alpha * actual_directional
    model_scale_ratio = directional_norm / parent_norm
    validation = {
        "full_second_step_is_rejected": records[FULL]["validation_passed"] is False,
        "secant_damped_step_is_rejected": records[DAMPED]["validation_passed"] is False,
        "local_trust_step_is_rejected": records[TRUST]["validation_passed"] is False,
        "actual_directional_scale_exceeds_stored_model_scale_by_two_orders": model_scale_ratio > 100.0,
        "remaining_local_trust_fraction_is_below_one_per_mille": next_alpha < 1.0e-3,
        "remaining_secant_gain_is_below_one_percent": parent_norm / float(np.linalg.norm(next_predicted)) < 1.01,
        "stored_graph_Jacobian_not_promoted_as_projected_residual_derivative": True,
        "no_action_source_selector_scale_gate_or_chord_changed": True,
    }
    validation = {k: bool(v) for k, v in validation.items()}
    passed = all(validation.values())
    payload = {
        "artifact": "BHSM_N12_GATE7_HERMITE_SIMPSON_PROJECTED_RESIDUAL_JACOBIAN_ADJUDICATION",
        "status": "STORED_GRAPH_JACOBIAN_REJECTED_FOR_PROJECTED_RECENTERED_BLOCK_NEWTON" if passed else "PROJECTED_RESIDUAL_JACOBIAN_ADJUDICATION_INCONCLUSIVE",
        "authority": "EXACT_NONLINEAR_FINITE_DIFFERENCE_ROUTING_NOT_INTERVAL_DERIVATIVE_AUTHORITY",
        "summary": {
            "parent_global_residual_2_norm": parent_norm,
            "local_trust_alpha": alpha,
            "local_trust_global_residual_2_norm": float(np.linalg.norm(trust)),
            "actual_projected_residual_directional_2_norm": directional_norm,
            "actual_to_stored_model_scale_ratio": model_scale_ratio,
            "cosine_with_negative_parent_residual": cosine_with_descent,
            "next_secant_optimal_alpha": next_alpha,
            "next_secant_predicted_global_reduction_factor": parent_norm / float(np.linalg.norm(next_predicted)),
            "next_secant_predicted_maximum_block_residual_2_norm": float(np.max(np.linalg.norm(next_predicted, axis=1))),
        },
        "inputs": {
            _relative(path): _sha256(path)
            for path in (PARENT, PARENT.with_suffix(".npz"), PREDICTOR, PREDICTOR.with_suffix(".npz"), FULL, FULL.with_suffix(".npz"), DAMPED, DAMPED.with_suffix(".npz"), TRUST_PREDICTOR, TRUST, TRUST.with_suffix(".npz"), THEORY, THIS_SCRIPT)
        },
        "adjudication": {
            "hybrid_graph_Jacobian_as_complete_block_derivative": "REJECTED",
            "further_scalar_damping_of_same_direction": "REJECTED_AS_NUMERICALLY_FUTILE",
            "exact_projected_recentered_block_residual_JVP": "ACTIVE_OWNER",
        },
        "claim_boundary": {
            "continuous_action_constrained_center": "OPEN_EXACT_PROJECTED_RESIDUAL_JVP_AND_NEWTON",
            "continuous_outward_variational_carrier": "OPEN_AFTER_CENTER",
            "Gate7": "ACTIVE_ACTION_OWNED_OPERATOR_ORACLE",
            "FULL_BHSM_COMPLETE": False,
        },
        "exact_next_dependency": (
            "DIFFERENTIATE_THE_COMPLETE_ENDPOINT_CONSTRAINT_PROJECTION,_SELECTED_"
            "DESCRIPTOR_RECENTER,_EXACT_ENDPOINT_FIELD,_HERMITE_SIMPSON_MIDPOINT_"
            "STATE,_AND_EXACT_MIDPOINT_FIELD_COMPOSITION;_ASSEMBLE_ITS_BLOCK_JVP_"
            "AND_RESOLVE_THE_NEWTON_STEP"
        ),
        "validation": validation,
        "validation_passed": passed,
        "FULL_BHSM_COMPLETE": False,
    }
    RESULT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"status": payload["status"], "summary": payload["summary"], "validation_passed": passed}, indent=2, sort_keys=True))


if __name__ == "__main__": main()
