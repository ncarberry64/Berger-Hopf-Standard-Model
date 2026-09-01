"""Replay the retained closed internal RHS/response on the exact cone."""

from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor
import json
import math
import os
from pathlib import Path
import sys
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import certify_n12_gate7_exact_affine_center_boundary_cluster_spectrum as exact_cone  # noqa: E402
import certify_n12_gate7_exact_affine_center_selected_projector_graph as exact_projector  # noqa: E402
import certify_n12_gate7_exact_affine_center_bordered_hard_inverse as exact_inverse  # noqa: E402
import certify_n12_gate7_recentered_cone_bordered_rhs_response as response  # noqa: E402


RESULT = exact_cone.BASE / (
    "BHSM_N12_GATE7_EXACT_AFFINE_CENTER_BORDERED_RHS_RESPONSE.json"
)
CHECKPOINT = exact_cone.BASE / (
    "BHSM_N12_GATE7_EXACT_AFFINE_CENTER_BORDERED_RHS_RESPONSE.checkpoint.jsonl"
)
ADAPTIVE_CHECKPOINT = exact_cone.BASE / (
    "BHSM_N12_GATE7_EXACT_AFFINE_CENTER_BORDERED_RHS_RESPONSE.adaptive.checkpoint.jsonl"
)
_RETAINED_ROW = response._row


def _row(
    task: tuple[int, int, float, float, int, int, int],
) -> dict[str, Any]:
    return _RETAINED_ROW(task)


def _parent_tasks(
    parent: tuple[int, int, float, float], refinement: int,
) -> list[tuple[int, int, float, float, int, int, int]]:
    seam, parent_local_index, left, right = parent
    boundaries = np.linspace(left, right, refinement + 1)
    return [
        (
            seam,
            parent_local_index * refinement + child,
            float(boundaries[child]),
            float(boundaries[child + 1]),
            parent_local_index,
            child,
            refinement,
        )
        for child in range(refinement)
    ]


def _closed(row: dict[str, Any]) -> bool:
    return bool(
        row["center_internal_rhs_finite"]
        and row["bordered_response_tube_finite"]
        and row["relative_bordered_operator_perturbation_upper"] < 1.0
    )


def _evaluate(
    indexed_tasks: list[tuple[int, tuple[int, int, float, float, int, int, int]]],
    workers: int,
    stage: str,
) -> dict[int, list[dict[str, Any]]]:
    grouped: dict[int, list[dict[str, Any]]] = {}
    tasks = [task for _, task in indexed_tasks]
    parent_indices = [index for index, _ in indexed_tasks]
    with ProcessPoolExecutor(max_workers=workers) as executor:
        for count, (parent_index, row) in enumerate(
            zip(parent_indices, executor.map(_row, tasks, chunksize=1)), 1,
        ):
            grouped.setdefault(parent_index, []).append(row)
            if count % 16 == 0 or count == len(tasks):
                print(json.dumps({
                    "adaptive_stage": stage,
                    "completed": count,
                    "total": len(tasks),
                    "closed_rows_so_far": sum(
                        _closed(item)
                        for rows in grouped.values() for item in rows
                    ),
                }), flush=True)
    return grouped


def _adaptive_tasks_and_rows(
    parents: list[tuple[int, int, float, float]],
) -> tuple[
    list[tuple[int, int, float, float, int, int, int]],
    list[dict[str, Any]],
    dict[int, int],
    int,
]:
    """Keep the certified uniform prefix and refine only remaining owners."""
    uniform_rows: list[dict[str, Any]] = []
    if CHECKPOINT.is_file():
        with CHECKPOINT.open("r", encoding="utf-8") as source:
            uniform_rows = [json.loads(line) for line in source if line.strip()]
    uniform_refinement = response.BASE_RESPONSE_REFINEMENT
    complete_prefix = min(
        len(parents), len(uniform_rows) // uniform_refinement,
    )
    retained_rows = uniform_rows[:complete_prefix * uniform_refinement]
    retained_tasks = [
        task
        for parent in parents[:complete_prefix]
        for task in _parent_tasks(parent, uniform_refinement)
    ]
    retained_prefix = [
        (
            row["seam"], row["local_index"], *row["action_interval"],
            row["parent_local_index"], row["child_within_parent"],
            row["response_refinement_per_parent"],
        )
        for row in retained_rows
    ]
    if retained_prefix != retained_tasks:
        raise RuntimeError("uniform checkpoint does not contain a valid complete-parent prefix")

    workers = min(
        int(os.environ.get("BHSM_N12_GATE7_CONE_WORKERS", "12")),
        os.cpu_count() or 1,
    )
    pending = list(range(complete_prefix, len(parents)))
    probe_tasks = [
        (index, _parent_tasks(parents[index], 1)[0]) for index in pending
    ]
    probes = _evaluate(probe_tasks, workers, "PARENT_PROBE")

    accepted: dict[int, list[dict[str, Any]]] = {}
    requested: dict[int, int] = {}
    for index in pending:
        probe = probes[index][0]
        if _closed(probe):
            accepted[index] = [probe]
            requested[index] = 1
            continue
        relative = float(probe["relative_bordered_operator_perturbation_upper"])
        requested[index] = min(8, max(2, int(math.ceil(relative / 0.70))))

    for refinement in sorted(set(requested.values()) - {1}):
        indices = [
            index for index in pending if requested[index] == refinement
        ]
        indexed_tasks = [
            (index, task)
            for index in indices
            for task in _parent_tasks(parents[index], refinement)
        ]
        grouped = _evaluate(
            indexed_tasks, workers, f"REFINEMENT_{refinement}",
        )
        for index in indices:
            rows = grouped[index]
            if len(rows) == refinement and all(_closed(row) for row in rows):
                accepted[index] = rows

    failed = [index for index in pending if index not in accepted]
    if failed:
        indexed_tasks = [
            (index, task)
            for index in failed
            for task in _parent_tasks(parents[index], 8)
        ]
        grouped = _evaluate(indexed_tasks, workers, "FALLBACK_REFINEMENT_8")
        for index in failed:
            rows = grouped[index]
            if len(rows) != 8 or not all(_closed(row) for row in rows):
                raise RuntimeError(f"adaptive refinement failed at parent {index}")
            accepted[index] = rows
            requested[index] = 8

    tasks = list(retained_tasks)
    rows = list(retained_rows)
    histogram: dict[int, int] = {uniform_refinement: complete_prefix}
    for index in pending:
        parent_rows = sorted(
            accepted[index], key=lambda row: row["child_within_parent"],
        )
        refinement = int(parent_rows[0]["response_refinement_per_parent"])
        histogram[refinement] = histogram.get(refinement, 0) + 1
        tasks.extend(_parent_tasks(parents[index], refinement))
        rows.extend(parent_rows)
    return tasks, rows, histogram, complete_prefix


