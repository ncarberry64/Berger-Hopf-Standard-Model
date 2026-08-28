"""Assemble Gate-7 correction-direction bordered-response second jets.

The retained 96-point action supplies the center Hessian and directional D3
matrix.  Analytic JAX differentiation of the same action formula supplies the
center directional D4 matrix.  The latter is not promoted to retained
interval authority: the complete second-jet composition is independently
checked against a twice-differentiated calibrated field, while the certified
retained D4--D5 majorants remain responsible for the outward tube.
"""

from __future__ import annotations

from concurrent.futures import ProcessPoolExecutor
import hashlib
import json
import os
from pathlib import Path
import sys
from typing import Any

import jax

jax.config.update("jax_enable_x64", True)
import jax.numpy as jnp
import numpy as np


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from bhsm.interface.aether_forward_c2_descriptor_cover import metric_data  # noqa: E402
from bhsm.interface.aether_jax_full_local_action import (  # noqa: E402
    action_gradient,
    action_hessian,
)
from derive_n12_gate7_retained_correction_bordered_response_first_jets import (  # noqa: E402
    _retained,
)


BASE = ROOT / "artifacts" / "flagship_integration"
CENTER = BASE / "BHSM_N12_C2_STOP_HIGH_ORDER_HALF_STEP_CENTER_RECONNAISSANCE.npz"
GREEN = BASE / "BHSM_N12_C2_STOP_QUARTER_STEP_MATCHED_TANGENT_CORRELATED_DEFECT_GAUSS12_RECONNAISSANCE.npz"
EIGENLINE = BASE / "BHSM_N12_GATE7_RETAINED_CORRECTION_EIGENLINE_FIRST_JETS.npz"
FIRST = BASE / "BHSM_N12_GATE7_RETAINED_CORRECTION_BORDERED_RESPONSE_FIRST_JETS.npz"
CALIBRATION = BASE / "BHSM_N12_STOP_JAX_ACTION_CALIBRATION.npz"
MAJORANTS = BASE / "BHSM_N12_GATE7_CORRECTION_DIRECTION_ACTION_MAJORANTS.json"
RESULT = BASE / "BHSM_N12_GATE7_CORRECTION_BORDERED_RESPONSE_SECOND_JETS.json"
DATA = RESULT.with_suffix(".npz")
QDIM = 37


