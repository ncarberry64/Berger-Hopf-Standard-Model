"""Refine only open joint spectrum/projector cells of the current stop path.

Original artifacts are read-only inputs. All unaffected rows are reused
unchanged; separate PROJECTOR_REFINED artifacts contain the resulting cover.
"""

from __future__ import annotations

import argparse
from collections import Counter
from concurrent.futures import ProcessPoolExecutor
from copy import deepcopy
from fractions import Fraction
import json
import math
import os
from pathlib import Path
import sys
from typing import Any


for _thread_variable in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ[_thread_variable] = "1"

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import certify_n12_c2_stop_dop853_adaptive_boundary_cluster_spectrum as spectral  # noqa: E402
import certify_n12_c2_stop_dop853_adaptive_selected_projector_graph as graph  # noqa: E402
import certify_n12_c2_stop_dop853_adaptive_bordered_hard_inverse as bordered  # noqa: E402
import verify_n12_c2_stop_dop853_adaptive_chain as verify  # noqa: E402


BASE = ROOT / "artifacts/flagship_integration"
SOURCE_SPECTRUM = BASE / "BHSM_N12_C2_STOP_DOP853_ADAPTIVE_BOUNDARY_CLUSTER_SPECTRUM.json"
SOURCE_PROJECTOR = BASE / "BHSM_N12_C2_STOP_DOP853_ADAPTIVE_SELECTED_PROJECTOR_GRAPH.json"
REFINED_SPECTRUM = BASE / "BHSM_N12_C2_STOP_DOP853_PROJECTOR_REFINED_BOUNDARY_CLUSTER_SPECTRUM.json"
REFINED_PROJECTOR = BASE / "BHSM_N12_C2_STOP_DOP853_PROJECTOR_REFINED_SELECTED_PROJECTOR_GRAPH.json"
REFINED_INVERSE = BASE / "BHSM_N12_C2_STOP_DOP853_PROJECTOR_REFINED_BORDERED_HARD_INVERSE.json"
NEXT_RHS = "ASSEMBLE_THE_ACTION_OWNED_INTERNAL_BORDERED_RIGHT_HAND_SIDE_ON_THE_IDENTICAL_PROJECTOR_REFINED_DOP853_ADAPTIVE_COVER"
NEXT_REFINEMENT = "REFINE_ONLY_THE_REPORTED_JOINT_SPECTRUM_PROJECTOR_FAILURES"


def _key(row: dict[str, Any]) -> tuple[int, int, int]:
    return tuple(int(row[name]) for name in ("interval", "subspan", "subdivisions"))


def _sort_key(pair: tuple[dict[str, Any], dict[str, Any]]) -> tuple[int, Fraction]:
    row = pair[0]
    return int(row["interval"]), Fraction(int(row["subspan"]), int(row["subdivisions"]))


def _joint_closed(pair: tuple[dict[str, Any], dict[str, Any]]) -> bool:
    return pair[0]["boundary_cluster_certificate_closed"] and pair[1]["graph_Neumann_closed"]


def _child(task: tuple[int, int, int]) -> tuple[dict[str, Any], dict[str, Any]]:
    row = spectral._compact(spectral._task(task), task[2])
    # The projector's existing numerical kernel reads its per-cell spectral
    # denominator from this cache. Insert only this exact child's new row.
    graph._spectrum_rows()[task] = row
    projector = graph._projector_row(task)
    return row, projector


def _hashes(paths: list[Path]) -> dict[str, str]:
    return {path.resolve().relative_to(ROOT).as_posix(): verify.normalized_sha256(path) for path in paths}


def _spectral_summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "minimum_selected_line_boundary_gap_lower": min(min(row["negative_selected_gap_lower"], row["selected_positive_gap_lower"]) for row in rows),
        "minimum_negative_selected_gap_lower": min(row["negative_selected_gap_lower"] for row in rows),
        "minimum_selected_positive_gap_lower": min(row["selected_positive_gap_lower"] for row in rows),
        "maximum_selected_line_shift_upper": max(row["selected_line_shift_upper"] for row in rows),
        "maximum_negative_cluster_shift_upper": max(row["negative_cluster_shift_upper"] for row in rows),
        "maximum_positive_cluster_shift_upper": max(row["positive_cluster_shift_upper"] for row in rows),
        "maximum_Bernstein_projection_column_norm": max(row["maximum_projection_column_norm"] for row in rows),
        "minimum_margin_owner": min(rows, key=lambda row: min(row["negative_selected_gap_lower"], row["selected_positive_gap_lower"])),
    }


