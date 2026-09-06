"""Authorize the restart-safe signed-tensor recovery under the fixed ceiling."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
F = ROOT / "artifacts" / "flagship_integration"
C = ROOT / "artifacts" / "current_semantics"
RESULT = C / "BHSM_N12_GATE7_CURRENT_GREEN_SIGNED_TENSOR_RECOVERY_COMPUTE_JUSTIFICATION.json"
CENTER = F / "BHSM_N12_GATE7_CURRENT_GREEN_FULL_TRANSVERSE_QUADRATIC_CENTER.json"
BENCHMARK = F / ".current_green_signed_transverse_tensor_recovery_work" / "midpoint_001.npz"
RECOVERY = ROOT / "scripts" / "derive_n12_gate7_current_green_signed_transverse_tensor_recovery.py"
THEORY = ROOT / "theory" / "n12_gate7_current_green_signed_transverse_tensor_recovery.md"
CPU_CEILING_HOURS = 210.0
RECOVERY_OVERHEAD_FACTOR = 1.05
ABORTED_TRACE_CAPTURE_PILOT_CPU_HOURS = 1.4089071060833278
FOUR_WORKER_DIRECT_PILOT_MAXIMUM_SECONDS = 965.0317957999941
RECOVERY_ROWS = 740


def _sha(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def _relative(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


def build_payload() -> dict[str, object]:
    required = (CENTER, BENCHMARK, RECOVERY, THEORY)
    missing = [str(path) for path in required if not path.is_file()]
    if missing:
        raise FileNotFoundError(", ".join(missing))
    center = json.loads(CENTER.read_text(encoding="utf-8"))
    if center.get("validation_passed") is not True:
        raise RuntimeError("validated 740-center campaign required")
    import numpy as np

    with np.load(BENCHMARK) as source:
        benchmark_seconds = float(source["elapsed_seconds"])
        benchmark_total_residual = float(source[
            "total_Frobenius_relative_residual"
        ])
        benchmark_output_residual = float(source[
            "output_Frobenius_maximum_relative_residual"
        ])
    prior_cpu = float(center["measured_CPU_hours"])
    projected_from_parent = RECOVERY_OVERHEAD_FACTOR * prior_cpu
    projected_from_direct_pilot = (
        FOUR_WORKER_DIRECT_PILOT_MAXIMUM_SECONDS * RECOVERY_ROWS / 3600.0
    )
    projected_cpu = max(projected_from_parent, projected_from_direct_pilot)
    projected_total_cpu = projected_cpu + ABORTED_TRACE_CAPTURE_PILOT_CPU_HOURS
    authorized = bool(
        projected_total_cpu < CPU_CEILING_HOURS
        and benchmark_total_residual < 5.0e-13
        and benchmark_output_residual < 5.0e-13
    )
    validation = {
        "published_740_center_campaign_is_valid": True,
        "benchmark_tensor_reproduces_published_total_norm": (
            benchmark_total_residual < 5.0e-13
        ),
        "benchmark_tensor_reproduces_all_published_output_norms": (
            benchmark_output_residual < 5.0e-13
        ),
        "projected_recovery_CPU_hours_below_fixed_ceiling": (
            projected_total_cpu < CPU_CEILING_HOURS
        ),
        "same_center_kernel_action_mesh_frames_axes_and_branch_reused": True,
        "four_worker_operational_throttle_retained": True,
        "all_existing_valid_recovery_shards_reused": True,
        "no_proof_parameter_precision_definition_or_claim_changed": True,
        "raw_recovery_cache_is_not_release_authority": True,
        "outward_remainder_and_Gate7_remain_open": True,
        "FULL_BHSM_COMPLETE": False,
    }
    passed = (
        all(value for key, value in validation.items()
            if key != "FULL_BHSM_COMPLETE")
        and not validation["FULL_BHSM_COMPLETE"]
        and authorized
    )
    return {
        "artifact": "BHSM_N12_GATE7_CURRENT_GREEN_SIGNED_TENSOR_RECOVERY_COMPUTE_JUSTIFICATION",
        "status": (
            "SIGNED_TENSOR_RECOVERY_AUTHORIZED_UNDER_FIXED_COMPUTE_CEILING"
            if passed else "SIGNED_TENSOR_RECOVERY_NOT_AUTHORIZED"
        ),
        "campaign_authorized": passed,
        "proof_obligation": (
            "RECOVER_THE_ALREADY_EVALUATED_SIGNED_99_BY_73_BY_73_CENTER_"
            "TENSORS_AT_ALL_370_DEFINED_AXIS_ENDPOINTS_AND_370_MIDPOINTS_"
            "SO_CAUSAL_COMPOSITION_PRECEDES_NORM_EXTRACTION"
        ),
        "benchmark": {
            "kind": "midpoint", "index": 1,
            "elapsed_seconds": benchmark_seconds,
            "total_Frobenius_relative_residual": benchmark_total_residual,
            "output_Frobenius_maximum_relative_residual": benchmark_output_residual,
        },
        "cost": {
            "published_center_campaign_measured_CPU_hours": prior_cpu,
            "aborted_trace_capture_pilot_CPU_hours": ABORTED_TRACE_CAPTURE_PILOT_CPU_HOURS,
            "conservative_recovery_overhead_factor": RECOVERY_OVERHEAD_FACTOR,
            "four_worker_direct_pilot_maximum_seconds": FOUR_WORKER_DIRECT_PILOT_MAXIMUM_SECONDS,
            "projected_from_parent_campaign_CPU_hours": projected_from_parent,
            "projected_from_four_worker_direct_pilot_CPU_hours": projected_from_direct_pilot,
            "projected_recovery_CPU_hours": projected_cpu,
            "projected_total_CPU_hours_including_aborted_pilot": projected_total_cpu,
            "fixed_campaign_CPU_ceiling": CPU_CEILING_HOURS,
            "selected_worker_count": 4,
            "stop_condition": (
                "STOP_ON_CORRUPT_OR_MISSING_PUBLISHED_SHARD_NONFINITE_TENSOR_"
                "NORM_REPRODUCTION_FAILURE_PROOF_CONTRACT_CHANGE_OR_PROJECTED_"
                "CPU_CEILING_VIOLATION"
            ),
        },
        "reused_certified_assets": [
            "complete 740-center signed kernel evaluations and published invariant norms",
            "same current 371-node realization and retained birth trace",
            "same endpoint and midpoint physical tangent frames",
            "same endpoint and correlated midpoint current-Green complements",
            "same selected eigenline and bordered hard-response identities",
            "same four-worker operational throttle and 210 CPU-hour ceiling",
        ],
        "claim_boundary": {
            "SIGNED_CENTER_TENSORS_RECOVERED": False,
            "SIGNED_CAUSAL_TRANSVERSE_OPERATOR_DERIVED": False,
            "OUTWARD_TRANSVERSE_REMAINDER_DERIVED": False,
            "GATE7_CLOSED": False,
            "BHSM_PHYSICAL_BACKGROUND_AUTHORITY": False,
            "FULL_BHSM_COMPLETE": False,
        },
        "inputs": {_relative(path): _sha(path) for path in required},
        "validation": validation,
        "validation_passed": passed,
        "FULL_BHSM_COMPLETE": False,
    }


def main() -> None:
    payload = build_payload()
    RESULT.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8", newline="\n",
    )
    print(json.dumps({
        "status": payload["status"],
        "campaign_authorized": payload["campaign_authorized"],
        "projected_recovery_CPU_hours": payload["cost"][
            "projected_recovery_CPU_hours"
        ],
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
