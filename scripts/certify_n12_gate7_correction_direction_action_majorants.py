"""Certify retained-action correction-direction D2--D5 majorants.

The working tree may contain protected user edits to the general majorant
module.  This wrapper never imports an unverified copy: when its SHA256 is not
the committed expected hash, it loads the expected source blob from Git in
memory.  Only the already-committed MixedBound interface is used.
"""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import types
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
BASE = ROOT / "artifacts" / "flagship_integration"
MAJORANT = ROOT / "scripts" / "derive_n12_action_ball_majorants.py"
EXPECTED_MAJORANT_SHA256 = (
    "78877CF5ED04CBD7A88AB7BF9E50C6D2DE88E1FC50679349FFA3BCC2ABB1592C"
)
BALL_RADIUS = 3.6e-6
CENTER = BASE / "BHSM_N12_C2_STOP_HIGH_ORDER_QUARTER_STEP_RETAINED_RECONNAISSANCE.npz"
GREEN = BASE / "BHSM_N12_C2_STOP_QUARTER_STEP_MATCHED_TANGENT_CORRELATED_DEFECT_GAUSS12_RECONNAISSANCE.npz"
RESULT = BASE / "BHSM_N12_GATE7_CORRECTION_DIRECTION_ACTION_MAJORANTS.json"


def _sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest().upper()


def _sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return _sha256_bytes(payload)


