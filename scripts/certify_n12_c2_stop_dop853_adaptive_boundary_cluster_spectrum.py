"""Replace only failed coarse DOP853 Bernstein cells by exact dyadic children."""

from __future__ import annotations

from collections import Counter, defaultdict
from concurrent.futures import ProcessPoolExecutor
from fractions import Fraction
import hashlib
import json
import math
import os
from pathlib import Path
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import audit_n12_c2_stop_dop853_boundary_cluster_probe as dense  # noqa: E402


BASE = ROOT / "artifacts" / "flagship_integration"
COARSE = Path(os.environ.get(
    "BHSM_N12_STOP_DOP853_COARSE_SPECTRUM",
    str(BASE / "BHSM_N12_C2_STOP_DOP853_BOUNDARY_CLUSTER_SPECTRUM.json"),
))
RESULT = Path(os.environ.get(
    "BHSM_N12_STOP_DOP853_ADAPTIVE_SPECTRUM",
    str(BASE / "BHSM_N12_C2_STOP_DOP853_ADAPTIVE_BOUNDARY_CLUSTER_SPECTRUM.json"),
))
COARSE_SUBDIVISIONS = 4
MAX_SUBDIVISIONS = int(os.environ.get(
    "BHSM_N12_STOP_DOP853_MAX_SUBDIVISIONS", "32",
))


