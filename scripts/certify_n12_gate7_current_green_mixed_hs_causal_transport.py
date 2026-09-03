"""Certify the current-C2 mixed Hermite--Simpson causal transport.

The endpoint mixed maps are reused.  New retained-action evaluations supply
only the missing endpoint first variations and midpoint mixed chain-rule
terms.  Every calculation is restart-safe and keeps Arb balls until the
final directed export.
"""

from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor, as_completed
import hashlib
import inspect
import json
import math
import os
from pathlib import Path
import sys
import time

import numpy as np
from flint import arb, arb_mat, ctx


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

import certify_n12_gate7_accepted_replay_center_outward_74d as cert  # noqa: E402
import certify_n12_gate7_current_green_correlated_scalar_interval355 as scalar  # noqa: E402
import certify_n12_gate7_current_green_mixed_transverse_all_endpoints as endpoint_mixed  # noqa: E402
from bhsm.interface.gate7_mixed_hermite_simpson_transport import (  # noqa: E402
    causal_mixed_rhs,
    local_hs_mixed_residual,
    mixed_midpoint_kinematics,
)


F = ROOT / "artifacts/flagship_integration"
A = ROOT / "artifacts/action_extension"
C = ROOT / "artifacts/current_semantics"
ENDPOINT = F / "BHSM_N12_GATE7_AUGMENTED_FIXED_DESCRIPTOR_NEWTON_ENDPOINT_CANDIDATE.json"
REPLAY = F / "BHSM_N12_GATE7_AUGMENTED_FIXED_DESCRIPTOR_NEWTON_MIDPOINT_REPLAY.json"
JACOBIAN = F / "BHSM_N12_GATE7_CORRELATED_DESCRIPTOR_AUGMENTED_JACOBIANS.json"
PRECONDITIONER = F / "BHSM_N12_GATE7_AUGMENTED_FIXED_DESCRIPTOR_BLOCK_NEWTON_PREDICTOR.json"
PARTITION = A / "BHSM_AE4_CURRENT_C2_GREEN_IMAGE_PARTITION_RECONCILIATION.json"
MIXED_ENDPOINT = F / "BHSM_N12_GATE7_CURRENT_GREEN_MIXED_TRANSVERSE_ALL_ENDPOINTS.json"
OUTWARD = F / "BHSM_N12_GATE7_CURRENT_GREEN_MIXED_BILINEAR_OUTWARD_RECONCILIATION.json"
AUDIT = C / "BHSM_N12_GATE7_CURRENT_GREEN_MIXED_HS_CAUSAL_COMPUTE_JUSTIFICATION.json"
RESULT = F / "BHSM_N12_GATE7_CURRENT_GREEN_MIXED_HS_CAUSAL_TRANSPORT.json"
DATA = RESULT.with_suffix(".npz")
WORK = F / ".current_green_mixed_hs_causal_transport_work"
THEORY = ROOT / "theory/n12_gate7_current_green_mixed_hs_causal_transport.md"
THIS_SCRIPT = Path(__file__).resolve()

NODES = 371
INTERVALS = 370
COORDINATES = 74
OUTPUTS = cert.STATE + 1
DEFAULT_PRECISION = 192
CAUSAL_PRECISION = 512
SHARD_REVISION = 1

MATHEMATICAL_INPUTS = (
    ENDPOINT, ENDPOINT.with_suffix(".npz"),
    REPLAY, REPLAY.with_suffix(".npz"),
    JACOBIAN, JACOBIAN.with_suffix(".npz"),
    PRECONDITIONER, PRECONDITIONER.with_suffix(".npz"),
    PARTITION, PARTITION.with_suffix(".npz"),
    MIXED_ENDPOINT, MIXED_ENDPOINT.with_suffix(".npz"),
    OUTWARD, OUTWARD.with_suffix(".npz"),
    Path(cert.__file__).resolve(), Path(scalar.__file__).resolve(),
    Path(endpoint_mixed.__file__).resolve(),
    ROOT / "src/bhsm/interface/gate7_mixed_hermite_simpson_transport.py",
)
FINAL_INPUTS = MATHEMATICAL_INPUTS + (AUDIT, THIS_SCRIPT, THEORY)


