"""Independently audit stored adaptive DOP853 spectrum/projector data.

This verifies provenance and data invariants, not the numerical Kato bounds,
interval rounding, an exact-flow shadowing theorem, or physical predictions.
No certificate generator is imported or executed.
"""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from fractions import Fraction
import hashlib
import json
import math
from pathlib import Path
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
BASE = Path("artifacts/flagship_integration")
COARSE = BASE / "BHSM_N12_C2_STOP_DOP853_BOUNDARY_CLUSTER_SPECTRUM.json"
SPECTRUM = BASE / "BHSM_N12_C2_STOP_DOP853_ADAPTIVE_BOUNDARY_CLUSTER_SPECTRUM.json"
PROJECTOR = BASE / "BHSM_N12_C2_STOP_DOP853_ADAPTIVE_SELECTED_PROJECTOR_GRAPH.json"
CENTER = BASE / "BHSM_N12_C2_STOP_HIGH_ORDER_QUARTER_STEP_RETAINED_RECONNAISSANCE.npz"
PROBE = Path("scripts/audit_n12_c2_stop_dop853_boundary_cluster_probe.py")
SPECTRUM_STATUS = "ALL_DOP853_STOP_PATH_ADAPTIVE_BOUNDARY_CLUSTER_DENOMINATORS_CERTIFIED"
PROJECTOR_STATUS = "ALL_DOP853_ADAPTIVE_STOP_PATH_SELECTED_PROJECTOR_GRAPHS_CERTIFIED"


class AuditError(ValueError):
    """A stored certificate fails an independently checked invariant."""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise AuditError(message)


def _integer(value: Any, label: str, minimum: int = 0) -> int:
    _require(type(value) is int and value >= minimum, f"{label}: integer >= {minimum} required")
    return value


def _number(value: Any, label: str, *, positive: bool = False, nonnegative: bool = False) -> float:
    _require(type(value) in (int, float), f"{label}: numeric value required")
    result = float(value)
    _require(math.isfinite(result), f"{label}: finite value required")
    if positive:
        _require(result > 0.0, f"{label}: strictly positive value required")
    if nonnegative:
        _require(result >= 0.0, f"{label}: nonnegative value required")
    return result


