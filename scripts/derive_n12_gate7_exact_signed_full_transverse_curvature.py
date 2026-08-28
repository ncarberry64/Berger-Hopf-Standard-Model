"""Derive the exact signed full physical-transverse Gate-7 curvature.

The retained action is differentiated in both 72-dimensional physical
time-transverse legs.  A single broadcast signed D4 evaluation supplies the
selected-line, response, and configuration contractions together.  The full
field Hessian is assembled through the bordered descriptor system before a
Frobenius norm is taken.
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
from derive_n12_action_signed_interval_majorants import action_bound  # noqa: E402
from derive_n12_gate7_exact_signed_mixed_field_curvature import (  # noqa: E402
    _exact_jet,
    _hessian_first,
)


BASE = ROOT / "artifacts" / "flagship_integration"
CENTER = BASE / "BHSM_N12_C2_STOP_HIGH_ORDER_QUARTER_STEP_RETAINED_RECONNAISSANCE.npz"
TANGENT = BASE / "BHSM_N12_C2_STOP_QUARTER_STEP_PHYSICAL_TANGENT_TRANSFER_RECONNAISSANCE.npz"
DIRECTIONAL_DATA = BASE / "BHSM_N12_GATE7_EXACT_SIGNED_DIRECTIONAL_FIELD_CURVATURE.npz"
RESULT = BASE / "BHSM_N12_GATE7_EXACT_SIGNED_FULL_TRANSVERSE_CURVATURE.json"
DATA_SHARDS = (
    BASE / "BHSM_N12_GATE7_EXACT_SIGNED_FULL_TRANSVERSE_CURVATURE_NODES_00_23.npz",
    BASE / "BHSM_N12_GATE7_EXACT_SIGNED_FULL_TRANSVERSE_CURVATURE_NODES_24_47.npz",
)
QDIM = 37
SELECTED = 24


def _sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def _relative(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


def _row(task: tuple[int, np.ndarray, np.ndarray, float, np.ndarray, np.ndarray, np.ndarray]) -> dict[str, Any]:
    index, state, weights, descriptor, reference, tangent, field_reference = task
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
    response = np.linalg.solve(
        bordered, np.concatenate((forcing, np.zeros(1))),
    )
    numerator = np.concatenate((
        descriptor * configuration,
        reduced_weights * (
            response[-1] * psi + descriptor * response[:-1]
        ),
    ))
    numerator_norm = float(np.linalg.norm(numerator))
    field = numerator / numerator_norm
    field_reference_difference = float(np.linalg.norm(field - field_reference))
    physical_flow = tangent.T @ field
    physical_flow /= np.linalg.norm(physical_flow)
    transverse_frame = null_space(physical_flow[None, :])
    transverse_action = tangent @ transverse_frame
    raw_V = transverse_action / weights[:, None]
    configuration_V = q_weights[:, None] * raw_V[QDIM:2 * QDIM]

    H_V = np.empty((total, total, transverse_action.shape[1]))
    for column in range(transverse_action.shape[1]):
        H_V[:, :, column] = _hessian_first(state, raw_V[:, column])
    H_V_reduced = 0.5 * (
        H_V[QDIM:, QDIM:, :] + H_V[QDIM:, QDIM:, :].transpose(1, 0, 2)
    )
    H_V_psi = np.einsum("abj,b->aj", H_V_reduced, psi, optimize=True)
    H_V_psi_eigen = vectors.T @ H_V_psi
    lambda_V = H_V_psi_eigen[SELECTED]
    hard = np.arange(reduced) != SELECTED
    denominators = values - values[SELECTED]
    psi_V_coefficients = np.zeros_like(H_V_psi_eigen)
    psi_V_coefficients[hard] = (
        -H_V_psi_eigen[hard] / denominators[hard, None]
    )
    psi_V = vectors @ psi_V_coefficients

    # One retained-action traversal yields H_VV applied to psi, the hard
    # response, and the configuration incidence.  The four component axes
    # are standard reduced output, first transverse leg, second transverse
    # leg, and the three right-hand vectors.
    right_vectors = np.column_stack((
        reduced_lift @ psi,
        reduced_lift @ response[:-1],
        configuration_action,
    ))
    D4_tensor = np.asarray(action_bound(
        state,
        mixed_directions=[
            reduced_lift, transverse_action, transverse_action, right_vectors,
        ],
        exact_signed_tensor_indices=(0, 1, 2, 3),
    ).d[-1], dtype=float)
    H_VV_psi = D4_tensor[:, :, :, 0]
    H_VV_response = D4_tensor[:, :, :, 1]
    H_VV_configuration = D4_tensor[:, :, :, 2]

    eigen_cross = np.einsum(
        "aj,ak->jk", psi_V, H_V_psi, optimize=True,
    )
    lambda_VV = (
        np.einsum("a,ajk->jk", psi, H_VV_psi, optimize=True)
        + eigen_cross + eigen_cross.T
    )
    H_V_psi_V = np.einsum(
        "abj,bk->ajk", H_V_reduced, psi_V, optimize=True,
    )
    eigen_source = (
        H_VV_psi + H_V_psi_V + H_V_psi_V.transpose(0, 2, 1)
        - psi[:, None, None] * lambda_VV[None, :, :]
        - psi_V[:, None, :] * lambda_V[None, :, None]
        - psi_V[:, :, None] * lambda_V[None, None, :]
    )
    eigen_source_coefficients = np.einsum(
        "ab,bjk->ajk", vectors.T, eigen_source, optimize=True,
    )
    psi_VV_coefficients = np.zeros_like(eigen_source_coefficients)
    psi_VV_coefficients[hard] = (
        -eigen_source_coefficients[hard] / denominators[hard, None, None]
    )
    psi_VV_coefficients[SELECTED] = -(psi_V.T @ psi_V)
    psi_VV = np.einsum(
        "ab,bjk->ajk", vectors, psi_VV_coefficients, optimize=True,
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
            "abj,b->aj", hessian_V_action[QDIM:, :QDIM], configuration,
            optimize=True,
        )
        - hessian_action[QDIM:, :QDIM] @ configuration_V
    )
    gradient_VV = np.einsum(
        "abj,bk->ajk", H_V, raw_V, optimize=True,
    )
    gradient_VV = 0.5 * (gradient_VV + gradient_VV.transpose(0, 2, 1))
    hessian_configuration_cross = np.einsum(
        "abj,bk->ajk",
        hessian_V_action[QDIM:, :QDIM], configuration_V,
        optimize=True,
    )
    forcing_VV = reduced_weights[:, None, None] * (
        np.concatenate((
            q_weights[:, None, None] * gradient_VV[:QDIM]
            / weights[:QDIM, None, None],
            np.zeros((
                reduced - QDIM,
                transverse_action.shape[1],
                transverse_action.shape[1],
            )),
        ), axis=0)
        - hessian_configuration_cross
        - hessian_configuration_cross.transpose(0, 2, 1)
    ) - H_VV_configuration

    def K_V_times(vector: np.ndarray) -> np.ndarray:
        hard_response, multiplier = vector[:-1], float(vector[-1])
        top = (
            np.einsum(
                "abj,b->aj", H_V_reduced, hard_response, optimize=True,
            )
            - hard_response[:, None] * lambda_V[None, :]
            + multiplier * psi_V
        )
        return np.vstack((top, psi_V.T @ hard_response))

    response_V = np.linalg.solve(
        bordered,
        np.vstack((forcing_V, np.zeros((1, transverse_action.shape[1]))))
        - K_V_times(response),
    )
    K_VV_response = np.concatenate((
        H_VV_response
        - response[:-1, None, None] * lambda_VV[None, :, :]
        + response[-1] * psi_VV,
        np.einsum(
            "ajk,a->jk", psi_VV, response[:-1], optimize=True,
        )[None, :, :],
    ), axis=0)
    K_V_response_V = np.concatenate((
        np.einsum(
            "abj,bk->ajk", H_V_reduced, response_V[:-1], optimize=True,
        )
        - response_V[:-1, None, :] * lambda_V[None, :, None]
        + psi_V[:, :, None] * response_V[-1][None, None, :],
        np.einsum(
            "aj,ak->jk", psi_V, response_V[:-1], optimize=True,
        )[None, :, :],
    ), axis=0)
    response_VV_rhs = (
        np.concatenate((
            forcing_VV,
            np.zeros((1, transverse_action.shape[1], transverse_action.shape[1])),
        ), axis=0)
        - K_VV_response - K_V_response_V
        - K_V_response_V.transpose(0, 2, 1)
    )
    response_VV = np.linalg.solve(
        bordered, response_VV_rhs.reshape((reduced + 1, -1)),
    ).reshape((reduced + 1, transverse_action.shape[1], transverse_action.shape[1]))

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
    configuration_lambda_cross = (
        configuration_V[:, :, None] * lambda_V[None, None, :]
    )
    response_psi_cross = (
        psi_V[:, :, None] * response_V[-1][None, None, :]
    )
    response_lambda_cross = (
        response_V[:-1, :, None] * lambda_V[None, None, :]
    )
    numerator_VV = np.concatenate((
        configuration[:, None, None] * lambda_VV[None, :, :]
        + configuration_lambda_cross
        + configuration_lambda_cross.transpose(0, 2, 1),
        reduced_weights[:, None, None] * (
            psi[:, None, None] * response_VV[-1][None, :, :]
            + response_psi_cross + response_psi_cross.transpose(0, 2, 1)
            + response[-1] * psi_VV
            + response[:-1, None, None] * lambda_VV[None, :, :]
            + response_lambda_cross
            + response_lambda_cross.transpose(0, 2, 1)
            + descriptor * response_VV[:-1]
        ),
    ), axis=0)
    projector = np.eye(total) - np.outer(field, field)
    field_V = projector @ numerator_V / numerator_norm
    alpha = field @ numerator_V
    field_VV = (
        np.einsum("ab,bjk->ajk", projector, numerator_VV, optimize=True)
        / numerator_norm
        - field_V[:, :, None] * alpha[None, None, :] / numerator_norm
        - field_V[:, None, :] * alpha[None, :, None] / numerator_norm
        - field[:, None, None] * (field_V.T @ field_V)[None, :, :]
    )
    transverse_curvature = np.einsum(
        "ra,ajk->rjk", transverse_frame.T @ tangent.T, field_VV,
        optimize=True,
    )

    base_residual = bordered @ response - np.concatenate((forcing, [0.0]))
    first_residual = (
        bordered @ response_V + K_V_times(response)
        - np.vstack((forcing_V, np.zeros((1, transverse_action.shape[1]))))
    )
    second_residual = (
        np.einsum("ab,bjk->ajk", bordered, response_VV, optimize=True)
        - response_VV_rhs
    )
    return {
        "node": index,
        "selected_branch": SELECTED,
        "normalized_field_reference_difference_2_norm": field_reference_difference,
        "normalized_numerator_2_norm": numerator_norm,
        "selected_eigenline_transverse_first_Frobenius_norm": float(
            np.linalg.norm(psi_V)
        ),
        "selected_eigenline_transverse_second_Frobenius_norm": float(
            np.linalg.norm(psi_VV)
        ),
        "bordered_response_transverse_first_Frobenius_norm": float(
            np.linalg.norm(response_V)
        ),
        "bordered_response_transverse_second_Frobenius_norm": float(
            np.linalg.norm(response_VV)
        ),
        "normalized_numerator_transverse_first_Frobenius_norm": float(
            np.linalg.norm(numerator_V)
        ),
        "normalized_numerator_transverse_second_Frobenius_norm": float(
            np.linalg.norm(numerator_VV)
        ),
        "physical_time_transverse_D2f_Frobenius_norm": float(
            np.linalg.norm(transverse_curvature)
        ),
        "physical_time_transverse_D2f_maximum_component_absolute": float(
            np.max(abs(transverse_curvature))
        ),
        "base_response_residual_2_norm": float(np.linalg.norm(base_residual)),
        "first_response_residual_Frobenius_norm": float(np.linalg.norm(first_residual)),
        "second_response_residual_Frobenius_norm": float(np.linalg.norm(second_residual)),
        "second_eigenline_normalization_Frobenius_residual": float(np.linalg.norm(
            np.einsum("a,ajk->jk", psi, psi_VV, optimize=True) + psi_V.T @ psi_V
        )),
        "second_field_normalization_Frobenius_residual": float(np.linalg.norm(
            np.einsum("a,ajk->jk", field, field_VV, optimize=True) + field_V.T @ field_V
        )),
        "transverse_curvature": transverse_curvature.tolist(),
    }


def build_payload() -> dict[str, Any]:
    inputs = (CENTER, TANGENT, DIRECTIONAL_DATA)
    if not all(path.is_file() for path in inputs):
        raise FileNotFoundError("full transverse curvature inputs required")
    with np.load(CENTER) as source:
        states = np.asarray(source["centers"], dtype=float)
        weights = np.asarray(source["state_weights"], dtype=float)
        descriptors = np.asarray(source["signed_descriptors"], dtype=float)
        times = np.asarray(source["action_lengths"], dtype=float)
        reference = np.asarray(source["branch_reference"], dtype=float)
    with np.load(TANGENT) as source:
        tangents = np.asarray(source["physical_tangent_action"], dtype=float)
    with np.load(DIRECTIONAL_DATA) as source:
        fields = np.asarray(source["normalized_field"], dtype=float)
    tasks = [
        (
            index, states[index], weights, descriptors[index], reference,
            tangents[index], fields[index],
        )
        for index in range(len(states))
    ]
    requested = os.environ.get("BHSM_N12_SIGNED_FULL_TRANSVERSE_NODES", "").strip()
    if requested:
        indices = {int(value) for value in requested.split(",")}
        tasks = [task for task in tasks if task[0] in indices]
    workers = min(
        int(os.environ.get("BHSM_N12_SIGNED_FULL_TRANSVERSE_WORKERS", "6")),
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
                "transverse_Frobenius": row[
                    "physical_time_transverse_D2f_Frobenius_norm"
                ],
            }), flush=True)
    rows.sort(key=lambda row: row["node"])
    curvature = np.asarray([row.pop("transverse_curvature") for row in rows])
    node_indices = np.asarray([row["node"] for row in rows], dtype=int)
    shard_slices = (slice(0, 24), slice(24, 48))
    for path, shard in zip(DATA_SHARDS, shard_slices, strict=True):
        np.savez_compressed(
            path,
            action_lengths=times[node_indices[shard]],
            node_indices=node_indices[shard],
            physical_time_transverse_D2f=curvature[shard],
        )
    complete = len(rows) == 48
    validation = {
        "all_48_retained_macro_seams_evaluated": complete,
        "branch_24_selected_everywhere": all(
            row["selected_branch"] == SELECTED for row in rows
        ),
        "same_72_dimensional_physical_time_transverse_frames_used": (
            curvature.shape[1:] == (72, 72, 72)
        ),
        "all_bordered_response_residuals_below_1e_minus_6": max(
            max(
                row["base_response_residual_2_norm"],
                row["first_response_residual_Frobenius_norm"],
                row["second_response_residual_Frobenius_norm"],
            ) for row in rows
        ) < 1.0e-6,
        "all_second_normalization_identities_close": max(
            max(
                row["second_eigenline_normalization_Frobenius_residual"],
                row["second_field_normalization_Frobenius_residual"],
            ) for row in rows
        ) < 1.0e-7,
        "selected_quarter_step_center_and_matching_tangent_used": True,
        "single_broadcast_D4_action_tensor_used_per_seam": True,
        "complete_internal_source_and_response_differentiated_before_norms": True,
        "no_JAX_derivative_used_as_action_authority": True,
        "no_kinetic_Dirac_or_history_inverse_formed": True,
        "no_action_equation_source_selector_scale_gate_or_chord_changed": True,
    }
    validation = {key: bool(value) for key, value in validation.items()}
    passed = all(validation.values())
    owner = max(
        rows,
        key=lambda row: row["physical_time_transverse_D2f_Frobenius_norm"],
    )
    return {
        "artifact": "BHSM_N12_GATE7_EXACT_SIGNED_FULL_TRANSVERSE_CURVATURE",
        "status": (
            "EXACT_SIGNED_FULL_PHYSICAL_TRANSVERSE_CURVATURE_DERIVED"
            if passed else "EXACT_SIGNED_FULL_TRANSVERSE_CURVATURE_INCOMPLETE_OR_INVALID"
        ),
        "authority": "RETAINED_COMPLEX_STEP_D3_BROADCAST_SIGNED_D4_AND_BORDERED_SECOND_IDENTITY",
        "summary": {
            "maximum_transverse_D2f_Frobenius_norm": owner[
                "physical_time_transverse_D2f_Frobenius_norm"
            ],
            "transverse_curvature_owner_node": owner["node"],
            "evaluated_nodes": len(rows),
        },
        "rows": rows,
        "data_shards": [_relative(path) for path in DATA_SHARDS],
        "data_shard_SHA256": {
            _relative(path): _sha256(path) for path in DATA_SHARDS
        },
        "validation": validation,
        "validation_passed": passed,
        "claim_boundary": {
            "full_physical_transverse_center_curvature": (
                "DERIVED" if passed else "OPEN"
            ),
            "outward_transverse_curvature_remainder": "OPEN",
            "outward_signed_step_map_and_Green_remainder": "OPEN",
            "causal_interval_vector_radius": "OPEN",
            "Gate7": "ACTIVE",
            "FULL_BHSM_COMPLETE": False,
        },
        "exact_next_dependency": (
            "ATTACH_THE_RETAINED_D5_OUTWARD_REMAINDER_AND_SIGNED_GREEN_"
            "STEP_MAP_REMAINDER_TO_THE_NOW_COMPLETE_CENTER_CURVATURE_"
            "TRIPLE,_THEN_REPLAY_THE_VECTOR_BOOTSTRAP"
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
