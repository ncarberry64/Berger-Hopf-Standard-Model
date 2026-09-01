"""Reconnoiter the anisotropic Gate-7 nonlinear remainder on 48 seams.

The retained JAX action is calibrated to the authoritative exact value,
gradient, and Hessian at each stored seam.  Higher derivatives remain a
reconnaissance realization until an outward retained-action remainder is
attached.  No reconnaissance value is promoted to interval authority.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys
import time
from typing import Any

import jax

jax.config.update("jax_enable_x64", True)
import jax.numpy as jnp
import numpy as np
from scipy.linalg import null_space


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bhsm.interface.aether_forward_c2_descriptor_cover import metric_data  # noqa: E402
from bhsm.interface.aether_jax_full_local_action import (  # noqa: E402
    action_gradient,
    action_hessian,
)


BASE = ROOT / "artifacts" / "flagship_integration"
CENTER = BASE / "BHSM_N12_C2_STOP_HIGH_ORDER_HALF_STEP_CENTER_RECONNAISSANCE.npz"
TANGENT = BASE / "BHSM_N12_C2_STOP_HIGH_ORDER_HALF_STEP_PHYSICAL_TANGENT_TRANSFER_RECONNAISSANCE.npz"
JACOBIAN = BASE / "BHSM_N12_C2_STOP_HIGH_ORDER_HALF_STEP_GRAPH_JACOBIAN_RECONNAISSANCE.npz"
GREEN = BASE / "BHSM_N12_C2_STOP_QUARTER_STEP_MATCHED_TANGENT_CORRELATED_DEFECT_GAUSS12_RECONNAISSANCE.npz"
CALIBRATION = BASE / "BHSM_N12_STOP_JAX_ACTION_CALIBRATION.npz"
RESULT = BASE / "BHSM_N12_GATE7_COMMON_FRAME_ANISOTROPIC_Z2_RECONNAISSANCE.json"
DATA_RESULT = RESULT.with_suffix(".npz")


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def _relative(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


def _field(
    z: jax.Array,
    x0: jax.Array,
    tangent: jax.Array,
    weights: jax.Array,
    reference: jax.Array,
    gradient_correction: jax.Array,
    hessian_correction: jax.Array,
    descriptor_offset: jax.Array,
    q_weights: jax.Array,
    reduced_weights: jax.Array,
) -> jax.Array:
    state = (x0 + tangent @ z) / weights
    gradient = action_gradient(state) + gradient_correction
    hessian = action_hessian(state) + hessian_correction
    reduced = 0.5 * (
        hessian[37:, 37:] + hessian[37:, 37:].T
    )
    values, vectors = jnp.linalg.eigh(reduced)
    psi = vectors[:, 24]
    psi = jnp.where(jnp.dot(psi, reference) < 0.0, -psi, psi)
    descriptor = values[24] + descriptor_offset
    configuration = q_weights * state[37:74]
    gradient_action = gradient / weights
    hessian_action = hessian / (
        weights[:, None] * weights[None, :]
    )
    rhs = reduced_weights * (
        jnp.concatenate((
            q_weights * gradient_action[:37], jnp.zeros(24),
        )) - hessian_action[37:, :37] @ configuration
    )
    bordered = jnp.block([
        [
            reduced - values[24] * jnp.eye(61),
            psi[:, None],
        ],
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


_JACOBIAN = jax.jit(jax.jacfwd(_field, argnums=0))
_HESSIAN = jax.jit(jax.jacfwd(jax.jacfwd(_field, argnums=0), argnums=0))


def build_payload() -> dict[str, Any]:
    inputs = (CENTER, TANGENT, JACOBIAN, GREEN, CALIBRATION)
    if not all(path.is_file() for path in inputs):
        raise FileNotFoundError("anisotropic Z2 reconnaissance inputs required")
    with np.load(CENTER) as data:
        states = np.asarray(data["centers"], dtype=float)
        descriptors = np.asarray(data["signed_descriptors"], dtype=float)
        action_lengths = np.asarray(data["action_lengths"], dtype=float)
        weights = np.asarray(data["state_weights"], dtype=float)
        reference = np.asarray(data["branch_reference"], dtype=float)
    with np.load(TANGENT) as data:
        tangents = np.asarray(data["physical_tangent_action"], dtype=float)
    with np.load(JACOBIAN) as data:
        exact_jacobians = np.asarray(data["graph_Jacobian_action"], dtype=float)
    with np.load(GREEN) as data:
        corrections = np.asarray(data["ambient_correction_profile"], dtype=float)
    with np.load(CALIBRATION) as data:
        calibration_times = np.asarray(data["action_lengths"], dtype=float)
        gradient_corrections = np.asarray(data["gradient_correction"], dtype=float)
        hessian_corrections = np.asarray(data["hessian_correction"], dtype=float)
    if not np.array_equal(calibration_times, action_lengths):
        raise RuntimeError("macro calibration and center grids differ")

    q_weights_raw, reduced_weights_raw, _, _ = metric_data()
    q_weights = jnp.asarray(q_weights_raw)
    reduced_weights = jnp.asarray(reduced_weights_raw)
    weights_jax = jnp.asarray(weights)
    reference_jax = jnp.asarray(reference)
    zero = jnp.zeros(73)
    rows: list[dict[str, Any]] = []
    correction_directions = []
    mixed_operators = []
    directional_outputs = []
    start = time.time()
    for index in range(states.shape[0]):
        calibrated_hessian = np.asarray(action_hessian(
            jnp.asarray(states[index])
        )) + hessian_corrections[index]
        selected_center = float(np.linalg.eigvalsh(
            calibrated_hessian[37:, 37:]
        )[24])
        descriptor_offset = descriptors[index] - selected_center
        arguments = (
            jnp.asarray(states[index] * weights),
            jnp.asarray(tangents[index]),
            weights_jax,
            reference_jax,
            jnp.asarray(gradient_corrections[index]),
            jnp.asarray(hessian_corrections[index]),
            jnp.asarray(descriptor_offset),
            q_weights,
            reduced_weights,
        )
        field = np.asarray(_field(zero, *arguments))
        jacobian = np.asarray(_JACOBIAN(zero, *arguments))
        hessian = np.asarray(_HESSIAN(zero, *arguments))
        tangent = tangents[index]
        physical_flow = tangent.T @ field
        physical_flow /= np.linalg.norm(physical_flow)
        time_transverse = null_space(physical_flow[None, :])
        restricted = np.einsum(
            "oa,oij,ip,jq->apq",
            tangent, hessian, time_transverse, time_transverse,
            optimize=True,
        )
        restricted = np.einsum(
            "ar,apq->rpq", time_transverse, restricted, optimize=True,
        )
        physical_correction = tangent.T @ corrections[index]
        transverse_correction = time_transverse.T @ physical_correction
        correction_norm = float(np.linalg.norm(transverse_correction))
        if correction_norm == 0.0:
            correction_unit = np.zeros(72)
        else:
            correction_unit = transverse_correction / correction_norm
        mixed = np.einsum(
            "oij,j->oi", restricted, correction_unit, optimize=True,
        )
        directional = mixed @ correction_unit
        exact_projected = exact_jacobians[index] @ tangent
        jacobian_difference = float(np.linalg.norm(
            jacobian - exact_projected, ord=2,
        ))
        exact_projected_norm = float(np.linalg.norm(exact_projected, ord=2))
        row = {
            "node": index,
            "action_length": float(action_lengths[index]),
            "calibrated_JAX_vs_exact_projected_J_operator_difference": jacobian_difference,
            "calibrated_JAX_vs_exact_projected_J_relative_difference": (
                jacobian_difference / exact_projected_norm
            ),
            "ambient_D2f_Frobenius_norm": float(np.linalg.norm(hessian)),
            "physical_time_transverse_D2f_Frobenius_norm": float(
                np.linalg.norm(restricted)
            ),
            "correction_ambient_2_norm": float(np.linalg.norm(corrections[index])),
            "correction_time_transverse_2_norm": correction_norm,
            "correction_flow_component_absolute": float(abs(
                physical_flow @ physical_correction
            )),
            "mixed_D2f_dot_correction_unit_operator_2_norm": float(
                np.linalg.norm(mixed, ord=2)
            ),
            "directional_D2f_correction_unit_squared_2_norm": float(
                np.linalg.norm(directional)
            ),
            "quadratic_center_term_half_2_norm": float(
                0.5 * correction_norm**2 * np.linalg.norm(directional)
            ),
        }
        rows.append(row)
        correction_directions.append(correction_unit)
        mixed_operators.append(mixed)
        directional_outputs.append(directional)
        print(json.dumps({
            "completed": index + 1,
            "total": states.shape[0],
            "node": index,
            "mixed": row["mixed_D2f_dot_correction_unit_operator_2_norm"],
            "directional": row["directional_D2f_correction_unit_squared_2_norm"],
        }), flush=True)

    np.savez_compressed(
        DATA_RESULT,
        correction_time_transverse_unit=np.asarray(correction_directions),
        mixed_D2f_dot_correction_unit=np.asarray(mixed_operators),
        directional_D2f_correction_unit_squared=np.asarray(directional_outputs),
    )
    validation = {
        "all_48_retained_macro_seams_evaluated": len(rows) == 48,
        "all_values_finite": all(
            np.isfinite(value)
            for row in rows for value in row.values()
            if isinstance(value, float)
        ),
        "calibrated_center_Jacobians_compared_to_authoritative_exact_Jacobians": True,
        "constraint_tangent_and_time_transverse_projection_applied": True,
        "common_scale_direction_not_deleted": True,
        "actual_signed_Green_correction_direction_used": True,
        "reconnaissance_not_interval_authority": True,
        "no_multiplier_or_hybrid_time_generator_projected_out_by_hand": True,
        "no_action_equation_source_selector_scale_gate_or_chord_changed": True,
    }
    return {
        "artifact": "BHSM_N12_GATE7_COMMON_FRAME_ANISOTROPIC_Z2_RECONNAISSANCE",
        "status": "ANISOTROPIC_GREEN_IMAGE_CURVATURE_RECONNOITERED_ON_48_SEAMS;_OUTWARD_REMAINDER_OPEN",
        "authority": "CALIBRATED_JAX_CENTER_RECONNAISSANCE_NOT_INTERVAL_AUTHORITY",
        "summary": {
            "elapsed_seconds": time.time() - start,
            "maximum_calibrated_JAX_vs_exact_projected_J_relative_difference": max(
                row["calibrated_JAX_vs_exact_projected_J_relative_difference"]
                for row in rows
            ),
            "maximum_ambient_D2f_Frobenius_norm": max(
                row["ambient_D2f_Frobenius_norm"] for row in rows
            ),
            "maximum_physical_time_transverse_D2f_Frobenius_norm": max(
                row["physical_time_transverse_D2f_Frobenius_norm"] for row in rows
            ),
            "maximum_mixed_D2f_dot_correction_unit_operator_2_norm": max(
                row["mixed_D2f_dot_correction_unit_operator_2_norm"] for row in rows
            ),
            "maximum_directional_D2f_correction_unit_squared_2_norm": max(
                row["directional_D2f_correction_unit_squared_2_norm"] for row in rows
            ),
            "maximum_quadratic_center_term_half_2_norm": max(
                row["quadratic_center_term_half_2_norm"] for row in rows
            ),
        },
        "rows": rows,
        "data": _relative(DATA_RESULT),
        "data_SHA256": _sha256(DATA_RESULT),
        "validation": validation,
        "validation_passed": False,
        "claim_boundary": {
            "anisotropic_center_curvature": "RECONNAISSANCE_ONLY",
            "outward_calibration_and_between_seam_remainder": "OPEN",
            "literal_Z2": "OPEN",
            "Gate7": "ACTIVE",
            "FULL_BHSM_COMPLETE": False,
        },
        "exact_next_dependency": "BUILD_AN_OUTWARD_RETAINED_ACTION_REMAINDER_FOR_THE_MIXED_GREEN_IMAGE_CURVATURE_AND_AN_ANISOTROPIC_TRANSVERSE_RADIUS_VECTOR;_DO_NOT_USE_THE_FULL_73_BALL_FROBENIUS_MAXIMUM",
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