def _graph_summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "maximum_selected_graph_derivative_l2_upper": max(row["selected_graph_derivative_l2_upper"] for row in rows),
        "maximum_selected_projector_motion_upper": max(row["selected_projector_motion_upper"] for row in rows),
        "minimum_consumed_gap_lower": min(row["certified_global_gap_lower"] for row in rows),
        "maximum_spectral_distance_bands": max(row["spectral_distance_bands"] for row in rows),
        "owner": max(rows, key=lambda row: row["selected_projector_motion_upper"]),
        "Neumann_factor": graph.NEUMANN_FACTOR,
    }


def _validate_pair(pair: tuple[dict[str, Any], dict[str, Any]], *, require_closed: bool) -> None:
    row, projector = pair
    verify._spectral_row(row, closed=require_closed)
    if _key(row) != _key(projector) or projector["selected_branch"] != 24:
        raise RuntimeError("spectrum/projector cell pairing or branch mismatch")
    gap = min(row["negative_selected_gap_lower"], row["selected_positive_gap_lower"])
    if projector["certified_global_gap_lower"] != gap or projector["selected_line_shift_upper"] != row["selected_line_shift_upper"]:
        raise RuntimeError("projector consumed a different spectral gap/shift")
    motion = float(projector["selected_projector_motion_upper"])
    if not math.isfinite(motion) or motion < 0.0 or motion != projector["selected_graph_derivative_l2_upper"]:
        raise RuntimeError("projector motion must be finite, nonnegative and match derivative")
    if projector["graph_Neumann_closed"] is not (motion < 1.0):
        raise RuntimeError("projector Neumann verdict contradicts motion")
    if require_closed and not _joint_closed(pair):
        raise RuntimeError("joint cell is open")
    for group in projector["groups"]:
        if group["consumed_gap_lower"] != max(gap, group["ordered_Weyl_gap_lower"]):
            raise RuntimeError("distance-band gap does not match its child spectrum")


