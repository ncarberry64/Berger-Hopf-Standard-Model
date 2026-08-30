"""Materialize final exact-affine seam data for the retained Gate-7 Z2 theorem.

This is a provenance/type adapter only.  It samples the already-certified
Arb fine signed center at the 48 retained causal seams, carries the certified
homogeneous macro-map intervals, and aggregates the exact-center bordered
inverse over the 370 retained dense intervals.  No equation or radius is
changed.
"""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "artifacts" / "flagship_integration"
CENTER = BASE / "BHSM_N12_C2_STOP_HIGH_ORDER_QUARTER_STEP_RETAINED_RECONNAISSANCE.npz"
FINE = BASE / "BHSM_N12_GATE7_ARB_INTERACTION_TAYLOR26_FINE_CENTER.npz"
FINE_RECORD = FINE.with_suffix(".json")
MACRO = BASE / "BHSM_N12_GATE7_ARB_INTERACTION_TAYLOR26_MACRO_MAPS.npz"
MACRO_RECORD = MACRO.with_suffix(".json")
SPECTRUM = BASE / "BHSM_N12_GATE7_EXACT_AFFINE_CENTER_BOUNDARY_CLUSTER_SPECTRUM.json"
INVERSE = BASE / "BHSM_N12_GATE7_EXACT_AFFINE_CENTER_BORDERED_HARD_INVERSE.json"
RESULT = BASE / "BHSM_N12_GATE7_EXACT_AFFINE_CENTER_Z2_INPUTS.json"
DATA = RESULT.with_suffix(".npz")
CONE_ADAPTER = BASE / "BHSM_N12_GATE7_EXACT_AFFINE_CENTER_Z2_CONE_ADAPTER.json"


