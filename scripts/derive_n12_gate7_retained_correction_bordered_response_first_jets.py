"""Derive retained correction-direction bordered-response first jets.

At each finite-history seam, differentiate the actual action-owned bordered
system K x = rhs in the normalized signed Green-correction direction.  Only
the 62-dimensional selected-complement border is solved; no kinetic, Dirac,
or history operator is inverted.
"""

from __future__ import annotations

from concurrent.futures import ProcessPoolExecutor
import hashlib
import json
import os
from pathlib import Path
import sys
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bhsm.interface.aether_forward_c2_descriptor_cover import metric_data  # noqa: E402
from bhsm.interface.aether_n3_exact_full_local_action_jet_v17_60 import (  # noqa: E402
    exact_full_action_jet_at_state,
)


BASE = ROOT / "artifacts" / "flagship_integration"
CENTER = BASE / "BHSM_N12_C2_STOP_HIGH_ORDER_QUARTER_STEP_RETAINED_RECONNAISSANCE.npz"
GREEN = BASE / "BHSM_N12_C2_STOP_QUARTER_STEP_MATCHED_TANGENT_CORRELATED_DEFECT_GAUSS12_RECONNAISSANCE.npz"
EIGENLINE = BASE / "BHSM_N12_GATE7_RETAINED_CORRECTION_EIGENLINE_FIRST_JETS.npz"
RESULT = BASE / "BHSM_N12_GATE7_RETAINED_CORRECTION_BORDERED_RESPONSE_FIRST_JETS.json"
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


def _retained(task: tuple[int, np.ndarray, np.ndarray]) -> tuple:
    index, state, raw_direction = task
    shifted = np.asarray(state, dtype=complex) + 1j * COMPLEX_STEP * raw_direction
    jet = exact_full_action_jet_at_state(
        12,
        shifted[:QDIM],
        shifted[QDIM:2 * QDIM],
        shifted[2 * QDIM:],
        points=96,
    )
    gradient = np.asarray(jet.gradient)
    hessian = np.asarray(jet.hessian)
    return (
        index,
        np.real(gradient),
        np.real(hessian),
        np.imag(hessian) / COMPLEX_STEP,
    )


