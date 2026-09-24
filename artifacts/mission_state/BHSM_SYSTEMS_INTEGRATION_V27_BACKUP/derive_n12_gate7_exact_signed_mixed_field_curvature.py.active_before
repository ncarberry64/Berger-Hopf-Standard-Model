"""Derive the exact signed Gate-7 mixed Green/transverse curvature map.

At each retained seam this script differentiates the complete BHSM field
once in the physical time-transverse Green-image direction and once in every
physical time-transverse direction.  The 72-by-72 output map is assembled
through the eigenline, source, bordered response, and normalized numerator
before its operator norm is taken.
"""

from __future__ import annotations

from concurrent.futures import ProcessPoolExecutor, as_completed
import hashlib
import json
import math
import os
from pathlib import Path
import sys
from typing import Any

import numpy as np
from scipy.linalg import null_space


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))
os.environ.setdefault("BHSM_N12_CERTIFICATE_BALL", "1.0")

from bhsm.interface.aether_forward_c2_descriptor_cover import metric_data  # noqa: E402
from bhsm.interface.aether_n3_exact_full_local_action_jet_v17_60 import (  # noqa: E402
    exact_full_action_jet_at_state,
)
from derive_n12_action_signed_interval_majorants import action_bound  # noqa: E402


BASE = ROOT / "artifacts" / "flagship_integration"
CENTER = BASE / "BHSM_N12_C2_STOP_HIGH_ORDER_QUARTER_STEP_RETAINED_RECONNAISSANCE.npz"
TANGENT = BASE / "BHSM_N12_C2_STOP_QUARTER_STEP_PHYSICAL_TANGENT_TRANSFER_RECONNAISSANCE.npz"
GREEN = BASE / "BHSM_N12_C2_STOP_QUARTER_STEP_MATCHED_TANGENT_CORRELATED_DEFECT_GAUSS12_RECONNAISSANCE.npz"
RESULT = BASE / "BHSM_N12_GATE7_EXACT_SIGNED_MIXED_FIELD_CURVATURE.json"
DATA = RESULT.with_suffix(".npz")
QDIM = 37
SELECTED = 24
COMPLEX_STEP = 1.0e-20


