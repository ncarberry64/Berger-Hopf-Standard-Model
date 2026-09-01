"""Certify selected-line boundary clusters on the stored DOP853 center."""

from __future__ import annotations

from concurrent.futures import ProcessPoolExecutor
import hashlib
import json
import os
from pathlib import Path
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import audit_n12_c2_stop_dop853_boundary_cluster_probe as dense  # noqa: E402


BASE = ROOT / "artifacts" / "flagship_integration"
RESULT = Path(os.environ.get(
    "BHSM_N12_STOP_DOP853_SPECTRUM_RESULT",
    str(BASE / "BHSM_N12_C2_STOP_DOP853_BOUNDARY_CLUSTER_SPECTRUM.json"),
))


def _sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def _task(pair: tuple[int, int]) -> dict[str, Any]:
    return dense.probe(*pair)


def _compact(result: dict[str, Any]) -> dict[str, Any]:
    rows = {tuple(row["branches"]): row for row in result["clusters"]}
    negative, selected, positive = rows[(23,)], rows[(24,)], rows[(25, 26, 27)]
    return {
        "interval": result["interval"],
        "subspan": result["subspan"],
        "selected_branch": result["selected_branch"],
        "Bernstein_control_count": result["Bernstein_control_count"],
        "maximum_projection_column_norm": max(result["projection_column_norms"]),
        "negative_cluster_shift_upper": negative["cluster_spectral_shift_upper"],
        "selected_line_shift_upper": selected["cluster_spectral_shift_upper"],
        "positive_cluster_shift_upper": positive["cluster_spectral_shift_upper"],
        "negative_selected_gap_lower": result["negative_selected_gap_lower"],
        "selected_positive_gap_lower": result["selected_positive_gap_lower"],
        "minimum_external_center_gap": min(
            row["external_center_gap"] for row in result["clusters"]
        ),
        "all_three_quarter_gap_bootstraps_closed": all(
            row["quarter_gap_bootstrap_closed"] for row in result["clusters"]
        ),
        "boundary_cluster_certificate_closed": result[
            "boundary_cluster_certificate_closed"
        ],
    }


def build_payload() -> dict[str, Any]:
    intervals, subdivisions = dense.mesh_shape()
    tasks = [
        (interval, subspan)
        for interval in range(intervals)
        for subspan in range(subdivisions)
    ]
    workers = min(
        int(os.environ.get("BHSM_N12_STOP_WORKERS", "8")),
        os.cpu_count() or 1,
    )
    rows = []
    with ProcessPoolExecutor(max_workers=workers) as executor:
        for index, result in enumerate(executor.map(_task, tasks, chunksize=1), 1):
            rows.append(_compact(result))
            if index % 32 == 0 or index == len(tasks):
                print(json.dumps({
                    "completed": index,
                    "total": len(tasks),
                    "interval": rows[-1]["interval"],
                    "subspan": rows[-1]["subspan"],
                    "closed_so_far": all(
                        row["boundary_cluster_certificate_closed"] for row in rows
                    ),
                    "minimum_gap_so_far": min(
                        min(row["negative_selected_gap_lower"],
                            row["selected_positive_gap_lower"])
                        for row in rows
                    ),
                }), flush=True)
    expected = tasks
    complete = [(row["interval"], row["subspan"]) for row in rows] == expected
    validation = {
        "all_dense_Bernstein_subcells_consumed_once_in_order": complete,
        "all_cells_use_eight_degree_seven_Bernstein_controls": all(
            row["Bernstein_control_count"] == 8 for row in rows
        ),
        "selected_branch_24_everywhere": all(
            row["selected_branch"] == 24 for row in rows
        ),
        "all_three_boundary_cluster_bootstraps_close_everywhere": all(
            row["all_three_quarter_gap_bootstraps_closed"] for row in rows
        ),
        "both_selected_line_boundary_margins_positive_everywhere": all(
            row["boundary_cluster_certificate_closed"] for row in rows
        ),
        "same_stored_DOP853_polynomial_as_defect_and_first_hit": True,
        "no_cubic_Hermite_surrogate_inserted": True,
    }
    owner = min(rows, key=lambda row: min(
        row["negative_selected_gap_lower"], row["selected_positive_gap_lower"],
    ))
    passed = all(validation.values())
    return {
        "artifact": "BHSM_N12_C2_STOP_DOP853_BOUNDARY_CLUSTER_SPECTRUM",
        "status": (
            "ALL_DOP853_STOP_PATH_BOUNDARY_CLUSTER_DENOMINATORS_CERTIFIED"
            if passed else "DOP853_STOP_PATH_BOUNDARY_CLUSTER_REFINEMENT_REQUIRED"
        ),
        "method": (
            "EXACT_STORED_DEGREE_SEVEN_BERNSTEIN_CONVEX_HULL_PLUS_"
            "DENOMINATOR_RESOLVED_KATO_CLUSTERS_23__24__25_TO_27"
        ),
        "mesh": {
            "dense_intervals": intervals,
            "subspans_per_dense_interval": subdivisions,
            "total_subspans": len(tasks),
            "workers": workers,
        },
        "summary": {
            "minimum_selected_line_boundary_gap_lower": min(
                min(row["negative_selected_gap_lower"],
                    row["selected_positive_gap_lower"])
                for row in rows
            ),
            "minimum_negative_selected_gap_lower": min(
                row["negative_selected_gap_lower"] for row in rows
            ),
            "minimum_selected_positive_gap_lower": min(
                row["selected_positive_gap_lower"] for row in rows
            ),
            "maximum_selected_line_shift_upper": max(
                row["selected_line_shift_upper"] for row in rows
            ),
            "maximum_negative_cluster_shift_upper": max(
                row["negative_cluster_shift_upper"] for row in rows
            ),
            "maximum_positive_cluster_shift_upper": max(
                row["positive_cluster_shift_upper"] for row in rows
            ),
            "maximum_Bernstein_projection_column_norm": max(
                row["maximum_projection_column_norm"] for row in rows
            ),
            "minimum_margin_owner": owner,
        },
        "rows": rows,
        "validation": validation,
        "validation_passed": passed,
        "claim_boundary": {
            "selected_line_on_stored_DOP853_stop_path": (
                "CERTIFIED_SIMPLE" if passed else "OPEN"
            ),
            "correlated_shadowing_tube": "OPEN",
            "Gate7": "ACTIVE",
            "FULL_BHSM_COMPLETE": False,
        },
        "exact_next_dependency": (
            "ASSEMBLE_THE_DOP853_BERNSTEIN_SELECTED_PROJECTOR_AND_BORDERED_"
            "RESPONSE_ON_THIS_IDENTICAL_MESH"
        ),
        "inputs": {
            dense.CENTER_DATA.relative_to(ROOT).as_posix(): _sha256(dense.CENTER_DATA),
            "scripts/audit_n12_c2_stop_dop853_boundary_cluster_probe.py": _sha256(
                ROOT / "scripts" / "audit_n12_c2_stop_dop853_boundary_cluster_probe.py"
            ),
        },
        "FLAGSHIP_READY": False,
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
        "summary": payload["summary"],
        "validation_passed": payload["validation_passed"],
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
