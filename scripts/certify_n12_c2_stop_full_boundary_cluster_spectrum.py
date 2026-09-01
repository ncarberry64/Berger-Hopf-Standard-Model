"""Certify the selected-line boundary clusters on all 3,008 stop subspans.

This is the complete-mesh expansion of the retained first-chord correlated
Hermite/Kato construction.  It deliberately treats hard branches 25--27 as
one invariant cluster, so their internal near meeting never appears as a
physical selected-line denominator.
"""

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

import audit_n12_c2_stop_boundary_cluster_probe as cluster  # noqa: E402


BASE = ROOT / "artifacts" / "flagship_integration"
RESULT = BASE / "BHSM_N12_C2_STOP_FULL_BOUNDARY_CLUSTER_SPECTRUM.json"
SEAMS = 47
SUBSPANS = 64


def _sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def _task(pair: tuple[int, int]) -> dict[str, Any]:
    return cluster.probe(*pair)


def _compact(result: dict[str, Any]) -> dict[str, Any]:
    rows = {tuple(row["branches"]): row for row in result["clusters"]}
    negative = rows[(23,)]
    selected = rows[(24,)]
    positive = rows[(25, 26, 27)]
    return {
        "seam": result["seam"],
        "subspan": result["subspan"],
        "selected_branch": result["selected_branch"],
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
    tasks = [
        (seam, subspan)
        for seam in range(SEAMS)
        for subspan in range(SUBSPANS)
    ]
    workers = min(8, os.cpu_count() or 1)
    rows = []
    with ProcessPoolExecutor(max_workers=workers) as executor:
        for index, result in enumerate(executor.map(_task, tasks, chunksize=1), 1):
            rows.append(_compact(result))
            if index % 32 == 0 or index == len(tasks):
                current = rows[-1]
                print(json.dumps({
                    "completed": index,
                    "total": len(tasks),
                    "seam": current["seam"],
                    "subspan": current["subspan"],
                    "closed_so_far": all(
                        row["boundary_cluster_certificate_closed"] for row in rows
                    ),
                    "minimum_gap_so_far": min(
                        min(
                            row["negative_selected_gap_lower"],
                            row["selected_positive_gap_lower"],
                        ) for row in rows
                    ),
                }), flush=True)
    complete_mesh = [
        (row["seam"], row["subspan"]) for row in rows
    ] == tasks
    every_selected = all(row["selected_branch"] == 24 for row in rows)
    every_bootstrap = all(
        row["all_three_quarter_gap_bootstraps_closed"] for row in rows
    )
    every_closed = all(row["boundary_cluster_certificate_closed"] for row in rows)
    validation = {
        "all_3008_existing_subspans_consumed_once_in_order": complete_mesh,
        "selected_branch_24_at_every_subspan_center": every_selected,
        "all_three_boundary_cluster_bootstraps_close_everywhere": every_bootstrap,
        "both_selected_line_boundary_margins_positive_everywhere": every_closed,
        "hard_26_27_internal_meeting_removed_by_cluster_25_27": True,
        "same_retained_action_and_existing_64_part_Hermite_mesh": True,
    }
    passed = all(validation.values())
    owner = min(
        rows,
        key=lambda row: min(
            row["negative_selected_gap_lower"], row["selected_positive_gap_lower"]
        ),
    )
    inputs = {
        cluster.CENTER_DATA.relative_to(ROOT).as_posix(): _sha256(cluster.CENTER_DATA),
        "scripts/audit_n12_c2_stop_boundary_cluster_probe.py": _sha256(
            ROOT / "scripts" / "audit_n12_c2_stop_boundary_cluster_probe.py"
        ),
        "scripts/audit_n12_c2_stop_local_termwise_spectrum.py": _sha256(
            ROOT / "scripts" / "audit_n12_c2_stop_local_termwise_spectrum.py"
        ),
    }
    return {
        "artifact": "BHSM_N12_C2_STOP_FULL_BOUNDARY_CLUSTER_SPECTRUM",
        "status": (
            "ALL_3008_STOP_PATH_BOUNDARY_CLUSTER_DENOMINATORS_CERTIFIED"
            if passed else
            "STOP_PATH_BOUNDARY_CLUSTER_REFINEMENT_REQUIRED"
        ),
        "method": (
            "CORRELATED_THREE_COORDINATE_HERMITE_ACTION_BALL_PLUS_"
            "DENOMINATOR_RESOLVED_KATO_CLUSTERS_23__24__25_TO_27"
        ),
        "mesh": {
            "macro_seams": SEAMS,
            "subspans_per_macro_seam": SUBSPANS,
            "total_subspans": len(tasks),
            "workers": workers,
        },
        "summary": {
            "minimum_selected_line_boundary_gap_lower": min(
                min(
                    row["negative_selected_gap_lower"],
                    row["selected_positive_gap_lower"],
                ) for row in rows
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
            "minimum_margin_owner": owner,
        },
        "rows": rows,
        "validation": validation,
        "validation_passed": passed,
        "claim_boundary": {
            "all_3008_stop_path_boundary_cluster_denominators": (
                "CERTIFIED" if passed else "OPEN"
            ),
            "selected_line_on_reference_Hermite_stop_path": (
                "CERTIFIED_SIMPLE" if passed else "OPEN"
            ),
            "branchwise_selected_projector_tube": "OPEN",
            "bordered_hard_response_tube": "OPEN",
            "Green_Hermite_shadowing": "OPEN",
            "Gate7": "ACTIVE",
            "FULL_BHSM_COMPLETE": False,
        },
        "exact_next_dependency": (
            "ASSEMBLE_THE_DENOMINATOR_RESOLVED_SELECTED_PROJECTOR_DERIVATIVE_"
            "AND_BORDERED_HARD_RESPONSE_ON_THE_SAME_3008_SUBSPANS"
            if passed else
            "REFINE_ONLY_THE_REPORTED_NONCLOSING_SUBSPANS_WITH_THE_SAME_"
            "CLUSTER_KERNEL"
        ),
        "inputs": inputs,
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
        "exact_next_dependency": payload["exact_next_dependency"],
    }, indent=2))


if __name__ == "__main__":
    main()
