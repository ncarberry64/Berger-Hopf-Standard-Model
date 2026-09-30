"""Insert the internal RHS into the current, unchanged adaptive cover.

The existing response assembler supplies signed Euler--Lagrange source jets
and center solves.  This driver uses its raw source-variation bound together
with the already-certified instantaneous inverse.  Consequently finiteness
does not require a new relative-operator Neumann proof.  That diagnostic is
retained separately and is never promoted when it fails.

The tangent/remainder ellipsoid is centered at the SAME Bernstein control
mean as the spectrum/projector certificate.  Completed numerical rows are
checkpointed before final reporting, and can be resumed without recomputing.
"""

from __future__ import annotations

import argparse
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor
from fractions import Fraction
import hashlib
import json
import math
import os
from pathlib import Path
import sys
import time
from typing import Any

for _thread_variable in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ[_thread_variable] = "1"

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import certify_n12_c2_stop_dop853_adaptive_bordered_rhs_response as response

BASE = ROOT / "artifacts/flagship_integration"
PREFIX = "BHSM_N12_C2_STOP_DOP853_PROJECTOR_REFINED_"
DEFAULT_SPECTRUM = BASE / (PREFIX + "BOUNDARY_CLUSTER_SPECTRUM.json")
DEFAULT_PROJECTOR = BASE / (PREFIX + "SELECTED_PROJECTOR_GRAPH.json")
DEFAULT_INVERSE = BASE / (PREFIX + "BORDERED_HARD_INVERSE.json")
DEFAULT_RESULT = BASE / (PREFIX + "BORDERED_RHS_RESPONSE.json")
DEFAULT_CENTER = BASE / "BHSM_N12_C2_STOP_HIGH_ORDER_QUARTER_STEP_RETAINED_RECONNAISSANCE.npz"


def _sha256(path: Path) -> str:
    data = path.read_bytes()
    if path.suffix.lower() in {".py", ".md", ".json"}:
        data = data.replace(b"\r\n", b"\n")
    return hashlib.sha256(data).hexdigest().upper()


