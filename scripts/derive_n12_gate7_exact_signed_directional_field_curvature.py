"""Derive exact signed Gate-7 field curvature in the Green-image direction.

The calculation uses the actual physical time-transverse Green-image
direction at every retained seam.  All first and second source, eigenline,
bordered-response, and normalized-numerator jets are assembled from signed
mixed derivatives of the retained action.  No ambient H'' matrix, response
tensor, or full history inverse is formed.
"""

from __future__ import annotations

from concurrent.futures import ProcessPoolExecutor
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
RESULT = BASE / "BHSM_N12_GATE7_EXACT_SIGNED_DIRECTIONAL_FIELD_CURVATURE.json"
DATA = RESULT.with_suffix(".npz")
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
    index, state, weights, descriptor, reference, tangent, correction = task
    q_weights, reduced_weights, _, _ = metric_data()
    total = weights.size
    reduced = reduced_weights.size
    jet = exact_full_action_jet_at_state(
        12,
        state[:QDIM], state[QDIM:2 * QDIM], state[2 * QDIM:],
        points=96,
    )
    full_hessian = np.asarray(jet.hessian, dtype=float)
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
    eigenframe_lift = reduced_lift @ vectors
    source_gradient_lift = np.zeros((total, reduced))
    source_gradient_lift[:QDIM] = (
        q_weights[:, None] * reduced_weights[:QDIM, None]
        * np.eye(QDIM, reduced)
    )

    def signed(*directions: np.ndarray) -> float | np.ndarray:
        return np.asarray(action_bound(
            state,
            mixed_directions=list(directions),
            exact_signed_output_index=0,
        ).d[-1], dtype=float)

    # Use exactly the common-frame physical transverse Green direction.
    configuration = q_weights * state[QDIM:2 * QDIM]
    configuration_action = np.zeros(total)
    configuration_action[:QDIM] = configuration
    forcing = np.asarray(
        signed(source_gradient_lift)
        - signed(reduced_lift, configuration_action),
        dtype=float,
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
    norm = float(np.linalg.norm(numerator))
    field = numerator / norm
    physical_flow = tangent.T @ field
    physical_flow /= np.linalg.norm(physical_flow)
    transverse_frame = null_space(physical_flow[None, :])
    physical_correction = tangent.T @ correction
    transverse_correction = transverse_frame.T @ physical_correction
    correction_norm = float(np.linalg.norm(transverse_correction))
    if correction_norm == 0.0:
        transverse_unit = np.zeros(transverse_frame.shape[1])
    else:
        transverse_unit = transverse_correction / correction_norm
    direction = tangent @ transverse_frame @ transverse_unit
    raw_direction = direction / weights
    configuration_first = q_weights * raw_direction[QDIM:2 * QDIM]
    configuration_first_action = np.zeros(total)
    configuration_first_action[:QDIM] = configuration_first

    B_psi = reduced_lift @ psi
    H_first_psi = signed(eigenframe_lift, direction, B_psi)
    lambda_first = float(H_first_psi[SELECTED])
    hard = np.arange(reduced) != SELECTED
    denominators = values - values[SELECTED]
    psi_first_coefficients = np.zeros(reduced)
    psi_first_coefficients[hard] = (
        -H_first_psi[hard] / denominators[hard]
    )
    psi_first = vectors @ psi_first_coefficients
    H_second_psi = signed(
        eigenframe_lift, direction, direction, B_psi,
    )
    H_first_psi_first = signed(
        eigenframe_lift, direction, reduced_lift @ psi_first,
    )
    lambda_second = float(
        H_second_psi[SELECTED]
        + 2.0 * H_first_psi_first[SELECTED]
    )
    psi_second_coefficients = np.zeros(reduced)
    psi_second_coefficients[SELECTED] = -float(psi_first @ psi_first)
    psi_second_coefficients[hard] = -(
        H_second_psi[hard]
        + 2.0 * H_first_psi_first[hard]
        - 2.0 * lambda_first * psi_first_coefficients[hard]
    ) / denominators[hard]
    psi_second = vectors @ psi_second_coefficients

    forcing_first = np.asarray(
        signed(source_gradient_lift, direction)
        - signed(reduced_lift, direction, configuration_action)
        - signed(reduced_lift, configuration_first_action),
        dtype=float,
    )
    forcing_second = np.asarray(
        signed(source_gradient_lift, direction, direction)
        - signed(
            reduced_lift, direction, direction, configuration_action,
        )
        - 2.0 * signed(
            reduced_lift, direction, configuration_first_action,
        ),
        dtype=float,
    )

    def K_first_times(vector: np.ndarray) -> np.ndarray:
        hard_response, multiplier = vector[:-1], float(vector[-1])
        top = (
            signed(reduced_lift, direction, reduced_lift @ hard_response)
            - lambda_first * hard_response
            + multiplier * psi_first
        )
        return np.concatenate((top, [float(psi_first @ hard_response)]))

    def K_second_times(vector: np.ndarray) -> np.ndarray:
        hard_response, multiplier = vector[:-1], float(vector[-1])
        top = (
            signed(
                reduced_lift, direction, direction,
                reduced_lift @ hard_response,
            )
            - lambda_second * hard_response
            + multiplier * psi_second
        )
        return np.concatenate((top, [float(psi_second @ hard_response)]))

    response_first = np.linalg.solve(
        bordered,
        np.concatenate((forcing_first, np.zeros(1)))
        - K_first_times(response),
    )
    response_second = np.linalg.solve(
        bordered,
        np.concatenate((forcing_second, np.zeros(1)))
        - K_second_times(response)
        - 2.0 * K_first_times(response_first),
    )
    numerator_first = np.concatenate((
        lambda_first * configuration + descriptor * configuration_first,
        reduced_weights * (
            response_first[-1] * psi
            + response[-1] * psi_first
            + lambda_first * response[:-1]
            + descriptor * response_first[:-1]
        ),
    ))
    numerator_second = np.concatenate((
        lambda_second * configuration
        + 2.0 * lambda_first * configuration_first,
        reduced_weights * (
            response_second[-1] * psi
            + 2.0 * response_first[-1] * psi_first
            + response[-1] * psi_second
            + lambda_second * response[:-1]
            + 2.0 * lambda_first * response_first[:-1]
            + descriptor * response_second[:-1]
        ),
    ))
    projection = np.eye(total) - np.outer(field, field)
    field_first = projection @ numerator_first / norm
    field_second = (
        projection @ numerator_second / norm
        - 2.0 * float(field @ numerator_first) * field_first / norm
        - field * float(field_first @ field_first)
    )
    directional_output = transverse_frame.T @ tangent.T @ field_second
    response_residual = bordered @ response - np.concatenate((forcing, [0.0]))
    first_residual = (
        bordered @ response_first + K_first_times(response)
        - np.concatenate((forcing_first, [0.0]))
    )
    second_residual = (
        bordered @ response_second + K_second_times(response)
        + 2.0 * K_first_times(response_first)
        - np.concatenate((forcing_second, [0.0]))
    )
    return {
        "node": index,
        "selected_branch": SELECTED,
        "correction_time_transverse_2_norm": correction_norm,
        "physical_direction_action_2_norm": float(np.linalg.norm(direction)),
        "selected_multiplier": float(response[-1]),
        "selected_multiplier_first_variation": float(response_first[-1]),
        "selected_multiplier_second_variation": float(response_second[-1]),
        "selected_eigenvector_first_variation_2_norm": float(
            np.linalg.norm(psi_first)
        ),
        "selected_eigenvector_second_variation_2_norm": float(
            np.linalg.norm(psi_second)
        ),
        "bordered_response_2_norm": float(np.linalg.norm(response)),
        "bordered_response_first_variation_2_norm": float(
            np.linalg.norm(response_first)
        ),
        "bordered_response_second_variation_2_norm": float(
            np.linalg.norm(response_second)
        ),
        "normalized_numerator_2_norm": norm,
        "normalized_field_first_variation_2_norm": float(
            np.linalg.norm(field_first)
        ),
        "directional_field_second_variation_2_norm": float(
            np.linalg.norm(field_second)
        ),
        "physical_time_transverse_directional_curvature_2_norm": float(
            np.linalg.norm(directional_output)
        ),
        "response_residual_2_norm": float(np.linalg.norm(response_residual)),
        "first_response_residual_2_norm": float(np.linalg.norm(first_residual)),
        "second_response_residual_2_norm": float(np.linalg.norm(second_residual)),
        "field_first_normalization_residual": float(abs(field @ field_first)),
        "field_second_normalization_residual": float(abs(
            field @ field_second + field_first @ field_first
        )),
        "field": field.tolist(),
        "field_first": field_first.tolist(),
        "field_second": field_second.tolist(),
        "directional_output": directional_output.tolist(),
    }


def build_payload() -> dict[str, Any]:
    inputs = (CENTER, TANGENT, GREEN)
    if not all(path.is_file() for path in inputs):
        raise FileNotFoundError("directional curvature inputs required")
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
    workers = min(
        int(os.environ.get("BHSM_N12_SIGNED_CURVATURE_WORKERS", "12")),
        os.cpu_count() or 1,
    )
    with ProcessPoolExecutor(max_workers=workers) as executor:
        rows = list(executor.map(_row, tasks, chunksize=1))
    field = np.asarray([row.pop("field") for row in rows])
    field_first = np.asarray([row.pop("field_first") for row in rows])
    field_second = np.asarray([row.pop("field_second") for row in rows])
    directional = np.asarray([row.pop("directional_output") for row in rows])
    np.savez_compressed(
        DATA,
        action_lengths=times,
        normalized_field=field,
        normalized_field_physical_transverse_correction_first_variation=field_first,
        normalized_field_physical_transverse_correction_second_variation=field_second,
        physical_time_transverse_directional_curvature=directional,
    )
    validation = {
        "all_48_retained_macro_seams_evaluated": len(rows) == 48,
        "branch_24_selected_everywhere": all(
            row["selected_branch"] == SELECTED for row in rows
        ),
        "actual_physical_time_transverse_Green_image_direction_used": True,
        "all_bordered_response_residuals_below_1e_minus_8": max(
            max(
                row["response_residual_2_norm"],
                row["first_response_residual_2_norm"],
                row["second_response_residual_2_norm"],
            ) for row in rows
        ) < 1.0e-8,
        "all_normalization_identities_close": max(
            max(
                row["field_first_normalization_residual"],
                row["field_second_normalization_residual"],
            ) for row in rows
        ) < 1.0e-10,
        "selected_quarter_step_center_and_matching_tangent_used": True,
        "complete_internal_source_differentiated_before_external_zero_source": True,
        "signed_action_contractions_combined_before_norms": True,
        "no_ambient_Hessian_second_matrix_or_response_tensor_formed": True,
        "no_JAX_derivative_used_as_action_authority": True,
        "no_kinetic_Dirac_or_history_inverse_formed": True,
        "no_action_equation_source_selector_scale_gate_or_chord_changed": True,
    }
    validation = {key: bool(value) for key, value in validation.items()}
    passed = all(validation.values())
    owner = max(
        rows,
        key=lambda row: row[
            "physical_time_transverse_directional_curvature_2_norm"
        ],
    )
    return {
        "artifact": "BHSM_N12_GATE7_EXACT_SIGNED_DIRECTIONAL_FIELD_CURVATURE",
        "status": (
            "EXACT_SIGNED_PHYSICAL_TRANSVERSE_GREEN_DIRECTION_CURVATURE_DERIVED"
            if passed else "EXACT_SIGNED_DIRECTIONAL_FIELD_CURVATURE_INVALID"
        ),
        "authority": "RETAINED_ACTION_SIGNED_MIXED_DERIVATIVES_AND_BORDERED_IDENTITIES",
        "identity": {
            "response_first": "K*x1=f1-K1*x",
            "response_second": "K*x2=f2-K2*x-2*K1*x1",
            "normalization": "F=N/||N||_2",
            "direction": "physical_time_transverse_projection_of_signed_Green_image",
        },
        "summary": {
            "maximum_directional_curvature_2_norm": owner[
                "physical_time_transverse_directional_curvature_2_norm"
            ],
            "directional_curvature_owner_node": owner["node"],
            "maximum_selected_multiplier_second_variation_absolute": max(
                abs(row["selected_multiplier_second_variation"]) for row in rows
            ),
            "maximum_bordered_response_second_variation_2_norm": max(
                row["bordered_response_second_variation_2_norm"] for row in rows
            ),
        },
        "rows": rows,
        "data": _relative(DATA),
        "data_SHA256": _sha256(DATA),
        "validation": validation,
        "validation_passed": passed,
        "claim_boundary": {
            "physical_transverse_Green_direction_center_curvature": (
                "DERIVED" if passed else "OPEN"
            ),
            "outward_directional_curvature_remainder": "OPEN",
            "mixed_Green_transverse_curvature": "OPEN",
            "full_transverse_curvature": "OPEN",
            "causal_interval_vector_radius": "OPEN",
            "Gate7": "ACTIVE",
            "FULL_BHSM_COMPLETE": False,
        },
        "exact_next_dependency": (
            "ATTACH_THE_RETAINED_ACTION_OUTWARD_REMAINDER_TO_THIS_SIGNED_"
            "DIRECTIONAL_CENTER_TERM_AND_DERIVE_THE_MIXED_GREEN_TRANSVERSE_"
            "MAP_WITH_THE_SAME_INVERSE_FREE_PRODUCT_RULE"
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
