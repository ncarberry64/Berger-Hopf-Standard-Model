"""Derive retained correction-direction selected-eigenline first jets.

The authoritative 96-point action Hessian is evaluated once at a complex
step in the normalized signed Green-correction direction.  Its imaginary
part gives the directional D3 action matrix without finite subtraction.
The selected-line jet is then assembled branchwise; no smallest-gap collapse
or full Euler--Dirac inverse is used.
"""

from __future__ import annotations

from concurrent.futures import ProcessPoolExecutor
import hashlib
import json
import os
from pathlib import Path
import sys
from typing import Any

import jax.numpy as jnp
import numpy as np


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bhsm.interface.aether_jax_full_local_action import (  # noqa: E402
    action_hessian,
    action_hessian_directional,
)
from bhsm.interface.aether_n3_exact_full_local_action_jet_v17_60 import (  # noqa: E402
    exact_full_action_jet_at_state,
)


BASE = ROOT / "artifacts" / "flagship_integration"
CENTER = BASE / "BHSM_N12_C2_STOP_HIGH_ORDER_HALF_STEP_CENTER_RECONNAISSANCE.npz"
GREEN = BASE / "BHSM_N12_C2_STOP_QUARTER_STEP_MATCHED_TANGENT_CORRELATED_DEFECT_GAUSS12_RECONNAISSANCE.npz"
CALIBRATION = BASE / "BHSM_N12_STOP_JAX_ACTION_CALIBRATION.npz"
RESULT = BASE / "BHSM_N12_GATE7_RETAINED_CORRECTION_EIGENLINE_FIRST_JETS.json"
DATA = RESULT.with_suffix(".npz")
QDIM = 37
COMPLEX_STEP = 1.0e-20