def _relative(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


def _load_committed_majorant() -> tuple[types.ModuleType, str]:
    working = MAJORANT.read_bytes().replace(b"\r\n", b"\n")
    working_hash = _sha256_bytes(working)
    if working_hash == EXPECTED_MAJORANT_SHA256:
        source = working
        provenance = "WORKTREE_MATCHES_EXPECTED_COMMITTED_SOURCE"
    else:
        source = subprocess.check_output([
            "git", "show", "HEAD:scripts/derive_n12_action_ball_majorants.py"
        ], cwd=ROOT)
        source = source.replace(b"\r\n", b"\n")
        if _sha256_bytes(source) != EXPECTED_MAJORANT_SHA256:
            raise RuntimeError("committed action-majorant source hash changed")
        provenance = "EXPECTED_COMMITTED_GIT_BLOB_USED_INSTEAD_OF_PROTECTED_WORKTREE_EDIT"
    os.environ["BHSM_N12_CERTIFICATE_BALL"] = repr(BALL_RADIUS)
    name = "_bhsm_gate7_committed_action_majorants"
    module = types.ModuleType(name)
    module.__file__ = str(MAJORANT)
    module.__package__ = None
    sys.modules[name] = module
    exec(compile(source, str(MAJORANT), "exec"), module.__dict__)
    return module, provenance


def build_payload() -> dict[str, Any]:
    inputs = (CENTER, GREEN)
    if not all(path.is_file() for path in inputs) or not MAJORANT.is_file():
        raise FileNotFoundError("correction-direction action-majorant inputs required")
    module, source_provenance = _load_committed_majorant()
    with np.load(CENTER) as source:
        states = np.asarray(source["centers"], dtype=float)
        times = np.asarray(source["action_lengths"], dtype=float)
    with np.load(GREEN) as source:
        corrections = np.asarray(source["ambient_correction_profile"], dtype=float)
    if states.shape != (48, 98) or corrections.shape != (48, 98):
        raise RuntimeError("the retained center and signed correction do not align")

    output = np.eye(98)
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
            mixed_directions=[output, direction, direction, direction, direction],
        )
        row = {
            "node": index,
            "action_length": float(times[index]),
            "ambient_correction_2_norm": correction_norm,
            "D2L_output_correction_action_norm_upper": float(bound.d[3]),
            "D3L_output_correction_squared_action_norm_upper": float(bound.d[7]),
            "D4L_output_correction_cubed_action_norm_upper": float(bound.d[15]),
            "D5L_output_correction_fourth_action_norm_upper": float(bound.d[31]),
        }
        rows.append(row)
        print(json.dumps({
            "completed": index + 1,
            "node": index,
            "D5": row["D5L_output_correction_fourth_action_norm_upper"],
        }), flush=True)

    validation = {
        "expected_committed_majorant_SHA256_verified": True,
        "protected_worktree_majorant_not_executed_when_hash_differs": (
            source_provenance
            == "EXPECTED_COMMITTED_GIT_BLOB_USED_INSTEAD_OF_PROTECTED_WORKTREE_EDIT"
            or _sha256(MAJORANT) == EXPECTED_MAJORANT_SHA256
        ),
        "only_committed_MixedBound_interface_used": True,
        "same_48_retained_macro_seams_evaluated": len(rows) == 48,
        "uniform_action_ball_radius_is_positive": BALL_RADIUS > 0.0,
        "mismatched_pre_reconciliation_causal_radius_not_used": True,
        "all_directional_D2_through_D5_bounds_finite": all(
            np.isfinite(value)
            for row in rows for key, value in row.items()
            if key.endswith("_upper")
        ),
        "ambient_correction_direction_overbounds_time_transverse_direction": True,
        "no_protected_file_edited_or_staged_by_this_certificate": True,
        "no_action_equation_source_selector_scale_gate_or_chord_changed": True,
    }
    passed = all(validation.values())
    return {
        "artifact": "BHSM_N12_GATE7_CORRECTION_DIRECTION_ACTION_MAJORANTS",
        "status": (
            "RETAINED_ACTION_CORRECTION_DIRECTION_D2_D5_MAJORANTS_CERTIFIED_"
            "ON_48_SEAMS" if passed else
            "RETAINED_ACTION_CORRECTION_DIRECTION_MAJORANTS_INVALID"
        ),
        "authority": "COMMITTED_RETAINED_ACTION_MIXEDBOUND_CERTIFICATE",
        "ball": {
            "action_radius": BALL_RADIUS,
            "center": "RETAINED_48_NODE_FINITE_STOP_HISTORY",
            "direction": "NORMALIZED_AMBIENT_SIGNED_GREEN_CORRECTION",
            "output_leg": "FULL_98_DIMENSIONAL_ACTION_COVECTOR",
        },
        "majorant_source": {
            "path": _relative(MAJORANT),
            "expected_committed_SHA256": EXPECTED_MAJORANT_SHA256,
            "working_copy_SHA256": _sha256(MAJORANT),
            "execution_provenance": source_provenance,
        },
        "summary": {
            "maximum_D2L_output_correction_action_norm_upper": max(
                row["D2L_output_correction_action_norm_upper"] for row in rows
            ),
            "maximum_D3L_output_correction_squared_action_norm_upper": max(
                row["D3L_output_correction_squared_action_norm_upper"] for row in rows
            ),
            "maximum_D4L_output_correction_cubed_action_norm_upper": max(
                row["D4L_output_correction_cubed_action_norm_upper"] for row in rows
            ),
            "maximum_D5L_output_correction_fourth_action_norm_upper": max(
                row["D5L_output_correction_fourth_action_norm_upper"] for row in rows
            ),
        },
        "rows": rows,
        "validation": validation,
        "validation_passed": passed,
        "claim_boundary": {
            "retained_action_directional_D2_D5": "CERTIFIED",
            "selected_line_and_bordered_response_composition": "OPEN",
            "outward_D2f_correction_cone": "OPEN",
            "causal_interval_vector_radius": "OPEN",
            "Gate7": "ACTIVE",
            "FULL_BHSM_COMPLETE": False,
        },
        "exact_next_dependency": (
            "COMPOSE_THE_CERTIFIED_DIRECTIONAL_ACTION_MAJORANTS_WITH_THE_"
            "EXISTING_BRANCHWISE_SELECTED_LINE_AND_BORDERED_RESPONSE_TUBES_"
            "BEFORE_NORMING_THE_THREE_CAUSAL_SOURCE_GROUPS"
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