response.cone = exact_cone.cone
response.INVERSE = exact_inverse.RESULT
response.PROJECTOR = exact_projector.RESULT
response.RESULT = RESULT
response.CHECKPOINT = CHECKPOINT
response._row = _row
response._inverse_rows.cache_clear()
response._projector_rows.cache_clear()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--central-probe", action="store_true")
    parser.add_argument("--adaptive", action="store_true")
    args = parser.parse_args()
    parents = exact_cone.cone._cells()
    if args.central_probe:
        by_seam: dict[int, list[tuple[int, int, float, float]]] = {}
        for task in parents:
            by_seam.setdefault(task[0], []).append(task)
        parents = [cells[len(cells) // 2] for cells in by_seam.values()]
    if response.BASE_RESPONSE_REFINEMENT < 1 or response.LATE_RESPONSE_REFINEMENT < 1:
        raise ValueError("positive response refinement required")
    adaptive_histogram: dict[int, int] | None = None
    if args.adaptive and not args.central_probe:
        tasks, rows, adaptive_histogram, complete_uniform_prefix = (
            _adaptive_tasks_and_rows(parents)
        )
        with ADAPTIVE_CHECKPOINT.open("w", encoding="utf-8", newline="\n") as target:
            for row in rows:
                target.write(json.dumps(row, sort_keys=True, separators=(",", ":")) + "\n")
        payload = response.build_payload(tasks, ADAPTIVE_CHECKPOINT)
        payload["mesh"]["adaptive_parent_refinement_histogram"] = {
            str(key): adaptive_histogram[key] for key in sorted(adaptive_histogram)
        }
        payload["mesh"]["adaptive_complete_uniform_prefix_parents"] = (
            complete_uniform_prefix
        )
        payload["validation"]["adaptive_refinement_covers_every_parent_exactly_once"] = (
            sum(adaptive_histogram.values()) == len(parents)
        )
        payload["validation_passed"] = all(payload["validation"].values())
    else:
        tasks = [
            task
            for parent in parents
            for task in _parent_tasks(
                parent,
                response.LATE_RESPONSE_REFINEMENT
                if parent[0] >= response.LATE_RESPONSE_SEAM_START
                else response.BASE_RESPONSE_REFINEMENT,
            )
        ]
        payload = response.build_payload(
            tasks, None if args.central_probe else CHECKPOINT,
        )
    payload["artifact"] = (
        "BHSM_N12_GATE7_EXACT_AFFINE_CENTER_BORDERED_RHS_RESPONSE"
    )
    if payload["validation_passed"]:
        payload["status"] = (
            "EXACT_AFFINE_CENTER_GATE7_CONE_ACTION_OWNED_BORDERED_RHS_"
            "RESPONSE_CERTIFIED"
        )
    if not args.central_probe:
        RESULT.write_text(
            json.dumps(payload, indent=2, sort_keys=True) + "\n",
            encoding="utf-8", newline="\n",
        )
        if CHECKPOINT.is_file():
            CHECKPOINT.unlink()
        if ADAPTIVE_CHECKPOINT.is_file():
            ADAPTIVE_CHECKPOINT.unlink()
    print(json.dumps({
        "status": payload["status"],
        "mesh": payload["mesh"],
        "summary": payload["summary"],
        "validation_passed": payload["validation_passed"],
        "central_probe_only": args.central_probe,
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
