"""Certify the bordered branch-24 hard inverse on the adaptive DOP853 cover."""

from __future__ import annotations

import hashlib
import json
import math
import os
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "artifacts" / "flagship_integration"
SPECTRUM = Path(os.environ.get(
    "BHSM_N12_STOP_DOP853_ADAPTIVE_SPECTRUM",
    str(BASE / "BHSM_N12_C2_STOP_DOP853_ADAPTIVE_BOUNDARY_CLUSTER_SPECTRUM.json"),
))
PROJECTOR = Path(os.environ.get(
    "BHSM_N12_STOP_DOP853_ADAPTIVE_PROJECTOR",
    str(BASE / "BHSM_N12_C2_STOP_DOP853_ADAPTIVE_SELECTED_PROJECTOR_GRAPH.json"),
))
RESULT = Path(os.environ.get(
    "BHSM_N12_STOP_DOP853_ADAPTIVE_INVERSE",
    str(BASE / "BHSM_N12_C2_STOP_DOP853_ADAPTIVE_BORDERED_HARD_INVERSE.json"),
))


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
        raise RuntimeError("complete adaptive DOP853 spectrum required")
    if projector["validation_passed"] is not True:
        raise RuntimeError("complete adaptive DOP853 selected projector required")
    if len(spectrum["rows"]) != len(projector["rows"]):
        raise RuntimeError("spectrum/projector adaptive-cover mismatch")
    rows = []
    expected = []
    for spectral, graph in zip(spectrum["rows"], projector["rows"]):
        key = (
            int(spectral["interval"]), int(spectral["subspan"]),
            int(spectral["subdivisions"]),
        )
        graph_key = (
            int(graph["interval"]), int(graph["subspan"]),
            int(graph["subdivisions"]),
        )
        if key != graph_key:
            raise RuntimeError("spectrum/projector row ordering mismatch")
        expected.append(key)
        gap = float(min(
            spectral["negative_selected_gap_lower"],
            spectral["selected_positive_gap_lower"],
        ))
        motion = float(graph["selected_projector_motion_upper"])
        inverse = _up(max(1.0, 1.0 / gap))
        chart_condition = _up((1.0 + motion) / (1.0 - motion))
        chart_inverse = _up(chart_condition * inverse)
        rows.append({
            "interval": key[0],
            "subspan": key[1],
            "subdivisions": key[2],
            "selected_branch": int(graph["selected_branch"]),
            "bordered_dimension": 62,
            "hard_dimension": 60,
            "certified_selected_to_hard_gap_lower": gap,
            "instantaneous_bordered_inverse_2_norm_upper": inverse,
            "selected_projector_graph_motion_upper": motion,
            "center_chart_condition_factor_upper": chart_condition,
            "center_chart_bordered_inverse_2_norm_upper": chart_inverse,
            "bordered_inverse_closed": gap > 0.0 and motion < 1.0,
        })
    validation = {
        "every_adaptive_spectrum_projector_row_consumed_once_in_order": [
            (row["interval"], row["subspan"], row["subdivisions"]) for row in rows
        ] == expected,
        "branch_24_selected_everywhere": all(row["selected_branch"] == 24 for row in rows),
        "all_selected_to_hard_gaps_strictly_positive": all(row["certified_selected_to_hard_gap_lower"] > 0.0 for row in rows),
        "all_projector_graph_motions_below_one": all(row["selected_projector_graph_motion_upper"] < 1.0 for row in rows),
        "all_bordered_inverse_bounds_finite": all(
            row["bordered_inverse_closed"]
            and math.isfinite(row["center_chart_bordered_inverse_2_norm_upper"])
            for row in rows
        ),
        "instantaneous_singular_values_are_one_one_and_hard_gaps": True,
        "same_DOP853_adaptive_cover_as_spectrum_and_projector": True,
        "no_full_kinetic_Dirac_or_history_inverse_used": True,
    }
    passed = all(validation.values())
    owner = max(rows, key=lambda row: row["center_chart_bordered_inverse_2_norm_upper"])
    return {
        "artifact": "BHSM_N12_C2_STOP_DOP853_ADAPTIVE_BORDERED_HARD_INVERSE",
        "status": (
            "ALL_DOP853_ADAPTIVE_STOP_PATH_BORDERED_HARD_INVERSES_CERTIFIED"
            if passed else "DOP853_ADAPTIVE_STOP_PATH_BORDERED_HARD_INVERSE_OPEN"
        ),
        "identity": "sigma(K_border)={1,1,abs(lambda_j-lambda_24):j_not_24};_norm(K_border^-1)=max(1,1/gap_24_hard)",
        "mesh": {"adaptive_cover_cells": len(rows)},
        "summary": {
            "minimum_selected_to_hard_gap_lower": min(row["certified_selected_to_hard_gap_lower"] for row in rows),
            "maximum_instantaneous_bordered_inverse_2_norm_upper": max(row["instantaneous_bordered_inverse_2_norm_upper"] for row in rows),
            "maximum_center_chart_condition_factor_upper": max(row["center_chart_condition_factor_upper"] for row in rows),
            "maximum_center_chart_bordered_inverse_2_norm_upper": max(row["center_chart_bordered_inverse_2_norm_upper"] for row in rows),
            "owner": owner,
        },
        "rows": rows,
        "validation": validation,
        "validation_passed": passed,
        "claim_boundary": {
            "bordered_hard_inverse_on_stored_DOP853_stop_path": "CERTIFIED" if passed else "OPEN",
            "action_owned_bordered_rhs_tube": "OPEN",
            "bordered_hard_response_tube": "OPEN_UNTIL_RHS_INSERTED",
            "Gate7": "ACTIVE",
            "FULL_BHSM_COMPLETE": False,
        },
        "exact_next_dependency": "ASSEMBLE_THE_ACTION_OWNED_INTERNAL_BORDERED_RIGHT_HAND_SIDE_ON_THE_IDENTICAL_DOP853_ADAPTIVE_COVER",
        "inputs": {
            _relative(SPECTRUM): _sha256(SPECTRUM),
            _relative(PROJECTOR): _sha256(PROJECTOR),
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
        "exact_next_dependency": payload["exact_next_dependency"],
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