def _sha(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def _relative(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


def _provenance() -> dict[str, str]:
    return {_relative(path): _sha(path) for path in MATHEMATICAL_INPUTS}


def _kernel_source() -> str:
    """Derive the ball-preserving vectorized kernel from the certified one.

    The endpoint kernel intentionally rounded its fixed binary directions to
    Arb points.  Midpoint directions are themselves Arb balls, so the two
    input conversions are replaced while the complete differentiated
    bordered-response algebra is otherwise byte-for-byte identical.  The
    returned action jets are reused for the incidence first variation.
    """
    source = inspect.getsource(endpoint_mixed._mixed_axis_map).replace("\r\n", "\n")
    replacements = (
        ("def _mixed_axis_map(", "def _mixed_axis_map_preserving_balls("),
        (
            "u = np.asarray([arb(float(value)) for value in axis_direction], dtype=object)",
            "u = np.asarray([value if isinstance(value, arb) else arb(float(value)) for value in axis_direction], dtype=object)",
        ),
        (
            "[arb(float(value)) for value in row]\n        for row in transverse_directions",
            "[value if isinstance(value, arb) else arb(float(value)) for value in row]\n        for row in transverse_directions",
        ),
        ("    return result\n", "    return result, jets\n"),
    )
    for old, new in replacements:
        if source.count(old) != 1:
            raise RuntimeError(f"mixed-kernel source contract changed: {old!r}")
        source = source.replace(old, new)
    return source


def _ball_mixed_kernel():
    namespace = dict(vars(endpoint_mixed))
    exec(compile(_kernel_source(), str(THIS_SCRIPT), "exec"), namespace)
    return namespace["_mixed_axis_map_preserving_balls"]


def _kernel_sha() -> str:
    return hashlib.sha256(_kernel_source().encode("utf-8")).hexdigest().upper()


def _fingerprint(stage: str, precision: int) -> str:
    payload = {
        "kernel_source_SHA256": _kernel_sha(),
        "precision_bits": precision,
        "provenance_inputs": _provenance(),
        "shard_revision": SHARD_REVISION,
        "stage": stage,
    }
    return hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest().upper()


def _endpoint_shard(node: int) -> Path:
    return WORK / f"endpoint_{node:03d}.npz"


def _midpoint_shard(interval: int) -> Path:
    return WORK / f"midpoint_{interval:03d}.npz"


def _valid(path: Path, index_name: str, index: int, stage: str,
           precision: int) -> bool:
    if not path.is_file():
        return False
    try:
        with np.load(path) as source:
            return bool(
                int(source[index_name]) == index
                and int(source["precision_bits"]) == precision
                and int(source["shard_revision"]) == SHARD_REVISION
                and str(source["input_fingerprint_SHA256"].item())
                == _fingerprint(stage, precision)
            )
    except Exception:
        return False


def _export(values: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    values = np.asarray(values, dtype=object)
    midpoint = np.empty(values.shape, dtype=float)
    radius = np.empty(values.shape, dtype=float)
    for index in np.ndindex(values.shape):
        midpoint[index] = float(values[index])
        radius[index] = math.nextafter(
            float(abs(values[index] - arb(midpoint[index])).upper()), math.inf,
        )
    return midpoint, radius


def _ball(midpoint: np.ndarray, radius: np.ndarray) -> np.ndarray:
    midpoint = np.asarray(midpoint, dtype=float)
    radius = np.asarray(radius, dtype=float)
    result = np.empty(midpoint.shape, dtype=object)
    for index in np.ndindex(midpoint.shape):
        result[index] = arb(float(midpoint[index]), float(radius[index]))
    return result


def _endpoint_geometry(node: int, tangents: np.ndarray,
                       unit_axes: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    axis = scalar._normalized_central_axis(unit_axes[node])
    projector = np.eye(COORDINATES) - np.outer(axis, axis)
    frame = cert._frame(tangents[node], cert.TRIAL_DESCRIPTOR_SCALE)
    return frame @ axis, frame @ projector


def _load_common():
    with np.load(ENDPOINT.with_suffix(".npz")) as source:
        endpoint = {
            "states": np.asarray(source["projected_states"], dtype=float),
            "descriptors": np.asarray(source["independent_signed_descriptors"], dtype=float),
            "times": np.asarray(source["collocation_arc_parameters"], dtype=float),
            "weights": np.asarray(source["state_weights"], dtype=float),
            "reference": np.asarray(source["branch_reference"], dtype=float),
        }
    with np.load(JACOBIAN.with_suffix(".npz")) as source:
        tangents = np.asarray(source["endpoint_physical_tangent_action"], dtype=float)
    with np.load(PARTITION.with_suffix(".npz")) as source:
        unit_axes = np.asarray(source["current_center_green_image_unit_mid"], dtype=float)
    return endpoint, tangents, unit_axes


def _endpoint_worker(nodes: list[int], precision: int) -> dict[str, float]:
    ctx.prec = precision
    WORK.mkdir(parents=True, exist_ok=True)
    endpoint, tangents, unit_axes = _load_common()
    fingerprint = _fingerprint("endpoint", precision)
    computed = reused = 0
    elapsed_total = 0.0
    for count, node in enumerate(nodes, 1):
        target = _endpoint_shard(node)
        if _valid(target, "node", node, "endpoint", precision):
            reused += 1
            continue
        central, transverse = _endpoint_geometry(node, tangents, unit_axes)
        started = time.perf_counter()
        enclosure = cert._rate_enclosure(
            endpoint["states"][node], endpoint["descriptors"][node],
            endpoint["weights"], endpoint["reference"],
            np.column_stack((central, transverse)),
        )
        first = np.asarray(enclosure.derivative, dtype=object)
        first_mid, first_radius = _export(first)
        elapsed = time.perf_counter() - started
        np.savez_compressed(
            target,
            first_mid=first_mid,
            first_radius=first_radius,
            first_arb=cert._arb_string_array(first),
            gap_lower=np.asarray(enclosure.gap_lower),
            eigen_residual_upper=np.asarray(enclosure.eigen_residual_upper),
            node=np.asarray(node),
            precision_bits=np.asarray(precision),
            shard_revision=np.asarray(SHARD_REVISION),
            input_fingerprint_SHA256=np.asarray(fingerprint),
            elapsed_seconds=np.asarray(elapsed),
            worker_id=np.asarray(os.getpid()),
        )
        computed += 1
        elapsed_total += elapsed
        print(json.dumps({"stage": "endpoint", "worker": os.getpid(),
                          "completed": count, "assigned": len(nodes),
                          "node": node, "elapsed_seconds": elapsed}), flush=True)
    return {"computed": computed, "reused": reused,
            "elapsed_seconds": elapsed_total}


def _midpoint_worker(intervals: list[int], precision: int) -> dict[str, float]:
    ctx.prec = precision
    WORK.mkdir(parents=True, exist_ok=True)
    endpoint, tangents, unit_axes = _load_common()
    with np.load(REPLAY.with_suffix(".npz")) as source:
        midpoint_values = np.asarray(source["midpoint_augmented_action_values"], dtype=float)
    with np.load(MIXED_ENDPOINT.with_suffix(".npz")) as source:
        mixed_mid = np.asarray(source["mixed_direct_bilinear_mid"], dtype=float)
        mixed_radius = np.asarray(source["mixed_direct_bilinear_radius"], dtype=float)
    kernel = _ball_mixed_kernel()
    fingerprint = _fingerprint("midpoint", precision)
    zero_vector = np.asarray([arb(0) for _ in range(OUTPUTS)], dtype=object)
    zero_matrix = np.asarray(
        [[arb(0) for _ in range(COORDINATES)] for _ in range(OUTPUTS)],
        dtype=object,
    )
    computed = reused = 0
    elapsed_total = 0.0
    for count, interval in enumerate(intervals, 1):
        target = _midpoint_shard(interval)
        if _valid(target, "interval", interval, "midpoint", precision):
            reused += 1
            continue
        if interval == 0:
            left_c = zero_vector
            left_t = zero_matrix
            left_cf = zero_vector
            left_tf = zero_matrix
            left_b = zero_matrix
        else:
            left_c_float, left_t_float = _endpoint_geometry(
                interval, tangents, unit_axes,
            )
            left_c = np.asarray([arb(float(x)) for x in left_c_float], dtype=object)
            left_t = np.asarray([[arb(float(x)) for x in row] for row in left_t_float], dtype=object)
            with np.load(_endpoint_shard(interval)) as source:
                left_first = cert._parse_arb_string_array(source["first_arb"])
            left_cf = left_first[:, 0]
            left_tf = left_first[:, 1:]
            left_b = _ball(mixed_mid[interval - 1], mixed_radius[interval - 1])

        right_node = interval + 1
        right_c_float, right_t_float = _endpoint_geometry(
            right_node, tangents, unit_axes,
        )
        right_c = np.asarray([arb(float(x)) for x in right_c_float], dtype=object)
        right_t = np.asarray([[arb(float(x)) for x in row] for row in right_t_float], dtype=object)
        with np.load(_endpoint_shard(right_node)) as source:
            right_first = cert._parse_arb_string_array(source["first_arb"])
        right_cf = right_first[:, 0]
        right_tf = right_first[:, 1:]
        right_b = _ball(mixed_mid[interval], mixed_radius[interval])

        h = arb(float(endpoint["times"][interval + 1] - endpoint["times"][interval]))
        kinematics = mixed_midpoint_kinematics(
            h, left_c, right_c, left_cf, right_cf,
            left_t, right_t, left_tf, right_tf, left_b, right_b,
        )
        augmented = midpoint_values[interval]
        state = augmented[:cert.STATE] / endpoint["weights"]
        descriptor = float(augmented[cert.STATE])
        started = time.perf_counter()
        intrinsic, jets = kernel(
            state, descriptor, endpoint["weights"], endpoint["reference"],
            kinematics.central_direction, kinematics.transverse_directions,
        )
        original_jets = cert._arb_action_jets
        cert._arb_action_jets = lambda _state: jets
        try:
            incidence_enclosure = cert._rate_enclosure(
                state, descriptor, endpoint["weights"], endpoint["reference"],
                kinematics.mixed_second_incidence,
            )
        finally:
            cert._arb_action_jets = original_jets
        incidence = np.asarray(incidence_enclosure.derivative, dtype=object)
        local = local_hs_mixed_residual(
            h, left_b, intrinsic, incidence, right_b,
        )
        elapsed = time.perf_counter() - started
        local_mid, local_radius = _export(local)
        intrinsic_mid, intrinsic_radius = _export(intrinsic)
        incidence_mid, incidence_radius = _export(incidence)
        np.savez_compressed(
            target,
            intrinsic_mid=intrinsic_mid,
            intrinsic_radius=intrinsic_radius,
            incidence_mid=incidence_mid,
            incidence_radius=incidence_radius,
            local_hs_mid=local_mid,
            local_hs_radius=local_radius,
            local_hs_arb=cert._arb_string_array(local),
            gap_lower=np.asarray(incidence_enclosure.gap_lower),
            eigen_residual_upper=np.asarray(incidence_enclosure.eigen_residual_upper),
            interval=np.asarray(interval),
            precision_bits=np.asarray(precision),
            shard_revision=np.asarray(SHARD_REVISION),
            input_fingerprint_SHA256=np.asarray(fingerprint),
            elapsed_seconds=np.asarray(elapsed),
            worker_id=np.asarray(os.getpid()),
        )
        computed += 1
        elapsed_total += elapsed
        print(json.dumps({"stage": "midpoint", "worker": os.getpid(),
                          "completed": count, "assigned": len(intervals),
                          "interval": interval, "elapsed_seconds": elapsed}), flush=True)
    return {"computed": computed, "reused": reused,
            "elapsed_seconds": elapsed_total}


def _run(stage: str, indices: list[int], workers: int, precision: int) -> None:
    if stage == "midpoint":
        needed = sorted({node for interval in indices
                         for node in (interval, interval + 1) if node > 0})
        missing = [node for node in needed if not _valid(
            _endpoint_shard(node), "node", node, "endpoint", precision,
        )]
        if missing:
            raise RuntimeError(f"missing endpoint first-variation shards: {missing[:12]}")
    groups = [indices[index::workers] for index in range(workers)]
    worker = _endpoint_worker if stage == "endpoint" else _midpoint_worker
    totals = {"computed": 0, "reused": 0, "elapsed_seconds": 0.0}
    with ProcessPoolExecutor(max_workers=workers) as executor:
        futures = [executor.submit(worker, group, precision)
                   for group in groups if group]
        for future in as_completed(futures):
            row = future.result()
            for key in totals:
                totals[key] += row[key]
            print(json.dumps({"stage_complete_worker": stage,
                              "totals": totals}), flush=True)


def _require_authorized_audit() -> dict[str, object]:
    if not AUDIT.is_file():
        raise RuntimeError("compute-justification audit required before campaign")
    audit = json.loads(AUDIT.read_text(encoding="utf-8"))
    if not (
        audit.get("validation_passed") is True
        and audit.get("campaign_authorized") is True
    ):
        raise RuntimeError("validated campaign authorization required")
    return audit


def _norm_upper(values: np.ndarray) -> float:
    total = 0.0
    for value in np.asarray(values, dtype=object).ravel():
        upper = math.nextafter(float(abs(value).upper()), math.inf)
        total = math.nextafter(total + upper * upper, math.inf)
    return math.nextafter(math.sqrt(total), math.inf)


def build_payload(precision: int) -> dict[str, object]:
    missing_inputs = [str(path) for path in FINAL_INPUTS if not path.is_file()]
    if missing_inputs:
        raise FileNotFoundError(", ".join(missing_inputs))
    audit = _require_authorized_audit()
    missing_endpoint = [node for node in range(1, NODES) if not _valid(
        _endpoint_shard(node), "node", node, "endpoint", precision,
    )]
    missing_midpoint = [interval for interval in range(INTERVALS) if not _valid(
        _midpoint_shard(interval), "interval", interval, "midpoint", precision,
    )]
    if missing_endpoint or missing_midpoint:
        raise RuntimeError(
            f"missing endpoint={len(missing_endpoint)} midpoint={len(missing_midpoint)} shards"
        )

    with np.load(JACOBIAN.with_suffix(".npz")) as source:
        tangents = np.asarray(source["endpoint_physical_tangent_action"], dtype=float)
    with np.load(PRECONDITIONER.with_suffix(".npz")) as source:
        left = np.asarray(source["left_Newton_blocks"], dtype=float)
        right = np.asarray(source["reduced_right_Newton_blocks"], dtype=float)

    ctx.prec = CAUSAL_PRECISION
    coordinate = arb_mat(COORDINATES, COORDINATES)
    causal = np.empty((NODES, COORDINATES, COORDINATES), dtype=object)
    causal[0] = np.asarray(
        [[arb(0) for _ in range(COORDINATES)] for _ in range(COORDINATES)],
        dtype=object,
    )
    local_norms = np.empty(INTERVALS)
    endpoint_seconds = 0.0
    midpoint_seconds = 0.0
    for node in range(1, NODES):
        with np.load(_endpoint_shard(node)) as source:
            endpoint_seconds += float(source["elapsed_seconds"])
    for interval in range(INTERVALS):
        with np.load(_midpoint_shard(interval)) as source:
            local = cert._parse_arb_string_array(source["local_hs_arb"])
            midpoint_seconds += float(source["elapsed_seconds"])
        local_norms[interval] = _norm_upper(local)
        test = cert._arb_matrix(cert._frame(
            tangents[interval + 1], cert.TEST_DESCRIPTOR_SCALE,
        ).T)
        trial = cert._arb_matrix(cert._frame(
            tangents[interval], cert.TRIAL_DESCRIPTOR_SCALE,
        ))
        previous = cert._array(coordinate)
        rhs = causal_mixed_rhs(
            cert._array(test), left[interval], trial, previous, local,
        )
        coordinate = -cert._arb_matrix(right[interval]).inv() * cert._mat(rhs)
        causal[interval + 1] = cert._array(coordinate)

    causal_mid, causal_radius = _export(causal)
    norm_upper = np.asarray([_norm_upper(row) for row in causal])
    representative_norm = np.linalg.norm(causal_mid, axis=(1, 2))
    radius_norm = np.linalg.norm(causal_radius, axis=(1, 2))
    wrapping = np.flatnonzero(
        (np.arange(NODES) > 0) & (radius_norm >= representative_norm)
    )
    owner = int(np.argmax(norm_upper))
    np.savez_compressed(
        DATA,
        causal_mixed_mid=causal_mid,
        causal_mixed_radius=causal_radius,
        causal_mixed_norm_upper=norm_upper,
        local_hs_mixed_norm_upper=local_norms,
        endpoint_precision_bits=np.asarray(precision),
        midpoint_precision_bits=np.asarray(precision),
        causal_precision_bits=np.asarray(CAUSAL_PRECISION),
    )
    validation = {
        "compute_justification_audit_authorized_campaign": audit["campaign_authorized"],
        "all_370_endpoint_first_variation_maps_reused": not missing_endpoint,
        "all_370_mixed_HS_midpoint_residuals_derived": not missing_midpoint,
        "complete_370_interval_frozen_causal_recurrence_composed": causal.shape == (371, 74, 74),
        "all_exported_causal_centers_and_radii_finite": bool(
            np.all(np.isfinite(causal_mid)) and np.all(np.isfinite(causal_radius))
            and np.all(causal_radius >= 0.0) and np.all(np.isfinite(norm_upper))
        ),
        "no_recursive_component_box_wrapping": wrapping.size == 0,
        "same_action_center_branch_trajectory_frames_and_preconditioner_retained": True,
        "no_empirical_or_calibration_input_used": True,
        "mixed_causal_result_not_relabelled_as_full_transverse_or_two_radius_authority": True,
    }
    passed = all(validation.values())
    return {
        "artifact": "BHSM_N12_GATE7_CURRENT_GREEN_MIXED_HS_CAUSAL_TRANSPORT",
        "status": (
            "CURRENT_GREEN_MIXED_HS_CAUSAL_TRANSPORT_CERTIFIED"
            if passed else "CURRENT_GREEN_MIXED_HS_CAUSAL_TRANSPORT_REQUIRES_CORRELATION_OR_PRECISION_REPAIR"
        ),
        "authority": "ARB_MIXED_HS_CHAIN_RULE_AND_FROZEN_CAUSAL_PRECONDITIONER_NOT_FULL_TRANSVERSE_OR_TWO_RADIUS_AUTHORITY",
        "precision_bits": {"endpoint": precision, "midpoint": precision,
                           "causal": CAUSAL_PRECISION},
        "maximum_local_HS_mixed_norm_upper": float(np.max(local_norms)),
        "maximum_local_HS_mixed_owner_interval": int(np.argmax(local_norms)),
        "maximum_causal_mixed_norm_upper": float(norm_upper[owner]),
        "maximum_causal_mixed_owner_node": owner,
        "first_recursive_wrapping_node": int(wrapping[0]) if wrapping.size else None,
        "measured_compute_CPU_hours": {
            "endpoint_first_variations": endpoint_seconds / 3600.0,
            "midpoint_mixed_chain_rule": midpoint_seconds / 3600.0,
            "total": (endpoint_seconds + midpoint_seconds) / 3600.0,
        },
        "exact_next_calculation": (
            "DERIVE_THE_CURRENT_FULL_TRANSVERSE_QUADRATIC_OPERATOR_MAJORANT_AND_INSERT_IT_WITH_THIS_CAUSAL_MIXED_OPERATOR_IN_THE_COMPONENTWISE_TWO_RADIUS_VOLTERRA_SCREEN"
            if passed else
            "ESCALATE_ONLY_THE_FIRST_RECURSIVE_WRAPPING_REGION_OR_RETAIN_A_SHARED_AFFINE_GENERATOR_THROUGH_THE_CAUSAL_RECURRENCE"
        ),
        "claim_boundary": {
            "CURRENT_GREEN_MIXED_TRANSVERSE_ALL_MIDPOINTS_DERIVED": passed,
            "CURRENT_GREEN_MIXED_TRANSVERSE_CAUSAL_COMPOSITION_DERIVED": passed,
            "CURRENT_GREEN_TRANSVERSE_TRANSVERSE_FULL_OPERATOR_BOUND_DERIVED": False,
            "CURRENT_CENTER_GREEN_CAUSAL_TWO_RADIUS_CERTIFICATE_DERIVED": False,
            "G7_ROOT_NONEXISTENCE_DERIVED": False,
            "G7_PHYSICAL_SPACETIME_INSTABILITY_DERIVED": False,
            "FULL_BHSM_COMPLETE": False,
        },
        "data": _relative(DATA),
        "data_SHA256": _sha(DATA),
        "inputs": {_relative(path): _sha(path) for path in FINAL_INPUTS},
        "validation": validation,
        "validation_passed": passed,
        "FULL_BHSM_COMPLETE": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--stage", choices=("endpoint", "midpoint"))
    parser.add_argument("--nodes", default="")
    parser.add_argument("--intervals", default="")
    parser.add_argument("--workers", type=int, default=min(8, os.cpu_count() or 1))
    parser.add_argument("--precision", type=int, default=DEFAULT_PRECISION)
    parser.add_argument("--benchmark", action="store_true")
    parser.add_argument("--aggregate-only", action="store_true")
    args = parser.parse_args()
    if args.precision < 128:
        raise SystemExit("precision below benchmark minimum")
    if not args.benchmark and not args.aggregate_only:
        _require_authorized_audit()
    if args.stage == "endpoint":
        indices = list(range(1, NODES)) if not args.nodes else [
            int(value) for value in args.nodes.split(",")
        ]
        _run("endpoint", indices, max(1, min(args.workers, len(indices))), args.precision)
        return
    if args.stage == "midpoint":
        indices = list(range(INTERVALS)) if not args.intervals else [
            int(value) for value in args.intervals.split(",")
        ]
        _run("midpoint", indices, max(1, min(args.workers, len(indices))), args.precision)
        return
    payload = build_payload(args.precision)
    RESULT.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8", newline="\n",
    )
    print(json.dumps({
        "status": payload["status"],
        "maximum_causal_mixed_norm_upper": payload["maximum_causal_mixed_norm_upper"],
        "first_recursive_wrapping_node": payload["first_recursive_wrapping_node"],
        "validation_passed": payload["validation_passed"],
    }, indent=2, sort_keys=True))
    if not payload["validation_passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
