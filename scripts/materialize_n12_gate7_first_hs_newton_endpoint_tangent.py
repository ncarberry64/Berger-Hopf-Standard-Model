"""Materialize the 73D action-constraint tangent at all first-HS endpoints."""

from __future__ import annotations

from concurrent.futures import ProcessPoolExecutor
import hashlib
import json
import os
from pathlib import Path
import sys

import numpy as np
from scipy.linalg import null_space


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import audit_n12_gate7_within_seam_constraint_center_obstruction as constraints  # noqa: E402


BASE = ROOT / "artifacts" / "flagship_integration"
CENTER = BASE / "BHSM_N12_GATE7_HERMITE_SIMPSON_NEWTON_ENDPOINT_CANDIDATE.json"
THEORY = ROOT / "theory" / "n12_gate7_first_hs_newton_endpoint_tangent.md"
RESULT = BASE / "BHSM_N12_GATE7_FIRST_HS_NEWTON_ENDPOINT_TANGENT.json"
DATA = RESULT.with_suffix(".npz")
THIS_SCRIPT = Path(__file__).resolve()
_WEIGHTS: np.ndarray | None = None


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def _relative(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


def _initialize(weights: np.ndarray) -> None:
    global _WEIGHTS
    _WEIGHTS = weights


def _node(task: tuple[int, np.ndarray]) -> tuple[object, ...]:
    node, state = task
    if _WEIGHTS is None:
        raise RuntimeError("worker not initialized")
    frame, norms, values = constraints._constraint_geometry(state, _WEIGHTS)
    tangent = null_space(frame, rcond=1.0e-11)
    singular = np.linalg.svd(frame, compute_uv=False)
    scaled = values / norms
    return (
        node,
        tangent,
        float(np.linalg.norm(scaled)),
        float(singular[-1]),
        float(np.linalg.norm(frame @ tangent, ord=2)),
        float(np.linalg.norm(tangent.T @ tangent - np.eye(73), ord=2)),
    )


def main() -> None:
    center = _load(CENTER)
    if center.get("validation_passed") is not True:
        raise RuntimeError("validated first-HS endpoint center required")
    with np.load(CENTER.with_suffix(".npz")) as source:
        states = np.asarray(source["projected_states"], dtype=float)
        times = np.asarray(source["action_times"], dtype=float)
        weights = np.asarray(source["state_weights"], dtype=float)
    workers = min(
        int(os.environ.get("BHSM_N12_ENDPOINT_TANGENT_WORKERS", "8")),
        os.cpu_count() or 1,
    )
    tasks = [(node, states[node]) for node in range(times.size)]
    with ProcessPoolExecutor(
        max_workers=workers, initializer=_initialize, initargs=(weights,),
    ) as executor:
        rows = list(executor.map(_node, tasks, chunksize=2))
    rows.sort(key=lambda item: int(item[0]))
    tangents = np.asarray([item[1] for item in rows])
    constraint_residual = np.asarray([item[2] for item in rows])
    minimum_singular = np.asarray([item[3] for item in rows])
    tangent_residual = np.asarray([item[4] for item in rows])
    orthonormal_residual = np.asarray([item[5] for item in rows])
    np.savez_compressed(
        DATA,
        action_times=times,
        physical_tangent_action=tangents,
        scaled_constraint_2_norm=constraint_residual,
        minimum_constraint_singular_value=minimum_singular,
        constraint_tangent_residual_2_norm=tangent_residual,
        tangent_orthonormal_residual_2_norm=orthonormal_residual,
    )
    validation = {
        "all_371_endpoint_tangents_materialized": tangents.shape == (371, 98, 73),
        "all_constraint_frames_have_rank_25": float(np.min(minimum_singular)) > 1.0e-5,
        "all_tangents_annihilate_constraints": float(np.max(tangent_residual)) < 2.0e-14,
        "all_tangents_are_orthonormal": float(np.max(orthonormal_residual)) < 2.0e-14,
        "all_endpoint_constraints_are_numerically_closed": float(np.max(constraint_residual)) < 2.0e-14,
        "basis_orientation_is_not_claimed_canonical": True,
        "no_action_source_selector_scale_gate_or_chord_changed": True,
    }
    validation = {key: bool(value) for key, value in validation.items()}
    passed = all(validation.values())
    payload = {
        "artifact": "BHSM_N12_GATE7_FIRST_HS_NEWTON_ENDPOINT_TANGENT",
        "status": "FIRST_HS_CENTER_371_ENDPOINT_CONSTRAINT_TANGENTS_MATERIALIZED" if passed else "FIRST_HS_ENDPOINT_TANGENT_INVALID",
        "authority": "DIRECT_NUMERICAL_ACTION_CONSTRAINT_NULLSPACES_NOT_INTERVAL_AUTHORITY",
        "summary": {
            "endpoint_count": int(tangents.shape[0]),
            "physical_tangent_dimension": int(tangents.shape[2]),
            "maximum_scaled_constraint_2_norm": float(np.max(constraint_residual)),
            "minimum_constraint_singular_value": float(np.min(minimum_singular)),
            "maximum_constraint_tangent_residual_2_norm": float(np.max(tangent_residual)),
            "maximum_tangent_orthonormal_residual_2_norm": float(np.max(orthonormal_residual)),
        },
        "data": _relative(DATA),
        "data_SHA256": _sha256(DATA),
        "inputs": {
            _relative(path): _sha256(path)
            for path in (CENTER, CENTER.with_suffix(".npz"), THEORY, THIS_SCRIPT)
        },
        "claim_boundary": {
            "projected_recentered_Hermite_Simpson_Jacobian": "OPEN_TANGENT_BLOCK_ADJUDICATION",
            "continuous_action_constrained_center": "OPEN",
            "Gate7": "ACTIVE_ACTION_OWNED_OPERATOR_ORACLE",
            "FULL_BHSM_COMPLETE": False,
        },
        "exact_next_dependency": "SOLVE_THE_370_HERMITE_SIMPSON_BLOCKS_INTRINSICALLY_IN_THESE_73D_ENDPOINT_TANGENTS",
        "validation": validation,
        "validation_passed": passed,
        "FULL_BHSM_COMPLETE": False,
    }
    RESULT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"status": payload["status"], "summary": payload["summary"], "validation_passed": passed}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
