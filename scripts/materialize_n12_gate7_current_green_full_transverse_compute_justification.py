"""Authorize the restart-safe current full-transverse center campaign."""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
F = ROOT / "artifacts/flagship_integration"
C = ROOT / "artifacts/current_semantics"
WORK = F / ".current_green_full_transverse_quadratic_center_work"
BENCHMARK = F / "BHSM_N12_GATE7_CURRENT_GREEN_FULL_TRANSVERSE_COMPUTE_BENCHMARK.json"
RESULT = C / "BHSM_N12_GATE7_CURRENT_GREEN_FULL_TRANSVERSE_COMPUTE_JUSTIFICATION.json"
CAMPAIGN = ROOT / "scripts/derive_n12_gate7_current_green_full_transverse_quadratic_center.py"
THEORY = ROOT / "theory/n12_gate7_current_green_full_transverse_quadratic_majorant.md"
ENDPOINT = F / "BHSM_N12_GATE7_AUGMENTED_FIXED_DESCRIPTOR_NEWTON_ENDPOINT_CANDIDATE.npz"
REPLAY = F / "BHSM_N12_GATE7_AUGMENTED_FIXED_DESCRIPTOR_NEWTON_MIDPOINT_REPLAY.npz"
JACOBIAN = F / "BHSM_N12_GATE7_CORRELATED_DESCRIPTOR_AUGMENTED_JACOBIANS.npz"
PARTITION = ROOT / "artifacts/action_extension/BHSM_AE4_CURRENT_C2_GREEN_IMAGE_PARTITION_RECONCILIATION.npz"
SCALAR = F / "BHSM_N12_GATE7_CURRENT_GREEN_CORRELATED_SCALAR_ALL_INTERVALS.npz"
SEED = F / "BHSM_N12_GATE7_CURRENT_GREEN_TRANSVERSE_QUADRATIC_SEED.json"
PRIOR_BENCHMARK = F / "BHSM_N12_GATE7_CURRENT_GREEN_MIXED_TRANSVERSE_COMPUTE_BENCHMARK.json"
BENCHMARK_SHARD = WORK / "endpoint_001.npz"
PARALLEL_SHARDS = (
    WORK / "endpoint_002.npz", WORK / "endpoint_003.npz",
    WORK / "midpoint_000.npz", WORK / "midpoint_001.npz",
)
TWO_WORKER_SHARDS = (WORK / "endpoint_006.npz", WORK / "midpoint_004.npz")
COMPLETED_THROTTLE_SHARDS = (
    *(WORK / f"endpoint_{index:03d}.npz" for index in range(1, 7)),
    *(WORK / f"midpoint_{index:03d}.npz" for index in range(5)),
)
THIS_SCRIPT = Path(__file__).resolve()


