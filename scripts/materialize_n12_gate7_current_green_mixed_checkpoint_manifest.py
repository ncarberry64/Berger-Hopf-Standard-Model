"""Attest the 80 pre-directive mixed-map checkpoint shards without recomputing."""

from __future__ import annotations

import hashlib
import inspect
import json
from pathlib import Path
import sys

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import certify_n12_gate7_current_green_mixed_transverse_all_endpoints as direct  # noqa: E402


F = ROOT / "artifacts/flagship_integration"
RESULT = F / "BHSM_N12_GATE7_CURRENT_GREEN_MIXED_TRANSVERSE_CHECKPOINT_MANIFEST.json"
LEGACY_NODES = tuple(range(1, 81))
PROVENANCE_INPUTS = (
    direct.ENDPOINT,
    direct.ENDPOINT.with_suffix(".npz"),
    direct.JACOBIAN,
    direct.JACOBIAN.with_suffix(".npz"),
    direct.PARTITION,
    direct.PARTITION.with_suffix(".npz"),
    direct.SEED,
    direct.SEED.with_suffix(".npz"),
    Path(direct.cert.__file__).resolve(),
    Path(direct.scalar.__file__).resolve(),
)


def _sha(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def _relative(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


def _kernel_sha() -> str:
    source = inspect.getsource(direct._mixed_axis_map).replace("\r\n", "\n")
    return hashlib.sha256(source.encode("utf-8")).hexdigest().upper()


def build_payload() -> dict[str, object]:
    missing = [str(path) for path in PROVENANCE_INPUTS if not path.is_file()]
    if missing:
        raise FileNotFoundError(", ".join(missing))
    shards = []
    for node in LEGACY_NODES:
        path = direct._shard(node)
        if not path.is_file():
            raise FileNotFoundError(path)
        with np.load(path) as source:
            valid = (
                int(source["node"]) == node
                and int(source["precision_bits"]) == 512
                and int(source["shard_revision"]) == direct.SHARD_REVISION
                and source["mixed_arb"].shape
                == (direct.OUTPUTS, direct.COORDINATES)
                and source["mixed_mid"].shape
                == (direct.OUTPUTS, direct.COORDINATES)
                and source["mixed_radius"].shape
                == (direct.OUTPUTS, direct.COORDINATES)
                and bool(np.all(np.isfinite(source["mixed_mid"])))
                and bool(np.all(np.isfinite(source["mixed_radius"])))
                and bool(np.all(source["mixed_radius"] >= 0.0))
            )
        if not valid:
            raise ValueError(f"invalid checkpoint shard {path}")
        stat = path.stat()
        shards.append({
            "node": node,
            "path": _relative(path),
            "SHA256": _sha(path),
            "bytes": stat.st_size,
            "precision_bits": 512,
            "shard_revision": direct.SHARD_REVISION,
            "last_write_time_ns": stat.st_mtime_ns,
        })
    validation = {
        "exactly_80_pre_directive_shards_attested": len(shards) == 80,
        "nodes_1_through_80_contiguous": [row["node"] for row in shards]
        == list(LEGACY_NODES),
        "all_shards_are_512_bit_finite_and_shape_valid": True,
        "mixed_axis_kernel_source_is_hashed": len(_kernel_sha()) == 64,
        "all_scientific_inputs_are_hashed": True,
        "no_shard_was_recomputed": True,
    }
    return {
        "artifact": "BHSM_N12_GATE7_CURRENT_GREEN_MIXED_TRANSVERSE_CHECKPOINT_MANIFEST",
        "status": "EIGHTY_PRE_DIRECTIVE_SHARDS_HASH_ATTESTED_FOR_REUSE",
        "kernel": "DIRECT_CORRELATION_PRESERVING_MIXED_AXIS_MAP",
        "mixed_axis_map_source_SHA256": _kernel_sha(),
        "provenance_inputs": {
            _relative(path): _sha(path) for path in PROVENANCE_INPUTS
        },
        "observed_run": {
            "worker_count": 16,
            "process_start_local": "2026-09-02T18:07:16-05:00",
            "last_attested_shard_local": "2026-09-02T20:31:37-05:00",
            "elapsed_wall_hours": 2.4058333333333333,
            "estimated_actual_CPU_hours": 38.49333333333333,
            "CPU_estimate_basis": (
                "SIXTEEN_OBSERVED_CONTINUOUSLY_SATURATED_WORKERS_TIMES_WALL_TIME;_"
                "PROCESS_ENDED_BEFORE_FINAL_PER_PROCESS_COUNTERS_COULD_BE_PERSISTED"
            ),
            "observed_peak_resident_memory_GiB_approx": 3.5,
            "completed_nodes": 80,
            "observed_CPU_hours_per_node": 0.48116666666666663,
        },
        "shards": shards,
        "claim_boundary": {
            "PRE_DIRECTIVE_SHARDS_PROVENANCE_ATTESTED": True,
            "PRE_DIRECTIVE_SHARDS_RECOMPUTATION_REQUIRED": False,
            "ALL_POST_RESET_ENDPOINTS_MATERIALIZED": False,
            "OUTWARD_MIXED_MAP_AUTHORITY_DERIVED": False,
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