def _write(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8", newline="\n")


def run(workers: int = 4, maximum: int = 32) -> dict[str, Any]:
    if maximum < 4 or maximum & (maximum - 1):
        raise ValueError("maximum subdivisions must be a dyadic integer >= 4")
    workers = min(max(1, workers), os.cpu_count() or 1)
    source_spectrum = json.loads(SOURCE_SPECTRUM.read_text(encoding="utf-8"))
    source_projector = json.loads(SOURCE_PROJECTOR.read_text(encoding="utf-8"))
    source_hashes = _hashes([SOURCE_SPECTRUM, SOURCE_PROJECTOR, spectral.dense.CENTER_DATA])
    coarse = json.loads(spectral.COARSE.read_text(encoding="utf-8"))
    verify.verify_input_hashes(coarse, ROOT, [spectral.dense.CENTER_DATA, ROOT / verify.PROBE])
    verify.verify_input_hashes(source_spectrum, ROOT, [spectral.COARSE, spectral.dense.CENTER_DATA, ROOT / verify.PROBE])
    verify.verify_input_hashes(source_projector, ROOT, [SOURCE_SPECTRUM, spectral.dense.CENTER_DATA, ROOT / verify.PROBE])
    intervals = verify.center_interval_count(spectral.dense.CENTER_DATA)
    verify.audit_spectrum_payloads(coarse, source_spectrum, intervals)
    if len(source_spectrum["rows"]) != len(source_projector["rows"]):
        raise RuntimeError("source spectrum/projector cover size mismatch")
    pairs = list(zip(source_spectrum["rows"], source_projector["rows"]))
    for pair in pairs:
        _validate_pair(pair, require_closed=False)
    if source_projector["summary"] != _graph_summary(source_projector["rows"]):
        raise RuntimeError("source projector summary mismatch")
    failed = [pair for pair in pairs if not _joint_closed(pair)]
    initial_failed_keys = {_key(pair[0]) for pair in failed}
    accepted = [pair for pair in pairs if _joint_closed(pair)]
    replaced_keys = []
    additional_counts: Counter[str] = Counter()
    while failed:
        eligible = [pair for pair in failed if _key(pair[0])[2] < maximum]
        at_maximum = [pair for pair in failed if _key(pair[0])[2] >= maximum]
        if not eligible:
            break
        tasks = []
        for pair in eligible:
            interval, subspan, subdivisions = _key(pair[0])
            replaced_keys.append([interval, subspan, subdivisions])
            tasks.extend(((interval, 2 * subspan, 2 * subdivisions), (interval, 2 * subspan + 1, 2 * subdivisions)))
        children = []
        with ProcessPoolExecutor(max_workers=workers) as executor:
            for task, pair in zip(tasks, executor.map(_child, tasks, chunksize=1)):
                _validate_pair(pair, require_closed=False)
                additional_counts[str(task[2])] += 1
                children.append(pair)
                print(json.dumps({"child": list(task), "spectral_closed": pair[0]["boundary_cluster_certificate_closed"], "projector_motion": pair[1]["selected_projector_motion_upper"], "joint_closed": _joint_closed(pair)}), flush=True)
        accepted.extend(pair for pair in children if _joint_closed(pair))
        failed = at_maximum + [pair for pair in children if not _joint_closed(pair)]
    cover = sorted(accepted + failed, key=_sort_key)
    spectral_rows, graph_rows = [pair[0] for pair in cover], [pair[1] for pair in cover]
    if not spectral._partition_is_exact(spectral_rows, intervals):
        raise RuntimeError("refined cover is not an exact Fraction partition")
    source_pairs = {_key(pair[0]): pair for pair in pairs}
    reused = [pair for pair in cover if _key(pair[0]) in source_pairs]
    if any(pair != source_pairs[_key(pair[0])] for pair in reused):
        raise RuntimeError("an unaffected source row changed")
    if {_key(pair[0]) for pair in reused} != set(source_pairs) - initial_failed_keys:
        raise RuntimeError("refinement changed cells outside the initially failed joint cover")
    if _hashes([SOURCE_SPECTRUM, SOURCE_PROJECTOR, spectral.dense.CENTER_DATA]) != source_hashes:
        raise RuntimeError("source input changed while refinement was running")
    spectral_closed = all(row["boundary_cluster_certificate_closed"] for row in spectral_rows)
    joint_closed = not failed
    metadata = {
        "source_spectrum_coarse_cells_replaced": source_spectrum["mesh"]["coarse_cells_replaced"],
        "source_spectrum_cover_cells": len(pairs), "unchanged_source_cells_reused": len(reused),
        "initial_projector_directed_source_cells_replaced": len(initial_failed_keys),
        "projector_directed_parent_cells_replaced_total": len(replaced_keys),
        "projector_directed_replaced_parent_keys": replaced_keys,
        "additional_children_audited_by_subdivisions": dict(additional_counts),
        "refinement_reason": "JOINT_SPECTRAL_BOOTSTRAP_OR_PROJECTOR_NEUMANN_FAILURE_ONLY",
    }
    validation = {
        "current_input_hashes_and_NPZ_stop_mesh_match": True,
        "unaffected_source_spectrum_and_projector_rows_reused_unchanged": True,
        "only_failed_joint_cells_replaced_by_exact_dyadic_children": True,
        "adaptive_cover_is_exact_Fraction_partition": True,
        "every_spectral_row_has_positive_gaps_and_unchanged_bootstraps": spectral_closed,
        "spectrum_projector_pairing_and_consumed_gaps_match": True,
        "every_projector_Neumann_motion_is_finite_and_below_one": joint_closed,
        "same_retained_DOP853_center_without_new_trajectory": True,
    }
    refined_spectrum = deepcopy(source_spectrum)
    refined_spectrum["artifact"] = "BHSM_N12_C2_STOP_DOP853_PROJECTOR_REFINED_BOUNDARY_CLUSTER_SPECTRUM"
    refined_spectrum["method"] += "_PLUS_TARGETED_PROJECTOR_DIRECTED_DYADIC_REFINEMENT"
    refined_spectrum["rows"] = spectral_rows
    refined_spectrum["summary"] = _spectral_summary(spectral_rows)
    refined_spectrum["refinement"] = metadata
    refined_spectrum["unresolved_cells"] = [pair[0] for pair in failed if not pair[0]["boundary_cluster_certificate_closed"]]
    refined_spectrum["validation"].pop("failed_cells_replaced_only_by_exact_dyadic_de_Casteljau_children", None)
    refined_spectrum["validation"].update({key: value for key, value in validation.items() if key != "every_projector_Neumann_motion_is_finite_and_below_one"})
    refined_spectrum["validation_passed"] = spectral_closed
    refined_spectrum["status"] = verify.SPECTRUM_STATUS if spectral_closed else "DOP853_STOP_PATH_ADAPTIVE_REFINEMENT_REQUIRED"
    refined_spectrum["exact_next_dependency"] = NEXT_RHS if joint_closed else NEXT_REFINEMENT
    refined_spectrum["claim_boundary"]["selected_line_on_stored_DOP853_stop_path"] = "CERTIFIED_SIMPLE" if spectral_closed else "OPEN"
    refined_spectrum["mesh"].update({
        "maximum_subdivisions_per_interval": maximum,
        "coarse_cells_replaced": 4 * intervals - sum(row["subdivisions"] == 4 for row in spectral_rows),
        "accepted_cover_cells_by_subdivisions": dict(Counter(str(row["subdivisions"]) for row in spectral_rows)),
        "accepted_cover_cell_count": len(spectral_rows), "workers": workers,
        "refinement_cells_audited_by_subdivisions": dict(Counter(source_spectrum["mesh"]["refinement_cells_audited_by_subdivisions"]) + additional_counts),
    })
    refined_spectrum["inputs"] = {**source_spectrum["inputs"], **source_hashes, **_hashes([Path(__file__)])}
    _write(REFINED_SPECTRUM, refined_spectrum)
    refined_projector = deepcopy(source_projector)
    refined_projector.update({
        "artifact": "BHSM_N12_C2_STOP_DOP853_PROJECTOR_REFINED_SELECTED_PROJECTOR_GRAPH",
        "status": verify.PROJECTOR_STATUS if joint_closed else "DOP853_ADAPTIVE_STOP_PATH_SELECTED_PROJECTOR_GRAPH_OPEN",
        "validation_passed": joint_closed, "rows": graph_rows, "summary": _graph_summary(graph_rows),
        "refinement": metadata, "unresolved_cells": [pair[1] for pair in failed],
        "exact_next_dependency": NEXT_RHS if joint_closed else NEXT_REFINEMENT,
    })
    refined_projector["mesh"] = {"adaptive_cover_cells": len(graph_rows), "workers": workers}
    refined_projector["validation"].update(validation)
    refined_projector["validation"]["all_distance_band_graph_Neumann_bounds_below_one"] = joint_closed
    refined_projector["claim_boundary"]["selected_projector_graph_on_stored_DOP853_stop_path"] = "CERTIFIED" if joint_closed else "OPEN"
    refined_projector["inputs"] = {**source_hashes, **_hashes([REFINED_SPECTRUM, ROOT / verify.PROBE, Path(__file__)])}
    _write(REFINED_PROJECTOR, refined_projector)
    result = {"joint_cover_closed": joint_closed, "refinement": metadata, "spectrum_summary": refined_spectrum["summary"], "projector_summary": refined_projector["summary"], "outputs": [str(REFINED_SPECTRUM), str(REFINED_PROJECTOR)]}
    if joint_closed:
        for pair in cover:
            _validate_pair(pair, require_closed=True)
        bordered.SPECTRUM, bordered.PROJECTOR, bordered.RESULT = REFINED_SPECTRUM, REFINED_PROJECTOR, REFINED_INVERSE
        inverse = bordered.build_payload()
        inverse["artifact"] = "BHSM_N12_C2_STOP_DOP853_PROJECTOR_REFINED_BORDERED_HARD_INVERSE"
        inverse["refinement"] = metadata
        inverse["exact_next_dependency"] = NEXT_RHS
        inverse["inputs"].update(_hashes([Path(__file__), spectral.dense.CENTER_DATA]))
        _write(REFINED_INVERSE, inverse)
        result.update({"inverse_status": inverse["status"], "inverse_validation_passed": inverse["validation_passed"], "inverse_summary": inverse["summary"]})
        result["outputs"].append(str(REFINED_INVERSE))
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--maximum-subdivisions", type=int, default=32)
    arguments = parser.parse_args()
    result = run(arguments.workers, arguments.maximum_subdivisions)
    print(json.dumps(result, indent=2, sort_keys=True, allow_nan=False))
    raise SystemExit(0 if result["joint_cover_closed"] else 1)


if __name__ == "__main__":
    main()