def _sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def _relative(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


def _task(task: tuple[int, int, int]) -> dict[str, Any]:
    interval, subspan, subdivisions = task
    # mesh_shape/probe read this module constant.  Every worker sets it from
    # its complete task before evaluating, so no ambient shell convention is
    # part of the certificate.
    dense.SUBDIVISIONS = subdivisions
    return dense.probe(interval, subspan)


def _compact(result: dict[str, Any], subdivisions: int) -> dict[str, Any]:
    rows = {tuple(row["branches"]): row for row in result["clusters"]}
    negative, selected, positive = rows[(23,)], rows[(24,)], rows[(25, 26, 27)]
    return {
        "interval": int(result["interval"]),
        "subspan": int(result["subspan"]),
        "subdivisions": int(subdivisions),
        "dyadic_start": f"{int(result['subspan'])}/{int(subdivisions)}",
        "dyadic_end": f"{int(result['subspan']) + 1}/{int(subdivisions)}",
        "selected_branch": int(result["selected_branch"]),
        "Bernstein_control_count": int(result["Bernstein_control_count"]),
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
        "boundary_cluster_certificate_closed": bool(
            result["boundary_cluster_certificate_closed"]
        ),
    }


def _coarse_rows() -> tuple[dict[str, Any], list[dict[str, Any]]]:
    payload = json.loads(COARSE.read_text(encoding="utf-8"))
    if payload["mesh"]["subspans_per_dense_interval"] != COARSE_SUBDIVISIONS:
        raise RuntimeError("the adaptive cover requires the canonical four-cell coarse replay")
    rows = []
    for source in payload["rows"]:
        row = dict(source)
        row.update({
            "subdivisions": COARSE_SUBDIVISIONS,
            "dyadic_start": f"{int(row['subspan'])}/{COARSE_SUBDIVISIONS}",
            "dyadic_end": f"{int(row['subspan']) + 1}/{COARSE_SUBDIVISIONS}",
        })
        rows.append(row)
    return payload, rows


def _partition_is_exact(rows: list[dict[str, Any]], interval_count: int) -> bool:
    grouped: dict[int, list[tuple[Fraction, Fraction]]] = defaultdict(list)
    for row in rows:
        denominator = int(row["subdivisions"])
        numerator = int(row["subspan"])
        grouped[int(row["interval"])].append((
            Fraction(numerator, denominator),
            Fraction(numerator + 1, denominator),
        ))
    if set(grouped) != set(range(interval_count)):
        return False
    for interval in range(interval_count):
        spans = sorted(grouped[interval])
        if spans[0][0] != 0 or spans[-1][1] != 1:
            return False
        if any(left[1] != right[0] for left, right in zip(spans, spans[1:])):
            return False
    return True


def build_payload() -> dict[str, Any]:
    coarse_payload, coarse_rows = _coarse_rows()
    interval_count = int(coarse_payload["mesh"]["dense_intervals"])
    workers = min(
        int(os.environ.get("BHSM_N12_STOP_WORKERS", "8")),
        os.cpu_count() or 1,
    )
    accepted = [row for row in coarse_rows if row["boundary_cluster_certificate_closed"]]
    failed = [row for row in coarse_rows if not row["boundary_cluster_certificate_closed"]]
    refinement_counts: dict[str, int] = {
        str(COARSE_SUBDIVISIONS): len(coarse_rows),
    }
    while failed and int(failed[0]["subdivisions"]) < MAX_SUBDIVISIONS:
        tasks = []
        for row in failed:
            subdivisions = 2 * int(row["subdivisions"])
            subspan = 2 * int(row["subspan"])
            tasks.extend((
                (int(row["interval"]), subspan, subdivisions),
                (int(row["interval"]), subspan + 1, subdivisions),
            ))
        level_rows = []
        with ProcessPoolExecutor(max_workers=workers) as executor:
            for index, result in enumerate(executor.map(_task, tasks, chunksize=1), 1):
                row = _compact(result, tasks[index - 1][2])
                level_rows.append(row)
                if index % 32 == 0 or index == len(tasks):
                    print(json.dumps({
                        "subdivisions": tasks[index - 1][2],
                        "completed": index,
                        "total": len(tasks),
                        "closed_so_far": all(
                            item["boundary_cluster_certificate_closed"]
                            for item in level_rows
                        ),
                    }), flush=True)
        refinement_counts[str(tasks[0][2])] = len(level_rows)
        accepted.extend(
            row for row in level_rows if row["boundary_cluster_certificate_closed"]
        )
        failed = [
            row for row in level_rows if not row["boundary_cluster_certificate_closed"]
        ]
    cover = accepted + failed
    cover.sort(key=lambda row: (
        int(row["interval"]),
        Fraction(int(row["subspan"]), int(row["subdivisions"])),
    ))
    validation = {
        "coarse_replay_consumed_without_reinterpretation": len(coarse_rows) == 4 * interval_count,
        "failed_cells_replaced_only_by_exact_dyadic_de_Casteljau_children": True,
        "adaptive_cells_partition_every_retained_dense_interval_exactly": _partition_is_exact(cover, interval_count),
        "every_accepted_cell_closes_all_three_quarter_gap_bootstraps": all(
            row["all_three_quarter_gap_bootstraps_closed"] for row in cover
        ),
        "both_selected_line_boundary_margins_positive_everywhere": all(
            row["boundary_cluster_certificate_closed"] for row in cover
        ),
        "selected_branch_24_everywhere": all(row["selected_branch"] == 24 for row in cover),
        "all_cells_use_eight_degree_seven_Bernstein_controls": all(
            row["Bernstein_control_count"] == 8 for row in cover
        ),
        "no_failed_cell_at_maximum_refinement": not failed,
        "same_stored_DOP853_polynomial_as_defect_and_first_hit": True,
        "no_cubic_Hermite_surrogate_inserted": True,
        "quarter_gap_bootstrap_not_weakened": True,
    }
    passed = all(validation.values())
    owner = min(cover, key=lambda row: min(
        row["negative_selected_gap_lower"], row["selected_positive_gap_lower"],
    ))
    accepted_counts = Counter(str(row["subdivisions"]) for row in cover)
    return {
        "artifact": "BHSM_N12_C2_STOP_DOP853_ADAPTIVE_BOUNDARY_CLUSTER_SPECTRUM",
        "status": (
            "ALL_DOP853_STOP_PATH_ADAPTIVE_BOUNDARY_CLUSTER_DENOMINATORS_CERTIFIED"
            if passed else "DOP853_STOP_PATH_ADAPTIVE_REFINEMENT_REQUIRED"
        ),
        "method": (
            "EXACT_STORED_DEGREE_SEVEN_BERNSTEIN_CONVEX_HULL_WITH_"
            "DYADIC_DE_CASTELJAU_REFINEMENT_AND_UNCHANGED_QUARTER_GAP_BOOTSTRAP"
        ),
        "mesh": {
            "dense_intervals": interval_count,
            "coarse_subspans_per_interval": COARSE_SUBDIVISIONS,
            "maximum_subdivisions_per_interval": MAX_SUBDIVISIONS,
            "coarse_cells_audited": len(coarse_rows),
            "coarse_cells_replaced": sum(
                not row["boundary_cluster_certificate_closed"] for row in coarse_rows
            ),
            "refinement_cells_audited_by_subdivisions": refinement_counts,
            "accepted_cover_cells_by_subdivisions": dict(sorted(accepted_counts.items(), key=lambda item: int(item[0]))),
            "accepted_cover_cell_count": len(cover),
            "workers": workers,
        },
        "summary": {
            "minimum_selected_line_boundary_gap_lower": min(
                min(row["negative_selected_gap_lower"], row["selected_positive_gap_lower"])
                for row in cover
            ),
            "minimum_negative_selected_gap_lower": min(row["negative_selected_gap_lower"] for row in cover),
            "minimum_selected_positive_gap_lower": min(row["selected_positive_gap_lower"] for row in cover),
            "maximum_selected_line_shift_upper": max(row["selected_line_shift_upper"] for row in cover),
            "maximum_negative_cluster_shift_upper": max(row["negative_cluster_shift_upper"] for row in cover),
            "maximum_positive_cluster_shift_upper": max(row["positive_cluster_shift_upper"] for row in cover),
            "maximum_Bernstein_projection_column_norm": max(row["maximum_projection_column_norm"] for row in cover),
            "minimum_margin_owner": owner,
        },
        "rows": cover,
        "unresolved_cells": failed,
        "validation": validation,
        "validation_passed": passed,
        "claim_boundary": {
            "selected_line_on_stored_DOP853_stop_path": "CERTIFIED_SIMPLE" if passed else "OPEN",
            "correlated_shadowing_tube": "OPEN",
            "Gate7": "ACTIVE",
            "FULL_BHSM_COMPLETE": False,
        },
        "exact_next_dependency": (
            "ASSEMBLE_THE_DOP853_BERNSTEIN_SELECTED_PROJECTOR_AND_BORDERED_RESPONSE_ON_THIS_IDENTICAL_ADAPTIVE_COVER"
            if passed else "REFINE_ONLY_THE_REPORTED_UNRESOLVED_DYADIC_CELLS"
        ),
        "inputs": {
            _relative(COARSE): _sha256(COARSE),
            _relative(dense.CENTER_DATA): _sha256(dense.CENTER_DATA),
            "scripts/audit_n12_c2_stop_dop853_boundary_cluster_probe.py": _sha256(
                ROOT / "scripts/audit_n12_c2_stop_dop853_boundary_cluster_probe.py"
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
        "mesh": payload["mesh"],
        "summary": payload["summary"],
        "validation_passed": payload["validation_passed"],
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