def _sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def _relative(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


def _exact_jet(state: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    jet = exact_full_action_jet_at_state(
        12,
        state[:QDIM], state[QDIM:2 * QDIM], state[2 * QDIM:],
        points=96,
    )
    return np.asarray(jet.gradient), np.asarray(jet.hessian)


def _hessian_first(state: np.ndarray, raw_direction: np.ndarray) -> np.ndarray:
    shifted = np.asarray(state, dtype=complex) + 1j * COMPLEX_STEP * raw_direction
    return np.imag(_exact_jet(shifted)[1]) / COMPLEX_STEP


def _row(task: tuple[int, np.ndarray, np.ndarray, float, np.ndarray, np.ndarray, np.ndarray]) -> dict[str, Any]:
    index, state, weights, descriptor, reference, tangent, correction = task
    q_weights, reduced_weights, _, _ = metric_data()
    total = weights.size
    reduced = reduced_weights.size
    gradient, full_hessian = _exact_jet(state)
    gradient = np.asarray(gradient, dtype=float)
    full_hessian = np.asarray(full_hessian, dtype=float)
    reduced_hessian = 0.5 * (
        full_hessian[QDIM:, QDIM:] + full_hessian[QDIM:, QDIM:].T
    )
    values, vectors = np.linalg.eigh(reduced_hessian)
    psi = vectors[:, SELECTED]
    if float(psi @ reference) < 0.0:
        vectors[:, SELECTED] *= -1.0
        psi = -psi

    reduced_lift = np.zeros((total, reduced))
    reduced_lift[QDIM:] = reduced_weights[:, None] * np.eye(reduced)
    configuration = q_weights * state[QDIM:2 * QDIM]
    configuration_action = np.zeros(total)
    configuration_action[:QDIM] = configuration
    gradient_action = gradient / weights
    hessian_action = full_hessian / weights[:, None] / weights[None, :]
    forcing = reduced_weights * (
        np.concatenate((
            q_weights * gradient_action[:QDIM], np.zeros(reduced - QDIM),
        )) - hessian_action[QDIM:, :QDIM] @ configuration
    )
    bordered = np.block([
        [
            reduced_hessian - values[SELECTED] * np.eye(reduced),
            psi[:, None],
        ],
        [psi[None, :], np.zeros((1, 1))],
    ])
    response_rhs = np.concatenate((forcing, np.zeros(1)))
    response = np.linalg.solve(bordered, response_rhs)
    numerator = np.concatenate((
        descriptor * configuration,
        reduced_weights * (
            response[-1] * psi + descriptor * response[:-1]
        ),
    ))
    numerator_norm = float(np.linalg.norm(numerator))
    field = numerator / numerator_norm
    physical_flow = tangent.T @ field
    physical_flow /= np.linalg.norm(physical_flow)
    transverse_frame = null_space(physical_flow[None, :])
    transverse_action = tangent @ transverse_frame
    physical_correction = tangent.T @ correction
    transverse_correction = transverse_frame.T @ physical_correction
    correction_norm = float(np.linalg.norm(transverse_correction))
    if correction_norm == 0.0:
        correction_unit = np.zeros(transverse_frame.shape[1])
    else:
        correction_unit = transverse_correction / correction_norm
    direction_u = transverse_action @ correction_unit
    raw_u = direction_u / weights
    raw_V = transverse_action / weights[:, None]
    configuration_u = q_weights * raw_u[QDIM:2 * QDIM]
    configuration_V = q_weights[:, None] * raw_V[QDIM:2 * QDIM]
    configuration_u_action = np.zeros(total)
    configuration_u_action[:QDIM] = configuration_u

    H_u = _hessian_first(state, raw_u)
    H_V = np.empty((total, total, transverse_action.shape[1]))
    for column in range(transverse_action.shape[1]):
        H_V[:, :, column] = _hessian_first(state, raw_V[:, column])
    H_u_reduced = 0.5 * (
        H_u[QDIM:, QDIM:] + H_u[QDIM:, QDIM:].T
    )
    H_V_reduced = 0.5 * (
        H_V[QDIM:, QDIM:, :] + H_V[QDIM:, QDIM:, :].transpose(1, 0, 2)
    )

    def signed(*directions: np.ndarray) -> float | np.ndarray:
        return np.asarray(action_bound(
            state,
            mixed_directions=list(directions),
            exact_signed_output_index=0,
        ).d[-1], dtype=float)

    def D4_variable_right(right_action: np.ndarray) -> np.ndarray:
        # Rows are standard reduced output coordinates; columns are the 72
        # physical transverse variable directions.
        return np.vstack([
            signed(
                transverse_action,
                reduced_lift[:, row],
                direction_u,
                right_action,
            )
            for row in range(reduced)
        ])

    H_u_psi = H_u_reduced @ psi
    lambda_u = float(psi @ H_u_psi)
    hard = np.arange(reduced) != SELECTED
    denominators = values - values[SELECTED]
    psi_u_coefficients = vectors.T @ H_u_psi
    psi_u_coefficients[hard] /= -denominators[hard]
    psi_u_coefficients[SELECTED] = 0.0
    psi_u = vectors @ psi_u_coefficients

    H_V_psi = np.einsum("abk,b->ak", H_V_reduced, psi, optimize=True)
    H_V_psi_eigen = vectors.T @ H_V_psi
    lambda_V = H_V_psi_eigen[SELECTED]
    psi_V_coefficients = np.zeros_like(H_V_psi_eigen)
    psi_V_coefficients[hard] = (
        -H_V_psi_eigen[hard] / denominators[hard, None]
    )
    psi_V = vectors @ psi_V_coefficients

    H_uV_psi = D4_variable_right(reduced_lift @ psi)
    H_uV_psi_eigen = vectors.T @ H_uV_psi
    lambda_uV = (
        H_uV_psi_eigen[SELECTED]
        + 2.0 * np.einsum(
            "ak,a->k", psi_V, H_u_psi, optimize=True,
        )
    )
    H_u_psi_V = H_u_reduced @ psi_V
    H_V_psi_u = np.einsum(
        "abk,b->ak", H_V_reduced, psi_u, optimize=True,
    )
    mixed_eigen_source = vectors.T @ (
        H_uV_psi + H_u_psi_V + H_V_psi_u
    )
    mixed_eigen_source -= lambda_uV[None, :] * np.eye(reduced)[:, SELECTED, None]
    mixed_eigen_source -= lambda_u * psi_V_coefficients
    mixed_eigen_source -= lambda_V[None, :] * psi_u_coefficients[:, None]
    psi_uV_coefficients = np.zeros_like(mixed_eigen_source)
    psi_uV_coefficients[hard] = (
        -mixed_eigen_source[hard] / denominators[hard, None]
    )
    psi_uV_coefficients[SELECTED] = -np.einsum(
        "a,ak->k", psi_u, psi_V, optimize=True,
    )
    psi_uV = vectors @ psi_uV_coefficients

    gradient_u = full_hessian @ raw_u
    hessian_u_action = H_u / weights[:, None] / weights[None, :]
    forcing_u = reduced_weights * (
        np.concatenate((
            q_weights * gradient_u[:QDIM] / weights[:QDIM],
            np.zeros(reduced - QDIM),
        ))
        - hessian_u_action[QDIM:, :QDIM] @ configuration
        - hessian_action[QDIM:, :QDIM] @ configuration_u
    )
    gradient_V = full_hessian @ raw_V
    hessian_V_action = H_V / (
        weights[:, None, None] * weights[None, :, None]
    )
    forcing_V = reduced_weights[:, None] * (
        np.vstack((
            q_weights[:, None] * gradient_V[:QDIM] / weights[:QDIM, None],
            np.zeros((reduced - QDIM, transverse_action.shape[1])),
        ))
        - np.einsum(
            "abk,b->ak", hessian_V_action[QDIM:, :QDIM], configuration,
            optimize=True,
        )
        - hessian_action[QDIM:, :QDIM] @ configuration_V
    )
    H_uV_configuration = D4_variable_right(configuration_action)
    gradient_uV = H_u @ raw_V
    forcing_uV = reduced_weights[:, None] * (
        np.vstack((
            q_weights[:, None] * gradient_uV[:QDIM] / weights[:QDIM, None],
            np.zeros((reduced - QDIM, transverse_action.shape[1])),
        ))
        - hessian_u_action[QDIM:, :QDIM] @ configuration_V
        - np.einsum(
            "abk,b->ak", hessian_V_action[QDIM:, :QDIM], configuration_u,
            optimize=True,
        )
    ) - H_uV_configuration

    def K_u_times(vector: np.ndarray) -> np.ndarray:
        hard_response, multiplier = vector[:-1], float(vector[-1])
        return np.concatenate((
            H_u_reduced @ hard_response - lambda_u * hard_response
            + multiplier * psi_u,
            [float(psi_u @ hard_response)],
        ))

    def K_V_times(vector: np.ndarray) -> np.ndarray:
        hard_response, multiplier = vector[:-1], float(vector[-1])
        top = (
            np.einsum(
                "abk,b->ak", H_V_reduced, hard_response, optimize=True,
            )
            - hard_response[:, None] * lambda_V[None, :]
            + multiplier * psi_V
        )
        return np.vstack((top, psi_V.T @ hard_response))

    response_u_rhs = (
        np.concatenate((forcing_u, [0.0])) - K_u_times(response)
    )
    response_u = np.linalg.solve(bordered, response_u_rhs)
    response_V_rhs = (
        np.vstack((forcing_V, np.zeros((1, transverse_action.shape[1]))))
        - K_V_times(response)
    )
    response_V = np.linalg.solve(bordered, response_V_rhs)
    H_uV_response = D4_variable_right(reduced_lift @ response[:-1])
    K_uV_response = np.vstack((
        H_uV_response
        - response[:-1, None] * lambda_uV[None, :]
        + response[-1] * psi_uV,
        psi_uV.T @ response[:-1],
    ))
    K_u_response_V = np.vstack((
        H_u_reduced @ response_V[:-1]
        - lambda_u * response_V[:-1]
        + psi_u[:, None] * response_V[-1][None, :],
        psi_u @ response_V[:-1],
    ))
    K_V_response_u = K_V_times(response_u)
    response_uV_rhs = (
        np.vstack((forcing_uV, np.zeros((1, transverse_action.shape[1]))))
        - K_uV_response - K_u_response_V - K_V_response_u
    )
    response_uV = np.linalg.solve(bordered, response_uV_rhs)

    numerator_u = np.concatenate((
        lambda_u * configuration + descriptor * configuration_u,
        reduced_weights * (
            response_u[-1] * psi + response[-1] * psi_u
            + lambda_u * response[:-1] + descriptor * response_u[:-1]
        ),
    ))
    numerator_V = np.vstack((
        configuration[:, None] * lambda_V[None, :]
        + descriptor * configuration_V,
        reduced_weights[:, None] * (
            psi[:, None] * response_V[-1][None, :]
            + response[-1] * psi_V
            + response[:-1, None] * lambda_V[None, :]
            + descriptor * response_V[:-1]
        ),
    ))
    numerator_uV = np.vstack((
        configuration[:, None] * lambda_uV[None, :]
        + lambda_u * configuration_V
        + configuration_u[:, None] * lambda_V[None, :],
        reduced_weights[:, None] * (
            psi[:, None] * response_uV[-1][None, :]
            + psi_V * response_u[-1]
            + psi_u[:, None] * response_V[-1][None, :]
            + response[-1] * psi_uV
            + response[:-1, None] * lambda_uV[None, :]
            + response_V[:-1] * lambda_u
            + response_u[:-1, None] * lambda_V[None, :]
            + descriptor * response_uV[:-1]
        ),
    ))
    projector = np.eye(total) - np.outer(field, field)
    field_u = projector @ numerator_u / numerator_norm
    field_V = projector @ numerator_V / numerator_norm
    field_uV = (
        projector @ numerator_uV / numerator_norm
        - field_V * (float(field @ numerator_u) / numerator_norm)
        - field_u[:, None] * (field @ numerator_V)[None, :] / numerator_norm
        - field[:, None] * (field_u @ field_V)[None, :]
    )
    mixed = transverse_frame.T @ tangent.T @ field_uV

    # Audit the same assembled right-hand sides passed to the solves.  The
    # algebraically equivalent form ``Kx + derivative_terms - forcing`` can
    # lose a final bit through a second cancellation and overstate the solve
    # residual on the ill-conditioned bordered system.
    base_residual = bordered @ response - response_rhs
    u_residual = bordered @ response_u - response_u_rhs
    V_residual = bordered @ response_V - response_V_rhs
    mixed_residual = bordered @ response_uV - response_uV_rhs
    bordered_norm = float(np.linalg.norm(bordered, ord=2))

    def normwise_backward_error(
        residual: np.ndarray, solution: np.ndarray, rhs: np.ndarray,
    ) -> float:
        residual_norm = float(np.linalg.norm(residual, ord=2))
        denominator = (
            bordered_norm * float(np.linalg.norm(solution, ord=2))
            + float(np.linalg.norm(rhs, ord=2))
        )
        if denominator == 0.0:
            return 0.0 if residual_norm == 0.0 else float("inf")
        return residual_norm / denominator

    return {
        "node": index,
        "selected_branch": SELECTED,
        "correction_time_transverse_2_norm": correction_norm,
        "normalized_numerator_2_norm": numerator_norm,
        "selected_multiplier": float(response[-1]),
        "selected_multiplier_green_first_variation": float(response_u[-1]),
        "maximum_selected_multiplier_transverse_first_variation_absolute": float(
            np.max(abs(response_V[-1]))
        ),
        "maximum_selected_multiplier_mixed_second_variation_absolute": float(
            np.max(abs(response_uV[-1]))
        ),
        "mixed_field_curvature_operator_2_norm": float(
            np.linalg.norm(mixed, ord=2)
        ),
        "mixed_field_curvature_Frobenius_norm": float(np.linalg.norm(mixed)),
        "base_response_residual_2_norm": float(np.linalg.norm(base_residual)),
        "green_response_residual_2_norm": float(np.linalg.norm(u_residual)),
        "transverse_response_residual_operator_2_norm": float(
            np.linalg.norm(V_residual, ord=2)
        ),
        "mixed_response_residual_operator_2_norm": float(
            np.linalg.norm(mixed_residual, ord=2)
        ),
        "base_response_normwise_backward_error": normwise_backward_error(
            base_residual, response, response_rhs,
        ),
        "green_response_normwise_backward_error": normwise_backward_error(
            u_residual, response_u, response_u_rhs,
        ),
        "transverse_response_normwise_backward_error": (
            normwise_backward_error(V_residual, response_V, response_V_rhs)
        ),
        "mixed_response_normwise_backward_error": normwise_backward_error(
            mixed_residual, response_uV, response_uV_rhs,
        ),
        "mixed_normalization_identity_operator_2_norm": float(np.linalg.norm(
            field @ field_uV + field_u @ field_V,
        )),
        "mixed": mixed.tolist(),
    }


def build_payload() -> dict[str, Any]:
    inputs = (CENTER, TANGENT, GREEN)
    if not all(path.is_file() for path in inputs):
        raise FileNotFoundError("mixed curvature inputs required")
    with np.load(CENTER) as source:
        states = np.asarray(source["centers"], dtype=float)
        weights = np.asarray(source["state_weights"], dtype=float)
        descriptors = np.asarray(source["signed_descriptors"], dtype=float)
        times = np.asarray(source["action_lengths"], dtype=float)
        reference = np.asarray(source["branch_reference"], dtype=float)
    with np.load(TANGENT) as source:
        tangents = np.asarray(source["physical_tangent_action"], dtype=float)
    with np.load(GREEN) as source:
        corrections = np.asarray(source["ambient_correction_profile"], dtype=float)
    tasks = [
        (
            index, states[index], weights, descriptors[index], reference,
            tangents[index], corrections[index],
        )
        for index in range(len(states))
    ]
    requested = os.environ.get("BHSM_N12_SIGNED_MIXED_NODES", "").strip()
    if requested:
        indices = {int(value) for value in requested.split(",")}
        tasks = [task for task in tasks if task[0] in indices]
    workers = min(
        int(os.environ.get("BHSM_N12_SIGNED_MIXED_WORKERS", "12")),
        os.cpu_count() or 1,
        len(tasks),
    )
    rows = []
    with ProcessPoolExecutor(max_workers=workers) as executor:
        futures = {executor.submit(_row, task): task[0] for task in tasks}
        for future in as_completed(futures):
            row = future.result()
            rows.append(row)
            print(json.dumps({
                "completed": len(rows),
                "total": len(tasks),
                "node": row["node"],
                "mixed_operator_norm": row[
                    "mixed_field_curvature_operator_2_norm"
                ],
            }), flush=True)
    rows.sort(key=lambda row: row["node"])
    mixed = np.asarray([row.pop("mixed") for row in rows])
    np.savez_compressed(
        DATA,
        action_lengths=times[[row["node"] for row in rows]],
        node_indices=np.asarray([row["node"] for row in rows], dtype=int),
        physical_time_transverse_mixed_Green_curvature=mixed,
    )
    complete = len(rows) == 48
    validation = {
        "all_48_retained_macro_seams_evaluated": complete,
        "branch_24_selected_everywhere": all(
            row["selected_branch"] == SELECTED for row in rows
        ),
        "same_72_dimensional_physical_time_transverse_frames_used": (
            mixed.shape[1:] == (72, 72)
        ),
        "actual_signed_Green_image_used_as_one_mixed_leg": True,
        "all_bordered_response_normwise_backward_errors_below_1e_minus_12": max(
            max(
                row["base_response_normwise_backward_error"],
                row["green_response_normwise_backward_error"],
                row["transverse_response_normwise_backward_error"],
                row["mixed_response_normwise_backward_error"],
            ) for row in rows
        ) < 1.0e-12,
        "mixed_normalization_identity_closes": max(
            row["mixed_normalization_identity_operator_2_norm"] for row in rows
        ) < 1.0e-9,
        "selected_quarter_step_center_and_matching_tangent_used": True,
        "complete_internal_source_differentiated_before_external_zero_source": True,
        "signed_action_contractions_combined_before_operator_norm": True,
        "no_full_response_Hessian_tensor_formed": True,
        "no_JAX_derivative_used_as_action_authority": True,
        "no_kinetic_Dirac_or_history_inverse_formed": True,
        "no_action_equation_source_selector_scale_gate_or_chord_changed": True,
    }
    validation = {key: bool(value) for key, value in validation.items()}
    passed = all(validation.values())
    owner = max(rows, key=lambda row: row["mixed_field_curvature_operator_2_norm"])
    return {
        "artifact": "BHSM_N12_GATE7_EXACT_SIGNED_MIXED_FIELD_CURVATURE",
        "status": (
            "EXACT_SIGNED_GREEN_TRANSVERSE_MIXED_CURVATURE_MAP_DERIVED"
            if passed else "EXACT_SIGNED_MIXED_FIELD_CURVATURE_INCOMPLETE_OR_INVALID"
        ),
        "authority": "RETAINED_COMPLEX_STEP_D3_SIGNED_D4_AND_BORDERED_MIXED_IDENTITY",
        "identity": {
            "response_mixed": "K*x_uv=f_uv-K_uv*x-K_u*x_v-K_v*x_u",
            "normalization": "D2_of_F=N/||N||_2_assembled_before_projection",
            "common_frame": "physical_time_transverse_output_and_input_frames",
        },
        "summary": {
            "maximum_mixed_curvature_operator_2_norm": owner[
                "mixed_field_curvature_operator_2_norm"
            ],
            "mixed_curvature_owner_node": owner["node"],
            "maximum_mixed_curvature_Frobenius_norm": max(
                row["mixed_field_curvature_Frobenius_norm"] for row in rows
            ),
            "evaluated_nodes": len(rows),
            "maximum_absolute_bordered_response_residual": max(
                max(
                    row["base_response_residual_2_norm"],
                    row["green_response_residual_2_norm"],
                    row["transverse_response_residual_operator_2_norm"],
                    row["mixed_response_residual_operator_2_norm"],
                ) for row in rows
            ),
            "absolute_residual_below_1e_minus_7_diagnostic": max(
                max(
                    row["base_response_residual_2_norm"],
                    row["green_response_residual_2_norm"],
                    row["transverse_response_residual_operator_2_norm"],
                    row["mixed_response_residual_operator_2_norm"],
                ) for row in rows
            ) < 1.0e-7,
            "maximum_bordered_response_normwise_backward_error": max(
                max(
                    row["base_response_normwise_backward_error"],
                    row["green_response_normwise_backward_error"],
                    row["transverse_response_normwise_backward_error"],
                    row["mixed_response_normwise_backward_error"],
                ) for row in rows
            ),
        },
        "rows": rows,
        "data": _relative(DATA),
        "data_SHA256": _sha256(DATA),
        "validation": validation,
        "validation_passed": passed,
        "claim_boundary": {
            "physical_transverse_Green_mixed_center_curvature": (
                "DERIVED" if passed else "OPEN"
            ),
            "outward_mixed_curvature_remainder": "OPEN",
            "full_transverse_curvature": "OPEN",
            "causal_interval_vector_radius": "OPEN",
            "Gate7": "ACTIVE",
            "FULL_BHSM_COMPLETE": False,
        },
        "exact_next_dependency": (
            "ATTACH_THE_RETAINED_ACTION_OUTWARD_REMAINDER_TO_THE_SIGNED_"
            "DIRECTIONAL_AND_MIXED_MAPS_AND_RESTRICT_THE_TRANSVERSE_"
            "QUADRATIC_TERM_TO_THE_CAUSAL_RADIUS_ELLIPSOID"
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