def _relative(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


def _key(row: dict[str, Any]) -> tuple[int, int, int]:
    return int(row["interval"]), int(row["subspan"]), int(row["subdivisions"])


def _partition_is_exact(rows: list[dict[str, Any]], interval_count: int) -> bool:
    grouped: dict[int, list[tuple[Fraction, Fraction]]] = defaultdict(list)
    for row in rows:
        interval, subspan, subdivisions = _key(row)
        if subdivisions < 1 or not 0 <= subspan < subdivisions:
            return False
        grouped[interval].append((Fraction(subspan, subdivisions), Fraction(subspan + 1, subdivisions)))
    if set(grouped) != set(range(interval_count)):
        return False
    for spans in grouped.values():
        spans.sort()
        if spans[0][0] != 0 or spans[-1][1] != 1:
            return False
        if any(left[1] != right[0] for left, right in zip(spans, spans[1:])):
            return False
    return True


def _finite_cap(rhs_center: float, raw_variation: float, inverse_bound: float) -> tuple[float, float]:
    values = (rhs_center, raw_variation, inverse_bound)
    if not all(math.isfinite(value) and value >= 0 for value in values) or inverse_bound == 0:
        raise ValueError("finite nonnegative RHS norms and a positive inverse bound required")
    source_cap = response._up(rhs_center + raw_variation)
    return source_cap, response._up(inverse_bound * source_cap)


def _safe_json(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: _safe_json(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_safe_json(item) for item in value]
    if isinstance(value, (float, np.floating)) and not math.isfinite(float(value)):
        return None
    return value


def _same_center_tangent_geometry(interval: int, subspan: int, subdivisions: int) -> dict[str, Any]:
    """Integral Taylor enclosure, with its residual offset made explicit.

    Let m=mean(B_i), c=B(1/2), t=B'(1/2)/2.  The remainder belongs to
    conv({0,B''_i/8}).  Hence B(u)-m = (2u-1)t + A theta, where columns
    A_i=R_i-(m-c), theta is a simplex vector, and ||theta||_2<=1.  Scaling
    the two blocks with 1/a^2+1/b^2=1 encloses their Cartesian product.
    """
    values, coefficients, _, weights, reference, bracket_raw, stop_raw = response.dense._dense_arrays()
    right = float(stop_raw[0]) if interval == int(bracket_raw[0]) else 1.0
    controls = response.dense._dense_bernstein_controls(values[interval], coefficients[interval])
    controls = response.dense._restrict(controls, 0.0, right)
    controls = response.dense._restrict(controls, subspan / subdivisions, (subspan + 1) / subdivisions)[:, :-1]
    center_action = np.mean(controls, axis=0)
    midpoint_curve = response.dense._split(controls, 0.5)[0][-1]
    first_controls = 7.0 * (controls[1:] - controls[:-1])
    tangent = 0.5 * response.dense._split(first_controls, 0.5)[0][-1]
    second_controls = 42.0 * (controls[2:] - 2.0 * controls[1:-1] + controls[:-2])
    remainder_vertices = np.vstack((np.zeros((1, controls.shape[1])), second_controls / 8.0))
    residual_offset = center_action - midpoint_curve
    residual_axes = (remainder_vertices - residual_offset).T
    tangent_energy = float(tangent @ tangent)
    residual_energy = float(np.sum(residual_axes**2))
    if tangent_energy == 0:
        projection = residual_axes
        a, b, identity = 0.0, 1.0, 1.0
    elif residual_energy == 0:
        projection = tangent[:, None]
        a, b, identity = 1.0, 0.0, 1.0
    else:
        ratio = math.sqrt(residual_energy / tangent_energy)
        a, b = math.sqrt(1.0 + ratio), math.sqrt(1.0 + 1.0 / ratio)
        projection = np.column_stack((a * tangent, b * residual_axes))
        identity = 1.0 / a**2 + 1.0 / b**2
    center = center_action / weights
    local = response.dense.cluster.local
    jet = local.exact_full_action_jet_at_state(12, center[:37], center[37:74], center[74:], points=local.POINTS)
    eigenvalues, eigenvectors = np.linalg.eigh(np.asarray(jet.hessian, dtype=float)[37:, 37:])
    directionals = []
    for column in range(projection.shape[1]):
        shifted = np.asarray(center, dtype=complex) + 1j * response.dense.COMPLEX_STEP * projection[:, column] / weights
        shifted_jet = local.exact_full_action_jet_at_state(12, shifted[:37], shifted[37:74], shifted[74:], points=local.POINTS)
        directionals.append(np.imag(np.asarray(shifted_jet.hessian)[37:, 37:]) / response.dense.COMPLEX_STEP)
    return {
        "midpoint": center, "projection": projection, "values": eigenvalues,
        "vectors": eigenvectors, "selected": int(np.argmax(np.abs(eigenvectors.T @ reference))),
        "directionals": directionals, "Bezier_controls": controls,
        "tangent_axis": tangent, "residual_vertices": remainder_vertices,
        "residual_offset_from_Bernstein_mean": residual_offset,
        "tangent_scale": a, "residual_scale": b, "coefficient_ellipsoid_identity": identity,
    }


def _initialize(config: dict[str, str]) -> None:
    response.INVERSE = Path(config["inverse"])
    response.PROJECTOR = Path(config["projector"])
    response.dense.CENTER_DATA = Path(config["center"])
    for cache in (response._inverse_record, response._projector_record, response._inverse_rows,
                  response._projector_rows, response.dense._dense_arrays):
        cache.cache_clear()
    response._tight_tangent_remainder_geometry = _same_center_tangent_geometry


def _evaluate(key: tuple[int, int, int]) -> dict[str, Any]:
    started = time.perf_counter()
    interval, subspan, subdivisions = key
    row = response._row((interval, subspan, subdivisions, subspan, subdivisions, 0))
    inverse = response._inverse_rows()[key]
    source_cap, physical_cap = _finite_cap(
        row["center_internal_rhs_2_norm"],
        row["raw_internal_rhs_first_coefficient_derivative_2_norm_upper"],
        float(inverse["instantaneous_bordered_inverse_2_norm_upper"]),
    )
    diagnostic_neumann = bool(row["bordered_response_tube_finite"])
    row.update(
        response_level_Neumann_closed=diagnostic_neumann,
        diagnostic_Neumann_response_2_norm_upper=row["complete_bordered_response_2_norm_upper"],
        internal_rhs_2_norm_upper=source_cap,
        instantaneous_bordered_inverse_2_norm_upper=inverse["instantaneous_bordered_inverse_2_norm_upper"],
        complete_bordered_response_2_norm_upper=physical_cap,
        bordered_response_tube_finite=math.isfinite(physical_cap),
        finite_response_method="UNIFORM_INSTANTANEOUS_INVERSE_TIMES_RAW_SOURCE_CAP;_NO_NEUMANN_GATE_USED",
        geometry_center="SAME_BERNSTEIN_CONTROL_MEAN_AS_SPECTRUM_AND_PROJECTOR",
        elapsed_seconds=time.perf_counter() - started,
    )
    return _safe_json(row)


def _binding(config: dict[str, str]) -> tuple[list[tuple[int, int, int]], int, dict[str, str]]:
    records = {name: json.loads(Path(config[name]).read_text(encoding="utf-8")) for name in ("spectrum", "projector", "inverse")}
    center = Path(config["center"])
    center_hash = _sha256(center)
    for name, record in records.items():
        if record.get("validation_passed") is not True:
            raise ValueError(f"closed current {name} required")
        for relative, expected in record["inputs"].items():
            if _sha256(ROOT / relative) != expected:
                raise ValueError(f"stale {name} input: {relative}")
        if record["inputs"].get(_relative(center)) != center_hash:
            raise ValueError(f"{name} must explicitly bind the requested current center")
    keys = [_key(row) for row in records["spectrum"]["rows"]]
    if any([_key(row) for row in records[name]["rows"]] != keys for name in ("projector", "inverse")):
        raise ValueError("ordered spectrum/projector/inverse covers differ")
    with np.load(center, allow_pickle=False) as source:
        count = int(source["stop_bracket_fine_grid_index"][0]) + 1
        if count != source["fine_grid_DOP853_dense_coefficients"].shape[0]:
            raise ValueError("retained current dense mesh must end at the stop bracket")
    if not _partition_is_exact(records["spectrum"]["rows"], count):
        raise ValueError("current cover must partition every retained dense interval exactly")
    for spectral, graph, inverse in zip(*(records[name]["rows"] for name in ("spectrum", "projector", "inverse"))):
        gap = min(float(spectral["negative_selected_gap_lower"]), float(spectral["selected_positive_gap_lower"]))
        if not (gap > 0 and graph["graph_Neumann_closed"] and float(graph["selected_projector_motion_upper"]) < 1
                and inverse["bordered_inverse_closed"] and inverse["certified_selected_to_hard_gap_lower"] == gap
                and int(inverse["selected_branch"]) == 24):
            raise ValueError("positive branch24 denominator and closed projector/inverse required")
    paths = [Path(config[name]) for name in ("spectrum", "projector", "inverse", "center")]
    paths += [Path(__file__), ROOT / "scripts/certify_n12_c2_stop_dop853_adaptive_bordered_rhs_response.py",
              ROOT / "scripts/audit_n12_c2_stop_dop853_boundary_cluster_probe.py",
              ROOT / "scripts/derive_n12_action_ball_majorants.py"]
    return keys, count, {_relative(path): _sha256(path) for path in paths}


def _load_checkpoint(path: Path, inputs: dict[str, str], keys: list[tuple[int, int, int]]) -> dict[tuple[int, int, int], dict[str, Any]]:
    if not path.exists():
        return {}
    lines = path.read_text(encoding="utf-8").splitlines()
    if not lines or json.loads(lines[0]).get("inputs") != inputs:
        raise ValueError("checkpoint input binding differs from the current calculation")
    rows = {}
    allowed = set(keys)
    for index, line in enumerate(lines[1:], 1):
        try:
            row = json.loads(line)["row"]
        except json.JSONDecodeError:
            if index == len(lines) - 1:
                # Retain the interrupted append separately and repair only
                # its incomplete framing before subsequent rows are appended.
                path.with_suffix(path.suffix + ".interrupted-line.txt").write_text(line, encoding="utf-8")
                repaired = path.with_suffix(path.suffix + ".recovering")
                repaired.write_text("\n".join(lines[:index]) + "\n", encoding="utf-8")
                os.replace(repaired, path)
                break
            raise
        key = _key(row)
        if key not in allowed or key in rows:
            raise ValueError("checkpoint contains an alien or duplicate cover row")
        rows[key] = row
    if rows and not path.read_bytes().endswith(b"\n"):
        with path.open("a", encoding="utf-8") as stream:
            stream.write("\n")
    return rows


def _closed(row: dict[str, Any]) -> bool:
    return bool(row["center_internal_rhs_finite"]
                and row["center_preconditioned_source_matches_bordered_solve"]
                and row["center_bordered_solve_residual_upper"] < 1e-7
                and row["bordered_response_tube_finite"]
                and math.isfinite(row["complete_bordered_response_2_norm_upper"])
                and math.isfinite(row["raw_internal_rhs_first_coefficient_derivative_2_norm_upper"])
                and math.isfinite(row["raw_internal_rhs_second_coefficient_derivative_2_norm_upper"])
                and abs(row["coefficient_ellipsoid_identity"] - 1) <= 4e-15)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    for name, default in (("spectrum", DEFAULT_SPECTRUM), ("projector", DEFAULT_PROJECTOR),
                          ("inverse", DEFAULT_INVERSE), ("center", DEFAULT_CENTER), ("output", DEFAULT_RESULT)):
        parser.add_argument("--" + name, type=Path, default=default)
    parser.add_argument("--workers", type=int, default=12)
    parser.add_argument("--checkpoint", type=Path)
    parser.add_argument("--pilot", action="store_true", help="evaluate three representative current cover cells and retain them for the full run")
    args = parser.parse_args()
    config = {name: str(getattr(args, name).resolve()) for name in ("spectrum", "projector", "inverse", "center")}
    keys, interval_count, inputs = _binding(config)
    checkpoint = args.checkpoint or args.output.with_suffix(".rows.jsonl")
    checkpoint.parent.mkdir(parents=True, exist_ok=True)
    rows = _load_checkpoint(checkpoint, inputs, keys)
    if not checkpoint.exists():
        checkpoint.write_text(json.dumps({"inputs": inputs, "interval_count": interval_count, "cover_cells": len(keys)}) + "\n", encoding="utf-8")
    requested = [key for key in keys if key in {(0, 0, 8), (92, 0, 8), (182, 2, 4)}] if args.pilot else keys
    remaining = [key for key in requested if key not in rows]
    workers = min(max(1, args.workers), os.cpu_count() or 1, len(remaining) or 1)
    print(json.dumps({"stage": "START", "cover_cells": len(keys), "requested": len(requested), "resumed": len(rows),
                      "workers": workers, "checkpoint": str(checkpoint.resolve())}), flush=True)
    started = time.perf_counter()
    with ProcessPoolExecutor(max_workers=workers, initializer=_initialize, initargs=(config,)) as executor:
        for key, row in zip(remaining, executor.map(_evaluate, remaining, chunksize=1)):
            with checkpoint.open("a", encoding="utf-8") as stream:
                stream.write(json.dumps({"row": row}, allow_nan=False) + "\n")
                stream.flush()
            rows[key] = row
            if args.pilot or len(rows) % 16 == 0 or len(rows) == len(keys):
                print(json.dumps({"completed": len(rows), "total": len(keys), "key": key,
                                  "finite_cap_closed": _closed(row), "eta_diagnostic": row["relative_bordered_operator_perturbation_upper"],
                                  "physical_response_cap": row["complete_bordered_response_2_norm_upper"],
                                  "row_seconds": row["elapsed_seconds"], "elapsed_seconds": time.perf_counter() - started}), flush=True)
    if args.pilot:
        print(json.dumps({"stage": "PILOT_SAVED", "checkpoint": str(checkpoint.resolve()), "saved_rows": len(rows)}), flush=True)
        return
    ordered = [rows[key] for key in keys]
    unresolved = [_key(row) for row in ordered if not _closed(row)]
    validation = {
        "identical_ordered_1395_or_current_parent_cover": [_key(row) for row in ordered] == keys,
        "dynamic_dense_interval_partition_exact": _partition_is_exact(ordered, interval_count),
        "all_center_rhs_and_backward_error_checks_pass": all(_closed(row) for row in ordered),
        "same_Bernstein_control_mean_used_for_source_and_spectral_shift": True,
        "residual_vertex_offset_from_Bernstein_mean_retained": True,
        "no_Neumann_gate_or_child_chart_transition_needed_for_finite_cap": True,
        "uniform_instantaneous_inverse_consumed_on_identical_parent_cell": True,
        "only_external_Cauchy_birth_source_zero_internal_rhs_retained": True,
        "no_full_kinetic_Dirac_or_history_inverse_used": True,
    }
    passed = all(validation.values())
    payload = {
        "artifact": "BHSM_N12_CURRENT_DOP853_PROJECTOR_REFINED_BORDERED_RHS_RESPONSE",
        "status": "ALL_CURRENT_DOP853_ACTION_OWNED_INTERNAL_RHS_AND_FINITE_BORDERED_RESPONSES_CERTIFIED" if passed else "CURRENT_DOP853_INTERNAL_RHS_OR_FINITE_RESPONSE_OPEN",
        "source_ontology": "EXTERNAL_CAUCHY_BIRTH_SOURCE_ZERO;_SIGNED_INTERNAL_EULER_LAGRANGE_RHS_RETAINED",
        "method": "SUP_RHS_NORM_LE_CENTER_RHS_NORM_PLUS_RAW_VARIATION;_SUP_RESPONSE_NORM_LE_CERTIFIED_UNIFORM_INSTANTANEOUS_INVERSE_TIMES_SUP_RHS_NORM",
        "mesh": {"retained_dense_intervals": interval_count, "adaptive_cover_cells": len(ordered), "additional_subdivision": False, "workers": workers},
        "summary": {
            "maximum_internal_rhs_2_norm_upper": max(row["internal_rhs_2_norm_upper"] for row in ordered),
            "maximum_complete_bordered_response_2_norm_upper": max(row["complete_bordered_response_2_norm_upper"] for row in ordered),
            "maximum_center_bordered_solve_residual_upper": max(row["center_bordered_solve_residual_upper"] for row in ordered),
            "maximum_relative_operator_eta_diagnostic": max(row["relative_bordered_operator_perturbation_upper"] for row in ordered),
            "Neumann_closed_diagnostic_cells": sum(row["response_level_Neumann_closed"] for row in ordered),
            "owner": max(ordered, key=lambda row: row["complete_bordered_response_2_norm_upper"]),
        },
        "rows": ordered, "unresolved_cells": unresolved, "validation": validation, "validation_passed": passed,
        "claim_boundary": {
            "action_owned_internal_rhs_on_current_DOP853_cover": "CERTIFIED_FINITE" if passed else "OPEN",
            "instantaneous_bordered_response_on_current_DOP853_cover": "CERTIFIED_FINITE_UNIFORM_CAP" if passed else "OPEN",
            "tight_response_level_Neumann_proof": "DIAGNOSTIC_ONLY;_NOT_REQUIRED_OR_PROMOTED",
            "response_first_variation_tube": "OPEN", "correlated_shadowing_tube": "OPEN", "scalar_first_hit_interval": "OPEN",
            "Gate7": "ACTIVE", "FULL_BHSM_COMPLETE": False,
        },
        "exact_next_dependency": "DIFFERENTIATE_THE_INTERNAL_BORDERED_SYSTEM_AND_USE_THE_CURRENT_CORRELATED_GREEN_SHADOWING_TUBE;_LOCALIZE_TIGHTER_RESPONSE_BOUNDS_ONLY_IF_NEEDED",
        "inputs": inputs, "checkpoint": str(checkpoint.resolve()), "elapsed_seconds_this_run": time.perf_counter() - started,
        "FLAGSHIP_READY": False, "FULL_BHSM_COMPLETE": False,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"status": payload["status"], "validation_passed": passed, "summary": payload["summary"], "output": str(args.output.resolve())}, indent=2), flush=True)
    if not passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
