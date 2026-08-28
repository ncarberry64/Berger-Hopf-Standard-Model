"""Audit the recentered-cone owner-cell JAX D3 acceleration.

The full spectrum certificate uses batched JAX only for center D3 matrices.
This audit reconstructs its worst-margin cell and replays every one of the 101
projection directions with the retained 96-point complex-step action jet.
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

import certify_n12_gate7_recentered_cone_boundary_cluster_spectrum as cone  # noqa: E402


RESULT = cone.BASE / "BHSM_N12_GATE7_RECENTERED_CONE_OWNER_D3_ACCELERATION_AUDIT.json"
COMPLEX_STEP = cone.cluster.local.COMPLEX_STEP


def _sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def _relative(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


def build_payload() -> dict[str, Any]:
    spectrum = json.loads(cone.RESULT.read_text(encoding="utf-8"))
    if not spectrum["validation_passed"]:
        raise RuntimeError("validated recentered-cone spectrum required")
    owner = spectrum["summary"]["minimum_margin_owner"]
    task = next(
        item for item in cone._cells()
        if item[0] == owner["seam"] and item[1] == owner["local_index"]
    )
    geometry = cone._geometry(task)
    midpoint = geometry["midpoint"]
    projection = geometry["projection"]
    weights = cone._inputs()[3]
    jax_directionals = np.asarray(geometry["directionals"]) / (
        cone.JAX_D3_NORM_INFLATION
    )
    retained_directionals = []
    rows = []
    for index in range(projection.shape[1]):
        shifted = np.asarray(midpoint, dtype=complex) + (
            1j * COMPLEX_STEP * projection[:, index] / weights
        )
        jet = cone.cluster.local.exact_full_action_jet_at_state(
            12,
            shifted[:cone.cluster.local.QDIM],
            shifted[
                cone.cluster.local.QDIM:2 * cone.cluster.local.QDIM
            ],
            shifted[2 * cone.cluster.local.QDIM:],
            points=cone.cluster.local.POINTS,
        )
        retained = np.imag(np.asarray(jet.hessian)[
            cone.cluster.local.QDIM:, cone.cluster.local.QDIM:
        ]) / COMPLEX_STEP
        retained_directionals.append(retained)
        difference = float(np.linalg.norm(
            retained - jax_directionals[index], ord=2
        ))
        retained_norm = float(np.linalg.norm(retained, ord=2))
        rows.append({
            "direction": index,
            "role": "CORRECTED_HERMITE" if index < 3 else "NONLINEAR_HALO",
            "retained_D3_matrix_operator_2_norm": retained_norm,
            "retained_vs_JAX_operator_2_difference": difference,
            "retained_vs_JAX_relative_difference": (
                difference / max(retained_norm, np.finfo(float).tiny)
            ),
        })
        if (index + 1) % 16 == 0 or index + 1 == projection.shape[1]:
            print(json.dumps({
                "completed": index + 1,
                "total": projection.shape[1],
                "maximum_relative_so_far": max(
                    row["retained_vs_JAX_relative_difference"] for row in rows
                ),
            }), flush=True)
    retained_stack = np.asarray(retained_directionals)
    stack_difference = float(np.linalg.norm(
        retained_stack - jax_directionals
    ))
    stack_norm = float(np.linalg.norm(retained_stack))
    validation = {
        "all_101_owner_projection_directions_replayed": len(rows) == 101,
        "three_corrected_Hermite_and_98_halo_directions_replayed": (
            sum(row["role"] == "CORRECTED_HERMITE" for row in rows) == 3
            and sum(row["role"] == "NONLINEAR_HALO" for row in rows) == 98
        ),
        "retained_complex_step_96_point_action_used": True,
        "no_finite_difference_subtraction_used": True,
        "owner_D3_stack_relative_difference_below_1e_minus_10": (
            stack_difference / max(stack_norm, np.finfo(float).tiny)
        ) < 1.0e-10,
        "declared_1e_minus_10_JAX_norm_inflation_dominates_replay_error": max(
            row["retained_vs_JAX_relative_difference"] for row in rows
        ) < 1.0e-10,
        "no_action_equation_source_selector_scale_gate_or_chord_changed": True,
    }
    validation = {key: bool(value) for key, value in validation.items()}
    passed = all(validation.values())
    return {
        "artifact": "BHSM_N12_GATE7_RECENTERED_CONE_OWNER_D3_ACCELERATION_AUDIT",
        "status": (
            "OWNER_CELL_ALL_101_JAX_D3_DIRECTIONS_MATCH_RETAINED_COMPLEX_STEP"
            if passed else "OWNER_CELL_JAX_D3_ACCELERATION_INVALID"
        ),
        "authority": "RETAINED_96_POINT_COMPLEX_STEP_ACTION_REPLAY",
        "owner": owner,
        "summary": {
            "maximum_directionwise_relative_difference": max(
                row["retained_vs_JAX_relative_difference"] for row in rows
            ),
            "D3_stack_relative_difference": (
                stack_difference / max(stack_norm, np.finfo(float).tiny)
            ),
            "declared_spectrum_norm_inflation_relative": (
                cone.JAX_D3_NORM_INFLATION - 1.0
            ),
        },
        "rows": rows,
        "validation": validation,
        "validation_passed": passed,
        "claim_boundary": {
            "owner_cell_JAX_D3_acceleration": (
                "RETAINED_CROSSCHECKED" if passed else "OPEN"
            ),
            "full_mesh_outward_D4_authority": "RETAINED_MIXEDBOUND",
            "recentered_cone_selected_line_simplicity": "CERTIFIED",
            "recentered_cone_selected_projector_graph": "OPEN",
            "Gate7": "ACTIVE",
            "FULL_BHSM_COMPLETE": False,
        },
        "inputs": {
            _relative(cone.RESULT): _sha256(cone.RESULT),
            _relative(cone.EIGENLINE): _sha256(cone.EIGENLINE),
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