def normalized_sha256(path: Path) -> str:
    """Use the existing certificates' newline-normalized text hash convention."""
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def _relative(root: Path, path: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError as error:
        raise AuditError(f"input path lies outside audit root: {path}") from error


def verify_input_hashes(payload: dict[str, Any], root: Path, required: list[Path]) -> int:
    """Check every declared dependency and require the actual chain inputs."""
    inputs = payload.get("inputs")
    _require(isinstance(inputs, dict) and bool(inputs), "nonempty input hash map required")
    for path in required:
        relative = _relative(root, path)
        _require(relative in inputs, f"required input hash missing: {relative}")
    for relative, expected in inputs.items():
        _require(isinstance(relative, str), "input hash path must be text")
        path = root / relative
        _require(_relative(root, path) == relative, f"noncanonical input hash path: {relative}")
        _require(
            isinstance(expected, str) and len(expected) == 64
            and all(char in "0123456789abcdefABCDEF" for char in expected),
            f"invalid SHA256 for {relative}",
        )
        _require(path.is_file(), f"input file missing: {relative}")
        _require(normalized_sha256(path) == expected.upper(), f"stale input hash: {relative}")
    return len(inputs)


def center_interval_count(path: Path) -> int:
    """Read the retained stop bracket instead of trusting JSON mesh metadata."""
    with np.load(path, allow_pickle=False) as source:
        bracket = np.asarray(source["stop_bracket_fine_grid_index"])
        _require(bracket.size == 1 and bracket.dtype.kind in "iu", "NPZ stop bracket must be one integer")
        intervals = int(bracket.reshape(-1)[0]) + 1
        _require(intervals > 0, "NPZ retained dense interval count must be positive")
        stop = np.asarray(source["stop_dense_fraction"])
        _require(stop.size == 1, "NPZ stop fraction must be one value")
        stop_fraction = _number(float(stop.reshape(-1)[0]), "NPZ stop fraction", positive=True)
        _require(stop_fraction <= 1.0, "NPZ stop fraction exceeds its dense interval")
        for name, needed in (
            ("fine_grid_augmented_action_values", intervals + 1),
            ("fine_grid_DOP853_dense_coefficients", intervals),
            ("fine_grid_action_lengths", intervals + 1),
        ):
            array = np.asarray(source[name])
            _require(array.ndim >= 1 and array.shape[0] >= needed, f"NPZ {name}: retained mesh truncated")
    return intervals


def _dyadic_level(value: Any, label: str, maximum: int) -> int:
    level = _integer(value, label, 4)
    _require(level <= maximum and level & (level - 1) == 0, f"{label}: dyadic level 4..{maximum} required")
    return level


def _cell_key(row: dict[str, Any], intervals: int, maximum: int) -> tuple[int, int, int]:
    interval = _integer(row["interval"], "cell interval")
    subdivisions = _dyadic_level(row["subdivisions"], "cell subdivisions", maximum)
    subspan = _integer(row["subspan"], "cell subspan")
    _require(interval < intervals and subspan < subdivisions, "cell index lies outside retained mesh")
    return interval, subspan, subdivisions


def _spectral_row(row: dict[str, Any], *, closed: bool) -> None:
    _require(type(row["selected_branch"]) is int and row["selected_branch"] == 24, "selected branch must be 24")
    _require(type(row["Bernstein_control_count"]) is int and row["Bernstein_control_count"] == 8, "eight Bernstein controls required")
    for name in (
        "negative_cluster_shift_upper", "selected_line_shift_upper", "positive_cluster_shift_upper",
        "maximum_projection_column_norm",
    ):
        _number(row[name], name, nonnegative=True)
    _number(row["minimum_external_center_gap"], "minimum_external_center_gap", positive=True)
    negative = _number(row["negative_selected_gap_lower"], "negative_selected_gap_lower", positive=closed)
    positive = _number(row["selected_positive_gap_lower"], "selected_positive_gap_lower", positive=closed)
    bootstrap = row["all_three_quarter_gap_bootstraps_closed"]
    verdict = row["boundary_cluster_certificate_closed"]
    _require(type(bootstrap) is bool and type(verdict) is bool, "spectral closure flags must be booleans")
    _require(verdict == (bootstrap and negative > 0.0 and positive > 0.0), "spectral closure flag contradicts margins/bootstrap")
    if closed:
        _require(bootstrap and verdict, "every adaptive cell must close the unchanged quarter-gap bootstrap")


def _claim_flags(payload: dict[str, Any]) -> None:
    _require(payload.get("FULL_BHSM_COMPLETE") is False, "FULL_BHSM_COMPLETE must remain false")
    _require(payload.get("FLAGSHIP_READY") is False, "FLAGSHIP_READY must remain false")
    boundary = payload["claim_boundary"]
    _require(boundary.get("FULL_BHSM_COMPLETE") is False, "claim boundary cannot promote BHSM completion")
    _require(boundary.get("correlated_shadowing_tube") == "OPEN", "stored-path audit cannot promote shadowing")
    _require(boundary.get("Gate7") == "ACTIVE", "stored-path audit cannot close Gate7")


def _validation_flags(payload: dict[str, Any], required: tuple[str, ...]) -> None:
    _require(payload.get("validation_passed") is True, "validation_passed must be true")
    validation = payload["validation"]
    _require(isinstance(validation, dict) and bool(validation), "validation map required")
    _require(all(value is True for value in validation.values()), "every declared validation must be true")
    _require(all(validation.get(name) is True for name in required), "required validation flags absent or false")


def _spectrum_summaries(payload: dict[str, Any], rows: list[dict[str, Any]]) -> None:
    summary = payload["summary"]
    expected = {
        "minimum_selected_line_boundary_gap_lower": min(
            min(row["negative_selected_gap_lower"], row["selected_positive_gap_lower"]) for row in rows
        ),
        "minimum_negative_selected_gap_lower": min(row["negative_selected_gap_lower"] for row in rows),
        "minimum_selected_positive_gap_lower": min(row["selected_positive_gap_lower"] for row in rows),
        "maximum_selected_line_shift_upper": max(row["selected_line_shift_upper"] for row in rows),
        "maximum_negative_cluster_shift_upper": max(row["negative_cluster_shift_upper"] for row in rows),
        "maximum_positive_cluster_shift_upper": max(row["positive_cluster_shift_upper"] for row in rows),
        "maximum_Bernstein_projection_column_norm": max(row["maximum_projection_column_norm"] for row in rows),
        "minimum_margin_owner": min(rows, key=lambda row: min(
            row["negative_selected_gap_lower"], row["selected_positive_gap_lower"]
        )),
    }
    for name, value in expected.items():
        _require(summary.get(name) == value, f"spectrum summary mismatch: {name}")


def audit_spectrum_payloads(
    coarse: dict[str, Any], spectrum: dict[str, Any], intervals: int,
) -> dict[str, Any]:
    """Reconstruct cover, refinement ancestry, closure, and aggregate metadata."""
    _require(spectrum.get("status") == SPECTRUM_STATUS, "certified adaptive spectrum status required")
    _require(spectrum.get("unresolved_cells") == [], "adaptive spectrum has unresolved cells")
    _claim_flags(spectrum)
    _validation_flags(spectrum, (
        "failed_cells_replaced_only_by_exact_dyadic_de_Casteljau_children",
        "adaptive_cells_partition_every_retained_dense_interval_exactly",
        "every_accepted_cell_closes_all_three_quarter_gap_bootstraps",
        "both_selected_line_boundary_margins_positive_everywhere",
        "selected_branch_24_everywhere", "all_cells_use_eight_degree_seven_Bernstein_controls",
        "no_failed_cell_at_maximum_refinement", "quarter_gap_bootstrap_not_weakened",
        "same_stored_DOP853_polynomial_as_defect_and_first_hit", "no_cubic_Hermite_surrogate_inserted",
        "coarse_replay_consumed_without_reinterpretation",
    ))
    mesh = spectrum["mesh"]
    maximum = _integer(mesh["maximum_subdivisions_per_interval"], "maximum subdivisions", 4)
    _dyadic_level(maximum, "maximum subdivisions", maximum)
    _require(mesh["dense_intervals"] == intervals, "adaptive mesh disagrees with current NPZ stop mesh")
    _require(mesh["coarse_subspans_per_interval"] == 4, "canonical four-cell coarse mesh required")
    coarse_mesh = coarse["mesh"]
    _require(coarse_mesh["dense_intervals"] == intervals, "coarse mesh disagrees with current NPZ stop mesh")
    _require(coarse_mesh["subspans_per_dense_interval"] == 4, "coarse mesh must use four subspans")
    coarse_rows = coarse["rows"]
    _require(isinstance(coarse_rows, list) and len(coarse_rows) == 4 * intervals, "coarse row count mismatch")
    _require(coarse_mesh["total_subspans"] == len(coarse_rows), "coarse total_subspans mismatch")
    parents = {}
    failed_parents = set()
    for ordinal, source in enumerate(coarse_rows):
        _require(type(source["interval"]) is int and type(source["subspan"]) is int, "coarse indices must be integers")
        key = source["interval"], source["subspan"]
        _require(key == (ordinal // 4, ordinal % 4), "coarse rows must consume every canonical cell once in order")
        _spectral_row(source, closed=False)
        row = dict(source, subdivisions=4, dyadic_start=f"{key[1]}/4", dyadic_end=f"{key[1] + 1}/4")
        parents[key] = row
        if not source["boundary_cluster_certificate_closed"]:
            failed_parents.add(key)
    _spectrum_summaries(coarse, coarse_rows)
    rows = spectrum["rows"]
    _require(isinstance(rows, list) and bool(rows), "nonempty adaptive cover required")
    spans = defaultdict(list)
    observed_keys = []
    descendant_counts: Counter[tuple[int, int, int]] = Counter()
    for row in rows:
        interval, subspan, subdivisions = _cell_key(row, intervals, maximum)
        start, end = Fraction(subspan, subdivisions), Fraction(subspan + 1, subdivisions)
        _require(row["dyadic_start"] == f"{subspan}/{subdivisions}" and row["dyadic_end"] == f"{subspan + 1}/{subdivisions}", "dyadic endpoint metadata mismatch")
        _spectral_row(row, closed=True)
        parent = interval, (4 * subspan) // subdivisions
        if subdivisions == 4:
            _require(parent not in failed_parents, "failed coarse parent reused without refinement")
            _require(row == parents[parent], "accepted coarse row changed during adaptive reuse")
        else:
            _require(parent in failed_parents, "refinement introduced below an accepted coarse parent")
            for level in range(3, subdivisions.bit_length()):
                denominator = 1 << level
                ancestor = interval, subspan // (subdivisions // denominator), denominator
                descendant_counts[ancestor] += 1
        observed_keys.append((interval, start))
        spans[interval].append((start, end))
    _require(observed_keys == sorted(observed_keys), "adaptive cover rows must be in interval/span order")
    _require(set(spans) == set(range(intervals)), "adaptive cover missing retained interval")
    for interval, cells in spans.items():
        ordered = sorted(cells)
        _require(ordered[0][0] == 0 and ordered[-1][1] == 1, f"interval {interval}: cover has an endpoint hole")
        _require(all(left[1] == right[0] for left, right in zip(ordered, ordered[1:])), f"interval {interval}: cover has overlap or a hole")
    accepted_counts = dict(sorted(Counter(str(row["subdivisions"]) for row in rows).items(), key=lambda item: int(item[0])))
    # Every non-leaf ancestor of a final leaf was audited once; count their
    # distinct dyadic cells, including accepted leaves at each refinement level.
    refinement_counts = {"4": len(coarse_rows)}
    for denominator in sorted({key[2] for key in descendant_counts}):
        refinement_counts[str(denominator)] = sum(key[2] == denominator for key in descendant_counts)
    expected_mesh = {
        "coarse_cells_audited": len(coarse_rows), "coarse_cells_replaced": len(failed_parents),
        "accepted_cover_cell_count": len(rows), "accepted_cover_cells_by_subdivisions": accepted_counts,
        "refinement_cells_audited_by_subdivisions": refinement_counts,
    }
    for name, value in expected_mesh.items():
        _require(mesh.get(name) == value, f"adaptive mesh/count mismatch: {name}")
    _spectrum_summaries(spectrum, rows)
    _require(spectrum["claim_boundary"].get("selected_line_on_stored_DOP853_stop_path") == "CERTIFIED_SIMPLE", "simple stored-path selected-line claim required")
    return {"dense_intervals": intervals, **expected_mesh}


def audit_projector_payload(spectrum: dict[str, Any], projector: dict[str, Any]) -> dict[str, Any]:
    """Check cell alignment and stored graph arithmetic without recomputing it."""
    _require(projector.get("status") == PROJECTOR_STATUS, "certified projector status required")
    _claim_flags(projector)
    _validation_flags(projector, (
        "every_adaptive_spectrum_cell_consumed_once_in_order", "branch_24_selected_everywhere",
        "every_certified_gap_strictly_positive", "all_distance_band_graph_Neumann_bounds_below_one",
        "same_DOP853_Bernstein_cover_as_spectrum", "no_cubic_Hermite_surrogate_inserted",
    ))
    spectral_rows, rows = spectrum["rows"], projector["rows"]
    _require(isinstance(rows, list) and len(rows) == len(spectral_rows), "projector/spectrum cover row count mismatch")
    _require(projector["mesh"]["adaptive_cover_cells"] == len(rows), "projector cover metadata mismatch")
    for spectral, row in zip(spectral_rows, rows):
        _require(tuple(row[name] for name in ("interval", "subspan", "subdivisions")) == tuple(spectral[name] for name in ("interval", "subspan", "subdivisions")), "projector cover differs from ordered spectrum cover")
        _require(type(row["selected_branch"]) is int and row["selected_branch"] == 24, "projector selected branch must be 24")
        gap = min(spectral["negative_selected_gap_lower"], spectral["selected_positive_gap_lower"])
        _require(_number(row["certified_global_gap_lower"], "projector certified gap", positive=True) == gap, "projector consumed spectrum gap mismatch")
        _require(row["selected_line_shift_upper"] == spectral["selected_line_shift_upper"], "projector selected shift differs from spectrum")
        motion = _number(row["selected_projector_motion_upper"], "projector motion", nonnegative=True)
        derivative = _number(row["selected_graph_derivative_l2_upper"], "projector derivative", nonnegative=True)
        _require(motion == derivative, "projector motion/derivative mismatch")
        verdict = row["graph_Neumann_closed"]
        _require(type(verdict) is bool and verdict == (motion < 1.0) and verdict, "projector Neumann verdict contradicts motion or fails closure")
        groups = row["groups"]
        _require(isinstance(groups, list) and bool(groups), "projector distance groups required")
        _require(type(row["spectral_distance_bands"]) is int and row["spectral_distance_bands"] == len(groups), "projector distance-band count mismatch")
        for group in groups:
            ordered_gap = _number(group["ordered_Weyl_gap_lower"], "ordered Weyl gap")
            consumed = _number(group["consumed_gap_lower"], "distance-band consumed gap", positive=True)
            _require(consumed == max(gap, ordered_gap), "distance-band consumed gap mismatch")
            for name in ("minimum_center_distance", "center_D3_coupling_l2_norm", "D4_coupling_change_upper", "coupling_numerator_upper", "selected_graph_derivative_upper"):
                _number(group[name], name, nonnegative=True)
    summary = projector["summary"]
    expected = {
        "maximum_selected_graph_derivative_l2_upper": max(row["selected_graph_derivative_l2_upper"] for row in rows),
        "maximum_selected_projector_motion_upper": max(row["selected_projector_motion_upper"] for row in rows),
        "minimum_consumed_gap_lower": min(row["certified_global_gap_lower"] for row in rows),
        "maximum_spectral_distance_bands": max(row["spectral_distance_bands"] for row in rows),
        "owner": max(rows, key=lambda row: row["selected_projector_motion_upper"]), "Neumann_factor": 2.0,
    }
    for name, value in expected.items():
        _require(summary.get(name) == value, f"projector summary mismatch: {name}")
    _require(projector["claim_boundary"].get("selected_projector_graph_on_stored_DOP853_stop_path") == "CERTIFIED", "stored-path projector claim required")
    return {"adaptive_cover_cells": len(rows), **{key: value for key, value in expected.items() if key != "owner"}}


def verify_chain(
    root: Path = ROOT, coarse_path: Path = COARSE, spectrum_path: Path = SPECTRUM,
    center_path: Path = CENTER, projector_path: Path | None = None,
) -> dict[str, Any]:
    """Return a machine-readable, fail-closed audit report for this data chain."""
    root = root.resolve()
    paths = {"coarse": coarse_path, "spectrum": spectrum_path, "center": center_path}
    if projector_path is not None:
        paths["projector"] = projector_path
    paths = {name: path.resolve() if path.is_absolute() else root / path for name, path in paths.items()}
    report: dict[str, Any] = {
        "artifact": "BHSM_N12_C2_STOP_DOP853_ADAPTIVE_CHAIN_DATA_AUDIT",
        "mode": "spectrum_and_projector" if projector_path is not None else "spectrum_only",
        "validation_passed": False, "checks": {}, "errors": [],
        "claim_boundary": {
            "provenance_and_stored_data_invariants_only": True,
            "numerical_Kato_bounds_recomputed": False, "directed_interval_arithmetic_verified": False,
            "exact_flow_shadowing_verified": False, "FULL_BHSM_COMPLETE": False,
        },
    }
    try:
        report_bytes = {name: path.read_bytes() for name, path in paths.items() if name != "center"}
        payloads = {name: json.loads(data) for name, data in report_bytes.items()}
        report["audited_report_files_SHA256"] = {
            _relative(root, paths[name]): hashlib.sha256(data).hexdigest().upper()
            for name, data in report_bytes.items()
        }
        for name, required in (
            ("coarse", [paths["center"], root / PROBE]),
            ("spectrum", [paths["coarse"], paths["center"], root / PROBE]),
        ):
            verify_input_hashes(payloads[name], root, required)
            report["checks"][f"{name}_input_hashes_current"] = True
        intervals = center_interval_count(paths["center"])
        report["checks"]["current_NPZ_stop_mesh_read"] = True
        report["spectrum"] = audit_spectrum_payloads(payloads["coarse"], payloads["spectrum"], intervals)
        report["checks"]["spectrum_cover_closure_ancestry_and_summaries"] = True
        if projector_path is not None:
            verify_input_hashes(payloads["projector"], root, [paths["spectrum"], paths["center"], root / PROBE])
            report["checks"]["projector_input_hashes_current"] = True
            report["projector"] = audit_projector_payload(payloads["spectrum"], payloads["projector"])
            report["checks"]["projector_cover_gaps_motion_and_summaries"] = True
        report["validation_passed"] = True
    except (AuditError, OSError, ValueError, TypeError, KeyError, IndexError) as error:
        report["errors"].append(f"{type(error).__name__}: {error}")
    report["status"] = "ADAPTIVE_CHAIN_DATA_INVARIANTS_VERIFIED" if report["validation_passed"] else "ADAPTIVE_CHAIN_DATA_AUDIT_FAILED"
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--coarse", type=Path, default=COARSE)
    parser.add_argument("--spectrum", type=Path, default=SPECTRUM)
    parser.add_argument("--center", type=Path, default=CENTER)
    parser.add_argument("--projector", type=Path, nargs="?", const=PROJECTOR, default=None)
    parser.add_argument("--output", type=Path, help="optional JSON report file; stdout is always emitted")
    arguments = parser.parse_args()
    report = verify_chain(arguments.root, arguments.coarse, arguments.spectrum, arguments.center, arguments.projector)
    encoded = json.dumps(report, indent=2, sort_keys=True, allow_nan=False) + "\n"
    if arguments.output is not None:
        arguments.output.write_text(encoded, encoding="utf-8", newline="\n")
    print(encoded, end="")
    raise SystemExit(0 if report["validation_passed"] else 1)


if __name__ == "__main__":
    main()
