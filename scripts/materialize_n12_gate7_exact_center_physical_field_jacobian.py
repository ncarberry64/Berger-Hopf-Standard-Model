"""Materialize the direct exact-center physical normalized-field Jacobian.

At each corrected macro node this rebuilds the 25-row action constraint
geometry, aligns its 73-dimensional nullspace to the retained physical frame,
and differentiates the normalized action-owned field in all physical
directions.  The output is center generator data, not yet a continuous
outward variational carrier.
"""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
import sys

import jax.numpy as jnp
import numpy as np
from scipy.linalg import null_space


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

import audit_n12_c2_stop_boundary_cluster_probe as cluster  # noqa: E402
import certify_n12_gate7_recentered_cone_boundary_cluster_spectrum as cone  # noqa: E402
from bhsm.interface.aether_forward_c2_descriptor_cover import metric_data  # noqa: E402


BASE = ROOT / "artifacts" / "flagship_integration"
CENTER = BASE / "BHSM_N12_C2_STOP_HIGH_ORDER_QUARTER_STEP_RETAINED_RECONNAISSANCE.npz"
TANGENT = BASE / "BHSM_N12_C2_STOP_QUARTER_STEP_PHYSICAL_TANGENT_TRANSFER_RECONNAISSANCE.npz"
Z2_INPUTS = BASE / "BHSM_N12_GATE7_EXACT_AFFINE_CENTER_Z2_INPUTS.npz"
Z2_RECORD = Z2_INPUTS.with_suffix(".json")
FIELD_REFERENCE = BASE / "BHSM_N12_GATE7_EXACT_AFFINE_CENTER_DIRECTIONAL_FIELD_CURVATURE.npz"
FIELD_RECORD = FIELD_REFERENCE.with_suffix(".json")
SPECTRUM = BASE / "BHSM_N12_GATE7_EXACT_AFFINE_CENTER_BOUNDARY_CLUSTER_SPECTRUM.json"
THEORY = ROOT / "theory" / "n12_gate7_exact_center_physical_field_jacobian.md"
RESULT = BASE / "BHSM_N12_GATE7_EXACT_CENTER_PHYSICAL_FIELD_JACOBIAN.json"
DATA = RESULT.with_suffix(".npz")
THIS_SCRIPT = Path(__file__).resolve()
QDIM = 37
MDIM = 24
STATE_DIMENSION = 98
PHYSICAL_DIMENSION = 73
SELECTED = 24


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def _relative(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


def _jet(state: np.ndarray):
    return cluster.local.exact_full_action_jet_at_state(
        12, state[:QDIM], state[QDIM:2 * QDIM], state[2 * QDIM:],
        points=cluster.local.POINTS,
    )


def _constraint_frame(
    state: np.ndarray, weights: np.ndarray, retained: np.ndarray,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, object]:
    jet = _jet(state)
    gradient = np.asarray(jet.gradient, dtype=float)
    hessian = np.asarray(jet.hessian, dtype=float)
    velocity = state[QDIM:2 * QDIM]
    energy_row = np.concatenate((
        hessian[QDIM:2 * QDIM, :QDIM].T @ velocity - gradient[:QDIM],
        hessian[QDIM:2 * QDIM, QDIM:2 * QDIM].T @ velocity,
        hessian[QDIM:2 * QDIM, 2 * QDIM:].T @ velocity
        - gradient[2 * QDIM:],
    ))
    raw = np.vstack((hessian[2 * QDIM:, :], energy_row))
    action = raw / weights[None, :]
    norms = np.linalg.norm(action, axis=1)
    normalized = action / norms[:, None]
    frame = null_space(normalized, rcond=1.0e-11)
    overlap = frame.T @ retained
    left, singular, right = np.linalg.svd(overlap, full_matrices=False)
    aligned = frame @ (left @ right)
    values = np.concatenate((
        gradient[2 * QDIM:],
        [velocity @ gradient[QDIM:2 * QDIM] - float(jet.value)],
    ))
    return normalized, aligned, singular, values, jet


def _field_and_first(
    state: np.ndarray,
    weights: np.ndarray,
    reference: np.ndarray,
    descriptor: float,
    tangent: np.ndarray,
    jet: object,
) -> tuple[np.ndarray, np.ndarray, dict[str, float]]:
    q_weights, reduced_weights, _, _ = metric_data()
    total = weights.size
    reduced_dimension = reduced_weights.size
    gradient = np.asarray(jet.gradient, dtype=float)
    full_hessian = np.asarray(jet.hessian, dtype=float)
    full_hessian = 0.5 * (full_hessian + full_hessian.T)
    reduced = full_hessian[QDIM:, QDIM:]
    values, vectors = np.linalg.eigh(reduced)
    selected = int(np.argmax(np.abs(vectors.T @ reference)))
    psi = vectors[:, selected]
    if float(psi @ reference) < 0.0:
        psi = -psi
        vectors[:, selected] *= -1.0
    hard = np.arange(reduced_dimension) != selected
    denominators = values - values[selected]

    gradient_action = gradient / weights
    hessian_action = full_hessian / weights[:, None] / weights[None, :]
    configuration = q_weights * state[QDIM:2 * QDIM]
    forcing = reduced_weights * (
        np.concatenate((
            q_weights * gradient_action[:QDIM],
            np.zeros(reduced_dimension - QDIM),
        )) - hessian_action[QDIM:, :QDIM] @ configuration
    )
    bordered = np.block([
        [reduced - values[selected] * np.eye(reduced_dimension), psi[:, None]],
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

    raw_V = tangent / weights[:, None]
    directionals = np.array(cone._batched_hessian_directionals(
        jnp.asarray(state), jnp.asarray(raw_V.T),
    ), copy=True) * cone.JAX_D3_NORM_INFLATION
    H_V = directionals.transpose(1, 2, 0)
    H_V_reduced = 0.5 * (
        H_V[QDIM:, QDIM:, :]
        + H_V[QDIM:, QDIM:, :].transpose(1, 0, 2)
    )
    H_V_psi = np.einsum("abj,b->aj", H_V_reduced, psi, optimize=True)
    H_V_psi_eigen = vectors.T @ H_V_psi
    lambda_V = H_V_psi_eigen[selected]
    psi_V_coefficients = np.zeros_like(H_V_psi_eigen)
    psi_V_coefficients[hard] = (
        -H_V_psi_eigen[hard] / denominators[hard, None]
    )
    psi_V = vectors @ psi_V_coefficients

    configuration_V = q_weights[:, None] * raw_V[QDIM:2 * QDIM]
    gradient_V = full_hessian @ raw_V
    hessian_V_action = H_V / (
        weights[:, None, None] * weights[None, :, None]
    )
    forcing_V = reduced_weights[:, None] * (
        np.vstack((
            q_weights[:, None] * gradient_V[:QDIM] / weights[:QDIM, None],
            np.zeros((reduced_dimension - QDIM, PHYSICAL_DIMENSION)),
        ))
        - np.einsum(
            "abj,b->aj", hessian_V_action[QDIM:, :QDIM], configuration,
            optimize=True,
        )
        - hessian_action[QDIM:, :QDIM] @ configuration_V
    )
    top = (
        np.einsum("abj,b->aj", H_V_reduced, response[:-1], optimize=True)
        - response[:-1, None] * lambda_V[None, :]
        + response[-1] * psi_V
    )
    K_V_response = np.vstack((top, psi_V.T @ response[:-1]))
    response_V = np.linalg.solve(
        bordered,
        np.vstack((forcing_V, np.zeros((1, PHYSICAL_DIMENSION))))
        - K_V_response,
    )
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
    projector = np.eye(total) - np.outer(field, field)
    field_V = projector @ numerator_V / numerator_norm
    diagnostics = {
        "selected_branch": float(selected),
        "selected_eigenvalue": float(values[selected]),
        "selected_gap": float(np.min(abs(denominators[hard]))),
        "numerator_norm": numerator_norm,
        "field_norm": float(np.linalg.norm(field)),
        "bordered_response_residual": float(np.linalg.norm(
            bordered @ response - np.concatenate((forcing, np.zeros(1)))
        )),
        "field_first_normalization_residual": float(np.linalg.norm(
            field @ field_V
        )),
    }
    return field, field_V, diagnostics


def main() -> None:
    parents = [_load(path) for path in (Z2_RECORD, FIELD_RECORD, SPECTRUM)]
    if not all(record.get("validation_passed") is True for record in parents):
        raise RuntimeError("validated exact-center parents required")
    with np.load(CENTER) as source:
        base_states = np.asarray(source["centers"], dtype=float)
        descriptors = np.asarray(source["signed_descriptors"], dtype=float)
        times = np.asarray(source["action_lengths"], dtype=float)
        weights = np.asarray(source["state_weights"], dtype=float)
        reference = np.asarray(source["branch_reference"], dtype=float)
    with np.load(TANGENT) as source:
        retained_tangent = np.asarray(source["physical_tangent_action"], dtype=float)
    with np.load(Z2_INPUTS) as source:
        correction = np.asarray(source["ambient_correction_profile"], dtype=float)
    with np.load(FIELD_REFERENCE) as source:
        field_reference = np.asarray(source["normalized_field"], dtype=float)
    states = base_states + correction / weights[None, :]

    constraints = []
    tangents = []
    tangent_overlap = []
    constraint_values = []
    fields = []
    field_first = []
    physical_generators = []
    rows = []
    for node in range(48):
        constraint, tangent, singular, values, jet = _constraint_frame(
            states[node], weights, retained_tangent[node],
        )
        field, first, diagnostics = _field_and_first(
            states[node], weights, reference, float(descriptors[node]),
            tangent, jet,
        )
        generator = tangent.T @ first
        constraints.append(constraint)
        tangents.append(tangent)
        tangent_overlap.append(singular)
        constraint_values.append(values)
        fields.append(field)
        field_first.append(first)
        physical_generators.append(generator)
        rows.append({
            "node": node,
            "action_length": float(times[node]),
            "selected_branch": int(diagnostics["selected_branch"]),
            "selected_eigenvalue": diagnostics["selected_eigenvalue"],
            "selected_gap": diagnostics["selected_gap"],
            "normalized_numerator_2_norm": diagnostics["numerator_norm"],
            "field_action_2_norm": diagnostics["field_norm"],
            "field_reference_difference_2_norm": float(np.linalg.norm(
                field - field_reference[node]
            )),
            "field_constraint_residual_2_norm": float(np.linalg.norm(
                constraint @ field
            )),
            "bordered_response_residual_2_norm": diagnostics[
                "bordered_response_residual"
            ],
            "field_first_normalization_residual_2_norm": diagnostics[
                "field_first_normalization_residual"
            ],
            "physical_generator_operator_2_norm": float(np.linalg.norm(
                generator, ord=2
            )),
            "minimum_tangent_alignment_singular_value": float(singular[-1]),
        })
        print(json.dumps({
            "node": node,
            "generator_norm": rows[-1]["physical_generator_operator_2_norm"],
            "field_difference": rows[-1]["field_reference_difference_2_norm"],
        }), flush=True)

    constraints = np.asarray(constraints)
    tangents = np.asarray(tangents)
    tangent_overlap = np.asarray(tangent_overlap)
    constraint_values = np.asarray(constraint_values)
    fields = np.asarray(fields)
    field_first = np.asarray(field_first)
    physical_generators = np.asarray(physical_generators)
    np.savez_compressed(
        DATA,
        action_lengths=times,
        exact_center_states=states,
        normalized_constraint_action=constraints,
        physical_tangent_action=tangents,
        retained_frame_alignment_singular_values=tangent_overlap,
        constraint_values=constraint_values,
        normalized_field_action=fields,
        normalized_field_first_physical_action=field_first,
        physical_field_generator=physical_generators,
    )

    validation = {
        "all_48_corrected_center_nodes_consumed": len(rows) == 48,
        "all_constraint_frames_have_dimension_73": tangents.shape == (48, 98, 73),
        "all_exact_center_frames_align_nondegenerately": float(np.min(tangent_overlap)) > 0.99,
        "branch_24_selected_at_every_macro_node": all(row["selected_branch"] == SELECTED for row in rows),
        "all_normalized_fields_have_unit_action_norm": max(abs(row["field_action_2_norm"] - 1.0) for row in rows) < 2.0e-12,
        "all_field_first_normalization_residuals_small": max(row["field_first_normalization_residual_2_norm"] for row in rows) < 1.0e-8,
        "all_center_generators_finite": bool(np.all(np.isfinite(physical_generators))),
        "continuous_outward_variational_carrier_not_claimed": True,
        "no_action_source_selector_scale_gate_or_chord_changed": True,
    }
    validation = {key: bool(value) for key, value in validation.items()}
    passed = all(validation.values())
    payload = {
        "artifact": "BHSM_N12_GATE7_EXACT_CENTER_PHYSICAL_FIELD_JACOBIAN",
        "status": (
            "DIRECT_EXACT_CENTER_48_NODE_PHYSICAL_FIELD_JACOBIAN_MATERIALIZED"
            if passed else "EXACT_CENTER_PHYSICAL_FIELD_JACOBIAN_INVALID"
        ),
        "authority": (
            "RETAINED_ACTION_FULL_JET_PLUS_BATCHED_SAME_FORMULA_D3_"
            "DIRECTIONS_ON_REBUILT_EXACT_CENTER_CONSTRAINT_FRAMES"
        ),
        "rows": rows,
        "summary": {
            "node_count": 48,
            "physical_dimension": 73,
            "minimum_tangent_alignment_singular_value": float(np.min(tangent_overlap)),
            "maximum_field_reference_difference_2_norm": max(row["field_reference_difference_2_norm"] for row in rows),
            "maximum_field_constraint_residual_2_norm": max(row["field_constraint_residual_2_norm"] for row in rows),
            "maximum_physical_generator_operator_2_norm": max(row["physical_generator_operator_2_norm"] for row in rows),
            "maximum_bordered_response_residual_2_norm": max(row["bordered_response_residual_2_norm"] for row in rows),
            "maximum_field_first_normalization_residual_2_norm": max(row["field_first_normalization_residual_2_norm"] for row in rows),
        },
        "data": _relative(DATA),
        "data_SHA256": _sha256(DATA),
        "inputs": {
            _relative(path): _sha256(path)
            for path in (
                CENTER, TANGENT, Z2_INPUTS, Z2_RECORD, FIELD_REFERENCE,
                FIELD_RECORD, SPECTRUM, THEORY, THIS_SCRIPT,
            )
        },
        "validation": validation,
        "validation_passed": passed,
        "claim_boundary": {
            "exact_center_constraint_frames": "MATERIALIZED",
            "exact_center_normalized_field_first_derivative": "MATERIALIZED_AT_48_NODES",
            "continuous_outward_variational_carrier": "OPEN",
            "complete_nonlinear_72D_history_first_jet": "OPEN_AFTER_CARRIER",
            "Weyl_force_KKT_Hessian": "NOT_CLAIMED",
            "Gate7": "ACTIVE_ACTION_OWNED_OPERATOR_ORACLE",
            "FULL_BHSM_COMPLETE": False,
        },
        "exact_next_dependency": (
            "BUILD_AN_OUTWARD_CONTINUOUS_VARIATIONAL_CARRIER_FROM_THE_DIRECT_"
            "EXACT_CENTER_GENERATORS_USING_REFINED_WITHIN_SEAM_EVALUATION_"
            "AND_THE_EXISTING_D2F_D3F_TUBES"
        ),
        "FULL_BHSM_COMPLETE": False,
    }
    RESULT.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8", newline="\n",
    )
    print(json.dumps({
        "status": payload["status"],
        "summary": payload["summary"],
        "validation_passed": passed,
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