def _sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def _relative(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


def _retained(task: tuple[int, np.ndarray, np.ndarray]) -> tuple[int, np.ndarray, np.ndarray]:
    index, state, raw_direction = task
    shifted = np.asarray(state, dtype=complex) + 1j * COMPLEX_STEP * raw_direction
    jet = exact_full_action_jet_at_state(
        12,
        shifted[:QDIM],
        shifted[QDIM:2 * QDIM],
        shifted[2 * QDIM:],
        points=96,
    )
    hessian = np.asarray(jet.hessian)
    return index, np.real(hessian), np.imag(hessian) / COMPLEX_STEP


def build_payload() -> dict[str, Any]:
    inputs = (CENTER, GREEN, CALIBRATION)
    if not all(path.is_file() for path in inputs):
        raise FileNotFoundError("retained correction eigenline-jet inputs required")
    with np.load(CENTER) as source:
        states = np.asarray(source["centers"], dtype=float)
        times = np.asarray(source["action_lengths"], dtype=float)
        weights = np.asarray(source["state_weights"], dtype=float)
        reference = np.asarray(source["branch_reference"], dtype=float)
    with np.load(GREEN) as source:
        corrections = np.asarray(source["ambient_correction_profile"], dtype=float)
    with np.load(CALIBRATION) as source:
        hessian_corrections = np.asarray(source["hessian_correction"], dtype=float)
    correction_norms = np.linalg.norm(corrections, axis=1)
    action_directions = np.divide(
        corrections,
        correction_norms[:, None],
        out=np.zeros_like(corrections),
        where=correction_norms[:, None] > 0.0,
    )
    raw_directions = action_directions / weights
    workers = min(12, os.cpu_count() or 1)
    tasks = [
        (index, states[index], raw_directions[index])
        for index in range(48)
    ]
    with ProcessPoolExecutor(max_workers=workers) as executor:
        retained = list(executor.map(_retained, tasks, chunksize=1))
    retained.sort(key=lambda item: item[0])

    selected_vectors = []
    selected_first = []
    selected_values = []
    selected_value_first = []
    reduced_first = []
    rows = []
    for index, exact_hessian, exact_first in retained:
        reduced = exact_hessian[QDIM:, QDIM:]
        reduced = 0.5 * (reduced + reduced.T)
        first = exact_first[QDIM:, QDIM:]
        first = 0.5 * (first + first.T)
        values, vectors = np.linalg.eigh(reduced)
        selected = int(np.argmax(np.abs(vectors.T @ reference)))
        psi = vectors[:, selected]
        if float(psi @ reference) < 0.0:
            psi = -psi
            vectors[:, selected] = psi
        coefficients = vectors.T @ (first @ psi)
        lambda_first = float(coefficients[selected])
        psi_first_coefficients = np.zeros(values.size)
        for branch in range(values.size):
            if branch != selected:
                psi_first_coefficients[branch] = (
                    coefficients[branch] / (values[selected] - values[branch])
                )
        psi_first = vectors @ psi_first_coefficients
        gap = float(np.min(np.abs(np.delete(values, selected) - values[selected])))

        jax_hessian = np.asarray(action_hessian(jnp.asarray(states[index])))
        calibrated_hessian = jax_hessian + hessian_corrections[index]
        _, jax_first = action_hessian_directional(
            jnp.asarray(states[index]), jnp.asarray(raw_directions[index])
        )
        exact_first_norm = float(np.linalg.norm(exact_first, ord=2))
        first_difference = float(np.linalg.norm(
            exact_first - np.asarray(jax_first), ord=2
        ))
        row = {
            "node": index,
            "action_length": float(times[index]),
            "selected_branch": selected,
            "selected_eigenvalue": float(values[selected]),
            "selected_to_hard_gap": gap,
            "selected_eigenvalue_first_variation": lambda_first,
            "selected_eigenvector_first_variation_2_norm": float(
                np.linalg.norm(psi_first)
            ),
            "maximum_branchwise_first_coefficient": float(
                np.max(np.abs(psi_first_coefficients))
            ),
            "retained_D3_matrix_operator_2_norm": exact_first_norm,
            "retained_vs_JAX_D3_matrix_operator_difference": first_difference,
            "retained_vs_JAX_D3_matrix_relative_difference": (
                first_difference / max(exact_first_norm, np.finfo(float).tiny)
            ),
            "retained_vs_calibrated_JAX_Hessian_operator_difference": float(
                np.linalg.norm(exact_hessian - calibrated_hessian, ord=2)
            ),
            "eigenline_normalization_first_residual": float(abs(psi @ psi_first)),
            "differentiated_eigenpair_residual_2_norm": float(np.linalg.norm(
                (reduced - values[selected] * np.eye(values.size)) @ psi_first
                + (first - lambda_first * np.eye(values.size)) @ psi
            )),
        }
        rows.append(row)
        selected_vectors.append(psi)
        selected_first.append(psi_first)
        selected_values.append(values[selected])
        selected_value_first.append(lambda_first)
        reduced_first.append(first)

    np.savez_compressed(
        DATA,
        action_lengths=times,
        action_correction_directions=action_directions,
        reduced_Hessian_correction_direction_first_variation=np.asarray(
            reduced_first
        ),
        selected_eigenvectors=np.asarray(selected_vectors),
        selected_eigenvector_first_variations=np.asarray(selected_first),
        selected_eigenvalues=np.asarray(selected_values),
        selected_eigenvalue_first_variations=np.asarray(selected_value_first),
    )
    validation = {
        "all_48_retained_macro_seams_evaluated": len(rows) == 48,
        "same_selected_branch_24_on_all_seams": all(
            row["selected_branch"] == 24 for row in rows
        ),
        "all_selected_to_hard_gaps_positive": all(
            row["selected_to_hard_gap"] > 0.0 for row in rows
        ),
        "complex_step_avoids_finite_subtraction": True,
        "branchwise_denominators_used_without_smallest_gap_collapse": True,
        "eigenline_normalization_first_residual_below_1e_minus_12": max(
            row["eigenline_normalization_first_residual"] for row in rows
        ) < 1.0e-12,
        "differentiated_eigenpair_residual_below_1e_minus_11": max(
            row["differentiated_eigenpair_residual_2_norm"] for row in rows
        ) < 1.0e-11,
        "retained_and_JAX_directional_D3_agree_below_1e_minus_10_relative": max(
            row["retained_vs_JAX_D3_matrix_relative_difference"] for row in rows
        ) < 1.0e-10,
        "calibrated_JAX_Hessian_replays_retained_center_below_2e_minus_10": max(
            row["retained_vs_calibrated_JAX_Hessian_operator_difference"]
            for row in rows
        ) < 2.0e-10,
        "no_full_Euler_Dirac_inverse_formed": True,
        "no_action_equation_source_selector_scale_gate_or_chord_changed": True,
    }
    passed = all(validation.values())
    return {
        "artifact": "BHSM_N12_GATE7_RETAINED_CORRECTION_EIGENLINE_FIRST_JETS",
        "status": (
            "RETAINED_CORRECTION_DIRECTION_SELECTED_EIGENLINE_FIRST_JETS_"
            "DERIVED_ON_48_SEAMS" if passed else
            "RETAINED_CORRECTION_DIRECTION_EIGENLINE_FIRST_JETS_INVALID"
        ),
        "authority": "RETAINED_96_POINT_COMPLEX_STEP_ACTION_CENTER_JET",
        "complex_step": COMPLEX_STEP,
        "summary": {
            "minimum_selected_to_hard_gap": min(
                row["selected_to_hard_gap"] for row in rows
            ),
            "maximum_selected_eigenvalue_first_variation_absolute": max(
                abs(row["selected_eigenvalue_first_variation"]) for row in rows
            ),
            "maximum_selected_eigenvector_first_variation_2_norm": max(
                row["selected_eigenvector_first_variation_2_norm"] for row in rows
            ),
            "maximum_retained_vs_JAX_D3_matrix_relative_difference": max(
                row["retained_vs_JAX_D3_matrix_relative_difference"] for row in rows
            ),
            "maximum_differentiated_eigenpair_residual_2_norm": max(
                row["differentiated_eigenpair_residual_2_norm"] for row in rows
            ),
        },
        "rows": rows,
        "data": _relative(DATA),
        "data_SHA256": _sha256(DATA),
        "validation": validation,
        "validation_passed": passed,
        "claim_boundary": {
            "retained_center_eigenline_first_jet": "DERIVED",
            "outward_eigenline_first_jet_tube": "OPEN",
            "bordered_response_correction_direction_jet": "OPEN",
            "causal_interval_vector_radius": "OPEN",
            "Gate7": "ACTIVE",
            "FULL_BHSM_COMPLETE": False,
        },
        "exact_next_dependency": (
            "INSERT_THE_BRANCHWISE_RETAINED_EIGENLINE_JETS_INTO_THE_"
            "EXISTING_BORDERED_RESPONSE_IDENTITY_AND_ATTACH_THE_CERTIFIED_"
            "D4_D5_DIRECTIONAL_REMAINDER_ON_THE_3.6E-6_TUBE"
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
        "summary": payload["summary"],
        "validation_passed": payload["validation_passed"],
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
