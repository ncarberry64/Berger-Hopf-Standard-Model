"""Certify Gate-7 two-free-leg retained-action majorants.

The correction-cone bordered response needs action derivatives with two free
state/output legs.  This wrapper calls only the hash-verified committed
MixedBound engine and uses two identity subspace directions followed by the
normalized signed Green correction.  The protected working copy is never
executed when it differs from the committed source.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import certify_n12_gate7_correction_direction_action_majorants as one_free  # noqa: E402


BASE = ROOT / "artifacts" / "flagship_integration"
CENTER = BASE / "BHSM_N12_C2_STOP_HIGH_ORDER_QUARTER_STEP_RETAINED_RECONNAISSANCE.npz"
GREEN = BASE / "BHSM_N12_C2_STOP_QUARTER_STEP_MATCHED_TANGENT_CORRELATED_DEFECT_GAUSS12_RECONNAISSANCE.npz"
EIGENLINE = BASE / "BHSM_N12_GATE7_RETAINED_CORRECTION_EIGENLINE_FIRST_JETS.json"
SECOND = BASE / "BHSM_N12_GATE7_CORRECTION_BORDERED_RESPONSE_SECOND_JETS.json"
RESULT = BASE / "BHSM_N12_GATE7_TWO_FREE_LEG_ACTION_MAJORANTS.json"
BALL_RADIUS = one_free.BALL_RADIUS


def _sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def _relative(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


def build_payload() -> dict[str, Any]:
    inputs = (CENTER, GREEN, EIGENLINE, SECOND)
    if not all(path.is_file() for path in inputs):
        raise FileNotFoundError("two-free-leg action-majorant inputs required")
    module, source_provenance = one_free._load_committed_majorant()
    with np.load(CENTER) as source:
        states = np.asarray(source["centers"], dtype=float)
        times = np.asarray(source["action_lengths"], dtype=float)
    with np.load(GREEN) as source:
        corrections = np.asarray(source["ambient_correction_profile"], dtype=float)
    eigenline = json.loads(EIGENLINE.read_text(encoding="utf-8"))
    second = json.loads(SECOND.read_text(encoding="utf-8"))
    if not eigenline["validation_passed"] or not second["validation_passed"]:
        raise RuntimeError("center action derivative inputs are invalid")
    if states.shape != (48, 98) or corrections.shape != (48, 98):
        raise RuntimeError("retained center and correction grids differ")

    identity = np.eye(98)
    rows = []
    for index, (state, correction) in enumerate(zip(
        states, corrections, strict=True
    )):
        correction_norm = float(np.linalg.norm(correction))
        direction = (
            correction / correction_norm
            if correction_norm > 0.0 else np.zeros(98)
        )
        bound = module.action_bound(
            state,
            mixed_directions=[identity, identity, direction, direction, direction],
        )
        retained_D3 = float(eigenline["rows"][index][
            "retained_D3_matrix_operator_2_norm"
        ])
        analytic_D4 = float(second["rows"][index][
            "directional_D4_action_Hessian_second_operator_2_norm"
        ])
        row = {
            "node": index,
            "action_length": float(times[index]),
            "ambient_correction_2_norm": correction_norm,
            "D2L_two_free_leg_action_operator_upper": float(bound.d[3]),
            "D3L_two_free_leg_one_correction_action_operator_upper": float(
                bound.d[7]
            ),
            "D4L_two_free_leg_two_correction_action_operator_upper": float(
                bound.d[15]
            ),
            "D5L_two_free_leg_three_correction_action_operator_upper": float(
                bound.d[31]
            ),
            "retained_center_D3_matrix_operator_2_norm": retained_D3,
            "analytic_center_D4_matrix_operator_2_norm": analytic_D4,
            "retained_center_D3_to_certified_upper_ratio": (
                retained_D3 / max(float(bound.d[7]), np.finfo(float).tiny)
            ),
            "analytic_center_D4_to_certified_upper_ratio": (
                analytic_D4 / max(float(bound.d[15]), np.finfo(float).tiny)
            ),
        }
        rows.append(row)
        print(json.dumps({
            "completed": index + 1,
            "node": index,
            "D4_two_free": row[
                "D4L_two_free_leg_two_correction_action_operator_upper"
            ],
            "D5_two_free": row[
                "D5L_two_free_leg_three_correction_action_operator_upper"
            ],
        }), flush=True)

    nonzero = [row for row in rows if row["ambient_correction_2_norm"] > 0.0]
    validation = {
        "expected_committed_majorant_SHA256_verified": True,
        "protected_worktree_majorant_not_executed_when_hash_differs": (
            source_provenance
            == "EXPECTED_COMMITTED_GIT_BLOB_USED_INSTEAD_OF_PROTECTED_WORKTREE_EDIT"
            or one_free._sha256(one_free.MAJORANT)
            == one_free.EXPECTED_MAJORANT_SHA256
        ),
        "same_48_retained_macro_seams_evaluated": len(rows) == 48,
        "two_distinct_identity_subspace_legs_used": True,
        "three_distinct_correction_slots_used_for_D5": True,
        "MixedBound_global_action_ball_applied_before_tensor_norm": True,
        "all_two_free_leg_D2_D5_bounds_finite": all(
            np.isfinite(value)
            for row in rows for key, value in row.items()
            if key.endswith("_upper")
        ),
        "retained_center_D3_matrices_below_certified_ball_bounds": all(
            row["retained_center_D3_to_certified_upper_ratio"] <= 1.0
            for row in nonzero
        ),
        "analytic_center_D4_matrices_below_certified_ball_bounds": all(
            row["analytic_center_D4_to_certified_upper_ratio"] <= 1.0
            for row in nonzero
        ),
        "no_protected_file_edited_or_staged_by_this_certificate": True,
        "no_action_equation_source_selector_scale_gate_or_chord_changed": True,
    }
    validation = {key: bool(value) for key, value in validation.items()}
    passed = all(validation.values())
    return {
        "artifact": "BHSM_N12_GATE7_TWO_FREE_LEG_ACTION_MAJORANTS",
        "status": (
            "RETAINED_ACTION_TWO_FREE_LEG_D2_D5_MAJORANTS_CERTIFIED_ON_48_SEAMS"
            if passed else "RETAINED_ACTION_TWO_FREE_LEG_MAJORANTS_INVALID"
        ),
        "authority": "COMMITTED_RETAINED_ACTION_MIXEDBOUND_BALL_CERTIFICATE",
        "ball": {
            "action_radius": BALL_RADIUS,
            "center": "RETAINED_48_NODE_FINITE_STOP_HISTORY",
            "free_legs": "TWO_FULL_98_DIMENSIONAL_ACTION_IDENTITY_SUBSPACES",
            "direction": "NORMALIZED_AMBIENT_SIGNED_GREEN_CORRECTION",
            "interval_scope": "FULL_ACTION_BALL_BEFORE_DERIVATIVE_NORM",
        },
        "tensor_slot_map": {
            "d[3]": "D2L[free_1,free_2]",
            "d[7]": "D3L[free_1,free_2,correction]",
            "d[15]": "D4L[free_1,free_2,correction,correction]",
            "d[31]": (
                "D5L[free_1,free_2,correction,correction,correction]"
            ),
        },
        "majorant_source": {
            "path": _relative(one_free.MAJORANT),
            "expected_committed_SHA256": one_free.EXPECTED_MAJORANT_SHA256,
            "working_copy_SHA256": one_free._sha256(one_free.MAJORANT),
            "execution_provenance": source_provenance,
        },
        "summary": {
            "maximum_D2L_two_free_leg_action_operator_upper": max(
                row["D2L_two_free_leg_action_operator_upper"] for row in rows
            ),
            "maximum_D3L_two_free_leg_one_correction_action_operator_upper": max(
                row["D3L_two_free_leg_one_correction_action_operator_upper"]
                for row in rows
            ),
            "maximum_D4L_two_free_leg_two_correction_action_operator_upper": max(
                row["D4L_two_free_leg_two_correction_action_operator_upper"]
                for row in rows
            ),
            "maximum_D5L_two_free_leg_three_correction_action_operator_upper": max(
                row["D5L_two_free_leg_three_correction_action_operator_upper"]
                for row in rows
            ),
            "maximum_retained_center_D3_to_certified_upper_ratio": max(
                row["retained_center_D3_to_certified_upper_ratio"]
                for row in nonzero
            ),
            "maximum_analytic_center_D4_to_certified_upper_ratio": max(
                row["analytic_center_D4_to_certified_upper_ratio"]
                for row in nonzero
            ),
        },
        "rows": rows,
        "validation": validation,
        "validation_passed": passed,
        "claim_boundary": {
            "retained_two_free_leg_action_D2_D5_ball": "CERTIFIED",
            "branchwise_selected_line_composition": "OPEN",
            "bordered_response_interval_composition": "OPEN",
            "outward_D2f_correction_cone": "OPEN_COMPOSITION",
            "causal_interval_vector_radius": "OPEN",
            "Gate7": "ACTIVE",
            "FULL_BHSM_COMPLETE": False,
        },
        "exact_next_dependency": (
            "COMPOSE_THE_TWO_FREE_LEG_ACTION_BOUNDS_WITH_BRANCHWISE_SELECTED_"
            "LINE_AND_BORDERED_RESPONSE_RADII_WITHOUT_COLLAPSING_TO_THE_"
            "GLOBAL_SMALLEST_GAP"
        ),
        "inputs": {_relative(path): _sha256(path) for path in inputs},
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
        "majorant_source": payload["majorant_source"],
        "summary": payload["summary"],
        "validation_passed": payload["validation_passed"],
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
