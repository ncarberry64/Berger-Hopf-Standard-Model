"""Replay the retained projector-graph kernel on the exact-affine cone."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import certify_n12_gate7_exact_affine_center_boundary_cluster_spectrum as exact_cone  # noqa: E402
import certify_n12_gate7_recentered_cone_selected_projector_graph as projector  # noqa: E402


RESULT = exact_cone.BASE / (
    "BHSM_N12_GATE7_EXACT_AFFINE_CENTER_SELECTED_PROJECTOR_GRAPH.json"
)
_RETAINED_PROJECTOR_ROW = projector._projector_row


def _projector_row(task: tuple[int, int, float, float]) -> dict[str, Any]:
    return _RETAINED_PROJECTOR_ROW(task)


projector.cone = exact_cone.cone
projector.SPECTRUM = exact_cone.RESULT
projector.RESULT = RESULT
projector._projector_row = _projector_row
projector._spectrum_rows.cache_clear()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--central-probe", action="store_true")
    args = parser.parse_args()
    tasks = exact_cone.cone._cells()
    if args.central_probe:
        by_seam: dict[int, list[tuple[int, int, float, float]]] = {}
        for task in tasks:
            by_seam.setdefault(task[0], []).append(task)
        tasks = [cells[len(cells) // 2] for cells in by_seam.values()]
    payload = projector.build_payload(tasks)
    payload["artifact"] = (
        "BHSM_N12_GATE7_EXACT_AFFINE_CENTER_SELECTED_PROJECTOR_GRAPH"
    )
    if payload["validation_passed"]:
        payload["status"] = (
            "EXACT_AFFINE_CENTER_GATE7_CONE_SELECTED_PROJECTOR_GRAPH_CERTIFIED"
        )
    payload["authority"] = (
        "RETAINED_DENOMINATOR_RESOLVED_DISTANCE_BAND_KATO_GRAPH_ON_THE_"
        "CERTIFIED_EXACT_AFFINE_CENTER_CONE"
    )
    if not args.central_probe:
        RESULT.write_text(
            json.dumps(payload, indent=2, sort_keys=True) + "\n",
            encoding="utf-8", newline="\n",
        )
    print(json.dumps({
        "status": payload["status"],
        "mesh": payload["mesh"],
        "summary": payload["summary"],
        "validation_passed": payload["validation_passed"],
        "central_probe_only": args.central_probe,
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