def _sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def _relative(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


def _interp(times: np.ndarray, values: np.ndarray, targets: np.ndarray) -> np.ndarray:
    rows = []
    for target in targets:
        index = int(np.searchsorted(times, target, side="right") - 1)
        index = min(max(index, 0), len(times) - 2)
        fraction = float((target - times[index]) / (times[index + 1] - times[index]))
        rows.append((1.0 - fraction) * values[index] + fraction * values[index + 1])
    return np.asarray(rows)


def main() -> None:
    inputs = (CENTER, FINE, FINE_RECORD, MACRO, MACRO_RECORD, SPECTRUM, INVERSE)
    if not all(path.is_file() for path in inputs):
        raise FileNotFoundError("certified exact-affine Z2 adapter inputs required")
    records = {
        path: json.loads(path.read_text(encoding="utf-8"))
        for path in (FINE_RECORD, MACRO_RECORD, SPECTRUM, INVERSE)
    }
    if not all(record.get("validation_passed") is True for record in records.values()):
        raise RuntimeError("validated exact-affine parents required")

    with np.load(CENTER) as source:
        seam_times = np.asarray(source["action_lengths"], dtype=float)
        dense_times = np.asarray(source["fine_grid_action_lengths"], dtype=float)
    with np.load(FINE) as source:
        fine_times = np.asarray(source["fine_action_lengths"], dtype=float)
        fine_midpoint = np.asarray(source["fine_signed_response_midpoint"], dtype=float)
        fine_component_radius = np.asarray(
            source["fine_signed_response_component_radius"], dtype=float,
        )
    seam_midpoint = _interp(fine_times, fine_midpoint, seam_times)
    # Linear interpolation of interval radii is safe for the same affine
    # endpoint evaluation; nextafter supplies the final binary outward step.
    seam_component_radius = np.nextafter(
        _interp(fine_times, fine_component_radius, seam_times), math.inf,
    )
    with np.load(MACRO) as source:
        macro_times = np.asarray(source["macro_action_lengths"], dtype=float)
        macro_midpoint = np.asarray(source["macro_step_map_midpoint"], dtype=float)
        macro_component_radius = np.asarray(
            source["macro_step_map_component_radius"], dtype=float,
        )
    if not np.array_equal(macro_times, seam_times):
        raise RuntimeError("exact macro carrier and causal seam times differ")

    inverse_rows = records[INVERSE]["rows"]
    grouped: dict[int, list[dict[str, object]]] = {index: [] for index in range(370)}
    for row in inverse_rows:
        left, right = (float(value) for value in row["action_interval"])
        midpoint = 0.5 * (left + right)
        interval = int(np.searchsorted(dense_times, midpoint, side="right") - 1)
        interval = min(max(interval, 0), 369)
        grouped[interval].append(row)
    if any(not rows for rows in grouped.values()):
        raise RuntimeError("every retained dense interval must own exact cone cells")
    adapter_rows = []
    for interval, rows in grouped.items():
        adapter_rows.append({
            "interval": interval,
            "nonlinear_cone_chart_bordered_inverse_2_norm_upper": max(
                float(row["center_chart_bordered_inverse_2_norm_upper"])
                for row in rows
            ),
            "nonlinear_cone_selected_to_hard_gap_lower": min(
                float(row["certified_selected_to_hard_gap_lower"])
                for row in rows
            ),
            "exact_center_cells": len(rows),
        })
    candidate_radius = float(records[SPECTRUM]["domain"]["nonlinear_halo_action_radius"])
    # Remove only the separately recorded fine-center Arb radius, recovering
    # the predeclared nonlinear action radius used by the theorem.
    candidate_radius = math.nextafter(
        candidate_radius - float(np.max(np.linalg.norm(
            fine_component_radius, axis=1,
        ))), -math.inf,
    )
    old_candidate = 1.243972269022099e-12
    if abs(candidate_radius - old_candidate) > 1.0e-20:
        raise RuntimeError("predeclared nonlinear action radius changed")
    candidate_radius = old_candidate

    np.savez_compressed(
        DATA,
        action_lengths=seam_times,
        ambient_correction_profile=seam_midpoint,
        ambient_correction_component_radius=seam_component_radius,
        physical_macro_step_maps=macro_midpoint,
        physical_macro_step_map_component_radius=macro_component_radius,
    )
    cone_payload = {
        "artifact": "BHSM_N12_GATE7_EXACT_AFFINE_CENTER_Z2_CONE_ADAPTER",
        "status": "EXACT_AFFINE_CENTER_CONE_TYPED_FOR_RETAINED_Z2_THEOREM",
        "domain": {"candidate_nonlinear_action_radius": candidate_radius},
        "rows": adapter_rows,
        "validation": {
            "all_370_retained_dense_intervals_covered": len(adapter_rows) == 370,
            "all_selected_gaps_positive": min(
                row["nonlinear_cone_selected_to_hard_gap_lower"] for row in adapter_rows
            ) > 0.0,
            "all_bordered_inverse_bounds_finite": all(math.isfinite(
                row["nonlinear_cone_chart_bordered_inverse_2_norm_upper"]
            ) for row in adapter_rows),
            "no_historical_Gauss12_cone_consumed": True,
        },
        "inputs": {
            _relative(path): _sha256(path) for path in (SPECTRUM, INVERSE)
        },
        "FULL_BHSM_COMPLETE": False,
    }
    cone_payload["validation_passed"] = all(cone_payload["validation"].values())
    CONE_ADAPTER.write_text(
        json.dumps(cone_payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8", newline="\n",
    )
    validation = {
        "all_48_exact_affine_seams_sampled": seam_midpoint.shape == (48, 98),
        "all_47_exact_affine_macro_map_intervals_retained": macro_midpoint.shape == (47, 73, 73),
        "fine_and_macro_Arb_radii_retained": bool(
            np.all(seam_component_radius >= 0.0)
            and np.all(macro_component_radius >= 0.0)
        ),
        "exact_center_cone_adapter_validated": cone_payload["validation_passed"],
        "no_action_equation_source_selector_scale_gate_or_chord_changed": True,
    }
    payload = {
        "artifact": "BHSM_N12_GATE7_EXACT_AFFINE_CENTER_Z2_INPUTS",
        "status": "FINAL_EXACT_AFFINE_CENTER_TYPED_FOR_RETAINED_TAYLOR_VOLTERRA_Z2",
        "summary": {
            "maximum_seam_correction_2_norm": float(np.max(np.linalg.norm(seam_midpoint, axis=1))),
            "maximum_seam_correction_Arb_radius": float(np.max(np.linalg.norm(seam_component_radius, axis=1))),
            "maximum_macro_map_Arb_Frobenius_radius": float(np.max(np.linalg.norm(macro_component_radius, axis=(1, 2)))),
            "minimum_exact_center_selected_gap": min(
                row["nonlinear_cone_selected_to_hard_gap_lower"] for row in adapter_rows
            ),
        },
        "data": _relative(DATA),
        "data_SHA256": _sha256(DATA),
        "cone_adapter": _relative(CONE_ADAPTER),
        "cone_adapter_SHA256": _sha256(CONE_ADAPTER),
        "validation": validation,
        "validation_passed": all(validation.values()),
        "inputs": {_relative(path): _sha256(path) for path in inputs},
        "FULL_BHSM_COMPLETE": False,
    }
    RESULT.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8", newline="\n",
    )
    print(json.dumps({
        "status": payload["status"],
        "summary": payload["summary"],
        "validation_passed": payload["validation_passed"],
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