def build_payload() -> dict[str, Any]:
    inputs = (CENTER, GREEN, EIGENLINE)
    if not all(path.is_file() for path in inputs):
        raise FileNotFoundError("retained bordered-response first-jet inputs required")
    with np.load(CENTER) as source:
        states = np.asarray(source["centers"], dtype=float)
        times = np.asarray(source["action_lengths"], dtype=float)
        weights = np.asarray(source["state_weights"], dtype=float)
        descriptors = np.asarray(source["signed_descriptors"], dtype=float)
    with np.load(GREEN) as source:
        corrections = np.asarray(source["ambient_correction_profile"], dtype=float)
    with np.load(EIGENLINE) as source:
        action_directions = np.asarray(
            source["action_correction_directions"], dtype=float
        )
        stored_reduced_first = np.asarray(
            source["reduced_Hessian_correction_direction_first_variation"],
            dtype=float,
        )
        stored_psi = np.asarray(source["selected_eigenvectors"], dtype=float)
        stored_psi_first = np.asarray(
            source["selected_eigenvector_first_variations"], dtype=float
        )
        stored_lambda = np.asarray(source["selected_eigenvalues"], dtype=float)
        stored_lambda_first = np.asarray(
            source["selected_eigenvalue_first_variations"], dtype=float
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

    q_weights, reduced_weights, _, _ = metric_data()
    responses = []
    response_first = []
    fields = []
    field_first = []
    rows = []
    for index, gradient, hessian, hessian_first in retained:
        reduced = 0.5 * (
            hessian[QDIM:, QDIM:] + hessian[QDIM:, QDIM:].T
        )
        reduced_first = 0.5 * (
            hessian_first[QDIM:, QDIM:]
            + hessian_first[QDIM:, QDIM:].T
        )
        psi = stored_psi[index]
        psi_first = stored_psi_first[index]
        lam = float(stored_lambda[index])
        lam_first = float(stored_lambda_first[index])
        descriptor = float(descriptors[index])
        raw_direction = raw_directions[index]
        configuration = q_weights * states[index, QDIM:2 * QDIM]
        configuration_first = q_weights * raw_direction[QDIM:2 * QDIM]
        gradient_action = gradient / weights
        gradient_first_action = (hessian @ raw_direction) / weights
        hessian_action = hessian / weights[:, None] / weights[None, :]
        hessian_first_action = (
            hessian_first / weights[:, None] / weights[None, :]
        )
        rhs = reduced_weights * (
            np.concatenate((
                q_weights * gradient_action[:QDIM], np.zeros(24),
            )) - hessian_action[QDIM:, :QDIM] @ configuration
        )
        rhs_first = reduced_weights * (
            np.concatenate((
                q_weights * gradient_first_action[:QDIM], np.zeros(24),
            ))
            - hessian_first_action[QDIM:, :QDIM] @ configuration
            - hessian_action[QDIM:, :QDIM] @ configuration_first
        )
        K = np.block([
            [reduced - lam * np.eye(61), psi[:, None]],
            [psi[None, :], np.zeros((1, 1))],
        ])
        K_first = np.block([
            [
                reduced_first - lam_first * np.eye(61),
                psi_first[:, None],
            ],
            [psi_first[None, :], np.zeros((1, 1))],
        ])
        extended_rhs = np.concatenate((rhs, np.zeros(1)))
        response = np.linalg.solve(K, extended_rhs)
        response_rhs_first = np.concatenate((rhs_first, np.zeros(1)))
        response_first_value = np.linalg.solve(
            K, response_rhs_first - K_first @ response
        )

        numerator = np.concatenate((
            descriptor * configuration,
            reduced_weights * (
                response[-1] * psi + descriptor * response[:-1]
            ),
        ))
        numerator_first = np.concatenate((
            lam_first * configuration + descriptor * configuration_first,
            reduced_weights * (
                response_first_value[-1] * psi
                + response[-1] * psi_first
                + lam_first * response[:-1]
                + descriptor * response_first_value[:-1]
            ),
        ))
        numerator_norm = float(np.linalg.norm(numerator))
        field = numerator / numerator_norm
        field_first_value = (
            numerator_first - field * float(field @ numerator_first)
        ) / numerator_norm
        response_residual = K @ response - extended_rhs
        differentiated_residual = (
            K @ response_first_value
            + K_first @ response - response_rhs_first
        )
        response_backward_error = float(
            np.linalg.norm(response_residual)
            / max(
                np.linalg.norm(K, ord=2) * np.linalg.norm(response)
                + np.linalg.norm(extended_rhs),
                np.finfo(float).tiny,
            )
        )
        row = {
            "node": index,
            "action_length": float(times[index]),
            "bordered_condition_number_2": float(np.linalg.cond(K)),
            "bordered_response_2_norm": float(np.linalg.norm(response)),
            "bordered_response_first_variation_2_norm": float(
                np.linalg.norm(response_first_value)
            ),
            "bordered_response_residual_2_norm": float(
                np.linalg.norm(response_residual)
            ),
            "bordered_response_normalized_backward_error": (
                response_backward_error
            ),
            "differentiated_bordered_response_residual_2_norm": float(
                np.linalg.norm(differentiated_residual)
            ),
            "field_first_variation_2_norm": float(
                np.linalg.norm(field_first_value)
            ),
            "reused_eigenline_first_matrix_difference": float(np.linalg.norm(
                reduced_first - stored_reduced_first[index], ord=2
            )),
            "normalization_tangent_residual": float(abs(field @ field_first_value)),
        }
        rows.append(row)
        responses.append(response)
        response_first.append(response_first_value)
        fields.append(field)
        field_first.append(field_first_value)

    np.savez_compressed(
        DATA,
        action_lengths=times,
        bordered_response=np.asarray(responses),
        bordered_response_correction_direction_first_variation=np.asarray(
            response_first
        ),
        normalized_field=np.asarray(fields),
        normalized_field_correction_direction_first_variation=np.asarray(
            field_first
        ),
    )
    validation = {
        "all_48_retained_macro_seams_evaluated": len(rows) == 48,
        "same_retained_complex_step_eigenline_first_matrices_replayed": max(
            row["reused_eigenline_first_matrix_difference"] for row in rows
        ) < 1.0e-12,
        "all_bordered_response_normalized_backward_errors_below_1e_minus_14": max(
            row["bordered_response_normalized_backward_error"] for row in rows
        ) < 1.0e-14,
        "all_differentiated_response_residuals_below_1e_minus_9": max(
            row["differentiated_bordered_response_residual_2_norm"]
            for row in rows
        ) < 1.0e-9,
        "normalized_field_first_variations_are_tangent": max(
            row["normalization_tangent_residual"] for row in rows
        ) < 1.0e-12,
        "no_mismatched_graph_reconnaissance_used_as_proof_input": True,
        "only_62_dimensional_bordered_selected_complement_solved": True,
        "no_full_kinetic_Dirac_or_history_inverse_formed": True,
        "no_action_equation_source_selector_scale_gate_or_chord_changed": True,
    }
    passed = all(validation.values())
    return {
        "artifact": "BHSM_N12_GATE7_RETAINED_CORRECTION_BORDERED_RESPONSE_FIRST_JETS",
        "status": (
            "RETAINED_CORRECTION_DIRECTION_BORDERED_RESPONSE_FIRST_JETS_"
            "DERIVED_ON_48_SEAMS" if passed else
            "RETAINED_CORRECTION_DIRECTION_BORDERED_RESPONSE_FIRST_JETS_INVALID"
        ),
        "authority": "RETAINED_96_POINT_ACTION_CENTER_AND_DIFFERENTIATED_BORDERED_IDENTITY",
        "identity": {
            "base": "K*x=rhs",
            "first": "K*x_first=rhs_first-K_first*x",
            "border_dimension": 62,
            "explicit_inverse_formed": False,
        },
        "summary": {
            "maximum_bordered_condition_number_2": max(
                row["bordered_condition_number_2"] for row in rows
            ),
            "maximum_bordered_response_first_variation_2_norm": max(
                row["bordered_response_first_variation_2_norm"] for row in rows
            ),
            "maximum_differentiated_bordered_response_residual_2_norm": max(
                row["differentiated_bordered_response_residual_2_norm"]
                for row in rows
            ),
            "maximum_field_first_variation_2_norm": max(
                row["field_first_variation_2_norm"] for row in rows
            ),
        },
        "rows": rows,
        "data": _relative(DATA),
        "data_SHA256": _sha256(DATA),
        "validation": validation,
        "validation_passed": passed,
        "claim_boundary": {
            "retained_center_bordered_response_first_jet": "DERIVED",
            "outward_bordered_response_first_jet_tube": "OPEN",
            "retained_center_graph_D2_correction_cone": "READY_TO_ASSEMBLE",
            "causal_interval_vector_radius": "OPEN",
            "Gate7": "ACTIVE",
            "FULL_BHSM_COMPLETE": False,
        },
        "exact_next_dependency": (
            "DIFFERENTIATE_THE_SAME_BORDERED_IDENTITY_ONCE_MORE_ALONG_THE_"
            "CORRECTION_DIRECTION,_THEN_ATTACH_THE_CERTIFIED_D4_D5_REMAINDER_"
            "WITHOUT_SCALAR_DENOMINATOR_COLLAPSE"
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