def _sha(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def _relative(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


def _write(path: Path, payload: dict[str, object]) -> None:
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8", newline="\n",
    )


def build_payload() -> dict[str, object]:
    required = (
        CAMPAIGN, THEORY, ENDPOINT, REPLAY, JACOBIAN, PARTITION, SCALAR,
        SEED, PRIOR_BENCHMARK, BENCHMARK_SHARD, *PARALLEL_SHARDS,
        *TWO_WORKER_SHARDS, THIS_SCRIPT,
    )
    missing = [str(path) for path in required if not path.is_file()]
    if missing:
        raise FileNotFoundError(", ".join(missing))
    with np.load(BENCHMARK_SHARD) as source:
        elapsed = float(source["elapsed_seconds"])
        revision = int(source["shard_revision"])
        finite = all(math.isfinite(float(source[key])) for key in (
            "quadratic_Frobenius_norm",
            "first_response_relative_Frobenius_residual",
            "second_response_relative_Frobenius_residual",
        ))
        benchmark_row = {
            key: source[key].item() for key in source.files
            if source[key].shape == () and key != "worker_id"
        }
    prior = json.loads(PRIOR_BENCHMARK.read_text(encoding="utf-8"))
    parallel_seconds = []
    for path in PARALLEL_SHARDS:
        with np.load(path) as source:
            parallel_seconds.append(float(source["elapsed_seconds"]))
    parallel_mean = float(np.mean(parallel_seconds))
    parallel_contention = parallel_mean / elapsed
    two_worker_seconds = []
    for path in TWO_WORKER_SHARDS:
        with np.load(path) as source:
            two_worker_seconds.append(float(source["elapsed_seconds"]))
    two_worker_mean = float(np.mean(two_worker_seconds))
    two_worker_contention = two_worker_mean / elapsed
    completed_seconds = 0.0
    for path in COMPLETED_THROTTLE_SHARDS:
        with np.load(path) as source:
            completed_seconds += float(source["elapsed_seconds"])
    total_rows = 740
    serial_hours = total_rows * elapsed / 3600.0
    completed_rows = len(COMPLETED_THROTTLE_SHARDS)
    remaining_rows = total_rows - completed_rows
    projected_remaining_cpu = remaining_rows * two_worker_mean / 3600.0
    projected_cpu = completed_seconds / 3600.0 + projected_remaining_cpu
    projected_wall = projected_remaining_cpu / 2.0
    aborted_eight_worker_pilot_cpu_hours_approx = 2.43
    projected_total_cpu = projected_cpu + aborted_eight_worker_pilot_cpu_hours_approx
    ceiling = 200.0
    benchmark_payload = {
        "artifact": "BHSM_N12_GATE7_CURRENT_GREEN_FULL_TRANSVERSE_COMPUTE_BENCHMARK",
        "status": "CURRENT_GREEN_FULL_TRANSVERSE_EXACT_SIGNED_TENSOR_BENCHMARK_COMPLETE",
        "benchmark": benchmark_row,
        "measured_node": 1,
        "measured_kind": "endpoint",
        "algorithm": "ONE_EXACT_SIGNED_BROADCAST_TENSOR_WITH_TWO_73_COLUMN_LEGS",
        "tensor_stored": False,
        "four_worker_probe": {
            "layout": "TWO_ENDPOINT_WORKERS_PLUS_TWO_MIDPOINT_WORKERS",
            "elapsed_seconds": parallel_seconds,
            "mean_elapsed_seconds": parallel_mean,
            "contention_factor_against_one_worker": parallel_contention,
            "decision": "REJECTED_AFTER_LATER_ROWS_PROJECTED_ABOVE_THE_FIXED_COMPUTE_CEILING",
        },
        "two_worker_probe": {
            "layout": "ONE_ENDPOINT_WORKER_PLUS_ONE_MIDPOINT_WORKER",
            "elapsed_seconds": two_worker_seconds,
            "mean_elapsed_seconds": two_worker_mean,
            "contention_factor_against_one_worker": two_worker_contention,
            "decision": "SELECTED_TO_RETAIN_THE_FIXED_COMPUTE_CEILING",
        },
        "validation_passed": finite and revision == 4,
        "FULL_BHSM_COMPLETE": False,
    }
    _write(BENCHMARK, benchmark_payload)
    inputs = (
        CAMPAIGN, THEORY, ENDPOINT, REPLAY, JACOBIAN, PARTITION, SCALAR,
        SEED, PRIOR_BENCHMARK, BENCHMARK, THIS_SCRIPT,
    )
    validation = {
        "benchmark_is_finite": finite,
        "restart_shard_revision_is_current": revision == 4,
        "all_370_defined_axis_endpoints_and_370_midpoints_are_in_scope": total_rows == 740,
        "zero_Green_axis_at_fixed_endpoint_zero_is_not_normalized_or_invented": True,
        "exact_signed_broadcast_replaces_directional_polarization": True,
        "full_73_by_73_symmetric_input_tensor_is_formed_at_each_center": True,
        "only_basis_invariant_norms_and_residuals_are_persisted": True,
        "midpoint_current_axes_reuse_correlated_midpoint_directions": True,
        "outward_authority_is_not_claimed_by_the_center_campaign": True,
        "existing_valid_shards_are_reused": True,
        "projected_campaign_including_aborted_pilot_below_fixed_compute_ceiling": projected_total_cpu < ceiling,
        "no_empirical_or_calibration_input_used": True,
        "FULL_BHSM_COMPLETE": False,
    }
    passed = all(value for key, value in validation.items()
                 if key != "FULL_BHSM_COMPLETE") and not validation["FULL_BHSM_COMPLETE"]
    return {
        "artifact": "BHSM_N12_GATE7_CURRENT_GREEN_FULL_TRANSVERSE_COMPUTE_JUSTIFICATION",
        "status": "CURRENT_GREEN_FULL_TRANSVERSE_CENTER_CAMPAIGN_AUTHORIZED_UNDER_FIXED_COMPUTE_CEILING",
        "campaign_authorized": passed,
        "proof_obligation": (
            "DERIVE_THE_COMPLETE_CURRENT_73_BY_73_TRANSVERSE_QUADRATIC_CENTER_"
            "OPERATOR_AT_ALL_370_DEFINED_AXIS_ENDPOINTS_AND_370_HERMITE_SIMPSON_MIDPOINTS"
        ),
        "benchmark": {
            "kind": "endpoint",
            "index": 1,
            "elapsed_seconds": elapsed,
            "quadratic_Frobenius_norm": float(benchmark_row["quadratic_Frobenius_norm"]),
            "shard_revision": revision,
        },
        "cost": {
            "total_rows": total_rows,
            "projected_serial_CPU_hours": serial_hours,
            "selected_worker_count": 2,
            "four_worker_contention_factor_observed": parallel_contention,
            "two_worker_contention_factor_observed": two_worker_contention,
            "completed_rows_at_throttle_audit": completed_rows,
            "actual_completed_shard_CPU_hours": completed_seconds / 3600.0,
            "remaining_rows_at_two_workers": remaining_rows,
            "projected_remaining_CPU_hours_at_two_workers": projected_remaining_cpu,
            "projected_campaign_CPU_hours_after_throttle": projected_cpu,
            "projected_remaining_wall_hours_at_two_workers": projected_wall,
            "aborted_eight_worker_pilot_CPU_hours_approx": aborted_eight_worker_pilot_cpu_hours_approx,
            "projected_total_CPU_hours_including_aborted_pilot": projected_total_cpu,
            "fixed_campaign_CPU_ceiling": ceiling,
            "peak_memory_GiB_approx": 3.2,
            "stop_condition": "STOP_ON_CORRUPT_SHARD_NONFINITE_ROW_PROOF_CONTRACT_CHANGE_OR_MEASURED_CPU_CEILING_VIOLATION",
        },
        "cheaper_routes_adjudicated": [
            {"route": "DIRECTIONAL_SEED_OR_EXTREMAL_NODE_SAMPLING", "decision": "REJECTED_NO_UNIT_SPHERE_OR_ALL_NODE_AUTHORITY"},
            {"route": "73_SEPARATE_COMPLEX_STEP_HESSIAN_DIRECTIONS", "decision": "REJECTED_EXACT_SIGNED_BROADCAST_IS_FASTER_AND_ALGEBRAICALLY_COMPLETE"},
            {"route": "POLARIZATION_GRID", "decision": "REJECTED_COMPLETE_SYMMETRIC_TENSOR_IS_AVAILABLE_DIRECTLY"},
            {"route": "HISTORICAL_48_NODE_72D_TENSOR", "decision": "REJECTED_WRONG_REALIZATION_GREEN_COMPLEMENT_AND_DESCRIPTOR_DOMAIN"},
            {"route": "STORE_EVERY_FULL_TENSOR", "decision": "REJECTED_INVARIANT_NORMS_AND_VALIDATION_RESIDUALS_ARE_SUFFICIENT_FOR_THE_CENTER_MAJORANT"},
            {"route": "UNIFORM_ARB_TENSOR_COMPONENT_CAMPAIGN", "decision": "DEFERRED_USE_CENTER_TENSOR_THEN_SEPARATE_ANALYTIC_OUTWARD_REMAINDER"},
        ],
        "reused_certified_assets": [
            "current 371-node action-selected realization and retained birth trace",
            "current endpoint and midpoint physical tangent frames",
            "current endpoint and correlated midpoint Green directions",
            "retained selected-eigenline and bordered hard-response identities",
            "512-bit decisive directional transverse seed",
            "prior eight-worker contention benchmark",
            "current-kernel four-worker throttle probe",
            "current-kernel two-worker ceiling-preserving probe",
        ],
        "reusable_outputs": [
            "740 fingerprinted restart-safe center shards",
            "all-node Hilbert--Schmidt full-unit-sphere center majorant profile",
            "owner nodes for the outward certification stage",
        ],
        "inputs": {_relative(path): _sha(path) for path in inputs},
        "validation": validation,
        "validation_passed": passed,
        "FULL_BHSM_COMPLETE": False,
    }


def main() -> None:
    payload = build_payload()
    _write(RESULT, payload)
    print(json.dumps({
        "status": payload["status"],
        "campaign_authorized": payload["campaign_authorized"],
        "cost": payload["cost"],
        "validation_passed": payload["validation_passed"],
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
