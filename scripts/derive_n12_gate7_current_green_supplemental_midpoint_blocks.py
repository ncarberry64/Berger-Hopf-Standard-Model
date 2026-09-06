"""Recover the missing signed midpoint Hessian blocks restart-safely.

The retained Gate-7 midpoint shards contain ``H[U,U]`` on 73 exact stored
directions.  The causal Hermite--Simpson midpoint map also has components in
the 26-direction complement ``C``.  This campaign evaluates only ``H[C,U]``
and the upper triangle of ``H[C,C]``: 2249 new direction pairs per midpoint.

All outputs are binary64 center data.  No rounding, outward remainder, or
Gate-7 claim is attached here.
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
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from bhsm.interface.current_green_supplemental_midpoint import (  # noqa: E402
    complete_ambient_basis,
)
import audit_n12_gate7_current_green_componentwise_two_radius as component  # noqa: E402
import certify_n12_gate7_accepted_replay_center_outward_74d as cert  # noqa: E402
import certify_n12_gate7_current_green_signed_transverse_causal_center as causal  # noqa: E402
import derive_n12_gate7_current_green_full_transverse_quadratic_center as center  # noqa: E402
import derive_n12_gate7_current_green_signed_transverse_tensor_recovery as recovery  # noqa: E402
from derive_n12_gate7_current_green_supplemental_mixed_rate import (  # noqa: E402
    mixed_rate_map,
)


F = ROOT / "artifacts" / "flagship_integration"
WORK = F / ".current_green_supplemental_midpoint_blocks_work"
ALGORITHM_ID = "CURRENT_GREEN_SUPPLEMENTAL_MIDPOINT_BLOCKS_V1"
SHARD_REVISION = 1
INTERVALS = 370
OUTPUTS = 99
RETAINED = 73
COMPLEMENT = 26
NEW_PAIRS = RETAINED * COMPLEMENT + COMPLEMENT * (COMPLEMENT + 1) // 2
THIS_SCRIPT = Path(__file__).resolve()


def _sha(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def _fingerprint() -> str:
    digest = hashlib.sha256(ALGORITHM_ID.encode("ascii"))
    digest.update(recovery._fingerprint().encode("ascii"))
    sources = (
        THIS_SCRIPT,
        Path(mixed_rate_map.__code__.co_filename).resolve(),
        ROOT / "src/bhsm/interface/current_green_supplemental_midpoint.py",
        Path(causal.__file__).resolve(),
        Path(center.__file__).resolve(),
        causal.JACOBIAN.with_suffix(".npz"),
        causal.ENDPOINT.with_suffix(".npz"),
        causal.PARTITION.with_suffix(".npz"),
    )
    for source in sources:
        digest.update(source.read_bytes())
    return digest.hexdigest().upper()


def _row_path(interval: int, row: int) -> Path:
    return WORK / f"midpoint_{interval:03d}_complement_{row:02d}.npz"


def _aggregate_path(interval: int) -> Path:
    return WORK / f"midpoint_{interval:03d}.npz"


def _valid_row(
    path: Path,
    interval: int,
    row: int,
    fingerprint: str,
    recovered_sha: str,
) -> bool:
    if not path.is_file():
        return False
    try:
        with np.load(path) as source:
            diagnostics = np.asarray(source["diagnostics"], dtype=float)
            return bool(
                int(source["interval"]) == interval
                and int(source["complement_row"]) == row
                and int(source["shard_revision"]) == SHARD_REVISION
                and str(source["campaign_fingerprint"].item()) == fingerprint
                and str(source["recovered_shard_SHA256"].item()) == recovered_sha
                and source["complement_retained_row"].shape == (OUTPUTS, RETAINED)
                and source["complement_complement_upper"].shape
                == (OUTPUTS, COMPLEMENT - row)
                and diagnostics.shape == (5,)
                and np.all(np.isfinite(source["complement_retained_row"]))
                and np.all(np.isfinite(source["complement_complement_upper"]))
                and np.all(np.isfinite(diagnostics))
            )
    except Exception:
        return False


def _load_geometry() -> dict[str, np.ndarray | dict[str, object]]:
    inputs = center._load_inputs()
    endpoint_axes = component._load_axes()
    with np.load(causal.JACOBIAN.with_suffix(".npz")) as source:
        endpoint_tangents = np.asarray(
            source["endpoint_physical_tangent_action"], dtype=float,
        )
        midpoint_tangents = np.asarray(
            source["midpoint_physical_tangent_action"], dtype=float,
        )
    with np.load(causal.ENDPOINT.with_suffix(".npz")) as source:
        times = np.asarray(source["collocation_arc_parameters"], dtype=float)
    return {
        "inputs": inputs,
        "endpoint_axes": endpoint_axes,
        "endpoint_tangents": endpoint_tangents,
        "midpoint_tangents": midpoint_tangents,
        "times": times,
    }


def _completion(interval: int, geometry: dict[str, object]):
    inputs = geometry["inputs"]
    assert isinstance(inputs, dict)
    midpoint_tangents = np.asarray(geometry["midpoint_tangents"], dtype=float)
    midpoint_axes = np.asarray(inputs["midpoint"][3], dtype=float)
    recovered = recovery._path("midpoint", interval)
    fingerprint = recovery._fingerprint()
    if not recovery._valid(recovered, "midpoint", interval, fingerprint):
        raise RuntimeError(f"validated signed midpoint shard required: {interval}")
    with np.load(recovered) as source:
        stored_basis = np.asarray(source["transverse_basis"], dtype=float)
    completion = complete_ambient_basis(
        center._frame(midpoint_tangents[interval]),
        midpoint_axes[interval],
        stored_basis,
    )
    if (
        completion.retained_directions.shape != (OUTPUTS, RETAINED)
        or completion.complement_directions.shape != (OUTPUTS, COMPLEMENT)
    ):
        raise RuntimeError("midpoint ambient completion dimensions changed")
    return completion, recovered


def _compute_interval(interval: int) -> dict[str, float]:
    geometry = _load_geometry()
    inputs = geometry["inputs"]
    assert isinstance(inputs, dict)
    fingerprint = _fingerprint()
    completion, recovered = _completion(interval, geometry)
    recovered_sha = _sha(recovered)
    states, descriptors = inputs["midpoint"][:2]
    weights = np.asarray(inputs["weights"], dtype=float)
    reference = np.asarray(inputs["reference"], dtype=float)
    computed = reused = 0
    elapsed = 0.0
    WORK.mkdir(parents=True, exist_ok=True)
    for row in range(COMPLEMENT):
        path = _row_path(interval, row)
        if _valid_row(path, interval, row, fingerprint, recovered_sha):
            reused += 1
            continue
        right = np.column_stack((
            completion.retained_directions,
            completion.complement_directions[:, row:],
        ))
        started = time.perf_counter()
        tensor, diagnostics = mixed_rate_map(
            np.asarray(states[interval], dtype=float),
            float(descriptors[interval]),
            weights,
            reference,
            completion.complement_directions[:, row],
            right,
        )
        duration = time.perf_counter() - started
        if tensor.shape != (OUTPUTS, RETAINED + COMPLEMENT - row):
            raise RuntimeError("supplemental mixed-rate output dimensions changed")
        diagnostic_values = np.asarray([
            diagnostics.base_response_residual_2_norm,
            diagnostics.left_first_response_relative_residual,
            diagnostics.right_first_response_relative_residual,
            diagnostics.mixed_response_relative_residual,
            diagnostics.mixed_eigenline_normalization_residual,
        ])
        np.savez_compressed(
            path,
            interval=np.asarray(interval), complement_row=np.asarray(row),
            complement_retained_row=tensor[:, :RETAINED],
            complement_complement_upper=tensor[:, RETAINED:],
            diagnostics=diagnostic_values,
            elapsed_seconds=np.asarray(duration), worker_id=np.asarray(os.getpid()),
            shard_revision=np.asarray(SHARD_REVISION),
            campaign_fingerprint=np.asarray(fingerprint),
            recovered_shard_SHA256=np.asarray(recovered_sha),
        )
        computed += 1
        elapsed += duration
        print(json.dumps({
            "interval": interval,
            "complement_row": row,
            "elapsed_seconds": duration,
        }), flush=True)
    return {"computed": computed, "reused": reused, "elapsed_seconds": elapsed}


def _aggregate_interval(interval: int) -> Path:
    geometry = _load_geometry()
    completion, recovered = _completion(interval, geometry)
    fingerprint = _fingerprint()
    recovered_sha = _sha(recovered)
    cu = np.empty((OUTPUTS, COMPLEMENT, RETAINED))
    cc = np.empty((OUTPUTS, COMPLEMENT, COMPLEMENT))
    diagnostics = np.empty((COMPLEMENT, 5))
    row_elapsed = np.empty(COMPLEMENT)
    for row in range(COMPLEMENT):
        path = _row_path(interval, row)
        if not _valid_row(path, interval, row, fingerprint, recovered_sha):
            raise RuntimeError(
                f"validated supplemental row required: midpoint {interval}, row {row}"
            )
        with np.load(path) as source:
            cu[:, row] = source["complement_retained_row"]
            upper = np.asarray(source["complement_complement_upper"], dtype=float)
            cc[:, row, row:] = upper
            cc[:, row:, row] = upper
            diagnostics[row] = source["diagnostics"]
            row_elapsed[row] = source["elapsed_seconds"]
    if not (np.all(np.isfinite(cu)) and np.all(np.isfinite(cc))):
        raise RuntimeError("assembled supplemental blocks are nonfinite")
    path = _aggregate_path(interval)
    np.savez_compressed(
        path,
        interval=np.asarray(interval),
        complement_retained=cu,
        complement_complement=cc,
        retained_directions=completion.retained_directions,
        complement_directions=completion.complement_directions,
        frame_qr_diagonal=completion.frame_qr_diagonal,
        coordinate_basis_residual=np.asarray(completion.coordinate_basis_residual),
        normal_frame_residual=np.asarray(completion.normal_frame_residual),
        full_basis_condition_2=np.asarray(completion.full_basis_condition_2),
        row_diagnostics=diagnostics,
        row_elapsed_seconds=row_elapsed,
        evaluated_new_direction_pairs=np.asarray(NEW_PAIRS),
        shard_revision=np.asarray(SHARD_REVISION),
        campaign_fingerprint=np.asarray(fingerprint),
        recovered_shard_SHA256=np.asarray(recovered_sha),
    )
    return path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--indices", required=True)
    parser.add_argument("--workers", type=int, default=1)
    parser.add_argument("--aggregate-only", action="store_true")
    args = parser.parse_args()
    indices = [int(value) for value in args.indices.split(",") if value]
    if any(index < 0 or index >= INTERVALS for index in indices):
        raise ValueError("midpoint index outside 0..369")
    if args.aggregate_only:
        for index in indices:
            print(_aggregate_interval(index), flush=True)
        return
    workers = max(1, min(args.workers, os.cpu_count() or 1, len(indices)))
    totals = {"computed": 0.0, "reused": 0.0, "elapsed_seconds": 0.0}
    with ProcessPoolExecutor(max_workers=workers) as executor:
        futures = {executor.submit(_compute_interval, index): index for index in indices}
        for future in as_completed(futures):
            result = future.result()
            for key in totals:
                totals[key] += result[key]
            print(json.dumps({"completed_interval": futures[future], "totals": totals}), flush=True)
    for index in indices:
        _aggregate_interval(index)


if __name__ == "__main__":
    main()
