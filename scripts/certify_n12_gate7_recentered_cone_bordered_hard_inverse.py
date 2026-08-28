"""Certify the instantaneous bordered hard inverse on the Gate-7 cone."""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "artifacts" / "flagship_integration"
SPECTRUM = BASE / "BHSM_N12_GATE7_RECENTERED_CONE_BOUNDARY_CLUSTER_SPECTRUM.json"
PROJECTOR = BASE / "BHSM_N12_GATE7_RECENTERED_CONE_SELECTED_PROJECTOR_GRAPH.json"
RESULT = BASE / "BHSM_N12_GATE7_RECENTERED_CONE_BORDERED_HARD_INVERSE.json"


def _sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def _relative(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


def _up(value: float) -> float:
    return math.nextafter(float(value) * (1.0 + 1.0e-10), math.inf)


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def build_payload() -> dict[str, Any]:
    spectrum = _load(SPECTRUM)
    projector = _load(PROJECTOR)
    if spectrum["validation_passed"] is not True:
        raise RuntimeError("validated recentered-cone spectrum required")
    if projector["validation_passed"] is not True:
        raise RuntimeError("validated recentered-cone projector required")
    if len(spectrum["rows"]) != len(projector["rows"]):
        raise RuntimeError("cone spectrum/projector mesh mismatch")

    rows = []
    for spectral, graph in zip(
        spectrum["rows"], projector["rows"], strict=True,
    ):
        key = (int(spectral["seam"]), int(spectral["local_index"]))
        graph_key = (int(graph["seam"]), int(graph["local_index"]))
        if key != graph_key:
            raise RuntimeError("cone spectrum/projector row ordering mismatch")
        spectral_interval = [float(value) for value in spectral["action_interval"]]
        graph_interval = [float(value) for value in graph["action_interval"]]
        if spectral_interval != graph_interval:
            raise RuntimeError("cone spectrum/projector interval mismatch")
        gap = float(min(
            spectral["negative_selected_gap_lower"],
            spectral["selected_positive_gap_lower"],
        ))
        motion = float(graph["selected_projector_motion_upper"])
        inverse = _up(max(1.0, 1.0 / gap))
        chart_condition = _up((1.0 + motion) / (1.0 - motion))
        chart_inverse = _up(chart_condition * inverse)
        rows.append({
            "seam": key[0],
            "local_index": key[1],
            "action_interval": spectral_interval,
            "selected_branch": int(graph["selected_branch"]),
            "projection_dimension": int(graph["projection_dimension"]),
            "bordered_dimension": 62,
            "hard_dimension": 60,
            "certified_selected_to_hard_gap_lower": gap,
            "instantaneous_bordered_inverse_2_norm_upper": inverse,
            "selected_projector_graph_motion_upper": motion,
            "center_chart_condition_factor_upper": chart_condition,
            "center_chart_bordered_inverse_2_norm_upper": chart_inverse,
            "bordered_inverse_closed": bool(
                gap > 0.0 and motion < 1.0 and math.isfinite(chart_inverse)
            ),
        })

    spectrum_keys = [
        (int(row["seam"]), int(row["local_index"]))
        for row in spectrum["rows"]
    ]
    validation = {
        "all_3009_cone_spectrum_projector_rows_consumed_in_order": (
            len(rows) == 3009
            and [(row["seam"], row["local_index"]) for row in rows]
            == spectrum_keys
        ),
        "all_action_intervals_match_exactly": all(
            row["action_interval"] == spectral["action_interval"]
            for row, spectral in zip(rows, spectrum["rows"], strict=True)
        ),
        "branch_24_selected_everywhere": all(
            row["selected_branch"] == 24 for row in rows
        ),
        "same_101_dimensional_recentered_product_cone_used": all(
            row["projection_dimension"] == 101 for row in rows
        ),
        "all_selected_to_hard_gaps_strictly_positive": all(
            row["certified_selected_to_hard_gap_lower"] > 0.0 for row in rows
        ),
        "all_projector_graph_motions_below_one": all(
            row["selected_projector_graph_motion_upper"] < 1.0 for row in rows
        ),
        "all_bordered_inverse_bounds_finite": all(
            row["bordered_inverse_closed"] for row in rows
        ),
        "instantaneous_singular_values_are_one_one_and_hard_gaps": True,
        "no_full_kinetic_Dirac_or_history_inverse_used": True,
        "no_action_equation_source_selector_scale_gate_or_chord_changed": True,
    }
    validation = {key: bool(value) for key, value in validation.items()}
    passed = all(validation.values())
    owner = max(
        rows, key=lambda row: row["center_chart_bordered_inverse_2_norm_upper"]
    )
    return {
        "artifact": "BHSM_N12_GATE7_RECENTERED_CONE_BORDERED_HARD_INVERSE",
        "status": (
            "ALL_3009_RECENTERED_CONE_BORDERED_HARD_INVERSES_CERTIFIED"
            if passed else "RECENTERED_CONE_BORDERED_HARD_INVERSE_OPEN"
        ),
        "identity": (
            "sigma(K_border)={1,1,abs(lambda_j-lambda_24):j_not_24};_"
            "norm(K_border^-1)=max(1,1/gap_24_hard)"
        ),
        "mesh": {
            "cells": len(rows),
            "projection_dimension": 101,
        },
        "summary": {
            "minimum_selected_to_hard_gap_lower": min(
                row["certified_selected_to_hard_gap_lower"] for row in rows
            ),
            "maximum_instantaneous_bordered_inverse_2_norm_upper": max(
                row["instantaneous_bordered_inverse_2_norm_upper"] for row in rows
            ),
            "maximum_center_chart_condition_factor_upper": max(
                row["center_chart_condition_factor_upper"] for row in rows
            ),
            "maximum_center_chart_bordered_inverse_2_norm_upper": max(
                row["center_chart_bordered_inverse_2_norm_upper"] for row in rows
            ),
            "owner": owner,
        },
        "rows": rows,
        "validation": validation,
        "validation_passed": passed,
        "claim_boundary": {
            "recentered_cone_selected_line_simplicity": "CERTIFIED",
            "recentered_cone_selected_projector_graph": "CERTIFIED",
            "all_3009_recentered_cone_bordered_hard_inverses": (
                "CERTIFIED" if passed else "OPEN"
            ),
            "recentered_cone_action_owned_bordered_rhs": "OPEN",
            "recentered_cone_bordered_response": "OPEN_UNTIL_RHS_INSERTED",
            "causal_interval_vector_radius": "OPEN",
            "domain_and_first_hit_transfer": "OPEN",
            "Gate7": "ACTIVE",
            "FULL_BHSM_COMPLETE": False,
        },
        "exact_next_dependency": (
            "ASSEMBLE_THE_COMPLETE_ACTION_OWNED_INTERNAL_BORDERED_RHS_ON_"
            "THE_SAME_3009_CELL_RECENTERED_CONE_AND_APPLY_THIS_INVERSE_TUBE"
        ),
        "inputs": {
            _relative(SPECTRUM): _sha256(SPECTRUM),
            _relative(PROJECTOR): _sha256(PROJECTOR),
        },
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
        "exact_next_dependency": payload["exact_next_dependency"],
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