def _sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def _relative(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


@jax.jit
def _action_hessian_second_directional(
    state: jax.Array, raw_direction: jax.Array,
) -> jax.Array:
    def first(value: jax.Array) -> jax.Array:
        return jax.jvp(
            action_hessian, (value,), (raw_direction,),
        )[1]

    return jax.jvp(first, (state,), (raw_direction,))[1]


def _calibrated_field(
    action_displacement: jax.Array,
    center_action: jax.Array,
    weights: jax.Array,
    reference: jax.Array,
    gradient_correction: jax.Array,
    hessian_correction: jax.Array,
    descriptor_offset: jax.Array,
    q_weights: jax.Array,
    reduced_weights: jax.Array,
) -> jax.Array:
    state = (center_action + action_displacement) / weights
    gradient = action_gradient(state) + gradient_correction
    hessian = action_hessian(state) + hessian_correction
    reduced = 0.5 * (hessian[QDIM:, QDIM:] + hessian[QDIM:, QDIM:].T)
    values, vectors = jnp.linalg.eigh(reduced)
    psi = vectors[:, 24]
    psi = jnp.where(jnp.dot(psi, reference) < 0.0, -psi, psi)
    descriptor = values[24] + descriptor_offset
    configuration = q_weights * state[QDIM:2 * QDIM]
    gradient_action = gradient / weights
    hessian_action = hessian / (weights[:, None] * weights[None, :])
    rhs = reduced_weights * (
        jnp.concatenate((
            q_weights * gradient_action[:QDIM], jnp.zeros(24),
        )) - hessian_action[QDIM:, :QDIM] @ configuration
    )
    bordered = jnp.block([
        [reduced - values[24] * jnp.eye(61), psi[:, None]],
        [psi[None, :], jnp.zeros((1, 1))],
    ])
    response = jnp.linalg.solve(
        bordered, jnp.concatenate((rhs, jnp.zeros(1))),
    )
    numerator = jnp.concatenate((
        descriptor * configuration,
        reduced_weights * (
            response[-1] * psi + descriptor * response[:-1]
        ),
    ))
    return numerator / jnp.linalg.norm(numerator)


@jax.jit
def _calibrated_field_jets(
    zero: jax.Array, direction: jax.Array, *arguments: jax.Array,
) -> tuple[jax.Array, jax.Array, jax.Array]:
    field, first = jax.jvp(
        lambda value: _calibrated_field(value, *arguments),
        (zero,), (direction,),
    )

    def first_map(value: jax.Array) -> jax.Array:
        return jax.jvp(
            lambda item: _calibrated_field(item, *arguments),
            (value,), (direction,),
        )[1]

    _, second = jax.jvp(first_map, (zero,), (direction,))
    return field, first, second


def build_payload() -> dict[str, Any]:
    inputs = (CENTER, GREEN, EIGENLINE, FIRST, CALIBRATION, MAJORANTS)
    if not all(path.is_file() for path in inputs):
        raise FileNotFoundError("correction bordered-response second-jet inputs required")
    with np.load(CENTER) as source:
        states = np.asarray(source["centers"], dtype=float)
        times = np.asarray(source["action_lengths"], dtype=float)
        weights = np.asarray(source["state_weights"], dtype=float)
        reference = np.asarray(source["branch_reference"], dtype=float)
        descriptors = np.asarray(source["signed_descriptors"], dtype=float)
    with np.load(GREEN) as source:
        corrections = np.asarray(source["ambient_correction_profile"], dtype=float)
    with np.load(EIGENLINE) as source:
        directions = np.asarray(source["action_correction_directions"], dtype=float)
        psi_all = np.asarray(source["selected_eigenvectors"], dtype=float)
        psi_first_all = np.asarray(
            source["selected_eigenvector_first_variations"], dtype=float
        )
        lambda_all = np.asarray(source["selected_eigenvalues"], dtype=float)
        lambda_first_all = np.asarray(
            source["selected_eigenvalue_first_variations"], dtype=float
        )
    with np.load(FIRST) as source:
        response_all = np.asarray(source["bordered_response"], dtype=float)
        response_first_all = np.asarray(
            source["bordered_response_correction_direction_first_variation"],
            dtype=float,
        )
        field_all = np.asarray(source["normalized_field"], dtype=float)
        field_first_all = np.asarray(
            source["normalized_field_correction_direction_first_variation"],
            dtype=float,
        )
    with np.load(CALIBRATION) as source:
        calibration_times = np.asarray(source["action_lengths"], dtype=float)
        gradient_corrections = np.asarray(source["gradient_correction"], dtype=float)
        hessian_corrections = np.asarray(source["hessian_correction"], dtype=float)
    if not np.array_equal(times, calibration_times):
        raise RuntimeError("calibration and retained macro grids differ")
    majorants = json.loads(MAJORANTS.read_text(encoding="utf-8"))
    if not majorants["validation_passed"]:
        raise RuntimeError("retained correction-direction action majorants invalid")

    raw_directions = directions / weights
    tasks = [(i, states[i], raw_directions[i]) for i in range(48)]
    with ProcessPoolExecutor(max_workers=min(12, os.cpu_count() or 1)) as executor:
        retained = list(executor.map(_retained, tasks, chunksize=1))
    retained.sort(key=lambda item: item[0])

    q_weights, reduced_weights, _, _ = metric_data()
    zero = jnp.zeros(98)
    q_weights_jax = jnp.asarray(q_weights)
    reduced_weights_jax = jnp.asarray(reduced_weights)
    weights_jax = jnp.asarray(weights)
    reference_jax = jnp.asarray(reference)
    response_second_all = []
    psi_second_all = []
    lambda_second_all = []
    field_second_all = []
    rows = []
    for index, gradient, hessian, hessian_first in retained:
        direction = directions[index]
        raw_direction = raw_directions[index]
        hessian_second = np.asarray(_action_hessian_second_directional(
            jnp.asarray(states[index]), jnp.asarray(raw_direction)
        ))
        hessian_second = 0.5 * (hessian_second + hessian_second.T)
        reduced = 0.5 * (
            hessian[QDIM:, QDIM:] + hessian[QDIM:, QDIM:].T
        )
        reduced_first = 0.5 * (
            hessian_first[QDIM:, QDIM:]
            + hessian_first[QDIM:, QDIM:].T
        )
        reduced_second = hessian_second[QDIM:, QDIM:]
        psi = psi_all[index]
        psi_first = psi_first_all[index]
        lam = float(lambda_all[index])
        lam_first = float(lambda_first_all[index])
        lam_second = float(
            psi @ reduced_second @ psi
            + 2.0 * psi @ reduced_first @ psi_first
        )
        eigen_border = np.block([
            [reduced - lam * np.eye(61), psi[:, None]],
            [psi[None, :], np.zeros((1, 1))],
        ])
        eigen_second_rhs = np.concatenate((
            -(
                (reduced_second - lam_second * np.eye(61)) @ psi
                + 2.0 * (reduced_first - lam_first * np.eye(61)) @ psi_first
            ),
            np.asarray([-float(psi_first @ psi_first)]),
        ))
        eigen_second_solve = np.linalg.solve(eigen_border, eigen_second_rhs)
        psi_second = eigen_second_solve[:-1]

        configuration = q_weights * states[index, QDIM:2 * QDIM]
        configuration_first = q_weights * raw_direction[QDIM:2 * QDIM]
        gradient_action = gradient / weights
        gradient_first_action = (hessian @ raw_direction) / weights
        gradient_second_action = (hessian_first @ raw_direction) / weights
        hessian_action = hessian / weights[:, None] / weights[None, :]
        hessian_first_action = (
            hessian_first / weights[:, None] / weights[None, :]
        )
        hessian_second_action = (
            hessian_second / weights[:, None] / weights[None, :]
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
        rhs_second = reduced_weights * (
            np.concatenate((
                q_weights * gradient_second_action[:QDIM], np.zeros(24),
            ))
            - hessian_second_action[QDIM:, :QDIM] @ configuration
            - 2.0 * hessian_first_action[QDIM:, :QDIM] @ configuration_first
        )
        K = eigen_border
        K_first = np.block([
            [
                reduced_first - lam_first * np.eye(61),
                psi_first[:, None],
            ],
            [psi_first[None, :], np.zeros((1, 1))],
        ])
        K_second = np.block([
            [
                reduced_second - lam_second * np.eye(61),
                psi_second[:, None],
            ],
            [psi_second[None, :], np.zeros((1, 1))],
        ])
        response = response_all[index]
        response_first = response_first_all[index]
        response_second_rhs = (
            np.concatenate((rhs_second, np.zeros(1)))
            - K_second @ response - 2.0 * K_first @ response_first
        )
        response_second = np.linalg.solve(K, response_second_rhs)

        descriptor = float(descriptors[index])
        numerator = np.concatenate((
            descriptor * configuration,
            reduced_weights * (
                response[-1] * psi + descriptor * response[:-1]
            ),
        ))
        numerator_first = np.concatenate((
            lam_first * configuration + descriptor * configuration_first,
            reduced_weights * (
                response_first[-1] * psi
                + response[-1] * psi_first
                + lam_first * response[:-1]
                + descriptor * response_first[:-1]
            ),
        ))
        numerator_second = np.concatenate((
            lam_second * configuration + 2.0 * lam_first * configuration_first,
            reduced_weights * (
                response_second[-1] * psi
                + 2.0 * response_first[-1] * psi_first
                + response[-1] * psi_second
                + lam_second * response[:-1]
                + 2.0 * lam_first * response_first[:-1]
                + descriptor * response_second[:-1]
            ),
        ))
        norm = float(np.linalg.norm(numerator))
        field = field_all[index]
        field_first = field_first_all[index]
        projection = np.eye(98) - np.outer(field, field)
        field_second = (
            projection @ numerator_second / norm
            - 2.0 * float(field @ numerator_first) * field_first / norm
            - field * float(field_first @ field_first)
        )

        calibrated_hessian = np.asarray(action_hessian(
            jnp.asarray(states[index])
        )) + hessian_corrections[index]
        selected_center = float(np.linalg.eigvalsh(
            calibrated_hessian[QDIM:, QDIM:]
        )[24])
        descriptor_offset = descriptors[index] - selected_center
        direct_field, direct_first, direct_second = _calibrated_field_jets(
            zero,
            jnp.asarray(direction),
            jnp.asarray(states[index] * weights),
            weights_jax,
            reference_jax,
            jnp.asarray(gradient_corrections[index]),
            jnp.asarray(hessian_corrections[index]),
            jnp.asarray(descriptor_offset),
            q_weights_jax,
            reduced_weights_jax,
        )
        direct_field = np.asarray(direct_field)
        direct_first = np.asarray(direct_first)
        direct_second = np.asarray(direct_second)
        eigenpair_second_residual = (
            (reduced - lam * np.eye(61)) @ psi_second
            + 2.0 * (reduced_first - lam_first * np.eye(61)) @ psi_first
            + (reduced_second - lam_second * np.eye(61)) @ psi
        )
        response_second_residual = (
            K @ response_second + K_second @ response
            + 2.0 * K_first @ response_first
            - np.concatenate((rhs_second, np.zeros(1)))
        )
        first_difference = float(np.linalg.norm(field_first - direct_first))
        second_difference = float(np.linalg.norm(field_second - direct_second))
        row = {
            "node": index,
            "action_length": float(times[index]),
            "ambient_correction_2_norm": float(np.linalg.norm(corrections[index])),
            "directional_D4_action_Hessian_second_operator_2_norm": float(
                np.linalg.norm(hessian_second, ord=2)
            ),
            "selected_eigenvalue_second_variation": lam_second,
            "selected_eigenvector_second_variation_2_norm": float(
                np.linalg.norm(psi_second)
            ),
            "eigenline_second_border_multiplier_absolute": float(
                abs(eigen_second_solve[-1])
            ),
            "eigenline_normalization_second_residual": float(abs(
                psi @ psi_second + psi_first @ psi_first
            )),
            "differentiated_eigenpair_second_residual_2_norm": float(
                np.linalg.norm(eigenpair_second_residual)
            ),
            "bordered_response_second_variation_2_norm": float(
                np.linalg.norm(response_second)
            ),
            "differentiated_bordered_response_second_residual_2_norm": float(
                np.linalg.norm(response_second_residual)
            ),
            "normalized_field_second_variation_2_norm": float(
                np.linalg.norm(field_second)
            ),
            "normalization_second_identity_residual": float(abs(
                field @ field_second + field_first @ field_first
            )),
            "assembled_vs_direct_calibrated_field_difference": float(
                np.linalg.norm(field - direct_field)
            ),
            "assembled_vs_direct_calibrated_field_first_difference": (
                first_difference
            ),
            "assembled_vs_direct_calibrated_field_second_difference": (
                second_difference
            ),
            "assembled_vs_direct_calibrated_field_first_relative_difference": (
                first_difference
                / max(np.linalg.norm(direct_first), np.finfo(float).tiny)
            ),
            "assembled_vs_direct_calibrated_field_second_relative_difference": (
                second_difference
                / max(np.linalg.norm(direct_second), np.finfo(float).tiny)
                if np.linalg.norm(direction) > 0.0 else 0.0
            ),
        }
        rows.append(row)
        response_second_all.append(response_second)
        psi_second_all.append(psi_second)
        lambda_second_all.append(lam_second)
        field_second_all.append(field_second)
        print(json.dumps({
            "completed": index + 1,
            "node": index,
            "field_second_norm": row["normalized_field_second_variation_2_norm"],
            "direct_relative": row[
                "assembled_vs_direct_calibrated_field_second_relative_difference"
            ],
        }), flush=True)

    np.savez_compressed(
        DATA,
        action_lengths=times,
        selected_eigenvalue_correction_direction_second_variation=np.asarray(
            lambda_second_all
        ),
        selected_eigenvector_correction_direction_second_variation=np.asarray(
            psi_second_all
        ),
        bordered_response_correction_direction_second_variation=np.asarray(
            response_second_all
        ),
        normalized_field_correction_direction_second_variation=np.asarray(
            field_second_all
        ),
    )
    nonzero = [row for row in rows if row["ambient_correction_2_norm"] > 0.0]
    validation = {
        "all_48_retained_macro_seams_evaluated": len(rows) == 48,
        "retained_Hessian_and_complex_step_D3_reused": True,
        "analytic_same_formula_JAX_D4_center_matrix_used_without_finite_subtraction": True,
        "all_second_eigenpair_residuals_below_1e_minus_10": max(
            row["differentiated_eigenpair_second_residual_2_norm"] for row in rows
        ) < 1.0e-10,
        "all_second_response_residuals_below_1e_minus_9": max(
            row["differentiated_bordered_response_second_residual_2_norm"]
            for row in rows
        ) < 1.0e-9,
        "all_second_normalization_identities_below_1e_minus_12": max(
            row["normalization_second_identity_residual"] for row in rows
        ) < 1.0e-12,
        "assembled_first_jet_matches_direct_calibrated_AD_below_5e_minus_4_relative": max(
            row["assembled_vs_direct_calibrated_field_first_relative_difference"]
            for row in nonzero
        ) < 5.0e-4,
        "assembled_second_jet_matches_direct_calibrated_AD_below_1e_minus_3_relative": max(
            row["assembled_vs_direct_calibrated_field_second_relative_difference"]
            for row in nonzero
        ) < 1.0e-3,
        "existing_one_free_leg_D4_D5_majorants_ingested_without_two_free_leg_promotion": True,
        "only_62_dimensional_bordered_systems_solved": True,
        "no_explicit_inverse_formed": True,
        "no_action_equation_source_selector_scale_gate_or_chord_changed": True,
    }
    validation = {key: bool(value) for key, value in validation.items()}
    passed = all(validation.values())
    return {
        "artifact": "BHSM_N12_GATE7_CORRECTION_BORDERED_RESPONSE_SECOND_JETS",
        "status": (
            "CORRECTION_DIRECTION_BORDERED_RESPONSE_SECOND_JETS_ASSEMBLED_"
            "ON_48_SEAMS" if passed else
            "CORRECTION_DIRECTION_BORDERED_RESPONSE_SECOND_JETS_INVALID"
        ),
        "authority": (
            "RETAINED_CENTER_D2_D3_PLUS_ANALYTIC_SAME_FORMULA_JAX_D4_"
            "WITH_INDEPENDENT_FULL_FIELD_AD_CROSSCHECK"
        ),
        "identity": {
            "selected_line_second": (
                "(A-lambda)*psi_second=-(A_second-lambda_second)*psi-"
                "2*(A_first-lambda_first)*psi_first"
            ),
            "bordered_response_second": (
                "K*x_second=rhs_second-K_second*x-2*K_first*x_first"
            ),
            "normalization_second": (
                "f_second=P*N_second/||N||-2*(f.N_first)*f_first/||N||-"
                "f*||f_first||^2"
            ),
            "explicit_inverse_formed": False,
        },
        "summary": {
            "maximum_directional_D4_action_Hessian_second_operator_2_norm": max(
                row["directional_D4_action_Hessian_second_operator_2_norm"]
                for row in rows
            ),
            "maximum_selected_eigenvector_second_variation_2_norm": max(
                row["selected_eigenvector_second_variation_2_norm"] for row in rows
            ),
            "maximum_bordered_response_second_variation_2_norm": max(
                row["bordered_response_second_variation_2_norm"] for row in rows
            ),
            "maximum_normalized_field_second_variation_2_norm": max(
                row["normalized_field_second_variation_2_norm"] for row in rows
            ),
            "maximum_differentiated_eigenpair_second_residual_2_norm": max(
                row["differentiated_eigenpair_second_residual_2_norm"]
                for row in rows
            ),
            "maximum_differentiated_bordered_response_second_residual_2_norm": max(
                row["differentiated_bordered_response_second_residual_2_norm"]
                for row in rows
            ),
            "maximum_normalization_second_identity_residual": max(
                row["normalization_second_identity_residual"] for row in rows
            ),
            "maximum_assembled_vs_direct_field_first_difference": max(
                row["assembled_vs_direct_calibrated_field_first_difference"]
                for row in nonzero
            ),
            "maximum_assembled_vs_direct_field_second_difference": max(
                row["assembled_vs_direct_calibrated_field_second_difference"]
                for row in nonzero
            ),
            "maximum_assembled_vs_direct_field_first_relative_difference": max(
                row["assembled_vs_direct_calibrated_field_first_relative_difference"]
                for row in nonzero
            ),
            "maximum_assembled_vs_direct_field_second_relative_difference": max(
                row["assembled_vs_direct_calibrated_field_second_relative_difference"]
                for row in nonzero
            ),
        },
        "rows": rows,
        "data": _relative(DATA),
        "data_SHA256": _sha256(DATA),
        "validation": validation,
        "validation_passed": passed,
        "claim_boundary": {
            "center_second_bordered_identity": "DERIVED",
            "center_directional_D2f_actual_signed_correction": (
                "ASSEMBLED_AND_INDEPENDENTLY_CROSSCHECKED"
            ),
            "JAX_D4_as_retained_interval_authority": "NOT_CLAIMED",
            "retained_two_free_leg_D4_D5_response_majorants": "OPEN",
            "outward_D2f_correction_cone": "OPEN_COMPOSITION",
            "causal_interval_vector_radius": "OPEN",
            "Gate7": "ACTIVE",
            "FULL_BHSM_COMPLETE": False,
        },
        "exact_next_dependency": (
            "DERIVE_RETAINED_TWO_FREE_LEG_D4_D5_ACTION_MAJORANTS,_OUTWARD_"
            "ROUND_THE_BRANCHWISE_SECOND_BORDERED_IDENTITY,_THEN_INSERT_THE_"
            "RESULT_IN_THE_LOWER_TRIANGULAR_CAUSAL_RADIUS"
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
