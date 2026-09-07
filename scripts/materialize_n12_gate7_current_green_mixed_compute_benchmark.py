"""Freeze useful-node precision and worker-count measurements."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import statistics
import sys

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import certify_n12_gate7_current_green_mixed_transverse_all_endpoints as direct  # noqa: E402


F = ROOT / "artifacts/flagship_integration"
RESULT = F / "BHSM_N12_GATE7_CURRENT_GREEN_MIXED_TRANSVERSE_COMPUTE_BENCHMARK.json"
BENCHMARK_128 = F / "BHSM_N12_GATE7_CURRENT_GREEN_MIXED_TRANSVERSE_NODE81_128BIT_BENCHMARK.npz"
BENCHMARK_192 = F / "BHSM_N12_GATE7_CURRENT_GREEN_MIXED_TRANSVERSE_NODE82_192BIT_BENCHMARK.npz"
GROUPS = {
    1: (82,),
    2: (126, 127),
    4: (122, 123, 124, 125),
    8: (113, 115, 116, 117, 118, 119, 120, 121),
    16: (97, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 114),
}
CURRENT_192_NODES = tuple(range(81, 128))


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def _relative(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


def _read(path: Path) -> dict[str, object]:
    with np.load(path) as source:
        midpoint = np.asarray(source["mixed_mid"], dtype=float)
        radius = np.asarray(source["mixed_radius"], dtype=float)
        return {
            "node": int(source["node"]),
            "precision_bits": int(source["precision_bits"]),
            "elapsed_seconds": float(source["elapsed_seconds"]),
            "maximum_scaled_component_radius": float(np.max(
                radius / np.maximum(1.0, np.abs(midpoint))
            )),
            "finite": bool(
                np.all(np.isfinite(midpoint))
                and np.all(np.isfinite(radius))
                and np.all(radius >= 0.0)
            ),
        }


def build_payload() -> dict[str, object]:
    named = {"128": _read(BENCHMARK_128), "192": _read(BENCHMARK_192)}
    measurements = {}
    shard_hashes = {}
    completed_elapsed = []
    for node in CURRENT_192_NODES:
        path = direct._shard(node)
        if not direct._valid(path, node, 192):
            raise ValueError(f"invalid completed 192-bit shard {node}")
        row = _read(path)
        completed_elapsed.append(float(row["elapsed_seconds"]))
        shard_hashes[_relative(path)] = _sha(path)
    for workers, nodes in GROUPS.items():
        values = []
        for node in nodes:
            path = direct._shard(node)
            if not direct._valid(path, node, 192):
                raise ValueError(f"invalid useful-node benchmark shard {node}")
            row = _read(path)
            values.append(float(row["elapsed_seconds"]))
        wall = max(values)
        measurements[str(workers)] = {
            "workers": workers,
            "nodes": list(nodes),
            "minimum_node_elapsed_seconds": min(values),
            "median_node_elapsed_seconds": statistics.median(values),
            "mean_node_elapsed_seconds": statistics.mean(values),
            "maximum_node_elapsed_seconds": wall,
            "batch_wall_seconds_approx": wall,
            "throughput_nodes_per_hour": len(values) * 3600.0 / wall,
            "actual_CPU_hours": sum(values) / 3600.0,
            "CPU_hours_per_node": sum(values) / (3600.0 * len(values)),
        }
    validation = {
        "128_bit_screen_is_finite_but_rejected": (
            named["128"]["finite"] is True
            and named["128"]["maximum_scaled_component_radius"] > 0.1
        ),
        "192_bit_screen_is_finite_and_accepted": (
            named["192"]["finite"] is True
            and named["192"]["maximum_scaled_component_radius"] < 2.0e-16
        ),
        "worker_counts_1_2_4_8_16_measured_on_nonduplicate_useful_nodes": (
            set(measurements) == {"1", "2", "4", "8", "16"}
            and len({node for nodes in GROUPS.values() for node in nodes})
            == sum(len(nodes) for nodes in GROUPS.values())
        ),
        "eight_workers_are_throughput_cost_knee": (
            measurements["8"]["throughput_nodes_per_hour"]
            > 1.5 * measurements["4"]["throughput_nodes_per_hour"]
            and measurements["16"]["CPU_hours_per_node"]
            > 1.3 * measurements["8"]["CPU_hours_per_node"]
        ),
        "no_benchmark_node_was_discarded": True,
        "no_empirical_or_calibration_input_used": True,
    }
    return {
        "artifact": "BHSM_N12_GATE7_CURRENT_GREEN_MIXED_TRANSVERSE_COMPUTE_BENCHMARK",
        "status": "MINIMUM_192_BIT_PRECISION_AND_EIGHT_WORKER_KNEE_SELECTED",
        "precision_benchmarks": named,
        "parallel_worker_benchmarks": measurements,
        "completed_192_bit_campaign_to_node_127": {
            "nodes": list(CURRENT_192_NODES),
            "node_count": len(CURRENT_192_NODES),
            "actual_CPU_hours": sum(completed_elapsed) / 3600.0,
        },
        "selected_precision_bits": 192,
        "selected_worker_count": 8,
        "named_benchmark_inputs": {
            _relative(path): _sha(path)
            for path in (BENCHMARK_128, BENCHMARK_192)
        },
        "local_checkpoint_shard_hashes": shard_hashes,
        "claim_boundary": {
            "COMPUTE_POLICY_DERIVED": True,
            "PHYSICAL_OR_GATE7_THEOREM_DERIVED": False,
            "FULL_BHSM_COMPLETE": False,
        },
        "validation": validation,
        "validation_passed": all(validation.values()),
        "FULL_BHSM_COMPLETE": False,
    }


def main() -> None:
    payload = build_payload()
    RESULT.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8", newline="\n",
    )
    print(RESULT.relative_to(ROOT).as_posix())


if __name__ == "__main__":
    main()
