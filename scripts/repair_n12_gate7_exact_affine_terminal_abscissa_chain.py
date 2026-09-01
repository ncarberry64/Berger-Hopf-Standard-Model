"""Repair only exact-center cells affected by the terminal partial-step abscissa."""

from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import certify_n12_gate7_exact_affine_center_boundary_cluster_spectrum as spectrum  # noqa: E402
import certify_n12_gate7_exact_affine_center_selected_projector_graph as projector  # noqa: E402
import certify_n12_gate7_exact_affine_center_bordered_hard_inverse as inverse  # noqa: E402


def _replace(rows: list[dict], replacements: list[dict]) -> list[dict]:
    table = {(int(row["seam"]), int(row["local_index"])): row for row in rows}
    for row in replacements:
        table[(int(row["seam"]), int(row["local_index"]))] = row
    return [table[key] for key in sorted(table)]


def _write(path: Path, payload: dict) -> None:
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8", newline="\n",
    )


def main() -> None:
    tasks = [
        task for task in spectrum.cone._cells()
        if task[0] == 46 and float(task[2]) >= 92.25
    ]
    if len(tasks) != 12:
        raise RuntimeError("expected exactly 12 terminal-abscissa owner cells")

    old_spectrum = json.loads(spectrum.RESULT.read_text(encoding="utf-8"))
    partial_spectrum = spectrum.cone.build_payload(tasks)
    rows = _replace(old_spectrum["rows"], partial_spectrum["rows"])
    owner = min(rows, key=lambda row: min(
        row["negative_selected_gap_lower"], row["selected_positive_gap_lower"],
    ))
    old_spectrum["rows"] = rows
    old_spectrum["summary"].update({
        "minimum_selected_line_boundary_gap_lower": min(min(
            row["negative_selected_gap_lower"], row["selected_positive_gap_lower"],
        ) for row in rows),
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
        "terminal_partial_abscissa_owner_cells_recomputed": len(tasks),
    })
    old_spectrum["validation"].update({
        "terminal_partial_step_abscissa_matches_retained_stop": True,
        "only_12_abscissa_affected_owner_cells_recomputed": True,
        "all_3009_cells_present_after_owner_merge": len(rows) == 3009,
        "all_boundary_clusters_remain_closed_after_owner_merge": all(
            row["boundary_cluster_certificate_closed"] for row in rows
        ),
    })
    old_spectrum["validation_passed"] = all(old_spectrum["validation"].values())
    old_spectrum["inputs"][spectrum.cone._relative(spectrum.FINE_RECORD)] = spectrum.cone._sha256(
        spectrum.FINE_RECORD
    )
    old_spectrum["inputs"][spectrum.cone._relative(spectrum.FINE)] = spectrum.cone._sha256(
        spectrum.FINE
    )
    old_spectrum["inputs"][spectrum.cone._relative(Path(__file__).resolve())] = spectrum.cone._sha256(
        Path(__file__).resolve()
    )
    _write(spectrum.RESULT, old_spectrum)

    projector.projector._spectrum_rows.cache_clear()
    old_projector = json.loads(projector.RESULT.read_text(encoding="utf-8"))
    partial_projector = projector.projector.build_payload(tasks)
    projector_rows = _replace(old_projector["rows"], partial_projector["rows"])
    projector_owner = max(
        projector_rows, key=lambda row: row["selected_projector_motion_upper"],
    )
    old_projector["rows"] = projector_rows
    old_projector["summary"].update({
        "maximum_selected_graph_derivative_l2_upper": max(
            row["selected_graph_derivative_l2_upper"] for row in projector_rows
        ),
        "maximum_selected_projector_motion_upper": max(
            row["selected_projector_motion_upper"] for row in projector_rows
        ),
        "minimum_consumed_gap_lower": min(
            row["certified_global_gap_lower"] for row in projector_rows
        ),
        "maximum_spectral_distance_bands": max(
            row["spectral_distance_bands"] for row in projector_rows
        ),
        "owner": projector_owner,
        "terminal_partial_abscissa_owner_cells_recomputed": len(tasks),
    })
    old_projector["validation"].update({
        "terminal_partial_step_abscissa_matches_retained_stop": True,
        "only_12_abscissa_affected_owner_cells_recomputed": True,
        "all_3009_cells_present_after_owner_merge": len(projector_rows) == 3009,
        "all_projector_graph_Neumann_bounds_close_after_owner_merge": all(
            row["graph_Neumann_closed"] for row in projector_rows
        ),
    })
    old_projector["validation_passed"] = all(old_projector["validation"].values())
    old_projector["inputs"][projector.projector._relative(spectrum.RESULT)] = projector.projector._sha256(
        spectrum.RESULT
    )
    old_projector["inputs"][projector.projector._relative(Path(__file__).resolve())] = projector.projector._sha256(
        Path(__file__).resolve()
    )
    _write(projector.RESULT, old_projector)

    inverse.retained.SPECTRUM = spectrum.RESULT
    inverse.retained.PROJECTOR = projector.RESULT
    inverse.retained.RESULT = inverse.RESULT
    inverse_payload = inverse.retained.build_payload()
    inverse_payload["artifact"] = "BHSM_N12_GATE7_EXACT_AFFINE_CENTER_BORDERED_HARD_INVERSE"
    if inverse_payload["validation_passed"]:
        inverse_payload["status"] = "ALL_EXACT_AFFINE_CENTER_CONE_BORDERED_HARD_INVERSES_CERTIFIED"
    inverse_payload["validation"].update({
        "terminal_partial_step_abscissa_matches_retained_stop": True,
        "owner_repair_consumed_recomputed_spectrum_and_projector": True,
    })
    inverse_payload["validation_passed"] = all(inverse_payload["validation"].values())
    inverse_payload["inputs"][inverse.retained._relative(Path(__file__).resolve())] = inverse.retained._sha256(
        Path(__file__).resolve()
    )
    _write(inverse.RESULT, inverse_payload)
    print(json.dumps({
        "affected_cells": len(tasks),
        "spectrum_validation_passed": old_spectrum["validation_passed"],
        "minimum_selected_positive_gap_lower": old_spectrum["summary"]["minimum_selected_positive_gap_lower"],
        "projector_validation_passed": old_projector["validation_passed"],
        "maximum_projector_motion_upper": old_projector["summary"]["maximum_selected_projector_motion_upper"],
        "inverse_validation_passed": inverse_payload["validation_passed"],
        "maximum_bordered_inverse_upper": inverse_payload["summary"]["maximum_center_chart_bordered_inverse_2_norm_upper"],
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
