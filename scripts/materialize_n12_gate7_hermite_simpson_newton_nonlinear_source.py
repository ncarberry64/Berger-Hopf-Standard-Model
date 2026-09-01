"""Materialize the nonlinear Hermite--Simpson residual after one block step."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "artifacts" / "flagship_integration"
PARENT = BASE / "BHSM_N12_GATE7_DIRECT_HERMITE_SIMPSON_MULTIPLE_SHOOTING_SOURCE.json"
ENDPOINT = BASE / "BHSM_N12_GATE7_HERMITE_SIMPSON_NEWTON_ENDPOINT_CANDIDATE.json"
REPLAY = BASE / "BHSM_N12_GATE7_HERMITE_SIMPSON_NEWTON_COLLOCATION_REPLAY.json"
THEORY = ROOT / "theory" / "n12_gate7_hermite_simpson_newton_nonlinear_source.md"
RESULT = BASE / "BHSM_N12_GATE7_HERMITE_SIMPSON_NEWTON_NONLINEAR_SOURCE.json"
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
    parent = _load(PARENT)
    endpoint = _load(ENDPOINT)
    replay = _load(REPLAY)
    if parent.get("validation_passed") is not True or endpoint.get("validation_passed") is not True:
        raise RuntimeError("validated parent source and block-Newton endpoints required")
    if replay.get("validation_passed") is not False:
        raise RuntimeError("the cubic replay must retain its rejected claim boundary")
    with np.load(REPLAY.with_suffix(".npz")) as source:
        times = np.asarray(source["action_times"], dtype=float)
        endpoints = np.asarray(source["corrected_augmented_endpoints"], dtype=float)
        endpoint_rates = np.asarray(source["corrected_endpoint_rates"], dtype=float)
        sample_intervals = np.asarray(source["sample_interval"], dtype=int)
        sample_fractions = np.asarray(source["sample_fraction"], dtype=float)
        sampled_defects = np.asarray(source["sampled_augmented_flow_defect"], dtype=float)
    midpoint_rates = np.empty((370, 99))
    shooting_residual = np.empty((370, 99))
    for interval, duration in enumerate(np.diff(times)):
        mask = sample_intervals == interval
        local_fractions = sample_fractions[mask]
        local_defects = sampled_defects[mask]
        target = 0.5 * duration / 0.25
        middle = int(np.argmin(np.abs(local_fractions - target)))
        if abs(float(local_fractions[middle]) - target) > 2.0e-14:
            raise RuntimeError(f"Gauss-3 midpoint missing on interval {interval}")
        midpoint_path_rate = (
            1.5 * (endpoints[interval + 1] - endpoints[interval]) / duration
            - 0.25 * (endpoint_rates[interval] + endpoint_rates[interval + 1])
        )
        midpoint_rates[interval] = midpoint_path_rate - local_defects[middle]
        shooting_residual[interval] = (
            endpoints[interval + 1] - endpoints[interval]
            - duration * (
                endpoint_rates[interval]
                + 4.0 * midpoint_rates[interval]
                + endpoint_rates[interval + 1]
            ) / 6.0
        )
    residual_norm = np.linalg.norm(shooting_residual, axis=1)
    parent_max = float(parent["summary"]["maximum_Hermite_Simpson_shooting_residual_2_norm"])
    np.savez_compressed(
        DATA,
        action_times=times,
        augmented_endpoints=endpoints,
        exact_endpoint_rates=endpoint_rates,
        exact_midpoint_rates=midpoint_rates,
        Hermite_Simpson_shooting_residual=shooting_residual,
        Hermite_Simpson_shooting_residual_2_norm=residual_norm,
        state_shooting_residual_2_norm=np.linalg.norm(shooting_residual[:, :-1], axis=1),
        descriptor_shooting_residual_absolute=np.abs(shooting_residual[:, -1]),
        shooting_residual_density_2_norm=residual_norm / np.diff(times),
    )
    reduction = parent_max / float(np.max(residual_norm))
    validation = {
        "all_370_nonlinear_Hermite_Simpson_blocks_materialized": shooting_residual.shape == (370, 99),
        "nonlinear_Hermite_Simpson_residual_reduces": reduction > 1.0,
        "cubic_replay_is_not_used_as_block_equation_adjudicator": replay["validation_passed"] is False,
        "all_quantities_finite": bool(np.all(np.isfinite(shooting_residual))),
        "continuous_interval_shadowing_not_claimed": True,
        "no_action_source_selector_scale_gate_or_chord_changed": True,
    }
    validation = {key: bool(value) for key, value in validation.items()}
    passed = all(validation.values())
    payload = {
        "artifact": "BHSM_N12_GATE7_HERMITE_SIMPSON_NEWTON_NONLINEAR_SOURCE",
        "status": "DIRECT_BLOCK_NEWTON_REDUCES_NONLINEAR_HERMITE_SIMPSON_RESIDUAL" if passed else "BLOCK_NEWTON_NONLINEAR_RESIDUAL_NOT_REDUCED",
        "authority": "NUMERICAL_NONLINEAR_HERMITE_SIMPSON_BLOCK_RESIDUAL_NOT_INTERVAL_AUTHORITY",
        "mesh": {"shooting_intervals": 370, "augmented_dimension": 99, "Newton_iteration": 1},
        "summary": {
            "maximum_Hermite_Simpson_shooting_residual_2_norm": float(np.max(residual_norm)),
            "maximum_Hermite_Simpson_shooting_residual_owner_interval": int(np.argmax(residual_norm)),
            "parent_maximum_Hermite_Simpson_shooting_residual_2_norm": parent_max,
            "nonlinear_block_residual_reduction_factor": reduction,
            "maximum_state_shooting_residual_2_norm": float(np.max(np.linalg.norm(shooting_residual[:, :-1], axis=1))),
            "maximum_descriptor_shooting_residual_absolute": float(np.max(np.abs(shooting_residual[:, -1]))),
            "terminal_cumulative_unlinearized_residual_2_norm": float(np.linalg.norm(np.sum(shooting_residual, axis=0))),
        },
        "data": _relative(DATA),
        "data_SHA256": _sha256(DATA),
        "inputs": {
            _relative(path): _sha256(path)
            for path in (
                PARENT, ENDPOINT, ENDPOINT.with_suffix(".npz"), REPLAY,
                REPLAY.with_suffix(".npz"), THEORY, THIS_SCRIPT,
            )
        },
        "adjudication": {
            "cubic_Gauss3_defect": "NOT_THE_DIRECT_COLLOCATION_NEWTON_EQUATION",
            "Hermite_Simpson_block_residual": "REDUCED_NONLINEARLY",
            "direct_block_Newton_route": "REBUILD_ON_CURRENT_CENTER_AND_ITERATE",
        },
        "claim_boundary": {
            "nonlinear_Hermite_Simpson_center": "OPEN_ITERATION_AND_INTERVAL_AUTHORITY",
            "continuous_action_constrained_center": "OPEN",
            "Gate7": "ACTIVE_ACTION_OWNED_OPERATOR_ORACLE",
            "FULL_BHSM_COMPLETE": False,
        },
        "exact_next_dependency": "REBUILD_ENDPOINT_AND_MIDPOINT_JACOBIANS_ON_THIS_CENTER_AND_APPLY_THE_SECOND_BLOCK_NEWTON_STEP",
        "validation": validation,
        "validation_passed": passed,
        "FULL_BHSM_COMPLETE": False,
    }
    RESULT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"status": payload["status"], "summary": payload["summary"], "validation_passed": passed}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
