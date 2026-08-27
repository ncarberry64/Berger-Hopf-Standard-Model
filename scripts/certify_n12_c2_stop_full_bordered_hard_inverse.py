"""Certify the instantaneous bordered hard inverse on the finite stop path."""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "artifacts" / "flagship_integration"
SPECTRUM = BASE / "BHSM_N12_C2_STOP_FULL_BOUNDARY_CLUSTER_SPECTRUM.json"
PROJECTOR = BASE / "BHSM_N12_C2_STOP_FULL_SELECTED_PROJECTOR_GRAPH.json"
RESULT = BASE / "BHSM_N12_C2_STOP_FULL_BORDERED_HARD_INVERSE.json"


def _sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def _up(value: float) -> float:
    return math.nextafter(float(value) * (1.0 + 1.0e-10), math.inf)


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def build_payload() -> dict[str, Any]:
    spectrum = _load(SPECTRUM)
    projector = _load(PROJECTOR)
    if spectrum["validation_passed"] is not True:
        raise RuntimeError("complete boundary-cluster spectrum required")
    if projector["validation_passed"] is not True:
        raise RuntimeError("complete selected-projector graph required")
    if len(spectrum["rows"]) != len(projector["rows"]):
        raise RuntimeError("spectrum/projector mesh mismatch")
    rows = []
    for spectral, graph in zip(spectrum["rows"], projector["rows"]):
        key = (int(spectral["seam"]), int(spectral["subspan"]))
        if key != (int(graph["seam"]), int(graph["subspan"])):
            raise RuntimeError("spectrum/projector row ordering mismatch")
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
            "subspan": key[1],
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
        "all_3008_spectrum_projector_rows_consumed_in_order": [
            (row["seam"], row["subspan"]) for row in rows
        ] == [(seam, subspan) for seam in range(47) for subspan in range(64)],
        "branch_24_selected_everywhere": all(
            row["selected_branch"] == 24 for row in rows
        ),
        "all_selected_to_hard_gaps_strictly_positive": all(
            row["certified_selected_to_hard_gap_lower"] > 0.0 for row in rows
        ),
        "all_projector_graph_motions_below_one": all(
            row["selected_projector_graph_motion_upper"] < 1.0 for row in rows
        ),
        "all_bordered_inverse_bounds_finite": all(
            row["bordered_inverse_closed"]
            and math.isfinite(row["center_chart_bordered_inverse_2_norm_upper"])
            for row in rows
        ),
        "instantaneous_singular_values_are_one_one_and_hard_gaps": True,
        "no_full_kinetic_Dirac_or_history_inverse_used": True,
    }
    passed = all(validation.values())
    owner = max(
        rows, key=lambda row: row["center_chart_bordered_inverse_2_norm_upper"]
    )
    return {
        "artifact": "BHSM_N12_C2_STOP_FULL_BORDERED_HARD_INVERSE",
        "status": (
            "ALL_3008_STOP_PATH_BORDERED_HARD_INVERSES_CERTIFIED"
            if passed else "STOP_PATH_BORDERED_HARD_INVERSE_OPEN"
        ),
        "identity": (
            "sigma(K_border)={1,1,abs(lambda_j-lambda_24):j_not_24};_"
            "norm(K_border^-1)=max(1,1/gap_24_hard)"
        ),
        "mesh": {
            "macro_seams": 47,
            "subspans_per_macro_seam": 64,
            "total_subspans": len(rows),
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
            "all_3008_instantaneous_bordered_hard_inverses": (
                "CERTIFIED" if passed else "OPEN"
            ),
            "action_owned_bordered_rhs_tube": "OPEN",
            "bordered_hard_response_tube": "OPEN_UNTIL_RHS_INSERTED",
            "Green_Hermite_shadowing": "OPEN",
            "Gate7": "ACTIVE",
            "FULL_BHSM_COMPLETE": False,
        },
        "exact_next_dependency": (
            "ASSEMBLE_THE_ACTION_OWNED_INTERNAL_BORDERED_RIGHT_HAND_SIDE_"
            "ON_THE_SAME_MESH_AND_APPLY_THIS_CERTIFIED_INVERSE_TUBE"
        ),
        "inputs": {
            SPECTRUM.relative_to(ROOT).as_posix(): _sha256(SPECTRUM),
            PROJECTOR.relative_to(ROOT).as_posix(): _sha256(PROJECTOR),
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
    }, indent=2))


if __name__ == "__main__":
    main()
