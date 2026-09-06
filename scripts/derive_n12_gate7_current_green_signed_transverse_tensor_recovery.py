"""Recover the signed tensors intentionally omitted from the center shards.

The completed center campaign retained invariant norms only.  A later causal
composition showed that taking componentwise absolute values before applying
the frozen Green map is too lossy.  This restart-safe recovery calls the same
unchanged center kernel and retains its already-computed local ``quadratic``
return array.  Every recovered tensor is checked against the
published per-output and total Frobenius norms before it is admitted.

This is center data only.  It neither supplies an outward remainder nor closes
Gate 7 by itself.
"""

from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor, as_completed
import hashlib
import json
import os
from pathlib import Path
import sys
import time

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import derive_n12_gate7_current_green_full_transverse_quadratic_center as center  # noqa: E402


F = ROOT / "artifacts" / "flagship_integration"
WORK = F / ".current_green_signed_transverse_tensor_recovery_work"
PUBLISHED_WORK = F / ".current_green_full_transverse_quadratic_center_work"
ALGORITHM_ID = "CURRENT_GREEN_SIGNED_TRANSVERSE_TENSOR_RECOVERY_V1"
SHARD_REVISION = 1
OUTPUTS = 99
TRANSVERSE = 73


def _sha(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def _fingerprint() -> str:
    digest = hashlib.sha256(ALGORITHM_ID.encode("ascii"))
    for path in (
        center.THIS_SCRIPT,
        center.ACTION_SCRIPT,
        center.JET_SCRIPT,
        center.METRIC_SCRIPT,
        center.ENDPOINT.with_suffix(".npz"),
        center.REPLAY.with_suffix(".npz"),
        center.JACOBIAN.with_suffix(".npz"),
        center.PARTITION.with_suffix(".npz"),
        center.SCALAR.with_suffix(".npz"),
    ):
        digest.update(path.read_bytes())
    return digest.hexdigest().upper()


def _path(kind: str, index: int) -> Path:
    return WORK / f"{kind}_{index:03d}.npz"


def _published_path(kind: str, index: int) -> Path:
    return PUBLISHED_WORK / f"{kind}_{index:03d}.npz"


def _valid(path: Path, kind: str, index: int, fingerprint: str) -> bool:
    if not path.is_file():
        return False
    try:
        with np.load(path) as source:
            tensor = np.asarray(source["quadratic_tensor"], dtype=float)
            return bool(
                str(source["kind"].item()) == kind
                and int(source["index"]) == index
                and int(source["shard_revision"]) == SHARD_REVISION
                and str(source["campaign_fingerprint"].item()) == fingerprint
                and tensor.shape == (OUTPUTS, TRANSVERSE, TRANSVERSE)
                and np.all(np.isfinite(tensor))
                and float(source["total_Frobenius_relative_residual"]) < 5.0e-13
                and float(source["output_Frobenius_maximum_relative_residual"]) < 5.0e-13
            )
    except Exception:
        return False


def _capture_quadratic(*args: object) -> tuple[dict[str, object], np.ndarray]:
    """Call the unchanged kernel with its lossless return option enabled."""
    row = center._quadratic_row(*args, retain_tensor=True)
    tensor = np.asarray(row.pop("quadratic_tensor"), dtype=float)
    if tensor.shape != (OUTPUTS, TRANSVERSE, TRANSVERSE):
        raise RuntimeError("center kernel did not expose the expected quadratic tensor")
    return row, np.array(tensor, copy=True)


def _worker(kind: str, indices: list[int]) -> dict[str, float]:
    inputs = center._load_inputs()
    fingerprint = _fingerprint()
    states, descriptors, tangents, axes, fields, axis_residuals = inputs[kind]
    WORK.mkdir(parents=True, exist_ok=True)
    computed = reused = 0
    elapsed = 0.0
    for index in indices:
        target = _path(kind, index)
        if _valid(target, kind, index, fingerprint):
            reused += 1
            continue
        published = _published_path(kind, index)
        if not published.is_file():
            raise FileNotFoundError(f"missing published center shard: {published}")
        started = time.perf_counter()
        row, tensor = _capture_quadratic(
            kind, index, states[index], float(descriptors[index]),
            inputs["weights"], inputs["reference"], tangents[index], axes[index],
            fields[index], float(axis_residuals[index]),
        )
        duration = time.perf_counter() - started
        recovered_total = float(np.linalg.norm(tensor))
        recovered_outputs = np.linalg.norm(tensor, axis=(1, 2))
        with np.load(published) as source:
            published_total = float(source["quadratic_Frobenius_norm"])
            published_outputs = np.asarray(
                source["quadratic_output_Frobenius_norms"], dtype=float,
            )
        tiny = np.finfo(float).tiny
        total_residual = abs(recovered_total - published_total) / max(
            published_total, tiny,
        )
        output_residual = float(np.max(
            abs(recovered_outputs - published_outputs)
            / np.maximum(published_outputs, tiny)
        ))
        if total_residual >= 5.0e-13 or output_residual >= 5.0e-13:
            raise RuntimeError(
                f"recovered tensor disagrees with published {kind} {index}: "
                f"total={total_residual}, output={output_residual}"
            )
        np.savez_compressed(
            target,
            kind=np.asarray(kind), index=np.asarray(index),
            quadratic_tensor=tensor,
            recovered_total_Frobenius_norm=np.asarray(recovered_total),
            recovered_output_Frobenius_norms=recovered_outputs,
            total_Frobenius_relative_residual=np.asarray(total_residual),
            output_Frobenius_maximum_relative_residual=np.asarray(output_residual),
            published_shard_SHA256=np.asarray(_sha(published)),
            elapsed_seconds=np.asarray(duration), worker_id=np.asarray(os.getpid()),
            shard_revision=np.asarray(SHARD_REVISION),
            campaign_fingerprint=np.asarray(fingerprint),
        )
        computed += 1
        elapsed += duration
        print(json.dumps({
            "kind": kind, "index": index, "elapsed_seconds": duration,
            "total_Frobenius_relative_residual": total_residual,
            "output_Frobenius_maximum_relative_residual": output_residual,
        }), flush=True)
    return {"computed": computed, "reused": reused, "elapsed_seconds": elapsed}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--kind", choices=("endpoint", "midpoint"), required=True)
    parser.add_argument("--indices", required=True)
    parser.add_argument("--workers", type=int, default=1)
    args = parser.parse_args()
    indices = [int(value) for value in args.indices.split(",") if value]
    groups = [indices[offset::args.workers] for offset in range(args.workers)]
    totals = {"computed": 0.0, "reused": 0.0, "elapsed_seconds": 0.0}
    with ProcessPoolExecutor(max_workers=args.workers) as executor:
        futures = [
            executor.submit(_worker, args.kind, group)
            for group in groups if group
        ]
        for future in as_completed(futures):
            result = future.result()
            for key in totals:
                totals[key] += result[key]
            print(json.dumps({"totals": totals}), flush=True)


if __name__ == "__main__":
    main()
