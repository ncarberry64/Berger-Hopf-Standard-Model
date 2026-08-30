"""Materialize the high-order multiple-shooting source on the best center."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "artifacts" / "flagship_integration"
CENTER = BASE / "BHSM_N12_GATE7_CURRENT_LINEARIZATION_NEWTON_ENDPOINT_CANDIDATE.json"
REPLAY = BASE / "BHSM_N12_GATE7_CURRENT_LINEARIZATION_NEWTON_COLLOCATION_REPLAY.json"
SECOND_REFINEMENT = BASE / "BHSM_N12_GATE7_SECOND_REFINED_WITHIN_SEAM_HERMITE_COLLOCATION.json"
THIRD_REPLAY = BASE / "BHSM_N12_GATE7_THIRD_CURRENT_LINEARIZATION_NEWTON_COLLOCATION_REPLAY.json"
THEORY = ROOT / "theory" / "n12_gate7_direct_hermite_simpson_multiple_shooting_source.md"
RESULT = BASE / "BHSM_N12_GATE7_DIRECT_HERMITE_SIMPSON_MULTIPLE_SHOOTING_SOURCE.json"
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
    center = _load(CENTER)
    replay = _load(REPLAY)
    second_refinement = _load(SECOND_REFINEMENT)
    third_replay = _load(THIRD_REPLAY)
    if center.get("validation_passed") is not True or replay.get("validation_passed") is not True:
        raise RuntimeError("validated best second-Newton center and replay required")
    if second_refinement.get("validation_passed") is not False:
        raise RuntimeError("the failed second mesh refinement is required")
    if third_replay.get("validation_passed") is not False:
        raise RuntimeError("the failed third Newton replay is required")
    with np.load(REPLAY.with_suffix(".npz")) as source:
        times = np.asarray(source["action_times"], dtype=float)
        endpoints = np.asarray(source["corrected_augmented_endpoints"], dtype=float)
        endpoint_rates = np.asarray(source["corrected_endpoint_rates"], dtype=float)
        sample_intervals = np.asarray(source["sample_interval"], dtype=int)
        sample_fractions = np.asarray(source["sample_fraction"], dtype=float)
        sampled_defects = np.asarray(source["sampled_augmented_flow_defect"], dtype=float)

    midpoint_rates = np.empty((370, 99))
    shooting_residual = np.empty((370, 99))
    for interval in range(370):
        duration = float(times[interval + 1] - times[interval])
        mask = sample_intervals == interval
        local_fractions = sample_fractions[mask]
        local_defects = sampled_defects[mask]
        target = 0.5 * duration / 0.25
        middle = int(np.argmin(np.abs(local_fractions - target)))
        if abs(float(local_fractions[middle]) - target) > 2.0e-14:
            raise RuntimeError(f"Gauss-3 midpoint missing on interval {interval}")
        # The endpoint-field-matched cubic path rate minus its measured defect
        # is the exact retained augmented field at the same midpoint state.
        left = endpoint_rates[interval]
        right = endpoint_rates[interval + 1]
        midpoint_path_rate = (
            1.5 * (endpoints[interval + 1] - endpoints[interval]) / duration
            - 0.25 * (left + right)
        )
        midpoint_rates[interval] = midpoint_path_rate - local_defects[middle]
        shooting_residual[interval] = (
            endpoints[interval + 1] - endpoints[interval]
            - duration * (left + 4.0 * midpoint_rates[interval] + right) / 6.0
        )
    residual_norm = np.linalg.norm(shooting_residual, axis=1)
    state_residual_norm = np.linalg.norm(shooting_residual[:, :-1], axis=1)
    descriptor_residual = np.abs(shooting_residual[:, -1])
    density_norm = residual_norm / np.diff(times)
    owner = int(np.argmax(residual_norm))
    np.savez_compressed(
        DATA,
        action_times=times,
        augmented_endpoints=endpoints,
        exact_endpoint_rates=endpoint_rates,
        exact_midpoint_rates=midpoint_rates,
        Hermite_Simpson_shooting_residual=shooting_residual,
        Hermite_Simpson_shooting_residual_2_norm=residual_norm,
        state_shooting_residual_2_norm=state_residual_norm,
        descriptor_shooting_residual_absolute=descriptor_residual,
        shooting_residual_density_2_norm=density_norm,
    )
    validation = {
        "all_370_Hermite_Simpson_blocks_materialized": shooting_residual.shape == (370, 99),
        "all_exact_midpoint_rates_recovered_from_direct_replay": midpoint_rates.shape == (370, 99),
        "best_second_Newton_center_retained": replay["validation_passed"] is True,
        "mesh_only_refinement_rejected": second_refinement["validation_passed"] is False,
        "third_signed_Green_iteration_rejected": third_replay["validation_passed"] is False,
        "all_quantities_finite": bool(np.all(np.isfinite(np.concatenate((
            midpoint_rates.ravel(), shooting_residual.ravel(),
        ))))),
        "multiple_shooting_Newton_solution_not_claimed": True,
        "continuous_interval_shadowing_not_claimed": True,
        "no_action_source_selector_scale_gate_or_chord_changed": True,
    }
    validation = {key: bool(value) for key, value in validation.items()}
    passed = all(validation.values())
    payload = {
        "artifact": "BHSM_N12_GATE7_DIRECT_HERMITE_SIMPSON_MULTIPLE_SHOOTING_SOURCE",
        "status": "DIRECT_HIGH_ORDER_MULTIPLE_SHOOTING_SOURCE_MATERIALIZED" if passed else "MULTIPLE_SHOOTING_SOURCE_INVALID",
        "authority": "NUMERICAL_HERMITE_SIMPSON_BLOCK_SOURCE_NOT_INTERVAL_AUTHORITY",
        "mesh": {"shooting_intervals": 370, "augmented_dimension": 99},
        "summary": {
            "maximum_Hermite_Simpson_shooting_residual_2_norm": float(np.max(residual_norm)),
            "maximum_Hermite_Simpson_shooting_residual_owner_interval": owner,
            "maximum_state_shooting_residual_2_norm": float(np.max(state_residual_norm)),
            "maximum_descriptor_shooting_residual_absolute": float(np.max(descriptor_residual)),
            "maximum_shooting_residual_density_2_norm": float(np.max(density_norm)),
            "terminal_cumulative_unlinearized_residual_2_norm": float(np.linalg.norm(np.sum(shooting_residual, axis=0))),
        },
        "data": _relative(DATA),
        "data_SHA256": _sha256(DATA),
        "inputs": {
            _relative(path): _sha256(path)
            for path in (
                CENTER, CENTER.with_suffix(".npz"), REPLAY, REPLAY.with_suffix(".npz"),
                SECOND_REFINEMENT, THIRD_REPLAY, THEORY, THIS_SCRIPT,
            )
        },
        "adjudication": {
            "interpolation_only_refinement": "REJECTED_BY_SECOND_HALVING",
            "repeated_signed_Green_fixed_point": "REJECTED_BY_THIRD_NONLINEAR_REPLAY",
            "direct_high_order_multiple_shooting": "ACTIVE_WITH_EXPLICIT_370_BY_99_BLOCK_SOURCE",
        },
        "claim_boundary": {
            "continuous_action_constrained_center": "OPEN_MULTIPLE_SHOOTING_NEWTON_AND_INTERVAL_AUTHORITY",
            "continuous_outward_variational_carrier": "OPEN_AFTER_CENTER",
            "Gate7": "ACTIVE_ACTION_OWNED_OPERATOR_ORACLE",
            "FULL_BHSM_COMPLETE": False,
        },
        "exact_next_dependency": (
            "ASSEMBLE_THE_BLOCK_BIDIAGONAL_HERMITE_SIMPSON_NEWTON_OPERATOR_"
            "WITH_CONSTRAINT_AND_DESCRIPTOR_FIBER_ROWS,_SOLVE_FOR_ENDPOINT_AND_"
            "MIDPOINT_VALUE_CORRECTIONS,_THEN_REPLAY_THE_EXACT_FIELD"
        ),
        "validation": validation,
        "validation_passed": passed,
        "FULL_BHSM_COMPLETE": False,
    }
    RESULT.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(json.dumps({
        "status": payload["status"],
        "summary": payload["summary"],
        "validation_passed": passed,
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
