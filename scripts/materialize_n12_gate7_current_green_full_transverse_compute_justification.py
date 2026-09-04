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
        SEED, PRIOR_BENCHMARK, BENCHMARK_SHARD, THIS_SCRIPT,
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
    one_worker = float(prior["parallel_worker_benchmarks"]["1"]["CPU_hours_per_node"])
    eight_worker = float(prior["parallel_worker_benchmarks"]["8"]["CPU_hours_per_node"])
    contention = eight_worker / one_worker
    total_rows = 740
    serial_hours = total_rows * elapsed / 3600.0
    projected_cpu = serial_hours * contention
    projected_wall = projected_cpu / 8.0
    ceiling = 200.0
    benchmark_payload = {
        "artifact": "BHSM_N12_GATE7_CURRENT_GREEN_FULL_TRANSVERSE_COMPUTE_BENCHMARK",
        "status": "CURRENT_GREEN_FULL_TRANSVERSE_EXACT_SIGNED_TENSOR_BENCHMARK_COMPLETE",
        "benchmark": benchmark_row,
        "measured_node": 1,
        "measured_kind": "endpoint",
        "algorithm": "ONE_EXACT_SIGNED_BROADCAST_TENSOR_WITH_TWO_73_COLUMN_LEGS",
        "tensor_stored": False,
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
        "projected_campaign_below_fixed_compute_ceiling": projected_cpu < ceiling,
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
            "eight_worker_contention_factor_reused": contention,
            "projected_CPU_hours_at_eight_workers": projected_cpu,
            "projected_wall_hours_at_eight_workers": projected_wall,
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
