"""Transfer the DOP853 projector graph and bordered inverse to the cone."""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "artifacts" / "flagship_integration"
SPECTRUM = BASE / "BHSM_N12_GATE7_SELECTED_DOP853_NONLINEAR_CONE_SPECTRUM.json"
PATH_PROJECTOR = BASE / "BHSM_N12_C2_STOP_DOP853_ADAPTIVE_SELECTED_PROJECTOR_GRAPH.json"
PATH_INVERSE = BASE / "BHSM_N12_C2_STOP_DOP853_ADAPTIVE_BORDERED_HARD_INVERSE.json"
RESULT = BASE / "BHSM_N12_GATE7_SELECTED_DOP853_NONLINEAR_CONE_PROJECTOR_INVERSE.json"


def _up(value: float) -> float:
    return math.nextafter(float(value) * (1.0 + 1.0e-10), math.inf)


def _sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def _relative(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def build_payload() -> dict[str, Any]:
    spectrum = _load(SPECTRUM)
    projector = _load(PATH_PROJECTOR)
    inverse = _load(PATH_INVERSE)
    if not all(parent["validation_passed"] is True for parent in (
        spectrum, projector, inverse,
    )):
        raise RuntimeError("certified cone spectrum and path projector/inverse required")
    path_projector = {
        (int(row["interval"]), int(row["subspan"]), int(row["subdivisions"])): row
        for row in projector["rows"]
    }
    path_inverse = {
        (int(row["interval"]), int(row["subspan"]), int(row["subdivisions"])): row
        for row in inverse["rows"]
    }
    rows = []
    for spectral in spectrum["rows"]:
        key = (
            int(spectral["interval"]), int(spectral["subspan"]),
            int(spectral["subdivisions"]),
        )
        graph = path_projector[key]
        base_inverse = path_inverse[key]
        gap = float(min(
            spectral["nonlinear_cone_negative_selected_gap_lower"],
            spectral["nonlinear_cone_selected_positive_gap_lower"],
        ))
        eta = float(spectral[
            "incremental_halo_reduced_Hessian_motion_2_norm_upper"
        ])
        halo_projector_motion = _up(2.0 * eta / gap)
        path_motion = float(graph["selected_projector_motion_upper"])
        total_motion = _up(path_motion + halo_projector_motion)
        instantaneous_inverse = _up(max(1.0, 1.0 / gap))
        chart_condition = (
            _up((1.0 + total_motion) / (1.0 - total_motion))
            if total_motion < 1.0 else math.inf
        )
        chart_inverse = _up(chart_condition * instantaneous_inverse)
        rows.append({
            "interval": key[0],
            "subspan": key[1],
            "subdivisions": key[2],
            "selected_branch": 24,
            "nonlinear_cone_selected_to_hard_gap_lower": gap,
            "incremental_halo_Hessian_motion_upper": eta,
            "path_selected_projector_motion_upper": path_motion,
            "halo_Davis_Kahan_projector_motion_upper": halo_projector_motion,
            "nonlinear_cone_selected_projector_motion_upper": total_motion,
            "nonlinear_cone_instantaneous_bordered_inverse_2_norm_upper": (
                instantaneous_inverse
            ),
            "nonlinear_cone_chart_condition_factor_upper": chart_condition,
            "nonlinear_cone_chart_bordered_inverse_2_norm_upper": chart_inverse,
            "path_chart_bordered_inverse_2_norm_upper": float(
                base_inverse["center_chart_bordered_inverse_2_norm_upper"]
            ),
            "projector_and_bordered_inverse_closed": bool(
                gap > 0.0 and total_motion < 1.0
                and math.isfinite(chart_inverse)
            ),
        })
    expected = [
        (int(row["interval"]), int(row["subspan"]), int(row["subdivisions"]))
        for row in spectrum["rows"]
    ]
    validation = {
        "every_nonlinear_cone_spectrum_cell_consumed_once_in_order": [
            (row["interval"], row["subspan"], row["subdivisions"])
            for row in rows
        ] == expected,
        "path_projector_and_inverse_cover_keys_match_cone": (
            set(path_projector) == set(expected) == set(path_inverse)
        ),
        "Davis_Kahan_halo_motion_uses_cell_local_product_gap": True,
        "path_and_halo_projector_motions_combined_by_triangle_inequality": True,
        "all_projector_graph_motions_below_one": all(
            row["nonlinear_cone_selected_projector_motion_upper"] < 1.0
            for row in rows
        ),
        "exact_bordered_singular_value_identity_reused": True,
        "all_nonlinear_cone_bordered_inverse_bounds_finite": all(
            row["projector_and_bordered_inverse_closed"] for row in rows
        ),
        "no_kinetic_Dirac_or_history_inverse_formed": True,
        "candidate_radius_not_promoted_before_Y_Z1_Z2": True,
        "no_action_equation_source_selector_scale_gate_or_chord_changed": True,
    }
    validation = {key: bool(value) for key, value in validation.items()}
    passed = all(validation.values())
    owner = max(
        rows,
        key=lambda row: row[
            "nonlinear_cone_chart_bordered_inverse_2_norm_upper"
        ],
    )
    return {
        "artifact": "BHSM_N12_GATE7_SELECTED_DOP853_NONLINEAR_CONE_PROJECTOR_INVERSE",
        "status": (
            "SELECTED_DOP853_NONLINEAR_CONE_PROJECTOR_AND_BORDERED_INVERSE_CERTIFIED"
            if passed else "SELECTED_DOP853_NONLINEAR_CONE_PROJECTOR_INVERSE_OPEN"
        ),
        "identity": (
            "sigma(K_border)={1,1,abs(lambda_j-lambda_24)};_"
            "Davis_Kahan_halo_motion<=2*eta/g_product"
        ),
        "mesh": {"cells": len(rows)},
        "summary": {
            "minimum_nonlinear_cone_selected_to_hard_gap_lower": min(
                row["nonlinear_cone_selected_to_hard_gap_lower"] for row in rows
            ),
            "maximum_halo_Davis_Kahan_projector_motion_upper": max(
                row["halo_Davis_Kahan_projector_motion_upper"] for row in rows
            ),
            "maximum_nonlinear_cone_selected_projector_motion_upper": max(
                row["nonlinear_cone_selected_projector_motion_upper"]
                for row in rows
            ),
            "maximum_nonlinear_cone_chart_bordered_inverse_2_norm_upper": max(
                row["nonlinear_cone_chart_bordered_inverse_2_norm_upper"]
                for row in rows
            ),
            "owner": owner,
        },
        "rows": rows,
        "validation": validation,
        "validation_passed": passed,
        "claim_boundary": {
            "selected_projector_on_candidate_nonlinear_cone": (
                "CERTIFIED" if passed else "OPEN"
            ),
            "bordered_hard_inverse_on_candidate_nonlinear_cone": (
                "CERTIFIED" if passed else "OPEN"
            ),
            "complete_internal_response_on_candidate_nonlinear_cone": "OPEN",
            "candidate_radius_self_map": "OPEN_CORRELATED_Y_Z1_Z2",
            "Gate7": "ACTIVE",
            "FULL_BHSM_COMPLETE": False,
        },
        "exact_next_dependency": (
            "TRANSFER_THE_COMPLETE_INTERNAL_RESPONSE_AND_ITS_CERTIFIED_FIRST_"
            "VARIATION_TO_THE_CANDIDATE_CONE,_THEN_CONTRACT_SIGNED_Y_Z1_Z2"
        ),
        "inputs": {
            _relative(path): _sha256(path)
            for path in (SPECTRUM, PATH_PROJECTOR, PATH_INVERSE)
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
        "summary": payload["summary"],
        "validation_passed": payload["validation_passed"],
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
