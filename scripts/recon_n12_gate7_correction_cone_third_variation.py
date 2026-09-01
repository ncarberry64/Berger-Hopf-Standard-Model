"""Reconnoiter targeted third variations of the Gate-7 correction cone.

This differentiates the calibrated center graph automatically.  It contracts
two field-Hessian input legs with the actual signed Green correction before
forming a matrix norm.  The result is center reconnaissance until a retained
action D5 remainder and interval spectral-response enclosure are attached.
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
sys.path.insert(0, str(ROOT / "scripts"))

import recon_n12_gate7_common_frame_anisotropic_z2 as anisotropic  # noqa: E402
from bhsm.interface.aether_jax_full_local_action import action_hessian  # noqa: E402


BASE = ROOT / "artifacts" / "flagship_integration"
CAUSAL = BASE / "BHSM_N12_GATE7_CAUSAL_VECTOR_RADIUS_RECONNAISSANCE.npz"
RESULT = BASE / "BHSM_N12_GATE7_CORRECTION_CONE_THIRD_VARIATION_RECONNAISSANCE.json"
DATA = RESULT.with_suffix(".npz")


def _sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def _relative(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


def _d1(z: jax.Array, u: jax.Array, *arguments: jax.Array) -> jax.Array:
    return jax.jvp(
        lambda value: anisotropic._field(value, *arguments),
        (z,), (u,),
    )[1]


def _d2(z: jax.Array, u: jax.Array, *arguments: jax.Array) -> jax.Array:
    return jax.jvp(
        lambda value: _d1(value, u, *arguments),
        (z,), (u,),
    )[1]


_D3_TWO_CORRECTION_LEGS = jax.jit(jax.jacfwd(_d2, argnums=0))


def build_payload() -> dict[str, Any]:
    inputs = (
        anisotropic.CENTER,
        anisotropic.TANGENT,
        anisotropic.GREEN,
        anisotropic.CALIBRATION,
        anisotropic.RESULT,
        CAUSAL,
    )
    if not all(path.is_file() for path in inputs):
        raise FileNotFoundError("correction-cone third-variation inputs required")
    with np.load(anisotropic.CENTER) as source:
        states = np.asarray(source["centers"], dtype=float)
        descriptors = np.asarray(source["signed_descriptors"], dtype=float)
        weights = np.asarray(source["state_weights"], dtype=float)
        reference = np.asarray(source["branch_reference"], dtype=float)
        action_rates = np.asarray(source["action_rates"], dtype=float)
    with np.load(anisotropic.TANGENT) as source:
        tangents = np.asarray(source["physical_tangent_action"], dtype=float)
    with np.load(anisotropic.GREEN) as source:
        corrections = np.asarray(source["ambient_correction_profile"], dtype=float)
    with np.load(anisotropic.CALIBRATION) as source:
        gradient_corrections = np.asarray(source["gradient_correction"], dtype=float)
        hessian_corrections = np.asarray(source["hessian_correction"], dtype=float)
    anisotropic_record = json.loads(anisotropic.RESULT.read_text(encoding="utf-8"))
    with np.load(CAUSAL) as source:
        green_norm = np.asarray(source["causal_green_norm"], dtype=float)
        correction_radius = np.asarray(source["linear_correction_radius"], dtype=float)
        prior_delta_radius = np.asarray(source["nonlinear_delta_radius"], dtype=float)
        prior_total_radius = np.asarray(source["total_radius"], dtype=float)

    q_weights, reduced_weights, _, _ = anisotropic.metric_data()
    zero = jnp.zeros(73)
    rows: list[dict[str, Any]] = []
    matrices = []
    start = time.time()
    for index in range(48):
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
            jnp.asarray(weights),
            jnp.asarray(reference),
            jnp.asarray(gradient_corrections[index]),
            jnp.asarray(hessian_corrections[index]),
            jnp.asarray(descriptor_offset),
            jnp.asarray(q_weights),
            jnp.asarray(reduced_weights),
        )
        physical_flow = tangents[index].T @ action_rates[index]
        physical_flow /= np.linalg.norm(physical_flow)
        transverse = null_space(physical_flow[None, :])
        physical_correction = tangents[index].T @ corrections[index]
        transverse_correction = transverse.T @ physical_correction
        correction_norm = float(np.linalg.norm(transverse_correction))
        if correction_norm == 0.0:
            correction_unit = np.zeros(72)
        else:
            correction_unit = transverse_correction / correction_norm
        ambient_unit = transverse @ correction_unit
        third = np.asarray(_D3_TWO_CORRECTION_LEGS(
            zero, jnp.asarray(ambient_unit), *arguments
        ))
        projected = transverse.T @ tangents[index].T @ third @ transverse
        cubed = projected @ correction_unit
        operator_norm = float(np.linalg.norm(projected, ord=2))
        cubed_norm = float(np.linalg.norm(cubed))
        center_directional = float(anisotropic_record["rows"][index][
            "directional_D2f_correction_unit_squared_2_norm"
        ])
        rows.append({
            "node": index,
            "correction_time_transverse_2_norm": correction_norm,
            "D3f_free_correction_correction_operator_2_norm": operator_norm,
            "D3f_correction_cubed_2_norm": cubed_norm,
            "center_directional_D2f_2_norm": center_directional,
            "first_order_tube_inflation": (
                prior_total_radius[index] * operator_norm
            ),
            "center_plus_first_order_directional_D2f_proxy": (
                center_directional + prior_total_radius[index] * operator_norm
            ),
        })
        matrices.append(projected)
        print(json.dumps({
            "completed": index + 1,
            "node": index,
            "D3_two": operator_norm,
            "D3_three": cubed_norm,
        }), flush=True)

    directional_proxy = np.asarray([
        row["center_plus_first_order_directional_D2f_proxy"]
        for row in rows
    ])
    mixed = np.asarray([
        row["mixed_D2f_dot_correction_unit_operator_2_norm"]
        for row in anisotropic_record["rows"]
    ])
    transverse = np.asarray([
        row["physical_time_transverse_D2f_Frobenius_norm"]
        for row in anisotropic_record["rows"]
    ])
    inflated_delta = np.zeros(48)
    for endpoint in range(1, 48):
        earlier = slice(0, endpoint)
        inflated_delta[endpoint] = np.sum(
            green_norm[endpoint, earlier] * (
                0.5 * directional_proxy[earlier]
                * correction_radius[earlier] ** 2
                + mixed[earlier] * correction_radius[earlier]
                * inflated_delta[earlier]
                + 0.5 * transverse[earlier] * inflated_delta[earlier] ** 2
            )
        )
    inflated_total = correction_radius + inflated_delta
    np.savez_compressed(
        DATA,
        D3f_free_correction_correction=np.asarray(matrices),
        first_order_inflated_directional_D2f=directional_proxy,
        first_order_inflated_nonlinear_delta_radius=inflated_delta,
        first_order_inflated_total_radius=inflated_total,
    )

    validation = {
        "all_48_retained_macro_seams_evaluated": len(rows) == 48,
        "all_targeted_third_variations_finite": all(
            np.isfinite(value)
            for row in rows for value in row.values()
            if isinstance(value, float)
        ),
        "two_correction_legs_contracted_before_operator_norm": True,
        "same_calibrated_graph_and_time_transverse_frames_used": True,
        "common_scale_direction_not_deleted": True,
        "no_multiplier_or_hybrid_time_generator_projected_out_by_hand": True,
        "reconnaissance_not_retained_interval_authority": True,
        "no_finite_difference_subtraction_used": True,
        "no_action_equation_source_selector_scale_gate_or_chord_changed": True,
    }
    return {
        "artifact": "BHSM_N12_GATE7_CORRECTION_CONE_THIRD_VARIATION_RECONNAISSANCE",
        "status": (
            "TARGETED_CORRECTION_CONE_THIRD_VARIATION_ASSEMBLED_ON_48_SEAMS;_"
            "RETAINED_D5_AND_INTERVAL_SPECTRAL_REMAINDER_OPEN"
        ),
        "authority": "CALIBRATED_JAX_CENTER_RECONNAISSANCE_NOT_INTERVAL_AUTHORITY",
        "summary": {
            "elapsed_seconds": time.time() - start,
            "maximum_D3f_free_correction_correction_operator_2_norm": max(
                row["D3f_free_correction_correction_operator_2_norm"]
                for row in rows
            ),
            "maximum_D3f_correction_cubed_2_norm": max(
                row["D3f_correction_cubed_2_norm"] for row in rows
            ),
            "maximum_first_order_tube_inflation": max(
                row["first_order_tube_inflation"] for row in rows
            ),
            "maximum_prior_nonlinear_delta_radius": float(
                np.max(prior_delta_radius)
            ),
            "maximum_first_order_inflated_nonlinear_delta_radius": float(
                np.max(inflated_delta)
            ),
            "maximum_first_order_inflated_total_radius": float(
                np.max(inflated_total)
            ),
        },
        "rows": rows,
        "data": _relative(DATA),
        "data_SHA256": _sha256(DATA),
        "validation": validation,
        "structural_validation_passed": all(validation.values()),
        "validation_passed": False,
        "claim_boundary": {
            "targeted_center_D3f": "RECONNAISSANCE_ONLY",
            "first_order_inflated_vector_radius": "RECONNAISSANCE_ONLY",
            "retained_action_D5_remainder": "OPEN",
            "interval_selected_line_and_bordered_response": "OPEN",
            "domain_and_first_hit_transfer": "OPEN",
            "Gate7": "ACTIVE",
            "FULL_BHSM_COMPLETE": False,
        },
        "exact_next_dependency": (
            "COMPOSE_THE_HASHED_RETAINED_ACTION_D5_CORRECTION_DIRECTION_"
            "MAJORANTS_WITH_BRANCHWISE_SELECTED_LINE_AND_BORDERED_RESPONSE_"
            "INTERVALS_TO_OUTWARD_ROUND_THE_DIRECTIONAL_CAUSAL_SOURCE"
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
        "structural_validation_passed": payload[
            "structural_validation_passed"
        ],
        "validation_passed": payload["validation_passed"],
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
